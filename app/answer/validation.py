"""Closed F3 records. Shape validation never establishes human approval."""
import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'specs/003-f3-grounded-rag/contracts/serialization.schema.json'
SCHEMAS = {p.resolve(): json.loads(p.read_text()) for p in (
    SCHEMA_PATH,
    ROOT / 'specs/002-f2-retrieval/contracts/serialization.schema.json',
    ROOT / 'specs/agentic-rag/f1-ingestion/contracts/serialization.schema.json',
)}


class AnswerError(ValueError):
    """Fixed safe error code; exception text contains no input or model output."""

    def __init__(self, code='invalid_input', *, fatal=False):
        self.code = code
        self.fatal = fatal
        super().__init__(code)


def strict_json(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise AnswerError()
            value[key] = item
        return value

    def invalid(_):
        raise AnswerError()

    try:
        result = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
        if not isinstance(result, dict):
            raise AnswerError()
        return result
    except (TypeError, ValueError, RecursionError, UnicodeError) as error:
        raise AnswerError() from error


def _shape(value, rule, path):
    if '$ref' in rule:
        file, fragment = rule['$ref'].split('#')
        target = (path.parent / file).resolve() if file else path
        if target not in SCHEMAS:
            raise AnswerError('configuration_mismatch')
        referenced = SCHEMAS[target]
        for key in fragment.strip('/').split('/'):
            referenced = referenced[key]
        _shape(value, referenced, target)
    if 'const' in rule and (value != rule['const'] or type(value) is not type(rule['const'])):
        raise AnswerError()
    if 'enum' in rule and not any(value == v and type(value) is type(v) for v in rule['enum']):
        raise AnswerError()
    for keyword in ('anyOf', 'oneOf'):
        if keyword in rule:
            count = 0
            for option in rule[keyword]:
                try:
                    _shape(value, option, path)
                    count += 1
                except AnswerError:
                    pass
            if not count or (keyword == 'oneOf' and count != 1):
                raise AnswerError()
    kind = rule.get('type')
    valid = {'object': type(value) is dict, 'array': type(value) is list,
             'string': type(value) is str, 'integer': type(value) is int,
             'number': type(value) in (int, float) and math.isfinite(value),
             'boolean': type(value) is bool, 'null': value is None}
    if kind and not valid[kind]:
        raise AnswerError()
    if type(value) in (int, float) and (not math.isfinite(value) or
            not rule.get('minimum', -math.inf) <= value <= rule.get('maximum', math.inf)):
        raise AnswerError()
    if isinstance(value, dict):
        props = rule.get('properties', {})
        if not set(rule.get('required', [])).issubset(value):
            raise AnswerError()
        if len(value) < rule.get('minProperties', 0):
            raise AnswerError()
        for key, item in value.items():
            if key in props:
                _shape(item, props[key], path)
            elif rule.get('additionalProperties') is False:
                raise AnswerError()
            elif isinstance(rule.get('additionalProperties'), dict):
                _shape(item, rule['additionalProperties'], path)
    if isinstance(value, list):
        if not rule.get('minItems', 0) <= len(value) <= rule.get('maxItems', math.inf):
            raise AnswerError()
        if rule.get('uniqueItems') and len({json.dumps(v, sort_keys=True, allow_nan=False) for v in value}) != len(value):
            raise AnswerError()
        for item in value:
            _shape(item, rule.get('items', {}), path)
    if isinstance(value, str):
        try:
            value.encode('utf-8')
        except UnicodeError as error:
            raise AnswerError() from error
        if not rule.get('minLength', 0) <= len(value) <= rule.get('maxLength', math.inf):
            raise AnswerError()
        if 'pattern' in rule and not re.search(rule['pattern'], value):
            raise AnswerError()
        if rule.get('format') == 'date-time':
            try:
                date = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if date.tzinfo is None or 'T' not in value:
                    raise ValueError()
            except ValueError as error:
                raise AnswerError() from error
    for condition in rule.get('allOf', []):
        if 'if' in condition:
            try:
                _shape(value, condition['if'], path)
                branch = 'then'
            except AnswerError:
                branch = 'else'
            _shape(value, condition.get(branch, {}), path)
        else:
            _shape(value, condition, path)


def validate_shape(value, name):
    try:
        _shape(value, SCHEMAS[SCHEMA_PATH]['$defs'][name], SCHEMA_PATH)
    except (RecursionError, TypeError, OverflowError) as error:
        raise AnswerError() from error
    return value


def bounded_json(path, limit):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise AnswerError('configuration_mismatch')
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise AnswerError('configuration_mismatch')
    return strict_json(raw)


def validate_catalog(value):
    validate_shape(value, 'GroundingCatalog')
    rules = {(r['use_case_id'], r['source_id'], r['revision'], r['content_sha256']) for r in value['source_rules']}
    if len(rules) != len(value['source_rules']) or len({r[:2] for r in rules}) != len(rules):
        raise AnswerError('catalog_mismatch')
    claims = {(c['use_case_id'], c['claim_id']): c for c in value['claims']}
    if len(claims) != len(value['claims']):
        raise AnswerError('catalog_mismatch')
    aliases = set()
    for c in value['claims']:
        for opponent in c['conflicting_claim_ids']:
            if opponent == c['claim_id'] or (c['use_case_id'], opponent) not in claims:
                raise AnswerError('catalog_mismatch')
        for alternative in c['support_alternatives']:
            for span in alternative:
                binding = (c['use_case_id'], span['source_id'], span['revision'], span['content_sha256'])
                if binding not in rules or span['end'] - span['start'] != len(span['quote']):
                    raise AnswerError('catalog_mismatch')
    for q in value['questions']:
        alias = (q['use_case_id'], q['question'])
        if alias in aliases or bool(q['expected_claim_ids']) != (q['insufficient_reason'] is None):
            raise AnswerError('catalog_mismatch')
        aliases.add(alias)
        if not any(r[0] == q['use_case_id'] for r in rules):
            raise AnswerError('catalog_mismatch')
        if any((q['use_case_id'], cid) not in claims for cid in q['expected_claim_ids']):
            raise AnswerError('catalog_mismatch')
    return value


def validate_receipt(value):
    validate_shape(value, 'RetrievalReceipt')
    result, snapshot = value['result'], value['scope_snapshot']
    if result['evidence_count'] != len(result['evidence']):
        raise AnswerError('configuration_mismatch')
    if result['status'] in ('matched', 'no_match'):
        if snapshot is None or snapshot['use_case_id'] != result['use_case_id']:
            raise AnswerError('configuration_mismatch')
        if result['configuration']['top_k'] != 3 or len(result['evidence']) > 3:
            raise AnswerError('configuration_mismatch')
    if snapshot is not None:
        sources = {s['source_id']: s for s in snapshot['represented_sources']}
        if len(sources) != len(snapshot['represented_sources']):
            raise AnswerError('configuration_mismatch')
        ids = set()
        previous_score = math.inf
        for rank, passage in enumerate(result['evidence'], 1):
            source = sources.get(passage['source_id'])
            if (passage['use_case_id'] != snapshot['use_case_id'] or not source
                    or any(passage[k] != source[k] for k in ('revision', 'content_sha256'))
                    or passage['end'] - passage['start'] != len(passage['text'])
                    or passage['rank'] != rank or passage['chunk_id'] in ids):
                raise AnswerError('configuration_mismatch')
            model = result['configuration']['model_configuration']
            if (any(passage[k] != model[k] for k in
                    ('model_id', 'model_commit', 'tokenizer_fingerprint', 'configuration_fingerprint'))
                    or not -1 <= passage['score'] <= 1
                    or passage['score'] < result['configuration']['min_score']
                    or passage['score'] > previous_score):
                raise AnswerError('configuration_mismatch')
            previous_score = passage['score']
            ids.add(passage['chunk_id'])
    if result['status'] == 'matched' and value['retrieval_searches'] != 1:
        raise AnswerError('configuration_mismatch')
    return value


def validate_result(value):
    validate_shape(value, 'AnswerResult')
    error = value['error']
    if error is not None and (error['code'] != error['message'] or
            (error['code'] != 'retrieval_failed' and error['cause_code'] is not None)):
        raise AnswerError('configuration_mismatch')
    if value['status'] == 'answered':
        used = {cid for c in value['claims'] for cid in c['chunk_ids']}
        ids = [p['chunk_id'] for p in value['citations']]
        if set(ids) != used or len(ids) != len(set(ids)) or len({c['claim_id'] for c in value['claims']}) != len(value['claims']):
            raise AnswerError('invalid_citation')
        if any(p['use_case_id'] != value['use_case_id'] for p in value['citations']):
            raise AnswerError('invalid_citation')
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
    if len(raw) + 1 > 131072:
        raise AnswerError('output_too_large')
    return value


def validate_assets(value, directory):
    validate_shape(value, 'GenerationAssetManifest')
    base = Path(directory)
    if base.is_symlink() or not base.is_dir() or any(parent.is_symlink() for parent in base.parents):
        raise AnswerError('configuration_mismatch')
    permitted = {'config.json', 'model.safetensors', 'tokenizer.json', 'tokenizer_config.json',
                 'special_tokens_map.json', 'generation_config.json'}
    required = {'config.json', 'model.safetensors', 'tokenizer.json', 'tokenizer_config.json'}
    names = [item['path'] for item in value['files']]
    if len(names) != len(set(names)) or not required <= set(names) <= permitted:
        raise AnswerError('configuration_mismatch')
    # Local-only loading can still consume optional files automatically.
    # The mounted snapshot must contain exactly the reviewed hash allowlist.
    if {path.name for path in base.iterdir()} != set(names):
        raise AnswerError('configuration_mismatch')
    for item in value['files']:
        path = base / item['path']
        if path.is_symlink() or not path.is_file():
            raise AnswerError('configuration_mismatch')
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(65536), b''):
                digest.update(block)
        if digest.hexdigest() != item['sha256']:
            raise AnswerError('configuration_mismatch')
    return value


def validate_cases(value, catalog):
    validate_shape(value, 'EvaluationCaseSet')
    validate_catalog(catalog)
    known = {(c['use_case_id'], c['claim_id']) for c in catalog['claims']}
    sources = {(s['use_case_id'], s['source_id']) for s in catalog['source_rules']}
    ids, positive, negative, shipping = set(), 0, 0, False
    for case in value['cases']:
        if case['case_id'] in ids:
            raise AnswerError('configuration_mismatch')
        ids.add(case['case_id'])
        if any((case['use_case_id'], cid) not in known for cid in case['expected_claim_ids']):
            raise AnswerError('configuration_mismatch')
        if any((case['use_case_id'], sid) not in sources for sid in case['acceptable_source_ids']):
            raise AnswerError('configuration_mismatch')
        if case['expected_status'] == 'answered':
            if not case['expected_claim_ids'] or case['expected_reason'] is not None:
                raise AnswerError('configuration_mismatch')
            positive += 1
        else:
            if case['expected_claim_ids'] or case['expected_reason'] is None:
                raise AnswerError('configuration_mismatch')
            negative += 1
            # Operator reviews semantics; this only checks presence of a labeled shipping probe.
            shipping |= 'shipping' in case['question'].lower()
    if positive < 3 or negative < 2 or not shipping:
        raise AnswerError('configuration_mismatch')
    return value


def validate_bindings(manifest, catalog, receipt, configuration, hashes, cases=None):
    """Cross-bind already reviewed records; this function never creates consent."""
    from app.ingestion.validation import validate_manifest

    try:
        validate_manifest(manifest)
        validate_catalog(catalog)
        validate_shape(receipt, 'F3ApprovalReceipt')
        validate_shape(configuration, 'AnswerConfiguration')
        for key in ('manifest', 'catalog', 'assets', 'generation', 'retrieval'):
            if not isinstance(hashes.get(key), str) or not re.fullmatch('[0-9a-f]{64}', hashes[key]):
                raise AnswerError('configuration_mismatch')
        if (catalog['manifest_sha256'] != hashes['manifest']
                or receipt['manifest_sha256'] != hashes['manifest']
                or receipt['catalog_sha256'] != hashes['catalog']):
            raise AnswerError('configuration_mismatch')
        generation = configuration['generation']
        if (generation['catalog_sha256'] != hashes['catalog']
                or generation['asset_manifest_sha256'] != hashes['assets']
                or generation['configuration_fingerprint'] != hashes['generation']):
            raise AnswerError('configuration_mismatch')
        approved = {(s['use_case_id'], s['source_id'], s['revision'], s['content_sha256'])
                    for s in manifest['allowed_sources']}
        reviewed = {(s['use_case_id'], s['source_id'], s['revision'], s['content_sha256'])
                    for s in catalog['source_rules']}
        # A manifest may authorize replacement revisions. Every catalog binding must
        # be approved; all source identities need a reviewed current-version rule.
        # A replacement remains a runtime catalog mismatch until matching rules exist.
        if not reviewed <= approved or {s[:2] for s in reviewed} != {s[:2] for s in approved}:
            raise AnswerError('catalog_mismatch')
        if len({s[:2] for s in approved}) > 32:
            raise AnswerError('catalog_mismatch')
        if cases is not None:
            validate_cases(cases, catalog)
            if (cases['manifest_sha256'] != hashes['manifest']
                    or cases['catalog_sha256'] != hashes['catalog']
                    or cases['generation_configuration_fingerprint'] != hashes['generation']
                    or cases['retrieval_configuration_fingerprint'] != hashes['retrieval']):
                raise AnswerError('configuration_mismatch')
    except (ValueError, TypeError, KeyError) as error:
        raise AnswerError('configuration_mismatch') from error
    return configuration
