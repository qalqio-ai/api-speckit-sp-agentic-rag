"""Actual F1/F2/F3 class composition with synthetic memory ports only."""
import copy

import pytest
from test_answer import SCHEMA as ANSWER_SCHEMA
from test_answer import catalog_probe, sample
from test_retrieval import make_service

from app.answer.service import AnswerService
from app.answer.validation import validate_receipt
from app.ingestion.types import IngestionError
from app.retrieval import service as retrieval_module


def test_f3_uses_implemented_f2_receipt_and_actual_f1_busy_guard():
    retrieval,f1,client,_encoder,_clock=make_service(1)
    configuration=sample(ANSWER_SCHEMA['$defs']['AnswerConfiguration'])
    configuration['retrieval']=copy.deepcopy(retrieval.configuration)
    calls=[]
    def model(context,deadline):
        assert f1.busy
        calls.append(context)
        return {'status':'answered','reason':None,'claims':[{'claim_id':'returns','text':'Unused items require a receipt.','chunk_ids':[context['evidence'][0]['chunk_id']]}]}
    svc=AnswerService(retrieval,catalog_probe(),model,configuration,clock=f1.clock)
    result=svc.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['status']=='answered' and result['retrieval_searches']==result['generation_attempts']==1
    assert len(calls)==1 and not f1.busy
    assert len([c for c in client.calls if c[1].endswith('/points/query')])==1


def test_real_f2_receipt_validates_without_deriving_counts_or_top_k_scope():
    svc,_f1,_client,_encoder,_clock=make_service(4)
    receipt=svc.retrieve_with_receipt({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})
    assert validate_receipt(receipt)==receipt
    assert receipt['result']['evidence_count']==3


def test_nonfatal_search_failure_preserves_f1_readiness_and_envelope():
    svc,f1,client,_encoder,_clock=make_service(1)
    before=copy.deepcopy(f1.states)
    client.mutate=lambda _:[]
    result=svc.dispatch({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})
    assert result['status']=='failed' and result['error']['code']=='invalid_search_result'
    assert f1.states==before and not f1.fatal
    client.mutate=None
    inspected=svc.dispatch({'op':'inspect','use_case_id':'scope'})
    assert inspected['schema_version']==1 and inspected['status']=='complete'


def test_reentrant_delegate_cannot_mutate_f1_inventory_during_retrieval():
    svc,f1,_client,_encoder,_clock=make_service(1)
    before=copy.deepcopy(f1.states)
    original=svc.processor.encode
    def encode(*args,**kwargs):
        result=svc.dispatch({'op':'inspect','use_case_id':'scope'})
        assert result['status']=='rejected' and f1.states==before
        return original(*args,**kwargs)
    svc.processor.encode=encode
    assert svc.retrieve({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})['status']=='matched'


def test_guard_remains_held_through_f2_result_validation(monkeypatch):
    svc,f1,_client,_encoder,_clock=make_service(1)
    original=retrieval_module.validate_result
    def check(result):
        assert f1.busy
        return original(result)
    monkeypatch.setattr(retrieval_module,'validate_result',check)
    assert svc.retrieve({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})['status']=='matched'
    assert not f1.busy


def test_fatal_query_failure_marks_original_f1_session_unavailable():
    svc,f1,_client,_encoder,_clock=make_service(1)
    def fail(*_,**__):raise IngestionError('embedding_failed',fatal=True)
    svc.processor.encode=fail
    assert svc.retrieve({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})['status']=='failed'
    assert f1.fatal and not f1.states[('scope','policy')].ready
    assert svc.retrieve({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})['error']['code']=='session_unavailable'


@pytest.mark.parametrize('bad_score',[True,float('nan'),float('inf'),1.1,-1.1])
def test_bad_server_scores_never_expose_partial_evidence(bad_score):
    svc,_f1,client,_encoder,_clock=make_service(1)
    client.scores=dict.fromkeys(client.records,bad_score)
    result=svc.retrieve({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})
    assert result['status']=='failed' and result['evidence']==[]


@pytest.mark.parametrize('module',['app.retrieval','app.retrieval.demo','app.answer.demo'])
def test_unready_live_entry_points_fail_closed_without_ready_marker(module):
    import subprocess
    import sys
    result=subprocess.run([sys.executable,'-B','-m',module],capture_output=True,timeout=5,check=False)
    assert result.returncode!=0 and result.stdout==b''
    assert b'READY' not in result.stderr
