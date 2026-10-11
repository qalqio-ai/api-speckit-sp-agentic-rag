"""Strict F1 protocol validation. A manifest's human provenance is reviewed by the operator."""
import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path

from .types import IngestionError, SourceDocument

SCHEMA_PATH = Path(__file__).resolve().parents[2] / 'specs/agentic-rag/f1-ingestion/contracts/serialization.schema.json'
SCHEMA = json.loads(SCHEMA_PATH.read_text())


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    def invalid(_):
        raise ValueError('nonfinite')
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
        if not isinstance(value, dict):
            raise TypeError('object required')
        return value
    except (ValueError, TypeError, RecursionError) as error:
        raise IngestionError() from error


def _shape(value, rule):
    if '$ref' in rule:
        return _shape(value, SCHEMA['$defs'][rule['$ref'].split('/')[-1]])
    if 'const' in rule and (value != rule['const'] or type(value) is not type(rule['const'])):
        raise IngestionError()
    if 'enum' in rule and value not in rule['enum']:
        raise IngestionError()
    for keyword in ('anyOf', 'oneOf'):
        if keyword in rule:
            count = 0
            for option in rule[keyword]:
                try:
                    _shape(value, option)
                    count += 1
                except IngestionError:
                    pass
            if count == 0 or (keyword == 'oneOf' and count != 1):
                raise IngestionError()
    kind = rule.get('type')
    valid = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str), 'integer': type(value) is int,
             'number': type(value) in (int, float) and math.isfinite(value),
             'boolean': type(value) is bool, 'null': value is None}
    if kind and not valid[kind]:
        raise IngestionError()
    if kind == 'object':
        props = rule.get('properties', {})
        if not set(rule.get('required', [])).issubset(value):
            raise IngestionError()
        if len(value) < rule.get('minProperties', 0):
            raise IngestionError()
        for key, item in value.items():
            if key in props:
                _shape(item, props[key])
            elif rule.get('additionalProperties') is False:
                raise IngestionError()
            elif isinstance(rule.get('additionalProperties'), dict):
                _shape(item, rule['additionalProperties'])
    if kind == 'array':
        if not rule.get('minItems', 0) <= len(value) <= rule.get('maxItems', math.inf):
            raise IngestionError()
        if rule.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise IngestionError()
        for item in value:
            _shape(item, rule.get('items', {}))
    if kind == 'string':
        if len(value) < rule.get('minLength', 0) or ('pattern' in rule and not re.search(rule['pattern'], value)):
            raise IngestionError()
        if rule.get('format') == 'date-time':
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if dt.tzinfo is None or 'T' not in value:
                    raise ValueError()
            except ValueError as error:
                raise IngestionError() from error
    if kind in ('integer', 'number') and value < rule.get('minimum', -math.inf):
        raise IngestionError()
    for constraint in rule.get('allOf', []):
        if 'if' in constraint:
            try:
                _shape(value, constraint['if'])
                branch = 'then'
            except IngestionError:
                branch = 'else'
            _shape(value, constraint.get(branch, {}))
        else:
            _shape(value, constraint)


def validate_shape(value, name):
    _shape(value, SCHEMA['$defs'][name])
    return value


def validate_manifest(value):
    validate_shape(value, 'ApprovalManifest')
    keys = [(s['use_case_id'], s['source_id'], s['revision']) for s in value['allowed_sources']]
    if len(set(keys)) != len(keys):
        raise IngestionError()
    return value


def validate_document(document, manifest):
    if not isinstance(document, SourceDocument):
        raise IngestionError()
    parse_request({'op': 'ingest', **vars(document)})
    try:
        content = document.text.encode('utf-8')
    except UnicodeError as error:
        raise IngestionError() from error
    if len(content) > 65536:
        raise IngestionError()
    key = (document.use_case_id, document.source_id, document.revision, hashlib.sha256(content).hexdigest())
    if not any(key == (s['use_case_id'], s['source_id'], s['revision'], s['content_sha256'])
               for s in manifest['allowed_sources']):
        raise IngestionError('source_not_approved')
    return document


def parse_request(value):
    return validate_shape(value, 'OperationRequest')


def validate_endpoint(value):
    if value != 'http://qdrant:6333':
        raise IngestionError('endpoint_not_allowed')
    return value


def allowed_ids(manifest, use_case_id, source_id=None):
    ids = {s['source_id'] for s in manifest['allowed_sources'] if s['use_case_id'] == use_case_id}
    if not ids or (source_id is not None and source_id not in ids):
        raise IngestionError('source_not_approved')
    return sorted(ids) if source_id is None else [source_id]
