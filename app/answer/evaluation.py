"""Frozen-case consumer. Expectations never enter model context or retrieval."""
from .validation import validate_cases, validate_result


def case_matches(case, result):
    validate_result(result)
    if result['status'] != case['expected_status'] or result['reason'] != case['expected_reason']:
        return False
    if {c['claim_id'] for c in result['claims']} != set(case['expected_claim_ids']):
        return False
    return all(c['source_id'] in case['acceptable_source_ids'] for c in result['citations'])


def iter_evaluate(service, cases):
    """Yield one actual normal result at a time; no retry, tuning or reopen."""
    validate_cases(cases, service.catalog)
    for case in cases['cases']:
        result = service.answer({'op':'answer','use_case_id':case['use_case_id'],'question':case['question']})
        yield {'case_id':case['case_id'],'result':result}


def evaluate(service, cases):
    return list(iter_evaluate(service,cases))
