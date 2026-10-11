"""F3 behavior probes; synthetic memory only, never consent or live evidence."""
import copy
import json
from pathlib import Path

import pytest

from app.answer import validation

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / 'specs/003-f3-grounded-rag/contracts/serialization.schema.json'
SCHEMA = json.loads(SCHEMA_PATH.read_text())


def sample(rule, path=SCHEMA_PATH):
    if '$ref' in rule:
        file, fragment = rule['$ref'].split('#')
        path = (path.parent / file).resolve() if file else path
        schema = json.loads(path.read_text())
        for key in fragment.strip('/').split('/'):
            schema = schema[key]
        return sample(schema, path)
    if 'const' in rule:
        return rule['const']
    if 'enum' in rule:
        return rule['enum'][0]
    if 'anyOf' in rule or 'oneOf' in rule:
        return sample(rule.get('anyOf', rule.get('oneOf'))[0], path)
    kind = rule.get('type')
    if kind == 'object':
        value = {k: sample(rule['properties'][k], path) for k in rule.get('required', [])}
        if not value and rule.get('minProperties'):
            value['synthetic'] = sample(rule['additionalProperties'], path)
        for condition in rule.get('allOf', []):
            branch = condition.get('then', {})
            if all(value.get(k) in v.get('enum', [v.get('const')]) for k, v in condition.get('if', {}).get('properties', {}).items()):
                for key, override in branch.get('properties', {}).items():
                    merged = {**rule['properties'].get(key, {}), **override}
                    if 'type' in override:
                        merged.pop('anyOf', None)
                        merged.pop('oneOf', None)
                    value[key] = sample(merged, path)
        return value
    if kind == 'array':
        return [sample(rule['items'], path) for _ in range(rule.get('minItems', 0))]
    if kind == 'string':
        if rule.get('format') == 'date-time':
            return '2026-10-03T00:00:00Z'
        pattern = rule.get('pattern', '')
        if '8}' in pattern:
            return '00000000-0000-0000-0000-000000000001'
        if '64}' in pattern:
            return 'a' * 64
        if '40}' in pattern:
            return 'b' * 40
        return 'synthetic'
    if kind in ('integer', 'number'):
        return max(0, rule.get('minimum', 0))
    if kind == 'boolean':
        return False
    return None


@pytest.mark.parametrize('name', list(SCHEMA['$defs']))
def test_closed_shapes_reject_missing_and_extra_fields(name):
    rule = SCHEMA['$defs'][name]
    value = sample(rule)
    validation.validate_shape(value, name)
    for field in rule.get('required', value.keys()):
        missing = copy.deepcopy(value)
        del missing[field]
        with pytest.raises(ValueError):
            validation.validate_shape(missing, name)
    with pytest.raises(ValueError):
        validation.validate_shape({**value, 'unapproved': True}, name)


@pytest.mark.parametrize('raw', ['{"a":1,"a":2}', '{"a":NaN}', '{} trailing', '[]'])
def test_json_rejects_ambiguous_or_nonobject_input(raw):
    with pytest.raises(ValueError):
        validation.strict_json(raw)


@pytest.mark.parametrize('reason', ['no_evidence', 'conflicting_evidence'])
def test_model_cannot_declare_conflict_or_no_evidence(reason):
    with pytest.raises(ValueError):
        validation.validate_shape({'status': 'insufficient_evidence', 'claims': [], 'reason': reason}, 'ModelResponse')


def test_limits_reject_boolean_numeric_aliases():
    limits = sample(SCHEMA['$defs']['ExecutionLimits'])
    limits['num_beams'] = 1
    with pytest.raises(ValueError):
        validation.validate_shape(limits, 'ExecutionLimits')
    snapshot = sample(SCHEMA['$defs']['ScopeSnapshot'])
    receipt = sample(SCHEMA['$defs']['RetrievalReceipt'])
    receipt['scope_snapshot'] = snapshot
    receipt['retrieval_searches'] = True
    with pytest.raises(ValueError):
        validation.validate_shape(receipt, 'RetrievalReceipt')


def test_review_dates_are_real_calendar_dates():
    value = sample(SCHEMA['$defs']['ReviewAttribution'])
    value['approved_at'] = '2026-02-30T00:00:00Z'
    with pytest.raises(ValueError):
        validation.validate_shape(value, 'ReviewAttribution')


def test_bounded_json_rejects_oversize_before_parsing(tmp_path):
    path = tmp_path / 'probe.json'
    path.write_bytes(b' ' * 17)
    with pytest.raises(ValueError):
        validation.bounded_json(path, 16)


def catalog_probe():
    catalog = sample(SCHEMA['$defs']['GroundingCatalog'])
    rule = catalog['source_rules'][0]
    rule.update(use_case_id='scope', source_id='policy', revision='v1')
    claim = catalog['claims'][0]
    claim.update(use_case_id='scope', claim_id='returns', text='Unused items require a receipt.', conflicting_claim_ids=[])
    span = claim['support_alternatives'][0][0]
    span.update(source_id='policy', revision='v1', start=0, end=31, quote=claim['text'])
    catalog['questions'][0].update(use_case_id='scope', question='Return policy?', expected_claim_ids=['returns'], insufficient_reason=None)
    return catalog


def receipt_probe(evidence=None):
    receipt = sample(SCHEMA['$defs']['RetrievalReceipt'])
    result = receipt['result']
    passage = sample(SCHEMA['$defs']['AnswerResult'])['citations'][0]
    passage.update(use_case_id='scope', source_id='policy', revision='v1', start=0, end=31, text='Unused items require a receipt.', rank=1, score=0.9)
    evidence = [passage] if evidence is None else evidence
    result.update(use_case_id='scope', evidence=evidence, evidence_count=len(evidence), status='matched' if evidence else 'no_match')
    result['configuration']['top_k'] = 3
    receipt.update(scope_snapshot={'use_case_id':'scope', 'registry_fingerprint':'c'*64,
        'represented_sources':[{'source_id':'policy','revision':'v1','content_sha256':'a'*64}]}, retrieval_searches=1, retrieval_deadline=120)
    return receipt


@pytest.mark.parametrize('change', ['duplicate_alias', 'unknown_claim', 'bad_span', 'missing_source', 'wrong_scope', 'negative_with_claims'])
def test_catalog_rejects_incoherent_rules(change):
    catalog = catalog_probe()
    validation.validate_catalog(catalog)
    if change == 'duplicate_alias':
        catalog['questions'].append(copy.deepcopy(catalog['questions'][0]))
    if change == 'unknown_claim':
        catalog['questions'][0]['expected_claim_ids'] = ['absent']
    if change == 'bad_span':
        catalog['claims'][0]['support_alternatives'][0][0]['end'] = 30
    if change == 'missing_source':
        catalog['source_rules'][0]['revision'] = 'v2'
    if change == 'wrong_scope':
        catalog['claims'][0]['use_case_id'] = 'neighbor'
    if change == 'negative_with_claims':
        catalog['questions'][0]['insufficient_reason'] = 'unsupported_question'
    with pytest.raises(ValueError):
        validation.validate_catalog(catalog)


@pytest.mark.parametrize('change', ['missing_snapshot','foreign_scope','count_mismatch','duplicate_source','bad_offsets','top_k','bool_deadline'])
def test_receipt_requires_complete_consistent_current_metadata(change):
    value = receipt_probe()
    validation.validate_receipt(value)
    if change == 'missing_snapshot':
        value['scope_snapshot'] = None
    if change == 'foreign_scope':
        value['result']['evidence'][0]['use_case_id'] = 'neighbor'
    if change == 'count_mismatch':
        value['result']['evidence_count'] = 2
    if change == 'duplicate_source':
        value['scope_snapshot']['represented_sources'] *= 2
    if change == 'bad_offsets':
        value['result']['evidence'][0]['end'] -= 1
    if change == 'top_k':
        value['result']['configuration']['top_k'] = 4
    if change == 'bool_deadline':
        value['retrieval_deadline'] = True
    with pytest.raises(ValueError):
        validation.validate_receipt(value)


def test_result_requires_every_citation_used_and_error_equality():
    result = sample(SCHEMA['$defs']['AnswerResult'])
    result['error'] = {'code':'invalid_input','message':'unknown_operation','cause_code':None}
    result.update(status='failed',claims=[],citations=[])
    with pytest.raises(ValueError):
        validation.validate_result(result)


from app.answer import grounding


def test_complete_reviewed_support_and_exact_rendering():
    catalog, receipt = catalog_probe(), receipt_probe()
    required = grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],receipt['result']['evidence'])
    response = {'status':'answered','reason':None,'claims':[{'claim_id':'returns','text':'Unused items require a receipt.','chunk_ids':[receipt['result']['evidence'][0]['chunk_id']]}]}
    claims, citations = grounding.validate_claims(response, required, receipt['result']['evidence'])
    assert claims == response['claims']
    assert citations == receipt['result']['evidence']
    response['claims'][0]['text'] = 'Any item can be returned.'
    with pytest.raises(ValueError):
        grounding.validate_claims(response, required, receipt['result']['evidence'])


@pytest.mark.parametrize('question',['return policy?','Return policy? ','What are returns?'])
def test_unseen_answerable_alias_abstains(question):
    receipt = receipt_probe()
    with pytest.raises(ValueError,match='unsupported_question'):
        grounding.eligible(catalog_probe(),'scope',question,receipt['scope_snapshot'],receipt['result']['evidence'])


def test_catalog_requires_full_current_source_coverage():
    receipt = receipt_probe()
    receipt['scope_snapshot']['represented_sources'].append({'source_id':'other','revision':'v1','content_sha256':'d'*64})
    with pytest.raises(ValueError,match='catalog_mismatch'):
        grounding.eligible(catalog_probe(),'scope','Return policy?',receipt['scope_snapshot'],receipt['result']['evidence'])


def test_valid_id_with_irrelevant_evidence_does_not_support_claim():
    catalog, receipt = catalog_probe(), receipt_probe()
    evidence = receipt['result']['evidence']
    required = grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],evidence)
    other = copy.deepcopy(evidence[0]);other.update(chunk_id='00000000-0000-0000-0000-000000000002',text='Shipping information irrelevant.',end=31)
    response={'status':'answered','reason':None,'claims':[{'claim_id':'returns','text':catalog['claims'][0]['text'],'chunk_ids':[other['chunk_id']]}]}
    with pytest.raises(ValueError,match='grounding_failed'):
        grounding.validate_claims(response,required,[*evidence,other])


def test_asset_manifest_rejects_traversal_symlink_duplicate_or_unlisted_files(tmp_path):
    from app.answer.validation import validate_assets
    value = sample(SCHEMA['$defs']['GenerationAssetManifest'])
    value['files'] = [{'path':'config.json','sha256':'a'*64},{'path':'model.safetensors','sha256':'b'*64},{'path':'tokenizer.json','sha256':'c'*64},{'path':'tokenizer_config.json','sha256':'d'*64}]
    # Hash validity must be checked against files, not merely format.
    with pytest.raises(ValueError):
        validate_assets(value, tmp_path)
    for filename in ['../config.json','unsafe.pkl','sub/config.json']:
        invalid = copy.deepcopy(value);invalid['files'][0]['path'] = filename
        with pytest.raises(ValueError):
            validate_assets(invalid, tmp_path)
    value['files'].append(copy.deepcopy(value['files'][0]))
    with pytest.raises(ValueError):
        validate_assets(value,tmp_path)


def test_case_set_requires_frozen_known_claims_and_shipping_negative():
    from app.answer.validation import validate_cases
    cases = sample(SCHEMA['$defs']['EvaluationCaseSet'])
    for index,c in enumerate(cases['cases']):
        c.update(case_id=str(index),use_case_id='scope',question='Return policy?',expected_claim_ids=['returns'],expected_reason=None,acceptable_source_ids=['policy'])
    for c, question in zip(cases['cases'][3:], ['What is shipping?', 'Other?']):
        c.update(question=question,expected_status='insufficient_evidence',expected_claim_ids=[],expected_reason='unsupported_question')
    validate_cases(cases,catalog_probe())
    cases['cases'][0]['expected_claim_ids']=['missing']
    with pytest.raises(ValueError):
        validate_cases(cases,catalog_probe())


@pytest.mark.parametrize('mutation',['partial','opposition_missing','opposition_returned','irrelevant_conflict'])
def test_partial_conditions_and_relevant_conflicts(mutation):
    catalog,receipt = catalog_probe(),receipt_probe()
    evidence=receipt['result']['evidence']
    claim=catalog['claims'][0]
    if mutation == 'partial':
        evidence[0].update(text='Unused items',end=12)
        with pytest.raises(ValueError,match='unsupported_question'):
            grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],evidence)
        return
    opponent=copy.deepcopy(claim);opponent.update(claim_id='opposite',text='No returns.',conflicting_claim_ids=[])
    opponent['support_alternatives'][0][0].update(start=32,end=43,quote='No returns.')
    catalog['claims'].append(opponent)
    if mutation != 'irrelevant_conflict':
        claim['conflicting_claim_ids']=['opposite']
    if mutation == 'opposition_returned':
        passage=copy.deepcopy(evidence[0]);passage.update(chunk_id='00000000-0000-0000-0000-000000000002',start=32,end=43,text='No returns.')
        evidence.append(passage)
    if mutation == 'irrelevant_conflict':
        assert grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],evidence)
    else:
        with pytest.raises(ValueError,match='conflicting_evidence' if mutation=='opposition_returned' else 'unsupported_question'):
            grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],evidence)


@pytest.mark.parametrize('field,value',[('tokenizer_fingerprint','d'*64),('configuration_fingerprint','e'*64),('model_commit','f'*40),('score',99)])
def test_receipt_rejects_mismatched_embedding_provenance_and_impossible_scores(field,value):
    receipt=receipt_probe()
    receipt['result']['evidence'][0][field]=value
    with pytest.raises(ValueError):
        validation.validate_receipt(receipt)


def test_later_returned_opposition_has_priority_over_earlier_missing_opposition():
    catalog,receipt=catalog_probe(),receipt_probe()
    claim=catalog['claims'][0]
    for name,quote,start in [('first','Never return.',40),('second','No returns.',60)]:
        opponent=copy.deepcopy(claim)
        opponent.update(claim_id=name,text=quote,conflicting_claim_ids=[])
        opponent['support_alternatives'][0][0].update(start=start,end=start+len(quote),quote=quote)
        catalog['claims'].append(opponent)
    claim['conflicting_claim_ids']=['first','second']
    passage=copy.deepcopy(receipt['result']['evidence'][0])
    passage.update(chunk_id='00000000-0000-0000-0000-000000000002',start=60,end=71,text='No returns.')
    with pytest.raises(ValueError,match='conflicting_evidence'):
        grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],[*receipt['result']['evidence'],passage])


def test_receipt_rejects_increasing_scores_and_below_threshold():
    receipt=receipt_probe()
    second=copy.deepcopy(receipt['result']['evidence'][0])
    second.update(chunk_id='00000000-0000-0000-0000-000000000002',rank=2,score=0.99)
    receipt['result']['evidence'].append(second);receipt['result']['evidence_count']=2
    with pytest.raises(ValueError):
        validation.validate_receipt(receipt)
    receipt=receipt_probe();receipt['result']['configuration']['min_score']=0.95
    with pytest.raises(ValueError):
        validation.validate_receipt(receipt)


@pytest.mark.parametrize('order',[['returns','missing'],['missing','returns']])
def test_full_question_support_precedes_conflicts_independent_of_claim_order(order):
    catalog,receipt=catalog_probe(),receipt_probe()
    original=catalog['claims'][0]
    missing=copy.deepcopy(original);missing.update(claim_id='missing',text='Missing condition.',conflicting_claim_ids=[])
    missing['support_alternatives'][0][0].update(start=80,end=98,quote='Missing condition.')
    opposition=copy.deepcopy(original);opposition.update(claim_id='opposite',text='No returns.',conflicting_claim_ids=[])
    opposition['support_alternatives'][0][0].update(start=40,end=51,quote='No returns.')
    original['conflicting_claim_ids']=['opposite']
    catalog['claims'].extend([missing,opposition]);catalog['questions'][0]['expected_claim_ids']=order
    passage=copy.deepcopy(receipt['result']['evidence'][0]);passage.update(chunk_id='00000000-0000-0000-0000-000000000002',start=40,end=51,text='No returns.')
    with pytest.raises(ValueError,match='unsupported_question'):
        grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],[*receipt['result']['evidence'],passage])


@pytest.mark.parametrize('name',list(SCHEMA['$defs']))
def test_contract_fields_reject_wrong_types_nullability_and_array_overflow(name):
    rule=SCHEMA['$defs'][name]
    value=sample(rule)
    for field,current in value.items():
        broken=copy.deepcopy(value)
        broken[field]=[] if not isinstance(current,list) else {}
        with pytest.raises(ValueError):
            validation.validate_shape(broken,name)
        field_rule=rule.get('properties',{}).get(field,{})
        if field_rule.get('type')=='array' and 'maxItems' in field_rule:
            broken=copy.deepcopy(value)
            item=sample(field_rule['items'])
            broken[field]=[copy.deepcopy(item) for _ in range(field_rule['maxItems']+1)]
            with pytest.raises(ValueError):
                validation.validate_shape(broken,name)
        if current is not None and field_rule.get('type') not in (None,'null'):
            broken=copy.deepcopy(value);broken[field]=None
            with pytest.raises(ValueError):
                validation.validate_shape(broken,name)


def test_frozen_catalog_receipt_manifest_and_configuration_bindings():
    catalog=catalog_probe()
    manifest=sample({'$ref':'../../agentic-rag/f1-ingestion/contracts/serialization.schema.json#/$defs/ApprovalManifest'})
    manifest['allowed_sources'][0].update(use_case_id='scope',source_id='policy',revision='v1',content_sha256='a'*64)
    receipt=sample(SCHEMA['$defs']['F3ApprovalReceipt'])
    config=sample(SCHEMA['$defs']['AnswerConfiguration'])
    hashes={'manifest':'a'*64,'catalog':'b'*64,'assets':'c'*64,'generation':'d'*64,'retrieval':'e'*64}
    catalog['manifest_sha256']=hashes['manifest']
    receipt.update(manifest_sha256=hashes['manifest'],catalog_sha256=hashes['catalog'])
    config['generation'].update(catalog_sha256=hashes['catalog'],asset_manifest_sha256=hashes['assets'],configuration_fingerprint=hashes['generation'])
    validation.validate_bindings(manifest,catalog,receipt,config,hashes)
    receipt['catalog_sha256']='f'*64
    with pytest.raises(ValueError):
        validation.validate_bindings(manifest,catalog,receipt,config,hashes)


def test_asset_hashes_allow_exact_files_and_reject_symlinks(tmp_path):
    import hashlib
    value=sample(SCHEMA['$defs']['GenerationAssetManifest'])
    value['files']=[]
    for filename in ['config.json','model.safetensors','tokenizer.json','tokenizer_config.json']:
        path=tmp_path/filename;path.write_bytes(b'synthetic-not-a-model')
        value['files'].append({'path':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    validation.validate_assets(value,tmp_path)
    (tmp_path/'config.json').unlink()
    (tmp_path/'config.json').symlink_to(tmp_path/'tokenizer.json')
    with pytest.raises(ValueError):
        validation.validate_assets(value,tmp_path)


@pytest.mark.parametrize('filename',['special_tokens_map.json','generation_config.json','custom.py'])
def test_asset_directory_rejects_unlisted_loader_inputs(tmp_path,filename):
    import hashlib
    value=sample(SCHEMA['$defs']['GenerationAssetManifest'])
    value['files']=[]
    for name in ['config.json','model.safetensors','tokenizer.json','tokenizer_config.json']:
        raw=b'synthetic';(tmp_path/name).write_bytes(raw)
        value['files'].append({'path':name,'sha256':hashlib.sha256(raw).hexdigest()})
    (tmp_path/filename).write_text('{}')
    with pytest.raises(ValueError,match='configuration_mismatch'):
        validation.validate_assets(value,tmp_path)


def test_bounded_json_rejects_fifo_before_open(tmp_path,monkeypatch):
    import os
    from pathlib import Path
    path=tmp_path/'not-a-file';os.mkfifo(path)
    def forbidden(*_,**__):
        raise AssertionError('FIFO must not be opened as a blocking file')
    monkeypatch.setattr(Path,'open',forbidden)
    with pytest.raises(ValueError,match='configuration_mismatch'):
        validation.bounded_json(path,64)


def test_bounded_json_rejects_parent_symlink(tmp_path):
    actual=tmp_path/'actual';actual.mkdir();(actual/'record.json').write_text('{}')
    alias=tmp_path/'alias';alias.symlink_to(actual,target_is_directory=True)
    with pytest.raises(ValueError,match='configuration_mismatch'):
        validation.bounded_json(alias/'record.json',64)


def test_unicode_split_and_support_requires_all_cited_spans():
    catalog,receipt=catalog_probe(),receipt_probe()
    claim=catalog['claims'][0];claim['text']='Café ☕'
    first=copy.deepcopy(claim['support_alternatives'][0][0]);first.update(start=0,end=4,quote='Café')
    second=copy.deepcopy(first);second.update(start=5,end=6,quote='☕')
    claim['support_alternatives']=[[first,second]]
    passage=receipt['result']['evidence'][0];passage.update(start=0,end=4,text='Café')
    other=copy.deepcopy(passage);other.update(chunk_id='00000000-0000-0000-0000-000000000002',start=5,end=6,text='☕',rank=2)
    evidence=[passage,other]
    required=grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],evidence)
    response={'status':'answered','reason':None,'claims':[{'claim_id':'returns','text':'Café ☕','chunk_ids':[p['chunk_id'] for p in evidence]}]}
    assert grounding.validate_claims(response,required,evidence)[1]==evidence
    response['claims'][0]['chunk_ids'].pop()
    with pytest.raises(ValueError,match='grounding_failed'):
        grounding.validate_claims(response,required,evidence)


def test_support_alternatives_are_or_not_all_required():
    catalog,receipt=catalog_probe(),receipt_probe()
    missing=copy.deepcopy(catalog['claims'][0]['support_alternatives'][0])
    missing[0].update(start=100,end=103,quote='abs')
    catalog['claims'][0]['support_alternatives'].insert(0,missing)
    assert grounding.eligible(catalog,'scope','Return policy?',receipt['scope_snapshot'],receipt['result']['evidence'])
