"""Synthetic memory probes: no corpus approval, model or semantic claims."""
import copy
import json
from pathlib import Path
from uuid import uuid4

import pytest
from test_answer import sample
from test_ingestion import FakeClient, FakeClock, FakeTokenizer

from app.ingestion.index import Index
from app.ingestion.service import Service
from app.ingestion.types import IngestionError, SourceState
from app.ingestion.validation import SCHEMA as F1_SCHEMA
from app.ingestion.validation import SCHEMA_PATH as F1_PATH
from app.retrieval import embedding, service, validation

PATH=Path(__file__).resolve().parents[1]/'specs/002-f2-retrieval/contracts/serialization.schema.json'
SCHEMA=json.loads(PATH.read_text())

class SearchClient(FakeClient):
    def __init__(self):
        super().__init__();self.scores={};self.mutate=None
    def request(self,method,path,body=None,timeout=None):
        if path.endswith('/points/query'):
            self.calls.append((method,path,copy.deepcopy(body),timeout))
            if self.fail:raise self.fail
            wanted=set(body['filter']['must'][2]['has_id'])
            points=[{'id':k,'payload':copy.deepcopy(self.records[k]['payload']),'score':self.scores[k]} for k in wanted]
            return {'points':self.mutate(points) if self.mutate else points}
        return super().request(method,path,body,timeout)

class Encoder:
    def __init__(self):self.calls=[]
    def encode(self,texts,**kwargs):
        self.calls.append((texts,kwargs));return [[1.0]+[0.0]*383]

def make_service(count=4):
    clock=FakeClock();client=SearchClient();encoder=Encoder()
    manifest=sample(F1_SCHEMA['$defs']['ApprovalManifest'],F1_PATH)
    manifest['allowed_sources']=[{'use_case_id':scope,'source_id':'policy','revision':'v1','content_sha256':'a'*64} for scope in ['scope','neighbor']]
    config=sample(F1_SCHEMA['$defs']['RunConfiguration'],F1_PATH)
    f1=Service(manifest,config,FakeTokenizer(),None,Index(client,clock,str(uuid4())),clock)
    ids=set()
    for _ in range(count):
        passage=sample(SCHEMA['$defs']['EvidencePassage'],PATH)
        passage.update(chunk_id=str(uuid4()),use_case_id='scope',source_id='policy',revision='v1',start=0,end=31,text='Unused items require a receipt.')
        passage.pop('rank');passage.pop('score')
        record={**passage,'vector':[1.0]+[0.0]*383};ident=record['chunk_id'];ids.add(ident)
        client.records[ident]={'id':ident,'payload':passage,'vector':record['vector']};client.scores[ident]=0.8
    if count:
        f1.states[('scope','policy')]=SourceState(current_verified_revision='v1',source_status='complete',ready=True,expected_count=count,current_count=count,expected_ids=ids,expected_payload_hashes={k:f1.payload_hash(client.records[k]['payload']) for k in ids})
    processor=embedding.QueryProcessor(f1.tokenizer,encoder,clock)
    return service.RetrievalService(f1,processor,0.5,'memory-probe'),f1,client,encoder,clock

@pytest.mark.parametrize('name',list(SCHEMA['$defs']))
def test_closed_f2_records_and_external_refs(name):
    value=sample(SCHEMA['$defs'][name],PATH)
    validation.validate_shape(value,name)
    if isinstance(value,dict):
        with pytest.raises(IngestionError):validation.validate_shape({**value,'extra':1},name)
        for key in SCHEMA['$defs'][name].get('required',[]):
            wrong=copy.deepcopy(value);wrong.pop(key)
            with pytest.raises(IngestionError):validation.validate_shape(wrong,name)

@pytest.mark.parametrize('patch',[{'question':' '},{'question':None},{'question':'é'*2049},{'top_k':True},{'top_k':0},{'top_k':11},{'extra':1}])
def test_rejected_input_never_reads_encodes_or_searches(patch):
    svc,_f1,client,encoder,_clock=make_service()
    result=svc.retrieve({'op':'retrieve','use_case_id':'scope','question':'Return policy?',**patch})
    assert result['status']=='rejected' and result['evidence']==[] and client.calls==encoder.calls==[]

def test_exact_full_scope_ties_are_globally_sorted_and_receipt_complete():
    svc,f1,client,encoder,_clock=make_service()
    receipt=svc.retrieve_with_receipt({'op':'retrieve','use_case_id':'scope','question':'Return policy?','top_k':2},request_started_at=0,deadline=120)
    result=receipt['result'];assert result['status']=='matched'
    assert [p['chunk_id'] for p in result['evidence']]==sorted(client.records)[:2]
    queries=[c for c in client.calls if c[1].endswith('/points/query')]
    assert len(queries)==1 and queries[0][2]['limit']==4 and queries[0][2]['params']=={'exact':True}
    assert queries[0][2]['with_vector'] is False and queries[0][2]['with_payload'] is True
    assert receipt['retrieval_searches']==1 and receipt['scope_snapshot']['represented_sources']==[{'source_id':'policy','revision':'v1','content_sha256':'a'*64}]
    assert not f1.busy and len(encoder.calls)==1 and f1.states[('scope','policy')].ready

@pytest.mark.parametrize('scenario',['empty','incomplete','unknown','over_tokens','below_threshold','dispatch_failure','missing_result','foreign_payload','registry_change'])
def test_empty_readiness_failures_and_counts(scenario):
    svc,f1,client,encoder,clock=make_service(0 if scenario=='empty' else 4)
    request={'op':'retrieve','use_case_id':'scope','question':'Return policy?'}
    expected='no_match' if scenario in ('empty','below_threshold') else ('rejected' if scenario in ('unknown','over_tokens') else 'failed')
    if scenario=='incomplete':f1.states[('scope','policy')].ready=False
    if scenario=='unknown':request['use_case_id']='Scope'
    if scenario=='over_tokens':request['question']='word '*255
    if scenario=='below_threshold':client.scores=dict.fromkeys(client.records,0.49)
    if scenario=='dispatch_failure':
        def failure(points):raise RuntimeError('private question')
        client.mutate=failure
    if scenario=='missing_result':client.mutate=lambda points:points[:-1]
    if scenario=='foreign_payload':
        def foreign(points):points[0]['payload']['use_case_id']='neighbor';return points
        client.mutate=foreign
    if scenario=='registry_change':
        def change(points):f1.states[('scope','policy')].ready=False;return points
        client.mutate=change
    receipt=svc.retrieve_with_receipt(request,request_started_at=clock(),deadline=120)
    assert receipt['result']['status']==expected and receipt['result']['evidence']==[]
    assert receipt['retrieval_searches']==(0 if scenario in ('empty','incomplete','unknown','over_tokens') else 1)
    assert 'private question' not in str(receipt)
    if scenario=='empty':assert encoder.calls==[]
    assert not f1.busy

def test_inclusive_boundary_and_original_deadline_before_dispatch():
    svc,_f1,client,_encoder,clock=make_service(1)
    client.scores=dict.fromkeys(client.records,0.5)
    request={'op':'retrieve','use_case_id':'scope','question':'Return policy?'}
    assert svc.retrieve(request)['status']=='matched'
    client.calls.clear();clock.now=121
    receipt=svc.retrieve_with_receipt(request,request_started_at=0,deadline=120)
    assert receipt['result']['error']['code']=='deadline_exceeded' and receipt['retrieval_searches']==0 and client.calls==[]


@pytest.mark.parametrize('scenario',['scope_cap','paging_cycle','unregistered_row','changed_payload','bad_vector','wrong_type_payload'])
def test_inventory_rejects_uncertain_scope_without_query(scenario):
    svc,f1,client,encoder,_clock=make_service(2049 if scenario=='scope_cap' else 4)
    first=next(iter(client.records))
    if scenario=='unregistered_row':f1.states.clear()
    if scenario=='changed_payload':client.records[first]['payload']['text']='altered'.ljust(31)
    if scenario=='bad_vector':client.records[first]['vector']=[0.0]*384
    if scenario=='wrong_type_payload':client.records[first]['payload']['start']=False
    if scenario=='paging_cycle':
        original=client.request
        def cyclic(method,path,body=None,timeout=None):
            result=original(method,path,body,timeout)
            if path.endswith('/points/scroll'):result['next_page_offset']=2
            return result
        client.request=cyclic
    receipt=svc.retrieve_with_receipt({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})
    assert receipt['result']['status']=='failed' and receipt['result']['evidence']==[]
    assert receipt['retrieval_searches']==0 and encoder.calls==[]
    assert not any(call[1].endswith('/points/query') for call in client.calls)
    if scenario=='scope_cap':assert receipt['result']['error']['code']=='scope_too_large'


def test_retrieval_never_sends_query_after_original_search_deadline():
    svc,f1,client,encoder,clock=make_service(1)
    # Time expires at the transport boundary after successful query processing.
    f1.index.clock=lambda:120 if encoder.calls else clock()
    receipt=svc.retrieve_with_receipt({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})
    assert receipt['result']['error']['code']=='deadline_exceeded'
    assert receipt['retrieval_searches']==0
    assert not any(call[1].endswith('/points/query') for call in client.calls)


@pytest.mark.parametrize('field,value',[('start',False),('end',31.0)])
def test_malformed_server_payload_cannot_hide_behind_python_scalar_equality(field,value):
    svc,_f1,client,_encoder,_clock=make_service(1)
    def malformed(points):points[0]['payload'][field]=value;return points
    client.mutate=malformed
    result=svc.retrieve({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})
    assert result['status']=='failed' and result['evidence']==[]


def test_calibration_uses_expected_source_full_rank_and_unfiltered_scores():
    from app.retrieval.evaluation import calibration_summary, propose_threshold
    positives=[{'case_id':f'p{i}','expected':{'status':'matched','source_ids':['policy']}} for i in range(3)]
    negative={'case_id':'n','expected':{'status':'no_match'}}
    # Expected source is below a prospective0.9 threshold and outside top_k1.
    candidates=[{'chunk_id':'b','source_id':'other','score':0.8},{'chunk_id':'a','source_id':'policy','score':0.6}]
    summaries=[calibration_summary(case,candidates) for case in positives]
    summaries.append(calibration_summary(negative,[{'chunk_id':'c','source_id':'other','score':0.2}]))
    assert summaries[0]=={'case_id':'p0','candidate_count':2,'maximum_candidate_score':0.8,'best_expected_source_score':0.6,'best_expected_source_rank':2}
    assert propose_threshold([*positives,negative],summaries)==pytest.approx(0.4)
    bad=[*summaries];bad[-1]={**bad[-1],'maximum_candidate_score':0.6}
    assert propose_threshold([*positives,negative],bad) is None


@pytest.mark.parametrize('scenario',['missing_expected','rank_four','empty_negative'])
def test_calibration_cannot_claim_separator_with_missing_or_bad_cases(scenario):
    from app.retrieval.evaluation import calibration_summary, propose_threshold
    positive={'case_id':'p','expected':{'status':'matched','source_ids':['policy']}}
    negative={'case_id':'n','expected':{'status':'no_match'}}
    rows=[{'chunk_id':str(i),'source_id':'other','score':0.9-i*0.01} for i in range(3)]
    if scenario!='missing_expected':rows.append({'chunk_id':'z','source_id':'policy','score':0.5})
    if scenario=='empty_negative':rows=rows[-1:]
    neg=[] if scenario=='empty_negative' else [{'chunk_id':'n','source_id':'other','score':0.1}]
    summaries=[calibration_summary(positive,rows),calibration_summary(negative,neg)]
    assert propose_threshold([positive,negative],summaries) is None


@pytest.mark.parametrize('mutation',[None,'duplicate','unknown_source','foreign_scope','manifest','configuration','held_out_minimum','question_bytes','contradictory','split_leakage'])
def test_frozen_case_binding_and_split_minima(mutation):
    _svc,f1,_client,_encoder,_clock=make_service(1)
    cases=sample(SCHEMA['$defs']['EvaluationCaseSet'],PATH)
    cases.update(manifest_sha256='a'*64,configuration_fingerprint='b'*64,cases=[])
    for i,split in enumerate(['calibration']*2+['held_out']*5):
        case=sample(SCHEMA['$defs']['EvaluationCase'],PATH)
        case.update(case_id=str(i),split=split,use_case_id='scope',question=f'Return policy {i}?',expected={'status':'matched','source_ids':['policy']})
        if i in (1,5,6):case['expected']={'status':'no_match'}
        cases['cases'].append(case)
    if mutation=='duplicate':cases['cases'][1]['case_id']='0'
    if mutation=='unknown_source':cases['cases'][0]['expected']['source_ids']=['unknown']
    if mutation=='foreign_scope':cases['cases'][0]['use_case_id']='Scope'
    if mutation=='manifest':cases['manifest_sha256']='c'*64
    if mutation=='configuration':cases['configuration_fingerprint']='c'*64
    if mutation=='held_out_minimum':cases['cases'].pop()
    if mutation=='question_bytes':cases['cases'][0]['question']='é'*2049
    if mutation=='contradictory':cases['cases'][1]['question']=cases['cases'][0]['question']
    if mutation=='split_leakage':cases['cases'][2]['question']=cases['cases'][0]['question']
    if mutation is None:
        assert validation.validate_cases(cases,f1.manifest,'a'*64,'b'*64)==cases
    else:
        with pytest.raises(IngestionError):validation.validate_cases(cases,f1.manifest,'a'*64,'b'*64)


def test_f2_scope_limit_is_chunks_without_f3_source_count_restriction():
    svc,f1,client,_encoder,_clock=make_service(33)
    f1.states.clear();f1.manifest['allowed_sources']=[]
    for i,(ident,point) in enumerate(client.records.items()):
        sid=f'policy-{i}';point['payload']['source_id']=sid
        f1.manifest['allowed_sources'].append({'use_case_id':'scope','source_id':sid,'revision':'v1','content_sha256':'a'*64})
        f1.states[('scope',sid)]=SourceState(current_verified_revision='v1',source_status='complete',ready=True,expected_count=1,current_count=1,expected_ids={ident},expected_payload_hashes={ident:f1.payload_hash(point['payload'])})
    assert svc.retrieve({'op':'retrieve','use_case_id':'scope','question':'Return policy?'})['status']=='matched'
