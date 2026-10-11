"""Exact reviewed rules applied only to current returned evidence."""
from .validation import AnswerError, validate_catalog, validate_shape


class Insufficient(AnswerError):
    """Application-only preflight abstention; never a model conflict verdict."""


def _alternatives(claim, evidence):
    supported = []
    for alternative in claim['support_alternatives']:
        chunks = []
        for span in alternative:
            matches = [p['chunk_id'] for p in evidence
                       if p['use_case_id'] == claim['use_case_id']
                       and all(p[k] == span[k] for k in ('source_id', 'revision', 'content_sha256'))
                       and p['start'] <= span['start'] < span['end'] <= p['end']
                       and p['text'][span['start']-p['start']:span['end']-p['start']] == span['quote']]
            if not matches:
                break
            chunks.append(matches)
        else:
            supported.append(chunks)
    return supported


def eligible(catalog, scope, question, snapshot, evidence):
    validate_catalog(catalog)
    validate_shape(snapshot, 'ScopeSnapshot')
    current = {(s['source_id'], s['revision'], s['content_sha256']) for s in snapshot['represented_sources']}
    reviewed = {(s['source_id'], s['revision'], s['content_sha256']) for s in catalog['source_rules'] if s['use_case_id'] == scope}
    if snapshot['use_case_id'] != scope or current != reviewed:
        raise AnswerError('catalog_mismatch')
    alias = next((q for q in catalog['questions'] if (q['use_case_id'], q['question']) == (scope, question)), None)
    if alias is None:
        raise Insufficient('unsupported_question')
    if alias['insufficient_reason']:
        raise Insufficient(alias['insufficient_reason'])
    all_claims = {c['claim_id']: c for c in catalog['claims'] if c['use_case_id'] == scope}
    required = [all_claims[cid] for cid in alias['expected_claim_ids']]
    if any(not _alternatives(claim, evidence) for claim in required):
        raise Insufficient('unsupported_question')
    uncertain = False
    for claim in required:
        for opponent_id in claim['conflicting_claim_ids']:
            opponent = all_claims[opponent_id]
            if _alternatives(opponent, evidence):
                raise Insufficient('conflicting_evidence')
            # Check every relevant opponent before classifying unresolved opposition.
            uncertain = True
    if uncertain:
        raise Insufficient('unsupported_question')
    return required


def validate_claims(response, required, evidence):
    try:
        validate_shape(response, 'ModelResponse')
    except ValueError as error:
        raise AnswerError('invalid_model_response') from error
    if response['status'] == 'insufficient_evidence':
        return [], []
    expected = {c['claim_id']: c for c in required}
    actual = response['claims']
    if len(actual) != len(expected) or {c['claim_id'] for c in actual} != set(expected):
        raise AnswerError('grounding_failed')
    passage_map = {p['chunk_id']: p for p in evidence}
    for claim in actual:
        reviewed = expected[claim['claim_id']]
        if claim['text'] != reviewed['text']:
            raise AnswerError('grounding_failed')
        if any(cid not in passage_map for cid in claim['chunk_ids']):
            raise AnswerError('invalid_citation')
        selected = [passage_map[cid] for cid in claim['chunk_ids']]
        alternatives = _alternatives(reviewed, selected)
        if not alternatives:
            raise AnswerError('grounding_failed')
        used = set(claim['chunk_ids'])
        if not any(used <= {cid for group in alternative for cid in group} for alternative in alternatives):
            raise AnswerError('invalid_citation')
    cited = {cid for c in actual for cid in c['chunk_ids']}
    return actual, [p for p in evidence if p['chunk_id'] in cited]
