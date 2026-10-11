"""Injected F3 session; no real source, embedding, model or Docker execution."""
import copy
import threading

import pytest
from test_answer import SCHEMA, catalog_probe, receipt_probe, sample

from app.answer import generation, service
from app.answer.__main__ import dispatch


class MemoryPort:
    def __init__(self):
        self.receipt = receipt_probe()
        self.calls = []
        self.busy = False
        self.registry_fingerprint = 'c' * 64

    def retrieve_with_receipt(self, request, *, request_started_at, deadline):
        assert not self.busy
        self.calls.append((copy.deepcopy(request), request_started_at, deadline))
        receipt = copy.deepcopy(self.receipt)
        receipt['retrieval_deadline'] = min(deadline, request_started_at+120)
        return receipt

    def dispatch(self, request):
        assert not self.busy
        return {'delegated': copy.deepcopy(request)}


def make_service(model=None, clock=lambda: 0):
    port = MemoryPort()
    config = sample(SCHEMA['$defs']['AnswerConfiguration'])
    config['retrieval'] = port.receipt['result']['configuration']
    response = {'status':'answered','reason':None,'claims':[{'claim_id':'returns','text':'Unused items require a receipt.','chunk_ids':[port.receipt['result']['evidence'][0]['chunk_id']]}]}
    calls = []
    def adapter(context, deadline):
        assert port.busy
        calls.append((context, deadline))
        return response if model is None else model(context, deadline)
    instance = service.AnswerService(port, catalog_probe(), adapter, config, clock=clock)
    return instance, port, calls


def test_answer_calls_one_receipt_and_one_generator_under_busy_guard():
    instance, port, calls = make_service()
    result = instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['status'] == 'answered'
    assert result['retrieval_searches'] == result['generation_attempts'] == 1
    assert len(port.calls) == len(calls) == 1
    assert port.calls[0] == ({'op':'retrieve','use_case_id':'scope','question':'Return policy?','top_k':3},0,120)
    assert not port.busy
    assert calls[0][1] == 110
    assert result['configuration']['mode'] == 'deterministic'
    assert 'question' not in result and 'prompt' not in result


@pytest.mark.parametrize('question',['Return policy? ','What is shipping?'])
def test_unseen_alias_never_invokes_model(question):
    instance, port, calls = make_service()
    result = instance.answer({'op':'answer','use_case_id':'scope','question':question})
    assert result['status'] == 'insufficient_evidence'
    assert result['reason'] == 'unsupported_question'
    assert result['generation_attempts'] == 0 and len(calls) == 0
    assert len(port.calls) == 1


def test_empty_scope_and_missing_support_are_zero_generation():
    instance, port, calls = make_service()
    port.receipt = receipt_probe([])
    result = instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['reason'] == 'no_evidence'
    assert not calls


@pytest.mark.parametrize('reason', ['conflicting_evidence','no_evidence'])
def test_model_fabricated_reason_fails_without_retry(reason):
    instance, port, calls = make_service(lambda *_: {'status':'insufficient_evidence','reason':reason,'claims':[]})
    result = instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['status'] == 'failed'
    assert result['error']['code'] == 'invalid_model_response'
    assert result['claims'] == result['citations'] == []
    assert len(calls) == 1 and not port.busy


def test_model_failure_never_substitutes_catalog_answer_or_raw_diagnostic():
    def fail(*_):
        raise RuntimeError('private model text')
    instance, _port, calls = make_service(fail)
    result = instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['error']['code'] == 'generation_failed'
    assert 'private' not in str(result)
    assert not result['claims'] and len(calls) == 1


def test_registry_change_after_model_fails_closed():
    instance, port, _calls = make_service()
    def mutate(*_):
        port.registry_fingerprint = 'd' * 64
        return {'status':'insufficient_evidence','reason':'unsupported_question','claims':[]}
    instance.adapter = mutate
    result = instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['error']['code'] == 'configuration_mismatch'
    assert not port.busy


def test_delegate_preserves_original_envelope_and_unknown_ops_reject():
    instance, _port, _ = make_service()
    assert dispatch(instance, {'op':'inspect','use_case_id':'scope'}) == {'delegated':{'op':'inspect','use_case_id':'scope'}}
    result = dispatch(instance, {'op':'tool','destination':'outside'})
    assert result['status'] == 'rejected' and result['op'] is None
    assert result['error']['code'] == 'unknown_operation'


def test_shared_outer_lock_blocks_delegated_mutation_during_generation():
    entered, release, delegated = threading.Event(), threading.Event(), threading.Event()
    def adapter(*_):
        entered.set()
        assert release.wait(1)
        return {'status':'insufficient_evidence','reason':'unsupported_question','claims':[]}
    instance, port, _ = make_service(adapter)
    answer_thread = threading.Thread(target=instance.answer,args=({'op':'answer','use_case_id':'scope','question':'Return policy?'},))
    def delegate():
        dispatch(instance, {'op':'clear','use_case_id':'scope'})
        delegated.set()
    answer_thread.start();assert entered.wait(1)
    delegate_thread = threading.Thread(target=delegate);delegate_thread.start()
    assert not delegated.wait(0.01)
    release.set();answer_thread.join(1);delegate_thread.join(1)
    assert delegated.is_set() and not port.busy


def test_generation_adapter_parses_exact_json_and_never_repairs():
    calls=[]
    def adapter(*_):
        calls.append(1)
        return '{"status":"insufficient_evidence","claims":[],"reason":"unsupported_question"} extra'
    with pytest.raises(ValueError,match='invalid_model_response'):
        generation.generate_response(adapter, {}, 110)
    assert len(calls) == 1


def test_busy_guard_is_held_through_final_validation(monkeypatch):
    from app.answer.validation import validate_result
    instance, port, _ = make_service()
    def check(result):
        assert port.busy
        return validate_result(result)
    monkeypatch.setattr(service,'validate_result',check)
    assert instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})['status'] == 'answered'
    assert not port.busy


def test_original_deadline_expiry_returns_no_partial_answer():
    now=[0]
    def delay(*_):
        now[0]=111
        return {'status':'insufficient_evidence','claims':[],'reason':'unsupported_question'}
    instance,port,_=make_service(delay,clock=lambda:now[0])
    result=instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['error']['code']=='deadline_exceeded'
    assert result['claims']==result['citations']==[] and not port.busy


def test_well_formed_model_insufficiency_has_one_attempt():
    instance,_,calls=make_service(lambda *_:{'status':'insufficient_evidence','claims':[],'reason':'unsupported_question'})
    result=instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['reason']=='unsupported_question' and result['generation_attempts']==1 and len(calls)==1


def test_port_failure_after_query_retains_actual_search_count():
    instance,port,calls=make_service()
    port.receipt['result'].update(status='failed',evidence=[],evidence_count=0,error={'code':'index_failed','message':'index_failed'})
    result=instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'})
    assert result['retrieval_searches']==1 and not calls
    assert result['status']=='failed'


def test_stopped_output_consumer_fails_by_deadline():
    import os
    import time

    from app.answer.__main__ import write_line
    read_fd,write_fd=os.pipe()
    os.set_blocking(write_fd,False)
    try:
        while True:
            try:
                os.write(write_fd,b'x'*4096)
            except BlockingIOError:
                break
        start=time.monotonic()
        with pytest.raises(ValueError,match='deadline_exceeded'):
            write_line(write_fd,b'{"ok":true}\n',start+0.03)
        assert time.monotonic()-start<1
    finally:
        os.close(read_fd);os.close(write_fd)


def test_broken_pipe_emits_no_second_result():
    import os

    from app.answer.__main__ import write_line
    read_fd,write_fd=os.pipe();os.close(read_fd)
    try:
        with pytest.raises(ValueError,match='session_unavailable'):
            write_line(write_fd,b'{}\n',1e20)
    finally:
        os.close(write_fd)


def test_partial_output_writes_transfer_complete_line(monkeypatch):
    import os
    import time

    from app.answer.__main__ import write_line
    read_fd,write_fd=os.pipe()
    real_write=os.write
    def partial(fd,raw):
        return real_write(fd,raw[:2])
    monkeypatch.setattr(os,'write',partial)
    try:
        write_line(write_fd,b'{"ok":true}\n',time.monotonic()+1)
        assert os.read(read_fd,4096)==b'{"ok":true}\n'
    finally:
        os.close(read_fd);os.close(write_fd)


def test_delivery_keeps_guard_and_uses_remaining_validation_budget():
    instance,port,_=make_service()
    delivered=[]
    def emit(result,deadline):
        assert port.busy
        delivered.append((result['status'],deadline))
    result=instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'},emit=emit)
    assert delivered==[('answered',10)] and result['status']=='answered' and not port.busy


def test_output_failure_runs_independent_cleanup_and_propagates(monkeypatch):
    import time

    from app.answer import __main__ as cli
    from app.answer.validation import AnswerError
    instance,port,_=make_service(clock=time.monotonic)
    def fail(*_):
        raise AnswerError('session_unavailable')
    monkeypatch.setattr(cli,'write_line',fail)
    cleaned=[]
    with pytest.raises(ValueError,match='session_unavailable'):
        cli.execute(instance,{'op':'answer','use_case_id':'scope','question':'Return policy?'},1,
                    cleanup=lambda deadline:cleaned.append(deadline),deadline=time.monotonic()+240)
    assert len(cleaned)==1 and cleaned[0]>time.monotonic() and not port.busy


def test_serialization_time_does_not_reset_delivery_budget(monkeypatch):
    from app.answer.validation import validate_result
    now=[0]
    instance,_,_=make_service(clock=lambda:now[0])
    def costly(result):
        now[0]+=8
        return validate_result(result)
    monkeypatch.setattr(service,'validate_result',costly)
    delivered=[]
    instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'},emit=lambda _,deadline:delivered.append(deadline))
    assert delivered==[10]


def test_nested_answer_rejection_does_not_steal_outer_guard():
    instance,port,_=make_service()
    request={'op':'answer','use_case_id':'scope','question':'Return policy?'}
    def nested(*_):
        assert instance.answer(request)['error']['code']=='session_unavailable'
        return {'status':'insufficient_evidence','claims':[],'reason':'unsupported_question'}
    instance.adapter=nested
    assert instance.answer(request)['status']=='insufficient_evidence'
    assert not port.busy


def test_expired_original_deadline_performs_no_retrieval_or_generation():
    instance,port,calls=make_service()
    with pytest.raises(ValueError,match='deadline_exceeded'):
        instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'},request_started_at=0,deadline=-1)
    assert not port.calls and not calls


def test_short_remaining_budget_is_passed_to_both_adapters():
    instance,port,calls=make_service()
    result=instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'},request_started_at=0,deadline=2)
    assert result['status']=='answered'
    assert port.calls[0][2]==2 and calls[0][1]==2


def test_expired_transport_deadline_never_invokes_adapters():
    import time

    from app.answer.__main__ import execute
    instance,port,calls=make_service(clock=time.monotonic)
    cleaned=[]
    with pytest.raises(ValueError,match='deadline_exceeded'):
        execute(instance,{'op':'answer','use_case_id':'scope','question':'Return policy?'},1,
                cleanup=lambda deadline:cleaned.append(deadline),deadline=time.monotonic()-1)
    assert not port.calls and not calls and len(cleaned)==1


def test_lock_wait_expires_without_extending_original_budget():
    import time

    from app.answer.validation import AnswerError
    instance,port,calls=make_service(clock=time.monotonic)
    held,release=threading.Event(),threading.Event()
    def hold():
        with instance.lock:
            held.set()
            release.wait(1)
    thread=threading.Thread(target=hold);thread.start();assert held.wait(1)
    try:
        started=time.monotonic()
        with pytest.raises(AnswerError,match='deadline_exceeded'):
            instance.answer({'op':'answer','use_case_id':'scope','question':'Return policy?'},
                            request_started_at=started,deadline=started+0.03)
        assert time.monotonic()-started<0.5 and not port.calls and not calls
    finally:
        release.set();thread.join(1)


def test_bounded_worker_hard_timeout_and_no_raw_exception():
    import time

    from app.answer.generation import supervised_call
    def hang(_):
        time.sleep(2)
        return {}
    started=time.monotonic()
    with pytest.raises(ValueError,match='deadline_exceeded'):
        supervised_call(hang,{},started+0.3)
    assert time.monotonic()-started<1
    def fail(_):
        raise RuntimeError('secret worker diagnostic')
    with pytest.raises(ValueError,match='generation_failed') as error:
        supervised_call(fail,{},time.monotonic()+1)
    assert 'secret' not in str(error.value)


def test_bounded_worker_returns_strict_json_without_pickle():
    import time

    from app.answer.generation import supervised_call
    result=supervised_call(lambda payload:{'echo':payload['value']},{'value':'synthetic'},time.monotonic()+1)
    assert result=={'echo':'synthetic'}


def test_framed_transport_rejects_oversize_before_body_read():
    import socket
    import struct
    import time

    from app.answer.generation import receive_message
    sender,receiver=socket.socketpair()
    try:
        sender.sendall(struct.pack('!I',16777217))
        with pytest.raises(ValueError,match='session_unavailable'):
            receive_message(receiver,time.monotonic()+1)
    finally:
        sender.close();receiver.close()


def test_framed_transport_rejects_oversize_frame():
    import socket
    import struct
    import time

    from app.answer.generation import receive_message
    sender,receiver=socket.socketpair()
    try:
        sender.sendall(struct.pack('!II',100,65537))
        with pytest.raises(ValueError,match='session_unavailable'):
            receive_message(receiver,time.monotonic()+1)
    finally:
        sender.close();receiver.close()


def test_evaluation_consumes_actual_normal_answers_without_expectations_as_context():
    from test_answer import catalog_probe

    from app.answer.evaluation import evaluate
    instance,_,calls=make_service()
    cases=sample(SCHEMA['$defs']['EvaluationCaseSet'])
    for index,case in enumerate(cases['cases']):
        case.update(case_id=str(index),use_case_id='scope',question='Return policy?',expected_status='answered',expected_claim_ids=['returns'],expected_reason=None,acceptable_source_ids=['policy'])
    for case,question in zip(cases['cases'][3:],['What is shipping?','Unknown?']):
        case.update(question=question,expected_status='insufficient_evidence',expected_claim_ids=[],expected_reason='unsupported_question')
    outputs=evaluate(instance,cases)
    assert len(outputs)==5 and len(calls)==3
    assert all(set(output)=={'case_id','result'} for output in outputs)
    assert outputs[0]['result']['status']=='answered'
    assert outputs[-1]['result']['generation_attempts']==0
    assert all('expected_claim_ids' not in context for context,_ in calls)
    assert instance.catalog==catalog_probe()


def test_local_decode_enforces_template_tokens_eos_and_exact_completion():
    from types import SimpleNamespace

    from app.answer.generation import decode_once
    class Tokenizer:
        def apply_chat_template(self,messages,**options):
            assert options=={'tokenize':False,'add_generation_prompt':True}
            assert len(messages)==2
            return 'synthetic prompt'
        def __call__(self,prompt,**options):
            assert options=={'return_tensors':'pt','add_special_tokens':False,'truncation':False}
            return {'input_ids':SimpleNamespace(shape=(1,self.count))}
        def decode(self,tokens,**options):
            assert tokens==[7,2] and options=={'skip_special_tokens':True}
            return '{"status":"insufficient_evidence","claims":[],"reason":"unsupported_question"}'
        count=10
    class Model:
        def generate(self,**options):
            assert options['max_new_tokens']==384 and options['do_sample'] is False and options['num_beams']==1
            return [[0]*10+[7,2]]
    tokenizer=Tokenizer();attempts=[]
    assert decode_once(tokenizer,Model(),{'question':'synthetic'},[2],2,lambda:attempts.append(1))['reason']=='unsupported_question'
    assert attempts==[1]
    tokenizer.count=2049
    with pytest.raises(ValueError,match='context_too_large'):
        decode_once(tokenizer,Model(),{'question':'synthetic'},[2],2,lambda:attempts.append(1))
    assert attempts==[1]


def test_missing_legitimate_eos_cannot_be_accepted():
    from types import SimpleNamespace

    from app.answer.generation import decode_once
    class Tokenizer:
        def apply_chat_template(self,*_,**__):return 'synthetic'
        def __call__(self,*_,**__):return {'input_ids':SimpleNamespace(shape=(1,1))}
        def decode(self,*_,**__):raise AssertionError('decode must not accept an unstopped completion')
    class Model:
        def generate(self,**__):return [[0]+[7]*384]
    with pytest.raises(ValueError,match='output_too_large'):
        decode_once(Tokenizer(),Model(),{},[2],2,lambda:None)


@pytest.mark.parametrize('scenario',['replacement','neighbor','clear','failure_before_dispatch'])
def test_current_scope_replacement_clear_and_zero_dispatch_failure(scenario):
    instance,port,calls=make_service()
    request={'op':'answer','use_case_id':'scope','question':'Return policy?'}
    if scenario=='replacement':
        port.receipt['scope_snapshot']['represented_sources'][0]['revision']='v2'
        port.receipt['result']['evidence'][0]['revision']='v2'
        expected='catalog_mismatch'
    elif scenario=='neighbor':
        request['use_case_id']='neighbor';expected='configuration_mismatch'
    elif scenario=='clear':
        port.receipt=receipt_probe([]);port.receipt['scope_snapshot']['represented_sources']=[]
        result=instance.answer(request)
        assert result['reason']=='no_evidence' and not calls
        return
    else:
        port.receipt['retrieval_searches']=0;port.receipt['scope_snapshot']=None
        port.receipt['result'].update(status='failed',evidence=[],evidence_count=0,error={'code':'index_failed','message':'index_failed'})
        expected='retrieval_failed'
    result=instance.answer(request)
    assert result['error']['code']==expected and not calls and result['claims']==result['citations']==[]
    assert result['retrieval_searches']==(0 if scenario=='failure_before_dispatch' else 1)


def test_generation_attempt_events_are_actual_and_not_inferred_from_errors():
    import time

    from app.answer.generation import supervised_call
    from app.answer.validation import AnswerError
    seen=[]
    def generate(_,announce):
        announce()
        raise AnswerError('generation_failed')
    with pytest.raises(ValueError,match='generation_failed'):
        supervised_call(generate,{},time.monotonic()+1,notify=seen.append,events=True)
    assert [event['kind'] for event in seen]==['owned','attempt']
    seen.clear()
    def unavailable(_,announce):
        raise AnswerError('model_unavailable')
    with pytest.raises(ValueError,match='model_unavailable'):
        supervised_call(unavailable,{},time.monotonic()+1,notify=seen.append,events=True)
    assert [event['kind'] for event in seen]==['owned']


def test_runtime_configuration_rejects_custom_code_and_short_context():
    from app.answer.generation import validate_model_configuration
    config={'model_type':'llama','architectures':['LlamaForCausalLM'],'max_position_embeddings':8192,'eos_token_id':2,'pad_token_id':2}
    assert validate_model_configuration(config)==config
    for key,value in [('model_type','custom'),('auto_map',{}),('max_position_embeddings',1024)]:
        broken={**config,key:value}
        with pytest.raises(ValueError,match='model_unavailable'):
            validate_model_configuration(broken)


def test_input_transport_drains_oversize_and_discards_incomplete_line():
    import tempfile
    import time

    from app.answer.__main__ import input_records
    with tempfile.TemporaryFile() as stream:
        stream.write(b'x'*524289+b'\n'+b'{"op":"inspect"}\n'+b'{"op":"clear"}')
        stream.seek(0)
        assert list(input_records(stream.fileno(),time.monotonic()+1))==[None,{'op':'inspect'}]


def test_input_transport_rejects_bad_json_without_poisoning_next_line():
    import tempfile
    import time

    from app.answer.__main__ import input_records
    with tempfile.TemporaryFile() as stream:
        stream.write(b'{"op":"inspect","op":"clear"}\n[1]\n{"op":"inspect"}\n')
        stream.seek(0)
        assert list(input_records(stream.fileno(),time.monotonic()+1))==[None,None,{'op':'inspect'}]


def test_session_close_stops_input_and_independent_cleanup_runs():
    import json
    import tempfile
    import time

    from app.answer.__main__ import consume_session
    instance,_port,_=make_service(clock=time.monotonic)
    clean=[]
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output:
        source.write(b'{"op":"inspect"}\n{"op":"close"}\n{"op":"clear"}\n');source.seek(0)
        assert consume_session(instance,source.fileno(),output.fileno(),cleanup=clean.append)==0
        output.seek(0)
        assert [json.loads(line)['delegated']['op'] for line in output]==['inspect','close']
    assert len(clean)==1 and 44<clean[0]-time.monotonic()<=45


def test_session_output_failure_stops_input_and_still_cleans():
    import os
    import tempfile
    import time

    from app.answer.__main__ import consume_session
    instance,_port,_=make_service(clock=time.monotonic)
    clean=[];read,write=os.pipe();os.close(read)
    try:
        with tempfile.TemporaryFile() as source:
            source.write(b'{"op":"inspect"}\n{"op":"clear"}\n');source.seek(0)
            assert consume_session(instance,source.fileno(),write,cleanup=clean.append)==1
    finally:os.close(write)
    assert len(clean)==1


def test_fresh_exec_worker_reports_owned_process_and_zero_attempt_on_platform_gate():
    import time

    from app.answer.generation import supervised_module
    events=[]
    # Deliberately invalid assets: no model acquisition or real load is attempted.
    with pytest.raises(ValueError,match='model_unavailable'):
        supervised_module({'op':'probe','directory':'/nonexistent','assets':{}},time.monotonic()+8,
                          notify=events.append,isolated=True)
    assert len(events)==1 and events[0]['kind']=='owned' and events[0]['pid']==events[0]['pgid']


@pytest.mark.parametrize('ingest_status',['complete','failed'])
def test_session_evaluation_runs_after_successful_ingest_eof_only(ingest_status):
    import json
    import tempfile
    import time

    from app.answer.__main__ import consume_session
    instance,port,calls=make_service(clock=time.monotonic)
    # Preserve the actual F1 status contract; no real source is ingested.
    port.dispatch=lambda request:{'op':'ingest','status':ingest_status}
    cases=sample(SCHEMA['$defs']['EvaluationCaseSet'])
    for index,case in enumerate(cases['cases']):
        case.update(case_id=str(index),use_case_id='scope',question='Return policy?',expected_status='answered',expected_claim_ids=['returns'],expected_reason=None,acceptable_source_ids=['policy'])
    for case,question in zip(cases['cases'][3:],['What is shipping?','Unknown?']):
        case.update(question=question,expected_status='insufficient_evidence',expected_claim_ids=[],expected_reason='unsupported_question')
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output:
        source.write(b'{"op":"ingest"}\n');source.seek(0)
        exit_code=consume_session(instance,source.fileno(),output.fileno(),cleanup=lambda _:None,cases=cases)
        output.seek(0);results=[json.loads(line) for line in output]
    assert exit_code==(0 if ingest_status=='complete' else 1)
    assert len(results)==(6 if ingest_status=='complete' else 1)
    assert len(calls)==(3 if ingest_status=='complete' else 0)


@pytest.mark.parametrize('raw',[b'',b'{"op":"ingest"}'])
def test_session_evaluation_requires_complete_successful_ingest_before_eof(raw):
    import tempfile
    import time

    from app.answer.__main__ import consume_session
    instance,_port,calls=make_service(clock=time.monotonic)
    cases=sample(SCHEMA['$defs']['EvaluationCaseSet'])
    for index,case in enumerate(cases['cases']):
        case.update(case_id=str(index),use_case_id='scope',question='Return policy?',expected_status='answered',expected_claim_ids=['returns'],expected_reason=None,acceptable_source_ids=['policy'])
    for case,question in zip(cases['cases'][3:],['What is shipping?','Unknown?']):
        case.update(question=question,expected_status='insufficient_evidence',expected_claim_ids=[],expected_reason='unsupported_question')
    clean=[]
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output:
        source.write(raw);source.seek(0)
        assert consume_session(instance,source.fileno(),output.fileno(),cleanup=clean.append,cases=cases)==1
        output.seek(0);assert output.read()==b''
    assert calls==[] and len(clean)==1


def test_evaluation_wrong_expected_reason_causes_nonzero_exit():
    import tempfile
    import time

    from app.answer.__main__ import consume_session
    instance,port,calls=make_service(clock=time.monotonic)
    port.dispatch=lambda request:{'op':'ingest','status':'complete'}
    cases=sample(SCHEMA['$defs']['EvaluationCaseSet'])
    for index,case in enumerate(cases['cases']):
        case.update(case_id=str(index),use_case_id='scope',question='Return policy?',expected_status='answered',expected_claim_ids=['returns'],expected_reason=None,acceptable_source_ids=['policy'])
    for case,question in zip(cases['cases'][3:],['What is shipping?','Unknown?']):
        case.update(question=question,expected_status='insufficient_evidence',expected_claim_ids=[],expected_reason='no_evidence')
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output:
        source.write(b'{"op":"ingest"}\n');source.seek(0)
        assert consume_session(instance,source.fileno(),output.fileno(),cleanup=lambda _:None,cases=cases)==1
    assert len(calls)==3
