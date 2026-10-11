"""Serialized injected F2 composition. This module never claims live execution."""
import copy
import json
import math
import threading
import time
from uuid import uuid4

from .generation import generate_response
from .grounding import Insufficient, eligible, validate_claims
from .validation import (
    AnswerError,
    validate_catalog,
    validate_receipt,
    validate_result,
    validate_shape,
)


class AnswerService:
    def __init__(self, retrieval, catalog, adapter, configuration, *, clock=time.monotonic):
        validate_catalog(catalog)
        validate_shape(configuration, 'AnswerConfiguration')
        self.live = configuration['mode']=='local_live'
        if self.live:
            from .generation import LocalGenerator
            from .runtime import LiveRetrieval
            if (type(adapter) is not LocalGenerator or not adapter.verified_live
                    or type(retrieval) is not LiveRetrieval or not retrieval.verified_live
                    or configuration['retrieval']!=retrieval.configuration
                    or configuration['generation']!=adapter.configuration):
                raise AnswerError('model_unavailable')
        elif configuration['retrieval']['mode']!='deterministic':
            raise AnswerError('model_unavailable')
        if configuration['retrieval']['top_k'] != 3:
            raise AnswerError('configuration_mismatch')
        self.retrieval = retrieval
        self.catalog = copy.deepcopy(catalog)
        self.configuration = copy.deepcopy(configuration)
        self.adapter, self.clock = adapter, clock
        self.lock = threading.RLock()
        self.run_id = str(uuid4())
        self.fatal = False

    def _base(self, start):
        return {'schema_version':3, 'request_id':str(uuid4()), 'run_id':self.run_id,
                'op':None, 'status':'rejected', 'use_case_id':None, 'configuration':None,
                'elapsed_ms':max(0, (self.clock()-start)*1000), 'retrieval_searches':0,
                'generation_attempts':0, 'claims':[], 'citations':[], 'reason':None,
                'error':{'code':'invalid_input','message':'invalid_input','cause_code':None}}

    def reject(self, code):
        result = self._base(self.clock())
        result['error'] = {'code':code,'message':code,'cause_code':None}
        return validate_result(result)

    def dispatch(self, request):
        with self.lock:
            return self.retrieval.dispatch(request)

    def answer(self, request, *, emit=None, request_started_at=None, deadline=None):
        start = self.clock() if request_started_at is None else request_started_at
        effective = start + 240 if deadline is None else min(deadline, start + 240)
        if (type(start) not in (int, float) or type(effective) not in (int, float)
                or not math.isfinite(start) or not math.isfinite(effective)):
            raise AnswerError('configuration_mismatch')
        remaining = effective - self.clock()
        if remaining <= 0 or not self.lock.acquire(timeout=remaining):
            raise AnswerError('deadline_exceeded')
        ownership = [False]
        try:
            if self.clock() >= effective:
                raise AnswerError('deadline_exceeded')
            return self._answer(request, ownership, start, effective, emit=emit)
        finally:
            if ownership[0]:
                self.retrieval.busy = False
            self.lock.release()

    def _answer(self, request, ownership, start, deadline, *, emit=None):
        result = self._base(start)
        fingerprint = None
        validation_elapsed = 0
        validation_start = None
        retrieval_cause = None
        retrieval_status = None
        try:
            validate_shape(request, 'AnswerRequest')
            if len(request['question'].encode('utf-8')) > 4096:
                raise AnswerError('question_too_long')
            result.update(op='answer', use_case_id=request['use_case_id'])
            if self.fatal or self.retrieval.busy:
                raise AnswerError('session_unavailable')
            receipt = self.retrieval.retrieve_with_receipt(
                {'op':'retrieve', 'use_case_id':request['use_case_id'], 'question':request['question'], 'top_k':3},
                request_started_at=start, deadline=min(deadline, start+120))
            # F2 returns actual counters; never derive attempts from matched/no_match.
            validate_receipt(receipt)
            result['retrieval_searches'] = receipt['retrieval_searches']
            if receipt['retrieval_deadline'] != min(deadline, start+120):
                raise AnswerError('configuration_mismatch')
            retrieved = receipt['result']
            if retrieved['status'] in ('failed','rejected'):
                code = retrieved['error']['code']
                retrieval_cause, retrieval_status = code, retrieved['status']
                raise AnswerError('retrieval_failed')
            if retrieved['use_case_id'] != request['use_case_id'] or retrieved['configuration'] != self.configuration['retrieval']:
                raise AnswerError('configuration_mismatch')
            if self.retrieval.busy:
                raise AnswerError('session_unavailable')
            self.retrieval.busy = ownership[0] = True
            fingerprint = receipt['scope_snapshot']['registry_fingerprint']
            result['configuration'] = copy.deepcopy(self.configuration)
            if self.clock() > min(deadline, start+120):
                raise AnswerError('deadline_exceeded')
            validation_start = self.clock()
            if not retrieved['evidence']:
                raise Insufficient('no_evidence')
            required = eligible(self.catalog, request['use_case_id'], request['question'], receipt['scope_snapshot'], retrieved['evidence'])
            context = {'question':request['question'], 'rules':[{'claim_id':c['claim_id'],'text':c['text']} for c in required],
                       'evidence':copy.deepcopy(retrieved['evidence'])}
            if len(json.dumps(context, ensure_ascii=False).encode('utf-8')) > 65536:
                raise AnswerError('context_too_large')
            validation_elapsed += self.clock()-validation_start
            validation_start = None
            if validation_elapsed > 10 or self.clock() >= deadline:
                raise AnswerError('deadline_exceeded')
            generation_deadline = min(deadline, self.clock()+110)
            result['generation_attempts'] = 0 if self.live else 1
            try:
                response = generate_response(self.adapter, context, generation_deadline)
            finally:
                if self.live:
                    result['generation_attempts'] = self.adapter.attempts
                    if type(self.adapter.attempts) is not int or self.adapter.attempts not in (0,1):
                        raise AnswerError('session_unavailable',fatal=True)
            if self.clock() > generation_deadline:
                raise AnswerError('deadline_exceeded')
            validation_start = self.clock()
            claims, citations = validate_claims(response, required, retrieved['evidence'])
            result.update(status=response['status'], claims=claims, citations=citations, reason=response['reason'], error=None)
        except Insufficient as error:
            result.update(status='insufficient_evidence', claims=[], citations=[], reason=error.code, error=None)
        except AnswerError as error:
            if error.fatal:
                self.fatal = True
                raise  # Cleanup takes precedence; no fabricated delivered record.
            rejected = error.code in ('invalid_input','unknown_operation','unknown_use_case','question_too_long','session_unavailable')
            result.update(status=retrieval_status or ('rejected' if rejected else 'failed'), claims=[], citations=[], reason=None,
                          error={'code':error.code,'message':error.code,'cause_code':retrieval_cause})
        except Exception as error:  # noqa: BLE001 -- injected boundary must suppress raw diagnostics
            result.update(status='failed', claims=[], citations=[], reason=None,
                          error={'code':'configuration_mismatch','message':'configuration_mismatch','cause_code':None})
            del error
        if fingerprint is not None and self.retrieval.registry_fingerprint != fingerprint:
            result.update(status='failed', claims=[], citations=[], reason=None,
                          error={'code':'configuration_mismatch','message':'configuration_mismatch','cause_code':None})
        result['elapsed_ms'] = max(0,(self.clock()-start)*1000)
        if validation_start is not None:
            validation_elapsed += self.clock()-validation_start
        if self.clock() > deadline or validation_elapsed > 10:
            result.update(status='failed', claims=[], citations=[], reason=None,
                          error={'code':'deadline_exceeded','message':'deadline_exceeded','cause_code':None})
        delivery_deadline = min(deadline, self.clock() + max(0, 10-validation_elapsed))
        validated = validate_result(result)
        if self.clock() > delivery_deadline:
            raise AnswerError('deadline_exceeded')
        if emit is not None:
            emit(validated, delivery_deadline)
        return validated
