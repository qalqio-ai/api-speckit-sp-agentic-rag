"""Closed F2/F1 record validation; no schema-valid record grants consent."""
import json
import math
import re
from datetime import datetime
from pathlib import Path

from app.ingestion.types import IngestionError

SCHEMA_PATH=Path(__file__).resolve().parents[2]/'specs/002-f2-retrieval/contracts/serialization.schema.json'
F1_PATH=Path(__file__).resolve().parents[2]/'specs/agentic-rag/f1-ingestion/contracts/serialization.schema.json'
SCHEMAS={p:json.loads(p.read_text()) for p in (SCHEMA_PATH,F1_PATH)}

def _shape(value, rule, path):
    if '$ref' in rule:
        file, fragment = rule['$ref'].split('#')
        target = (path.parent / file).resolve() if file else path
        if target not in SCHEMAS:
            raise IngestionError('configuration_mismatch')
        referenced = SCHEMAS[target]
        for key in fragment.strip('/').split('/'):
            referenced = referenced[key]
        _shape(value, referenced, target)
    if 'const' in rule and (value != rule['const'] or type(value) is not type(rule['const'])):
        raise IngestionError()
    if 'enum' in rule and not any(value == v and type(value) is type(v) for v in rule['enum']):
        raise IngestionError()
    for keyword in ('anyOf', 'oneOf'):
        if keyword in rule:
            count = 0
            for option in rule[keyword]:
                try:
                    _shape(value, option, path)
                    count += 1
                except IngestionError:
                    pass
            if not count or (keyword == 'oneOf' and count != 1):
                raise IngestionError()
    kind = rule.get('type')
    valid = {'object': type(value) is dict, 'array': type(value) is list,
             'string': type(value) is str, 'integer': type(value) is int,
             'number': type(value) in (int, float) and math.isfinite(value),
             'boolean': type(value) is bool, 'null': value is None}
    if kind and not valid[kind]:
        raise IngestionError()
    if type(value) in (int, float) and (not math.isfinite(value) or
            not rule.get('minimum', -math.inf) <= value <= rule.get('maximum', math.inf)):
        raise IngestionError()
    if isinstance(value, dict):
        props = rule.get('properties', {})
        if not set(rule.get('required', [])).issubset(value):
            raise IngestionError()
        if len(value) < rule.get('minProperties', 0):
            raise IngestionError()
        for key, item in value.items():
            if key in props:
                _shape(item, props[key], path)
            elif rule.get('additionalProperties') is False:
                raise IngestionError()
            elif isinstance(rule.get('additionalProperties'), dict):
                _shape(item, rule['additionalProperties'], path)
    if isinstance(value, list):
        if not rule.get('minItems', 0) <= len(value) <= rule.get('maxItems', math.inf):
            raise IngestionError()
        if rule.get('uniqueItems') and len({json.dumps(v, sort_keys=True, allow_nan=False) for v in value}) != len(value):
            raise IngestionError()
        for item in value:
            _shape(item, rule.get('items', {}), path)
    if isinstance(value, str):
        try:
            value.encode('utf-8')
        except UnicodeError as error:
            raise IngestionError() from error
        if not rule.get('minLength', 0) <= len(value) <= rule.get('maxLength', math.inf):
            raise IngestionError()
        if 'pattern' in rule and not re.search(rule['pattern'], value):
            raise IngestionError()
        if rule.get('format') == 'date-time':
            try:
                date = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if date.tzinfo is None or 'T' not in value:
                    raise ValueError()
            except ValueError as error:
                raise IngestionError() from error
    for condition in rule.get('allOf', []):
        if 'if' in condition:
            try:
                _shape(value, condition['if'], path)
                branch = 'then'
            except IngestionError:
                branch = 'else'
            _shape(value, condition.get(branch, {}), path)
        else:
            _shape(value, condition, path)


def validate_shape(value, name):
    try:
        _shape(value, SCHEMAS[SCHEMA_PATH]['$defs'][name], SCHEMA_PATH)
    except (RecursionError, TypeError, OverflowError) as error:
        raise IngestionError() from error
    return value


def parse_request(value):
    validate_shape(value,'RetrieveRequest')
    try:
        if len(value['question'].encode('utf-8'))>4096:
            raise IngestionError('question_too_long')
    except UnicodeError as error:
        raise IngestionError('invalid_input') from error
    return {**value,'top_k':value.get('top_k',3)}

def validate_result(value):
    validate_shape(value,'RetrievalResult')
    evidence=value['evidence']
    if value['evidence_count']!=len(evidence):
        raise IngestionError('invalid_search_result')
    if value['error'] and value['error']['code']!=value['error']['message']:
        raise IngestionError('configuration_mismatch')
    if evidence:
        if len(evidence)>value['configuration']['top_k'] or len({p['chunk_id'] for p in evidence})!=len(evidence):
            raise IngestionError('invalid_search_result')
        if evidence!=sorted(evidence,key=lambda p:(-p['score'],p['chunk_id'])):
            raise IngestionError('invalid_search_result')
        for rank,p in enumerate(evidence,1):
            if p['rank']!=rank or p['use_case_id']!=value['use_case_id'] or not -1<=p['score']<=1 or p['score']<value['configuration']['min_score'] or p['end']-p['start']!=len(p['text']):
                raise IngestionError('invalid_search_result')
    return value


def validate_cases(value,manifest,manifest_sha256,configuration_fingerprint):
    validate_shape(value,'EvaluationCaseSet')
    if value['manifest_sha256']!=manifest_sha256 or value['configuration_fingerprint']!=configuration_fingerprint:
        raise IngestionError('configuration_mismatch')
    ids=set();questions={};counts={'calibration':[0,0],'held_out':[0,0]}
    allowed={(s['use_case_id'],s['source_id']) for s in manifest['allowed_sources']}
    scopes={s[0] for s in allowed}
    for case in value['cases']:
        if case['case_id'] in ids or case['use_case_id'] not in scopes:
            raise IngestionError('configuration_mismatch')
        ids.add(case['case_id'])
        parse_request({'op':'retrieve','use_case_id':case['use_case_id'],'question':case['question']})
        expected=case['expected']
        question_key=(case['use_case_id'],case['question'])
        prior=questions.get(question_key)
        if prior is not None and (prior[0]!=expected or prior[1]!=case['split']):
            raise IngestionError('configuration_mismatch')
        questions[question_key]=(expected,case['split'])
        positive=expected['status']=='matched'
        if any((case['use_case_id'],source) not in allowed for source in expected.get('source_ids',[])):
            raise IngestionError('configuration_mismatch')
        counts[case['split']][0 if positive else 1]+=1
    if counts['calibration'][0]<1 or counts['calibration'][1]<1 or counts['held_out'][0]<3 or counts['held_out'][1]<2:
        raise IngestionError('configuration_mismatch')
    return value
