"""Synthetic native-process probes, never live model acceptance."""
import json
import os
import tempfile
import time

import pytest
from test_answer_cli import make_service

from app.answer.lifecycle import supervise_factory


def native_factory():
    return make_service(clock=time.monotonic)[0]


def run_factory(factory, raw, **options):
    with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as ready:
        source.write(raw)
        source.seek(0)
        code = supervise_factory(factory, source.fileno(), output.fileno(), ready.fileno(),
                                 stop_seconds=.4, **options)
        output.seek(0)
        ready.seek(0)
        return code, output.read(), ready.read()


def test_owned_factory_preserves_delegated_envelopes_and_stops_at_close():
    code, raw, ready = run_factory(native_factory, b'{"op":"inspect"}\n{"op":"close"}\n{"op":"clear"}\n')
    assert code == 0
    assert [json.loads(line)['delegated']['op'] for line in raw.splitlines()] == ['inspect', 'close']
    assert ready == b'F3_READY\n'


def test_factory_runs_outside_parent_group_before_readiness():
    def factory():
        assert os.getpid() == os.getpgrp()
        assert os.getpgrp() != os.getpgid(os.getppid())
        return native_factory()
    assert run_factory(factory, b'')[0] == 0


def test_stalled_startup_is_stopped_without_ready_or_input():
    def stalled():
        time.sleep(10)
    start = time.monotonic()
    assert run_factory(stalled, b'{"op":"inspect"}\n', startup_seconds=.15) == (1, b'', b'')
    assert time.monotonic() - start < 2


def test_factory_exception_does_not_expose_diagnostics():
    def failed():
        raise RuntimeError('private-source-or-model-text')
    assert run_factory(failed, b'') == (1, b'', b'')


def test_stalled_dispatch_is_hard_stopped():
    def factory():
        instance = native_factory()
        instance.retrieval.dispatch = lambda _: time.sleep(10)
        return instance
    start = time.monotonic()
    code, raw, ready = run_factory(factory, b'{"op":"inspect"}\n', request_seconds=.15)
    assert (code, raw, ready) == (1, b'', b'F3_READY\n')
    assert time.monotonic() - start < 2


def test_stopped_output_reader_cannot_block_owned_stop():
    def factory():
        instance = native_factory()
        instance.retrieval.dispatch = lambda _: {'data': 'x' * 1048576}
        return instance
    read, write = os.pipe()
    try:
        with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as ready:
            source.write(b'{"op":"inspect"}\n{"op":"clear"}\n')
            source.seek(0)
            start = time.monotonic()
            assert supervise_factory(factory, source.fileno(), write, ready.fileno(),
                                     request_seconds=.15, stop_seconds=.4) == 1
            assert time.monotonic() - start < 2
            os.set_blocking(read, False)
            assert not os.read(read, 1048576).endswith(b'\n')  # Undelivered partial line.
    finally:
        os.close(read)
        os.close(write)


def test_broken_readiness_channel_never_forwards_input():
    read, write = os.pipe()
    os.close(read)
    try:
        with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as output:
            source.write(b'{"op":"inspect"}\n')
            source.seek(0)
            assert supervise_factory(native_factory, source.fileno(), output.fileno(), write,
                                     stop_seconds=.4) == 1
            output.seek(0)
            assert output.read() == b''
    finally:
        os.close(write)


def test_shortened_test_budget_uses_actual_request_start():
    code,raw,ready = run_factory(native_factory,b'{"op":"answer","use_case_id":"scope","question":"Return policy?"}\n',request_seconds=1)
    result = json.loads(raw)
    assert code == 0 and ready == b'F3_READY\n'
    assert result['status']=='answered' and result['elapsed_ms'] < 1000


def test_fatal_ingestion_predecessor_stops_f3_input():
    from types import SimpleNamespace

    from app.answer.__main__ import consume_session
    instance = native_factory()
    instance.retrieval.ingestion = SimpleNamespace(fatal=False)
    seen=[]
    def dispatch(request):
        seen.append(request)
        instance.retrieval.ingestion.fatal=True
        return {'status':'failed'}
    instance.retrieval.dispatch=dispatch
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output:
        source.write(b'{"op":"inspect"}\n{"op":"clear"}\n')
        source.seek(0)
        assert consume_session(instance,source.fileno(),output.fileno(),cleanup=lambda _:None)==1
    assert len(seen)==1


def test_generation_transport_loss_stops_input_and_returns_nonzero():
    from app.answer.__main__ import consume_session
    from app.answer.validation import AnswerError
    calls=[]
    def adapter(*_):
        calls.append(1)
        raise AnswerError('session_unavailable')
    instance=make_service(adapter,clock=time.monotonic)[0]
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output:
        source.write(b'{"op":"answer","use_case_id":"scope","question":"Return policy?"}\n'*2)
        source.seek(0)
        assert consume_session(instance,source.fileno(),output.fileno(),cleanup=lambda _:None)==1
        output.seek(0)
        assert output.read()==b''
    assert calls==[1] and instance.fatal


def test_parent_term_handler_interrupts_and_is_restored(monkeypatch):
    import signal

    from app.answer import lifecycle
    from app.answer.validation import AnswerError
    old=signal.signal(signal.SIGTERM,signal.SIG_DFL)
    def interrupted_receive(*_):
        handler=signal.getsignal(signal.SIGTERM)
        if not callable(handler):
            raise AnswerError('session_unavailable')
        handler(signal.SIGTERM,None)
    monkeypatch.setattr(lifecycle,'receive_message',interrupted_receive)
    try:
        assert run_factory(native_factory,b'')[0]==130
        assert signal.getsignal(signal.SIGTERM)==signal.SIG_DFL
    finally:
        signal.signal(signal.SIGTERM,old)


def test_consumer_retains_nonfatal_failure_at_eof_and_close():
    from app.answer.__main__ import consume_session
    for ending in [b'', b'{"op":"close"}\n']:
        instance = native_factory()
        instance.retrieval.dispatch = lambda request: {'status': 'failed' if request['op']=='inspect' else 'complete'}
        with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as output:
            source.write(b'{"op":"inspect"}\n'+ending)
            source.seek(0)
            assert consume_session(instance, source.fileno(), output.fileno(), cleanup=lambda _:None) == 1


def test_cleanup_uncertainty_changes_successful_consumer_exit():
    from app.answer.__main__ import consume_session
    instance = native_factory()
    with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as output:
        assert consume_session(instance, source.fileno(), output.fileno(), cleanup=lambda _:False) == 1


def test_delegated_ceiling_reaches_hard_supervisor(monkeypatch):
    from app.answer import __main__ as consumer
    monkeypatch.setattr(consumer,'OPERATION_CEILINGS',{'inspect':.1})
    def factory():
        instance=native_factory()
        instance.retrieval.dispatch=lambda _:time.sleep(10)
        return instance
    start=time.monotonic()
    assert run_factory(factory,b'{"op":"inspect"}\n',request_seconds=1)[0]==1
    assert time.monotonic()-start<.8


def test_private_frozen_cases_never_solicit_stdin_again():
    import socket
    import threading

    from test_answer import SCHEMA, sample

    from app.answer.generation import receive_message, send_message
    def factory():
        instance=native_factory()
        instance.retrieval.dispatch=lambda request:{'op':'ingest','status':'complete'}
        cases=sample(SCHEMA['$defs']['EvaluationCaseSet'])
        for index,case in enumerate(cases['cases']):
            case.update(case_id=str(index),use_case_id='scope',question='Return policy?',expected_status='answered',expected_claim_ids=['returns'],expected_reason=None,acceptable_source_ids=['policy'])
        for case,question in zip(cases['cases'][3:],['What is shipping?','Unknown?']):
            case.update(question=question,expected_status='insufficient_evidence',expected_claim_ids=[],expected_reason='unsupported_question')
        instance.evaluation_cases=cases
        return instance
    parent,host=socket.socketpair();seen=[];errors=[]
    def drive():
        try:
            inputs=0
            while True:
                value=receive_message(host,time.monotonic()+5);seen.append(value['kind'])
                if value['kind'] in ('ready','result'):send_message(host,{'kind':'ack'},time.monotonic()+5)
                elif value['kind']=='input':
                    inputs+=1
                    send_message(host,{'kind':'request','value':{'op':'ingest'}} if inputs==1 else {'kind':'eof'},time.monotonic()+5)
                elif value['kind']=='done':break
        except (ValueError,OSError,StopIteration) as error:errors.append(error)
    thread=threading.Thread(target=drive);thread.start()
    try:
        with tempfile.TemporaryFile() as source:
            assert supervise_factory(factory,source.fileno(),-1,-1,control=parent,request_seconds=1,stop_seconds=.4)==0
        thread.join(5)
        assert not thread.is_alive() and not errors
        assert seen.count('input')==2 and seen.count('case')==5 and seen.count('result')==6
    finally:parent.close();host.close()


def test_no_read_after_fatal_service_result():
    from app.answer.__main__ import consume_session
    instance = native_factory()
    instance.retrieval.fatal = False
    seen = []
    def dispatch(request):
        seen.append(request)
        instance.retrieval.fatal = True
        return {'status': 'failed'}
    instance.retrieval.dispatch = dispatch
    with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as output:
        source.write(b'{"op":"inspect"}\n{"op":"clear"}\n')
        source.seek(0)
        assert consume_session(instance, source.fileno(), output.fileno(), cleanup=lambda _:None) == 1
    assert len(seen) == 1


@pytest.mark.parametrize('setting', [0, -1, True, float('nan'), 241])
def test_invalid_budget_rejected_before_fork(setting):
    with pytest.raises(ValueError):
        supervise_factory(native_factory, 0, 1, 2, request_seconds=setting)
