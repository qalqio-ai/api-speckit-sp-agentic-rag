"""Serialized F2 composition with actual internal F3 receipt metadata."""
import copy
import hashlib
import json
import math
import threading
from dataclasses import asdict
from uuid import uuid4

from app.ingestion.types import IngestionError, SourceDocument
from app.ingestion.validation import parse_request as parse_f1

from .index import search, verify_scope
from .validation import parse_request, validate_result, validate_shape


class RetrievalService:
    def __init__(self,ingestion,processor,min_score,calibration_id=None):
        self.ingestion,self.processor=ingestion,processor
        self.clock=ingestion.clock
        self.min_score,self.calibration_id=min_score,calibration_id
        self.lock=threading.RLock()
        self.configuration={'mode':processor.mode,'top_k':3,'min_score':min_score,'calibration_id':calibration_id,
            'query_encoding':'f1_compatible_generic_encode_no_prompt','scoring':'cosine_exact',
            'model_configuration':copy.deepcopy(ingestion.config),'retrieval_deadline_seconds':120,
            'inventory_deadline_seconds':10,'query_encoding_deadline_seconds':90,'search_deadline_seconds':10,'max_scope_chunks':2048}
        validate_shape(self.configuration,'RetrievalConfiguration')
        if processor.mode!='deterministic':raise IngestionError('model_unavailable')

    @property
    def busy(self):return self.ingestion.busy
    @busy.setter
    def busy(self,value):self.ingestion.busy=value
    @property
    def registry_fingerprint(self):
        states=[]
        for key,state in sorted(self.ingestion.states.items()):
            value=asdict(state);value['expected_ids']=sorted(value['expected_ids'])
            states.append([list(key),value])
        payload={'states':states,'closed':self.ingestion.closed,'fatal':self.ingestion.fatal,'manifest':self.ingestion.manifest,'config':self.ingestion.config}
        return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()

    def _base(self,start):
        return {'schema_version':2,'request_id':str(uuid4()),'run_id':self.ingestion.index.run_id,
            'op':None,'status':'rejected','use_case_id':None,'configuration':None,
            'elapsed_ms':max(0,(self.clock()-start)*1000),'evidence_count':0,'evidence':[],
            'error':{'code':'invalid_input','message':'invalid_input'}}

    def retrieve(self,request,**kwargs):
        return self.retrieve_with_receipt(request,**kwargs)['result']

    def retrieve_with_receipt(self,request,*,request_started_at=None,deadline=None):
        start=self.clock() if request_started_at is None else request_started_at
        if type(start) not in (int,float) or not math.isfinite(start) or (deadline is not None and (type(deadline) not in (int,float) or not math.isfinite(deadline))):
            raise IngestionError('configuration_mismatch')
        end=min(start+120,deadline) if deadline is not None else start+120
        result=self._base(start);count=[0];snapshot=None;owned=False;locked=False;fingerprint=None
        try:
            remaining=end-self.clock()
            if remaining<=0 or not self.lock.acquire(timeout=remaining):raise IngestionError('deadline_exceeded')
            locked=True
            request=parse_request(request);result['op']='retrieve'
            if not any(s['use_case_id']==request['use_case_id'] for s in self.ingestion.manifest['allowed_sources']):
                raise IngestionError('unknown_use_case')
            result['use_case_id']=request['use_case_id']
            if self.busy or self.ingestion.closed or self.ingestion.fatal:raise IngestionError('session_unavailable')
            self.busy=owned=True
            config=copy.deepcopy(self.configuration);config['top_k']=request['top_k'];result['configuration']=config
            if config['model_configuration']!=self.ingestion.config:raise IngestionError('configuration_mismatch')
            fingerprint=self.registry_fingerprint
            scope=verify_scope(self.ingestion,request['use_case_id'],min(end,self.clock()+10))
            snapshot={'use_case_id':request['use_case_id'],'registry_fingerprint':fingerprint,'represented_sources':scope['represented_sources']}
            vector=self.processor.encode(request['question'],min(end,self.clock()+90),validate_only=not scope['rows'])
            candidates=[]
            if scope['rows']:
                def dispatched():count[0]=1
                candidates=search(self.ingestion,scope,vector,min(end,self.clock()+10),dispatched)
            if self.registry_fingerprint!=fingerprint:raise IngestionError('scope_not_ready')
            evidence=[p for p in candidates if p['score']>=self.min_score][:request['top_k']]
            evidence=[{**p,'rank':rank} for rank,p in enumerate(evidence,1)]
            result.update(status='matched' if evidence else 'no_match',evidence=evidence,evidence_count=len(evidence),error=None)
        except IngestionError as error:
            self.ingestion.record_fatal(error)
            code=error.code
            if code=='source_not_approved':code='unknown_use_case'
            rejected=code in ('invalid_input','unknown_operation','unknown_use_case','question_too_long','session_unavailable')
            result.update(status='rejected' if rejected else 'failed',evidence=[],evidence_count=0,error={'code':code,'message':code})
        except Exception:  # noqa: BLE001 -- fixed safe boundary, never raw diagnostics
            result.update(status='failed',evidence=[],evidence_count=0,error={'code':'index_failed','message':'index_failed'})
        finally:
            try:
                result['elapsed_ms']=max(0,(self.clock()-start)*1000)
                if self.clock()>end:
                    result.update(status='failed',evidence=[],evidence_count=0,error={'code':'deadline_exceeded','message':'deadline_exceeded'})
                validate_result(result)
                if self.clock()>end and result['error'] is None:
                    result.update(status='failed',evidence=[],evidence_count=0,error={'code':'deadline_exceeded','message':'deadline_exceeded'})
                    validate_result(result)
            finally:
                if owned:self.busy=False
                if locked:self.lock.release()
        return {'result':result,'scope_snapshot':snapshot,'retrieval_searches':count[0],'retrieval_deadline':end}

    def dispatch(self,request):
        if isinstance(request,dict) and request.get('op')=='retrieve':return self.retrieve(request)
        with self.lock:
            if not isinstance(request,dict) or request.get('op') not in ('ingest','inspect','clear','close'):
                result=self._base(self.clock());code='unknown_operation' if isinstance(request,dict) else 'invalid_input'
                result['error']={'code':code,'message':code};return validate_result(result)
            try:
                operation=parse_f1(request);op=operation['op']
                if self.busy:
                    return self.ingestion.result(op,'rejected',error='invalid_input')
                if op=='ingest':return self.ingestion.ingest(SourceDocument(**{k:v for k,v in operation.items() if k!='op'}))
                if op=='close':return self.ingestion.close()
                return getattr(self.ingestion,op)(operation['use_case_id'],operation.get('source_id'))
            except IngestionError as error:
                return self.ingestion.result(request['op'],'rejected',error=error.code)
