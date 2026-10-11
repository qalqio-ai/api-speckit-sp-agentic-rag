"""Deterministic wiring probes, never live quality or resource-enforcement evidence."""
import copy
import hashlib
import json

import pytest
from test_answer import SCHEMA, catalog_probe, sample

from app.answer.runtime import bind_preflight, kernel_limits
from app.answer.validation import AnswerError


def kernel_files():
    return {'memory.max':'8589934592','memory.swap.max':'0','cpu.max':'400000 100000',
            'memory.events':'oom 0\noom_kill 0\n','memory.peak':'12345'}


def test_kernel_limits_require_actual_hard_memory_swap_cpu_values():
    assert kernel_limits(kernel_files().__getitem__)['peak_bytes']==12345


@pytest.mark.parametrize('field,value',[('memory.max','max'),('memory.swap.max','max'),
                                      ('cpu.max','max 100000'),('memory.max','1'),
                                      ('cpu.max','200000 100000'),('memory.events','oom_kill 1\n')])
def test_kernel_limit_mismatch_fails_closed(field,value):
    files=kernel_files();files[field]=value
    with pytest.raises(AnswerError):
        kernel_limits(files.__getitem__)


def preflight_records():
    from pathlib import Path

    from app.answer.validation import SCHEMAS
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'tests/fixtures/f1/approval.json').read_text())
    catalog=catalog_probe()
    manifest['allowed_sources']=[{k:rule[k] for k in ('use_case_id','source_id','revision','content_sha256')} for rule in catalog['source_rules']]
    digest=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    hashes={name:'a'*64 for name in ('assets','generation','retrieval')}
    hashes['manifest']=digest(manifest);catalog['manifest_sha256']=hashes['manifest'];hashes['catalog']=digest(catalog)
    receipt=sample(SCHEMA['$defs']['F3ApprovalReceipt']);receipt.update(manifest_sha256=hashes['manifest'],catalog_sha256=hashes['catalog'])
    config=sample(SCHEMA['$defs']['AnswerConfiguration'])
    config['generation'].update(asset_manifest_sha256=hashes['assets'],configuration_fingerprint=hashes['generation'],catalog_sha256=hashes['catalog'])
    f2=next(s for p,s in SCHEMAS.items() if '002-f2' in str(p))
    retrieval_receipt=sample(f2['$defs']['F2ApprovalReceipt'],root/'specs/002-f2-retrieval/contracts/serialization.schema.json');retrieval_receipt['manifest_sha256']=hashes['manifest']
    return manifest,catalog,receipt,retrieval_receipt,config,hashes


def test_bind_checks_both_purpose_receipts_before_factory_resources():
    args=preflight_records()
    assert bind_preflight(*args)==args[4]
    changed=copy.deepcopy(args);changed[3]['manifest_sha256']='f'*64
    with pytest.raises(AnswerError):
        bind_preflight(*changed)


def test_bad_source_purpose_binding_prevents_model_startup(tmp_path,monkeypatch):
    from app.answer import runtime
    manifest,catalog,receipt,retrieval_receipt,config,_hashes=preflight_records()
    retrieval_receipt['manifest_sha256']='f'*64
    values={'approval-manifest':manifest,'grounding-catalog':catalog,'answer-approval':receipt,
            'retrieval-approval':retrieval_receipt,'generation-assets':{},'tmpfs-proof':{'type':'tmpfs','size':268435456}}
    argv=[]
    for name,value in values.items():
        path=tmp_path/(name+'.json');path.write_text(json.dumps(value))
        argv+=['--'+name,str(path)]
    for name in ['embedding-model-dir','generation-model-dir']:
        path=tmp_path/name;path.mkdir();argv+=['--'+name,str(path)]
    (tmp_path/'embedding-model-dir'/'f1-model.json').write_text(json.dumps(config['retrieval']['model_configuration']))
    argv+=['--min-score','.5','--calibration-id','reviewed']
    monkeypatch.setattr(runtime,'observed_limits',dict)
    def forbidden(*args,**kwargs):raise AssertionError('model startup before source purpose approval')
    monkeypatch.setattr(runtime,'LocalGenerator',forbidden)
    with pytest.raises(AnswerError):runtime.build_factory(argv,1000)


def test_live_receipt_uses_worker_dispatch_not_outer_adapter_entry(monkeypatch):
    from types import SimpleNamespace

    from app.answer.runtime import LiveRetrieval
    from app.retrieval.service import RetrievalService
    service=object.__new__(LiveRetrieval)
    service.clock=__import__('time').monotonic
    service.lock=__import__('threading').RLock()
    transport=SimpleNamespace(query_dispatches=9)
    service.ingestion=SimpleNamespace(index=SimpleNamespace(client=transport))
    def outer(*args,**kwargs):
        assert transport.query_dispatches==0
        return {'retrieval_searches':1,'result':{'status':'failed'}}
    monkeypatch.setattr(RetrievalService,'retrieve_with_receipt',outer)
    assert service.retrieve_with_receipt({})['retrieval_searches']==0


def test_registry_checks_original_identity_even_after_group_escape():
    from app.answer.runtime import registry_absent
    identity={'pid':12,'pgid':12,'start_ticks':30,'cgroup_sha256':'a'*64}
    assert registry_absent([identity],lambda pid:None)
    assert registry_absent([identity],lambda pid:{**identity,'start_ticks':31})
    assert not registry_absent([identity],lambda pid:{**identity,'pgid':99})
