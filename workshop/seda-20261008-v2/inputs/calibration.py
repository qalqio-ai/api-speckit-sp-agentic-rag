import json
import os
import time
from pathlib import Path
from uuid import uuid4

from app.answer.runtime import (
    LiveEmbedder,
    LiveQuery,
    LiveTransport,
    _embedding_tokenizer,
    observed_limits,
)
from app.ingestion.index import Index
from app.ingestion.service import Service
from app.ingestion.types import SourceDocument
from app.retrieval.evaluation import calibration_summary, propose_threshold
from app.retrieval.index import search, verify_scope

if os.getpgrp()!=os.getpid():os.setsid()
limits=observed_limits()
manifest=json.loads(Path('/fixtures/approval.json').read_text())
config=json.loads(Path('/embedding/f1-model.json').read_text())
processor=LiveQuery('/embedding',config,None)
ingestion=Service(manifest,config,_embedding_tokenizer(Path('/embedding'),config),LiveEmbedder(processor),Index(LiveTransport(None),time.monotonic,str(uuid4())),time.monotonic)
cases=json.loads(Path('/input/development-calibration-v2.json').read_text())
regression={'case_id':'known-receipt-regression','question':'What proof should accompany a return?','expected':{'status':'matched','source_ids':['returns']}}
report={'kind':'live_calibration_measurement','mode':'local_live','cases':[],'acceptance_claimed':False}
start=time.monotonic()
try:
    ingestion.index.create(time.monotonic()+10)
    for line in Path('/fixtures/ingest.jsonl').read_text().splitlines():
        document=json.loads(line);document.pop('op')
        result=ingestion.ingest(SourceDocument(**document))
        if result['status']!='complete':raise RuntimeError(result['error']['code'])
    for case in [*cases,regression]:
        before=time.monotonic();deadline=before+120
        scope=verify_scope(ingestion,'f2-synthetic',min(deadline,time.monotonic()+10))
        vector=processor.encode(case['question'],min(deadline,time.monotonic()+90))
        ingestion.index.client.query_dispatches=0
        candidates=search(ingestion,scope,vector,min(deadline,time.monotonic()+10),lambda:None)
        summary=calibration_summary(case,candidates)
        summary.update(question=case['question'],candidates=[{'source_id':p['source_id'],'chunk_id':p['chunk_id'],'rank':i,'score':p['score'],'passes_original_threshold':p['score']>=0.45614706000000005,'scope_filter_pass':p['use_case_id']=='f2-synthetic','current_id_filter_pass':p['chunk_id'] in scope['rows']} for i,p in enumerate(candidates,1)],elapsed_ms=(time.monotonic()-before)*1000,retrieval_searches=ingestion.index.client.query_dispatches)
        report['cases'].append(summary)
    report['proposed_threshold']=propose_threshold(cases,report['cases'][:-1])
    report['known_regression']=report['cases'][-1]
    report['calibration_cases']=report['cases'][:-1]
    report['threshold_applied']=False
    report['elapsed_ms']=(time.monotonic()-start)*1000
    report['peak_bytes']=observed_limits()['peak_bytes']
finally:
    closed=ingestion.close();report['collection_absent']=closed['status']=='complete'
    if not report['collection_absent']:raise RuntimeError('cleanup_failed')
print(json.dumps(report),flush=True)
