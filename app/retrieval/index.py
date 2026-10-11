"""Read-only exhaustive scope inventory and one full-snapshot exact search."""
import copy
import math

from app.ingestion.embedding import validate_vectors
from app.ingestion.types import IngestionError
from app.ingestion.validation import allowed_ids, validate_shape

from .validation import validate_shape as validate_f2_shape


def verify_scope(ingestion,use_case_id,deadline):
    source_ids=allowed_ids(ingestion.manifest,use_case_id)
    states={key:copy.deepcopy(value) for key,value in ingestion.states.items() if key[0]==use_case_id}
    if any(not s.ready or s.source_status!='complete' for s in states.values()):
        raise IngestionError('scope_not_ready')
    rows={};offset=None;offsets=set()
    scope={'must':[{'key':'use_case_id','match':{'value':use_case_id}},
                   {'key':'source_id','match':{'any':source_ids}}]}
    while True:
        page=ingestion.index.call('POST','/points/scroll',{'filter':scope,'limit':128,'with_payload':True,'with_vector':True,'offset':offset},deadline)
        try:
            if not isinstance(page,dict) or not isinstance(page['points'],list) or len(page['points'])>128:
                raise IngestionError('index_failed')
            for point in page['points']:
                if len(rows)>=2048:raise IngestionError('scope_too_large')
                record={**point['payload'],'vector':point['vector']}
                validate_shape(record,'ChunkRecord');validate_vectors([record['vector']])
                if (str(point['id'])!=record['chunk_id'] or record['chunk_id'] in rows
                    or record['use_case_id']!=use_case_id or record['source_id'] not in source_ids
                    or record['end']-record['start']!=len(record['text'])):
                    raise IngestionError('scope_not_ready')
                expected=ingestion.config
                if any(record[k]!=expected[k] for k in ['model_id','model_commit','tokenizer_fingerprint','configuration_fingerprint']):
                    raise IngestionError('configuration_mismatch')
                rows[record['chunk_id']]=record
            offset=page['next_page_offset']
            if offset is None:break
            if type(offset) not in (str,int) or offset in offsets:raise IngestionError('index_failed')
            offsets.add(offset)
        except IngestionError as error:
            if error.code=='invalid_input':
                raise IngestionError('index_failed') from error
            raise
        except (TypeError,KeyError,ValueError) as error:raise IngestionError('index_failed') from error
        if ingestion.clock()>=deadline:raise IngestionError('deadline_exceeded')
    represented=[]
    for source_id in source_ids:
        actual={k:r for k,r in rows.items() if r['source_id']==source_id}
        state=states.get((use_case_id,source_id))
        if state is None:
            if actual:raise IngestionError('scope_not_ready')
            continue
        if (set(actual)!=state.expected_ids or len(actual)!=state.expected_count
            or len(actual)!=state.current_count or set(state.expected_payload_hashes)!=set(actual)):
            raise IngestionError('scope_not_ready')
        bindings=set()
        for k,r in actual.items():
            if r['revision']!=state.current_verified_revision or ingestion.payload_hash(r)!=state.expected_payload_hashes[k]:
                raise IngestionError('scope_not_ready')
            binding=(r['source_id'],r['revision'],r['content_sha256'])
            if not any((a['use_case_id'],a['source_id'],a['revision'],a['content_sha256'])==(use_case_id,*binding) for a in ingestion.manifest['allowed_sources']):
                raise IngestionError('scope_not_ready')
            bindings.add(binding)
        if len(bindings)>1:raise IngestionError('scope_not_ready')
        for sid,revision,digest in bindings:
            represented.append({'source_id':sid,'revision':revision,'content_sha256':digest})
    if ingestion.clock()>=deadline:raise IngestionError('deadline_exceeded')
    return {'use_case_id':use_case_id,'source_ids':source_ids,'rows':rows,'represented_sources':represented}


def search(ingestion,snapshot,vector,deadline,on_dispatch):
    rows=snapshot['rows']
    body={'query':vector,'params':{'exact':True},'filter':{'must':[
        {'key':'use_case_id','match':{'value':snapshot['use_case_id']}},
        {'key':'source_id','match':{'any':snapshot['source_ids']}},
        {'has_id':sorted(rows)}]},'limit':len(rows),'with_payload':True,'with_vector':False}
    if ingestion.clock()>=deadline:raise IngestionError('deadline_exceeded')
    # Count at the request boundary, after every pre-dispatch deadline check.
    remaining=deadline-ingestion.index.clock()
    if remaining<=0:raise IngestionError('deadline_exceeded')
    on_dispatch()
    try:
        result=ingestion.index.client.request('POST',ingestion.index.path+'/points/query',
                                             body,timeout=min(10,remaining))
    except IngestionError:raise
    except Exception as error:raise IngestionError('index_failed') from error
    try:
        points=result['points'];seen=set();candidates=[]
        if not isinstance(points,list) or len(points)!=len(rows):raise IngestionError('invalid_search_result')
        for p in points:
            ident=p['id'];score=p['score']
            if (not isinstance(ident,str) or ident not in rows or ident in seen
                or type(score) not in (int,float) or not math.isfinite(score) or not -1<=score<=1):
                raise IngestionError('invalid_search_result')
            payload={k:v for k,v in rows[ident].items() if k!='vector'}
            try:
                validate_f2_shape({**p['payload'],'rank':1,'score':score},'EvidencePassage')
            except IngestionError as error:
                raise IngestionError('invalid_search_result') from error
            if p['payload']!=payload:raise IngestionError('invalid_search_result')
            seen.add(ident);candidates.append({**payload,'score':score})
        if seen!=set(rows):raise IngestionError('invalid_search_result')
        if ingestion.clock()>=deadline:raise IngestionError('deadline_exceeded')
        return sorted(candidates,key=lambda p:(-p['score'],p['chunk_id']))
    except IngestionError:raise
    except (KeyError,TypeError,ValueError) as error:raise IngestionError('invalid_search_result') from error
