"""Workshop-only instrumented wrapper over unchanged production services."""
import inspect
import json
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

import app.answer.service as service_module
from app.answer import generation
from app.answer.evaluation import case_matches
from app.answer.grounding import eligible, validate_claims
from app.answer.runtime import build_factory, fingerprint, observed_limits

if os.getpid() != os.getpgrp():
    os.setsid()
mode = sys.argv[1]
assert mode in ('fresh', 'rehearsal', 'regression')
args = ['--approval-manifest', '/fixtures/approval.json', '--retrieval-approval',
        '/fixtures/retrieval-approval.json', '--answer-approval', '/fixtures/answer-approval.json',
        '--grounding-catalog', '/fixtures/grounding-catalog.json', '--embedding-model-dir', '/embedding',
        '--generation-model-dir', '/generation', '--generation-assets', '/input/generation-assets.json',
        '--tmpfs-proof', '/input/tmpfs-proof.json', '--evaluation-cases', '/fixtures/evaluation-cases.json',
        '--min-score', str(json.loads(Path('/input/run-settings.json').read_text())['threshold']), '--calibration-id', json.loads(Path('/input/run-settings.json').read_text())['calibration_id']]
original_supervised = generation.supervised_module
source = inspect.getsource(original_supervised).replace('def supervised_module(', 'def workshop_supervised(')
source = source.replace("[sys.executable,'-B','-m',worker_module,'worker',",
                        "[sys.executable,'-B','/input/constraint-v1-worker.py',")
namespace = dict(generation.__dict__)
exec(source, namespace)  # noqa: S102 -- fixed inspected production source; no user text is executed

def dispatch(payload, *a, **kw):
    if payload['op'] == 'generate':
        return namespace['workshop_supervised'](payload, *a, **kw)
    return original_supervised(payload, *a, **kw)

generation.supervised_module = dispatch
report = {'kind': mode, 'mode': 'constrained_selection_of_reviewed_claims',
          'fresh_acceptance': mode == 'fresh', 'cases': [], 'lifecycle': {}, 'acceptance_claimed': False}
service = None
try:
    start = time.monotonic()
    service = build_factory(args, start+240)
    report['cold_factory_startup_ms'] = (time.monotonic()-start)*1000
    report['retrieval_fingerprint'] = fingerprint(service.configuration['retrieval'])
    report['generation_fingerprint'] = service.adapter.fingerprint
    report['configuration'] = service.configuration
    report['ingest_results'] = []
    for line in Path('/fixtures/ingest.jsonl').read_text().splitlines():
        result = service.dispatch(json.loads(line))
        report['ingest_results'].append(result)
        assert result['status'] == 'complete'
    report['ready_with_corpus_ms'] = (time.monotonic()-start)*1000
    print('SEDA_READY constrained-selection; approved corpus ready', file=sys.stderr, flush=True)
    timing = {}
    original_retrieval = service.retrieval.retrieve_with_receipt
    original_generation = service_module.generate_response
    def retrieve(*a, **kw):
        started = time.monotonic()
        try:
            receipt = original_retrieval(*a, **kw)
            timing['receipt'] = receipt
            return receipt
        finally:
            timing['retrieval_ms'] = (time.monotonic()-started)*1000
    def generate(*a, **kw):
        context = a[1]
        receipt = timing['receipt']
        timing['nonce'] = uuid4().hex
        binding = {'nonce': timing['nonce'], 'catalog': service.catalog,
                   'scope': receipt['scope_snapshot']['use_case_id'],
                   'snapshot': receipt['scope_snapshot'], 'context': context}
        Path('/tmp/constraint-v1-binding.json').write_text(json.dumps(binding))
        started = time.monotonic()
        try:
            return original_generation(*a, **kw)
        finally:
            timing['generation_ms'] = (time.monotonic()-started)*1000
    service.retrieval.retrieve_with_receipt = retrieve
    service_module.generate_response = generate
    if mode == 'fresh':
        cases = json.loads(Path('/fixtures/evaluation-cases.json').read_text())['cases']
    else:
        original = json.loads(Path('/input/regression-cases.json').read_text())['cases']
        cases = [c for c in original if c['case_id'] in ('edm-answer-1', 'edm-answer-4')]
    for case in cases:
        timing.clear()
        result = service.answer({'op': 'answer', 'use_case_id': case['use_case_id'], 'question': case['question']})
        receipt = timing.get('receipt')
        evidence = receipt['result']['evidence'] if receipt else []
        by_id = {p['chunk_id']: p for p in evidence}
        checks = {'citation_correct': all(c == by_id.get(c['chunk_id']) for c in result['citations']),
                  'isolated': all(p['use_case_id'] == case['use_case_id'] for p in evidence),
                  'schema_valid': None, 'claim_support': None}
        diagnostic = None
        if result['generation_attempts']:
            diagnostic = json.loads(Path('/tmp/constraint-v1-diagnostic.json').read_text())
            assert diagnostic['nonce'] == timing['nonce']
            raw = generation.strict_json(diagnostic['raw_output'])
            generation.validate_shape(raw, 'ModelResponse')
            required = eligible(service.catalog, case['use_case_id'], case['question'], receipt['scope_snapshot'], evidence)
            validate_claims(raw, required, evidence)
            checks.update(schema_valid=True, claim_support=True)
            assert diagnostic['model_generate_calls'] == 1
            assert len(diagnostic['constraint_paths']) == 2
            assert {json.loads(p['text'])['status'] for p in diagnostic['constraint_paths']} == {'answered', 'insufficient_evidence'}
        passed = case_matches(case, result) and checks['citation_correct'] and checks['isolated']
        row = {'case_id': case['case_id'], 'question': case['question'], 'passed': passed,
               'result': result, 'receipt': receipt, 'checks': checks,
               'retrieval_ms': timing.get('retrieval_ms'), 'generation_ms': timing.get('generation_ms', 0),
               'diagnostics': diagnostic}
        report['cases'].append(row)
        print('SEDA_CASE '+case['case_id']+' '+result['status']+' '+str(passed), file=sys.stderr, flush=True)
    if mode == 'fresh':
        report['retrieval_acceptance'] = []
        for case in json.loads(Path('/input/retrieval-acceptance.json').read_text()):
            value = service.dispatch({'op':'retrieve','use_case_id':case['use_case_id'],'question':case['question']})
            passages = value.get('evidence', [])
            passed = value['status']==case['expected_status'] and all(p['use_case_id']==case['use_case_id'] for p in passages)
            if case['source_id'] is not None:passed = passed and bool(passages) and passages[0]['source_id']==case['source_id']
            report['retrieval_acceptance'].append({'case':case,'result':value,'passed':passed})
        report['lifecycle']['retrieval_acceptance_pass'] = all(c['passed'] for c in report['retrieval_acceptance'])
        receipt_regression = service.dispatch({'op':'retrieve','use_case_id':'f2-synthetic','question':'What proof should accompany a return?'})
        report['receipt_regression'] = receipt_regression
        report['lifecycle']['receipt_regression_pass'] = receipt_regression['status']=='matched' and any(p['source_id']=='returns' for p in receipt_regression['evidence'])
        # Independent scope with identical source_id must never enter synthetic answers.
        neighbor = service.dispatch({'op': 'retrieve', 'use_case_id': 'f2-neighbor', 'question': 'What is the return period for unopened items at the neighbor shop?'})
        report['lifecycle']['neighbor_result'] = neighbor
        neighbor_evidence = neighbor.get('evidence', [])
        report['lifecycle']['isolation_pass'] = bool(neighbor_evidence) and all(p['use_case_id'] == 'f2-neighbor' for p in neighbor_evidence)
        # Use only the already-approved shorter revision; never change source bytes.
        replaced = service.dispatch({'op': 'ingest', 'use_case_id': 'f2-synthetic', 'source_id': 'returns',
                                     'title': 'Approved synthetic returns', 'revision': 'v2',
                                     'text': Path('/fixtures/f2-synthetic-returns-v2.txt').read_text().rstrip('\n')})
        report['lifecycle']['replacement_ingest'] = replaced
        from app.retrieval.index import verify_scope
        scope = verify_scope(service.retrieval.ingestion, 'f2-synthetic', time.monotonic()+10)
        report['lifecycle']['verified_current_inventory'] = [{k:row[k] for k in ('chunk_id','source_id','revision','content_sha256','start','end')} for row in scope['rows'].values()]
        report['lifecycle']['old_ids_absent_pass'] = all(row['revision']=='v2' for row in scope['rows'].values() if row['source_id']=='returns')
        current = service.dispatch({'op': 'retrieve', 'use_case_id': 'f2-synthetic',
                                    'question': 'What documentation is demanded by the current policy for unused-item returns?'})
        report['lifecycle']['current_version_result'] = current
        evidence = current.get('evidence', [])
        report['lifecycle']['replacement_pass'] = replaced['status'] == 'complete' and bool(evidence) and all(p['revision'] == 'v2' for p in evidence if p['source_id'] == 'returns') and any(p['source_id'] == 'returns' and p['revision'] == 'v2' for p in evidence)
        mismatch = service.answer({'op': 'answer', 'use_case_id': 'f2-synthetic', 'question': cases[0]['question']})
        report['lifecycle']['post_replacement_answer'] = mismatch
        report['lifecycle']['catalog_mismatch_pass'] = mismatch['status'] == 'failed' and mismatch['error']['code'] == 'catalog_mismatch' and not mismatch['claims'] and not mismatch['citations'] and mismatch['generation_attempts'] == 0
        cleared = service.dispatch({'op': 'clear', 'use_case_id': 'f2-synthetic'})
        empty = service.answer({'op': 'answer', 'use_case_id': 'f2-synthetic', 'question': cases[1]['question']})
        report['lifecycle']['clear_result'] = cleared
        report['lifecycle']['after_clear_answer'] = empty
        report['lifecycle']['clear_pass'] = cleared['status'] == 'complete' and empty['status'] == 'insufficient_evidence' and empty['reason'] == 'no_evidence' and empty['generation_attempts'] == 0
    report['all_cases_pass'] = all(c['passed'] for c in report['cases']) and bool(report['cases'])
    report['lifecycle_pass'] = all(v for k, v in report['lifecycle'].items() if k.endswith('_pass'))
    report['peak_bytes'] = observed_limits()['peak_bytes']
finally:
    if service is not None:
        closed = service.dispatch({'op': 'close'})
        report['collection_absent'] = closed['status'] == 'complete'
        assert report['collection_absent']
print(json.dumps(report), flush=True)
