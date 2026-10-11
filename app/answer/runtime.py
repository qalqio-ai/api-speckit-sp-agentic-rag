"""F3-owned live adapters; F1/F2 implementations and public contracts are preserved."""
import argparse
import copy
import hashlib
import json
import math
import os
import platform
import socket
import sys
import threading
import time
from pathlib import Path
from uuid import uuid4

from app.ingestion.embedding import load_model, validate_vectors, verify_assets
from app.ingestion.index import Index, verify_tmpfs
from app.ingestion.service import Service
from app.ingestion.types import IngestionError
from app.retrieval.service import RetrievalService
from app.retrieval.validation import validate_shape as validate_f2

from .generation import LocalGenerator, receive_message, send_message, supervised_module
from .validation import (
    SCHEMA_PATH,
    SCHEMAS,
    AnswerError,
    bounded_json,
    validate_bindings,
    validate_catalog,
    validate_shape,
)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
                                    allow_nan=False).encode()).hexdigest()


def file_hash(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(65536),b''):
            digest.update(block)
    return digest.hexdigest()


def platform_gate():
    if sys.platform!='linux' or sys.version_info[:2]!=(3,12) or platform.machine()!='x86_64':
        raise AnswerError('model_unavailable')


def observed_limits():
    platform_gate()
    return kernel_limits(lambda name:(Path('/sys/fs/cgroup')/name).read_text())


def owned_identity(pid,group):
    """Capture kernel identity at each worker handshake, not inferred from a result."""
    stat=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
    if int(stat[2])!=group or os.getpgid(pid)!=group:
        raise AnswerError('session_unavailable',fatal=True)
    membership=Path(f'/proc/{pid}/cgroup').read_text()
    if membership!=Path('/proc/self/cgroup').read_text():
        raise AnswerError('session_unavailable',fatal=True)
    observed_limits()
    return {'pid':pid,'pgid':group,'start_ticks':int(stat[19]),
            'cgroup_sha256':hashlib.sha256(membership.encode()).hexdigest()}


def process_identity(pid):
    try:
        stat=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
        membership=Path(f'/proc/{pid}/cgroup').read_text()
        return {'pid':pid,'pgid':int(stat[2]),'start_ticks':int(stat[19]),
                'cgroup_sha256':hashlib.sha256(membership.encode()).hexdigest()}
    except FileNotFoundError:return None


def register_identity(registry,identity,group):
    if (not isinstance(identity,dict) or set(identity)!={'pid','pgid','start_ticks','cgroup_sha256'}
            or any(type(identity[k]) is not int or identity[k]<=0 for k in ('pid','pgid','start_ticks'))
            or identity['pgid']!=group):raise AnswerError('session_unavailable')
    expected=hashlib.sha256(Path('/proc/self/cgroup').read_bytes()).hexdigest()
    if identity['cgroup_sha256']!=expected:raise AnswerError('session_unavailable')
    current=process_identity(identity['pid'])
    if current is not None and current!=identity:raise AnswerError('session_unavailable')
    registry.append(identity)


def registry_absent(registry,read=process_identity):
    """A reused PID is not the original worker; never signal that new process."""
    for identity in registry:
        current=read(identity['pid'])
        if current is not None and current['start_ticks']==identity['start_ticks']:
            return False
    return True


def arguments(argv):
    parser=argparse.ArgumentParser()
    for name in ('approval-manifest','retrieval-approval','answer-approval','grounding-catalog',
                 'embedding-model-dir','generation-model-dir','generation-assets','tmpfs-proof'):
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--evaluation-cases')
    parser.add_argument('--min-score',type=float,required=True)
    parser.add_argument('--calibration-id',required=True)
    return parser.parse_args(argv)


class LiveQuery:
    mode='local_live'
    def __init__(self,root,config,notify):
        self.root,self.config,self.notify=str(root),config,notify
    def call(self,payload,deadline):
        try:
            return supervised_module({'directory':self.root,'config':self.config,**payload},
                                     deadline,notify=self.notify,worker_module='app.answer.runtime')
        except AnswerError as error:
            raise IngestionError(error.code,fatal=error.fatal or error.code=='session_unavailable') from error
    def encode(self,question,deadline,*,validate_only=False):
        result=self.call({'op':'encode','texts':[question],'validate_only':validate_only},deadline)
        if validate_only:
            if result!={'validated':True}:raise IngestionError('embedding_failed',fatal=True)
            return None
        return validate_vectors(result['vectors'])[0]


class LiveEmbedder:
    def __init__(self,query):self.query=query
    def encode(self,chunks,deadline):
        result=self.query.call({'op':'encode','texts':[c['text'] for c in chunks],'validate_only':False},deadline)
        vectors=validate_vectors(result['vectors'])
        if len(vectors)!=len(chunks):raise IngestionError('embedding_failed',fatal=True)
        return [{**chunk,'vector':vector} for chunk,vector in zip(chunks,vectors)]
    def close(self,deadline):return True  # Every fresh call already verifies reaping.


class LiveTransport:
    def __init__(self,notify):self.notify=notify;self.query_dispatches=0
    def request(self,method,path,body=None,timeout=None):
        if timeout is None or timeout<=0:raise IngestionError('deadline_exceeded')
        try:
            def observed(event):
                if event['kind']=='search':self.query_dispatches=event['count']
                elif self.notify is not None:self.notify(event)
            result=supervised_module({'op':'storage','method':method,'path':path,'body':body},
                time.monotonic()+timeout,notify=observed,worker_module='app.answer.runtime')
            return result['response']
        except AnswerError as error:
            code=error.code if error.code in ('deadline_exceeded','index_failed','cleanup_failed') else 'index_failed'
            raise IngestionError(code,fatal=error.fatal or error.code=='session_unavailable') from error
    def close(self):return None


class LiveRetrieval(RetrievalService):
    """F3-owned constructor reuses the unchanged F2 operation pipeline.

    F2's public deterministic-only constructor remains intact. No temporary fake
    mode or bypassed result validation is used to initialize this live adapter.
    """
    def __init__(self,ingestion,processor,min_score,calibration_id):
        if type(processor) is not LiveQuery:raise AnswerError('model_unavailable')
        self.ingestion,self.processor=ingestion,processor
        self.clock=ingestion.clock
        self.min_score,self.calibration_id=min_score,calibration_id
        self.lock=threading.RLock()
        self.configuration={'mode':'local_live','top_k':3,'min_score':min_score,'calibration_id':calibration_id,
            'query_encoding':'f1_compatible_generic_encode_no_prompt','scoring':'cosine_exact',
            'model_configuration':copy.deepcopy(ingestion.config),'retrieval_deadline_seconds':120,
            'inventory_deadline_seconds':10,'query_encoding_deadline_seconds':90,
            'search_deadline_seconds':10,'max_scope_chunks':2048}
        validate_f2(self.configuration,'RetrievalConfiguration')
        if not calibration_id or not calibration_id.strip():raise AnswerError('configuration_mismatch')
        self.verified_live=True
    def retrieve_with_receipt(self,request,**kwargs):
        start=kwargs.get('request_started_at')
        start=self.clock() if start is None else start
        deadline=kwargs.get('deadline')
        if (type(start) not in (int,float) or not math.isfinite(start)
                or deadline is not None and (type(deadline) not in (int,float) or not math.isfinite(deadline))):
            return super().retrieve_with_receipt(request,**kwargs)
        end=min(start+120,deadline) if deadline is not None else start+120
        kwargs['request_started_at']=start
        remaining=end-self.clock()
        if remaining<=0 or not self.lock.acquire(timeout=remaining):
            return super().retrieve_with_receipt(request,**kwargs)
        try:
            transport=self.ingestion.index.client
            transport.query_dispatches=0
            receipt=super().retrieve_with_receipt(request,**kwargs)
            receipt['retrieval_searches']=transport.query_dispatches
            return receipt
        finally:self.lock.release()


def build_factory(arguments, deadline, notify=None):
    """Only invoked inside the fresh owned session process after runtime inspection."""
    from .service import AnswerService
    observed_limits()
    args=globals()['arguments'](arguments)
    manifest=bounded_json(args.approval_manifest,1048576)
    catalog=bounded_json(args.grounding_catalog,1048576)
    receipt=bounded_json(args.answer_approval,16384)
    retrieval_receipt=bounded_json(args.retrieval_approval,16384)
    # Purpose/hash/attribution checks precede every tokenizer/model startup.
    from app.ingestion.validation import validate_manifest
    validate_manifest(manifest)
    validate_catalog(catalog)
    validate_shape(receipt,'F3ApprovalReceipt')
    validate_f2(retrieval_receipt,'F2ApprovalReceipt')
    manifest_hash=file_hash(args.approval_manifest)
    if (catalog['manifest_sha256']!=manifest_hash or receipt['manifest_sha256']!=manifest_hash
            or retrieval_receipt['manifest_sha256']!=manifest_hash
            or receipt['catalog_sha256']!=file_hash(args.grounding_catalog)):
        raise AnswerError('configuration_mismatch')
    assets=bounded_json(args.generation_assets,65536)
    cases=bounded_json(args.evaluation_cases,1048576) if args.evaluation_cases else None
    verify_tmpfs(bounded_json(args.tmpfs_proof,16384))
    root=Path(args.embedding_model_dir)
    config=bounded_json(root/'f1-model.json',1048576)
    generation=LocalGenerator(args.generation_model_dir,assets,file_hash(args.generation_assets),
                              file_hash(args.grounding_catalog),deadline,notify=notify)
    # The embedding tokenizer is initialized in this supervised factory, never its parent.
    tokenizer=_embedding_tokenizer(root,config)
    query=LiveQuery(root,config,notify)
    ingestion=Service(manifest,config,tokenizer,LiveEmbedder(query),
                      Index(LiveTransport(notify),time.monotonic,str(uuid4())),time.monotonic)
    retrieval=LiveRetrieval(ingestion,query,args.min_score,args.calibration_id)
    limits={name:rule['const'] for name,rule in SCHEMAS[SCHEMA_PATH]['$defs']['ExecutionLimits']['properties'].items()}
    configuration={'mode':'local_live','retrieval':retrieval.configuration,
                   'generation':generation.configuration,'limits':limits}
    hashes={'manifest':file_hash(args.approval_manifest),'catalog':file_hash(args.grounding_catalog),
            'assets':file_hash(args.generation_assets),'generation':generation.fingerprint,
            'retrieval':fingerprint(retrieval.configuration)}
    bind_preflight(manifest,catalog,receipt,retrieval_receipt,configuration,hashes,cases)
    if time.monotonic()>=deadline:raise AnswerError('deadline_exceeded')
    ingestion.index.create(min(deadline,time.monotonic()+10))
    try:
        service=AnswerService(retrieval,catalog,generation,configuration)
        service.lock=retrieval.lock
        service.evaluation_cases=cases
        service.collection_name=ingestion.index.collection
        return service
    except BaseException:
        ingestion.close()
        raise


def bind_preflight(manifest, catalog, receipt, retrieval_receipt, configuration, hashes, cases=None):
    validate_f2(retrieval_receipt,'F2ApprovalReceipt')
    if retrieval_receipt['manifest_sha256']!=hashes['manifest']:
        raise AnswerError('configuration_mismatch')
    return validate_bindings(manifest,catalog,receipt,configuration,hashes,cases)


def kernel_limits(read_text):
    try:
        memory=int(read_text('memory.max').strip())
        swap=int(read_text('memory.swap.max').strip())
        quota,period=map(int,read_text('cpu.max').split())
        events=dict(line.split() for line in read_text('memory.events').splitlines())
        peak=int(read_text('memory.peak').strip())
        if memory!=8589934592 or swap!=0 or period<=0 or quota!=4*period or int(events['oom_kill'])!=0 or peak<0:
            raise ValueError
        return {'peak_bytes':peak,'memory_bytes':memory,'cpu_quota':quota,'cpu_period':period}
    except (OSError,KeyError,TypeError,ValueError) as error:
        raise AnswerError('session_unavailable',fatal=True) from error


def _embedding_tokenizer(root,config):
    platform_gate()
    if (not root.is_absolute() or any(p.is_symlink() for p in (root,*root.parents))
            or not os.statvfs(root).f_flag & os.ST_RDONLY):raise AnswerError('model_unavailable')
    verify_assets(root,config['model_file_sha256'])
    import torch
    import transformers
    if torch.__version__!='2.14.1+cpu' or transformers.__version__!='5.18.0':
        raise AnswerError('model_unavailable')
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    tokenizer=transformers.AutoTokenizer.from_pretrained(str(root),local_files_only=True,
                                                        trust_remote_code=False,token=False)
    return tokenizer


def _worker(channel,deadline):
    send_message(channel,{'kind':'owned','pid':os.getpid(),'pgid':os.getpgrp()},deadline)
    payload=receive_message(channel,deadline)
    try:
        observed_limits()
        if payload.get('op')=='storage':
            if set(payload)!={'op','method','path','body'}:raise AnswerError('invalid_input')
            if payload['method'] not in ('GET','POST','PUT','DELETE') or not payload['path'].startswith('/collections/'):
                raise AnswerError('invalid_input')
            result={'response':_storage_request(payload,channel,deadline)}
        elif payload.get('op')=='encode':
            if set(payload)!={'op','directory','config','texts','validate_only'} or type(payload['validate_only']) is not bool:
                raise AnswerError('invalid_input')
            texts=payload['texts']
            if not isinstance(texts,list) or not 1<=len(texts)<=2048 or any(not isinstance(t,str) for t in texts):
                raise AnswerError('invalid_input')
            root=Path(payload['directory'])
            tokenizer=_embedding_tokenizer(root,payload['config'])
            if any(len(tokenizer(t,add_special_tokens=True,truncation=False)['input_ids'])>256 for t in texts):
                raise AnswerError('question_too_long')
            if payload['validate_only']:result={'validated':True}
            else:
                model=load_model(root)
                if model.get_embedding_dimension()!=384 or model.max_seq_length!=256:
                    raise AnswerError('model_unavailable')
                vectors=model.encode(texts,convert_to_numpy=True,show_progress_bar=False).tolist()
                if len(vectors)!=len(texts):raise AnswerError('embedding_failed')
                result={'vectors':validate_vectors(vectors)}
        else:raise AnswerError('invalid_input')
        send_message(channel,{'kind':'result','value':result},deadline)
    except (AnswerError,IngestionError) as error:
        send_message(channel,{'kind':'error','code':error.code},deadline)
    except Exception:  # noqa: BLE001 -- no source/vector/model diagnostic escapes
        send_message(channel,{'kind':'error','code':'model_unavailable'},deadline)


def _storage_request(payload,channel,deadline):
    import httpx
    with httpx.Client(base_url='http://qdrant:6333',trust_env=False,
                      follow_redirects=False,transport=httpx.HTTPTransport(retries=0)) as client:
        if time.monotonic()>=deadline:raise AnswerError('deadline_exceeded')
        if payload['path'].endswith('/points/query'):
            send_message(channel,{'kind':'search','count':1},deadline)
        with client.stream(payload['method'],payload['path'],json=payload['body'],
                           timeout=max(.001,deadline-time.monotonic())) as response:
            if response.status_code==404 and payload['method']=='GET' and '/points' not in payload['path']:
                return None
            if not 200<=response.status_code<300:raise AnswerError('index_failed')
            data=bytearray()
            for block in response.iter_bytes():
                if time.monotonic()>=deadline:raise AnswerError('deadline_exceeded')
                data.extend(block)
                if len(data)>16777216:raise AnswerError('index_failed')
            value=json.loads(data)
            if not isinstance(value,dict) or value.get('status')!='ok':raise AnswerError('index_failed')
            return value['result']


if __name__=='__main__':
    try:
        if len(sys.argv)!=4 or sys.argv[1]!='worker':raise AnswerError('session_unavailable')
        with socket.socket(fileno=int(sys.argv[2])) as channel:
            _worker(channel,float(sys.argv[3]))
    except (ValueError,OSError):raise SystemExit(1) from None
