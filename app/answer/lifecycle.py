"""Owned native factory supervision; production runtime activation is separate.

The fork entry point is for deterministic fixtures only. A fresh exec factory and
Docker/cgroup/collection verification must precede any production activation.
No callable, live model, approval or runtime is supplied by this module.
"""
import json
import math
import os
import resource
import signal
import socket
import subprocess
import sys
import time

from .__main__ import consume_session, write_line
from .generation import _stop_child, receive_message, send_message
from .validation import AnswerError


def _bounded(value, maximum):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= maximum:
        raise ValueError('invalid_budget')


def _native_child(factory, channel, input_fd, startup_deadline, request_seconds,remote=False):
    """Only the owned child can construct the fixture service; stdout stays private."""
    try:
        os.setsid()
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        null = os.open(os.devnull,os.O_RDWR)
        for fd in (1,2):
            os.dup2(null,fd)
        maximum = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        maximum = 65536 if maximum == resource.RLIM_INFINITY else int(maximum)
        keep = {channel.fileno(),input_fd,0,1,2}
        previous = 3
        for fd in sorted(fd for fd in keep if fd >= 3):
            os.closerange(previous,fd)
            previous = fd+1
        os.closerange(previous,maximum)
        send_message(channel, {'kind':'owned','pid':os.getpid(),'pgid':os.getpgrp()},startup_deadline)
        state=[startup_deadline]
        teardown=[None]
        if factory is None:
            from .runtime import build_factory, owned_identity
            setup=receive_message(channel,startup_deadline)
            if set(setup)!={'kind','arguments','remote'} or setup['kind']!='setup' or type(setup['remote']) is not bool:
                raise AnswerError('session_unavailable')
            remote=setup['remote']
            def notify(event):
                if event['kind']=='owned':
                    identity=owned_identity(event['pid'],os.getpgrp())
                    send_message(channel,{'kind':'descendant','identity':identity},state[0])
            instance=build_factory(setup['arguments'],startup_deadline,notify)
        else:
            instance = factory()
        send_message(channel, {'kind':'ready','evaluation':getattr(instance,'evaluation_cases',None) is not None},startup_deadline)
        if receive_message(channel,startup_deadline) != {'kind':'ack'}:
            raise AnswerError('session_unavailable')
        def started(deadline):
            state[0]=deadline
            send_message(channel,{'kind':'started','deadline':deadline},deadline)
        def case_started(deadline):
            state[0]=deadline
            send_message(channel,{'kind':'case-started','deadline':deadline},deadline)
        def operation_started(deadline):
            state[0]=deadline
            send_message(channel,{'kind':'operation','deadline':deadline},deadline)
        def delivery(result,deadline):
            send_message(channel,{'kind':'result','result':result,'deadline':deadline},deadline)
            if receive_message(channel,deadline) != {'kind':'ack'}:
                raise AnswerError('session_unavailable')
        def records(next_deadline):
            while True:
                deadline=next_deadline()
                value=receive_message(channel,deadline)
                if value=={'kind':'eof'}:return
                if set(value)!={'kind','value'} or value['kind']!='request':
                    raise AnswerError('session_unavailable',fatal=True)
                yield value['value']
        def begin_teardown():
            if teardown[0] is None:
                teardown[0]=time.monotonic()+45
                state[0]=min(teardown[0],time.monotonic()+10)
                send_message(channel,{'kind':'teardown','deadline':teardown[0]},state[0])
        def cleanup(_deadline):
            if factory is not None:return None
            begin_teardown()
            result=instance.retrieval.ingestion.close()
            send_message(channel,{'kind':'collection','absent':result['status']=='complete'},state[0])
            from .runtime import observed_limits
            send_message(channel,{'kind':'metrics','peak_bytes':observed_limits()['peak_bytes']},state[0])
            return result['status']=='complete'
        code = consume_session(instance,input_fd,-1,cleanup=cleanup,
                               cases=getattr(instance,'evaluation_cases',None),
                               delivery=delivery,started=started,request_seconds=request_seconds,
                               records=records if remote else None,
                               case_started=case_started,operation_started=operation_started,
                               begin_teardown=begin_teardown if factory is None else None)
        send_message(channel,{'kind':'done','code':code},min(time.monotonic()+1,teardown[0] or float('inf')))
    except BaseException:  # noqa: BLE001
        # Deliberately no raw diagnostic or second failed-channel write.
        os._exit(1)
    finally:
        channel.close()
        os._exit(0)


def supervise_factory(factory, input_fd, output_fd, readiness_fd, *, startup_seconds=120,
                      request_seconds=240, stop_seconds=5,argv=None,control=None):
    """Hard-stop a deterministic fixture group independently of public delivery.

    One private message at a time, acknowledged only after the full public line
    transfers. The child holds its service lock/busy flag during this handshake.
    An unreaped direct leader reserves the PID until whole-group stop is verified.
    Native group absence is not Docker, cgroup or owned collection absence.
    """
    for value,maximum in ((startup_seconds,120),(request_seconds,240),(stop_seconds,5)):
        _bounded(value,maximum)
    # signal.signal also rejects non-main-thread use before creating resources.
    original_handlers = {}
    def interrupted(_signum,_frame):
        raise KeyboardInterrupt
    for signum in (signal.SIGINT,signal.SIGTERM):
        original_handlers[signum] = signal.signal(signum,interrupted)
    startup_deadline = time.monotonic()+startup_seconds
    try:
        parent,child = socket.socketpair()
        try:
            process=None
            if factory is None:
                duplicate=os.dup(input_fd)
                try:
                    process=subprocess.Popen([sys.executable,'-B','-m','app.answer.lifecycle','session-worker',
                        str(child.fileno()),str(duplicate),str(startup_deadline)],
                        pass_fds=(child.fileno(),duplicate),close_fds=True,
                        stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                        env={'PATH':os.defpath,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1',
                             'TOKENIZERS_PARALLELISM':'false','PYTHONDONTWRITEBYTECODE':'1'})
                    pid=process.pid
                finally:os.close(duplicate)
            else:pid = os.fork()
        except BaseException:
            parent.close()
            child.close()
            raise
    except BaseException:
        for signum,handler in original_handlers.items():
            signal.signal(signum,handler)
        raise
    if pid == 0:
        parent.close()
        _native_child(factory,child,input_fd,startup_deadline,request_seconds,control is not None)
    child.close()
    code = 1
    grouped = False
    cleanup_deadline = None
    registry=[]
    def record(value):
        from .runtime import register_identity
        if set(value)!={'kind','identity'}:raise AnswerError('session_unavailable')
        register_identity(registry,value['identity'],pid)
    try:
        owned = receive_message(parent,startup_deadline)
        if owned != {'kind':'owned','pid':pid,'pgid':pid} or os.getpgid(pid) != pid:
            raise AnswerError('session_unavailable')
        grouped = True
        if factory is None:
            send_message(parent,{'kind':'setup','arguments':argv,'remote':control is not None},startup_deadline)
        message=receive_message(parent,startup_deadline)
        while message.get('kind')=='descendant':
            if factory is not None:raise AnswerError('session_unavailable')
            record(message)
            message=receive_message(parent,startup_deadline)
        if set(message)!={'kind','evaluation'} or message['kind']!='ready' or type(message['evaluation']) is not bool:
            raise AnswerError('session_unavailable')
        evaluation_mode=message['evaluation']
        if control is None:write_line(readiness_fd,b'F3_READY\n',startup_deadline)
        else:
            send_message(control,{'kind':'ready','remaining':max(0,startup_deadline-time.monotonic())},startup_deadline)
            if receive_message(control,startup_deadline)!={'kind':'ack'}:raise AnswerError('session_unavailable')
        send_message(parent,{'kind':'ack'},startup_deadline)
        phase = 'started'
        deadline = time.monotonic()+request_seconds
        input_ended=False
        while True:
            value = receive_message(parent,deadline)
            if not isinstance(value,dict):
                raise AnswerError('session_unavailable')
            if value.get('kind')=='descendant' and factory is None:
                record(value)
                continue  # Independent kernel check does not reset clocks.
            if value.get('kind')=='teardown' and factory is None and set(value)=={'kind','deadline'}:
                if cleanup_deadline is None:
                    _bounded(value['deadline']-time.monotonic(),45)
                    cleanup_deadline=value['deadline']
                    if control is not None:
                        send_message(control,{'kind':'teardown','remaining':max(0,cleanup_deadline-time.monotonic())},deadline)
                deadline=min(deadline,cleanup_deadline-35)
                continue
            if value.get('kind')=='collection' and factory is None and set(value)=={'kind','absent'} and type(value['absent']) is bool:
                if not value['absent']:code=1
                if control is not None:send_message(control,value,deadline)
                continue
            if value.get('kind')=='metrics' and factory is None and set(value)=={'kind','peak_bytes'} and type(value['peak_bytes']) is int:
                if control is not None:send_message(control,value,deadline)
                continue
            if value.get('kind') == 'done' and set(value)=={'kind','code'} and type(value['code']) is int and value['code'] in (0,1,130):
                code = value['code']
                break
            if value.get('kind')=='case-started' and set(value)=={'kind','deadline'} and cleanup_deadline is None:
                if not evaluation_mode:raise AnswerError('session_unavailable')
                if control is not None and not input_ended:raise AnswerError('session_unavailable')
                _bounded(value['deadline']-time.monotonic(),request_seconds)
                deadline=value['deadline'];phase='result'
                if control is not None:
                    send_message(control,{'kind':'case','remaining':max(0,deadline-time.monotonic())},deadline)
                continue
            if value.get('kind')=='operation' and phase=='result' and set(value)=={'kind','deadline'}:
                _bounded(value['deadline']-time.monotonic(),request_seconds)
                deadline=min(deadline,value['deadline'])
                if control is not None:
                    send_message(control,{'kind':'operation','remaining':max(0,deadline-time.monotonic())},deadline)
                continue
            if value.get('kind') == 'started' and phase == 'started' and set(value)=={'kind','deadline'}:
                _bounded(value['deadline']-time.monotonic(),request_seconds)
                deadline = min(deadline,value['deadline'])
                phase = 'result'
                if control is not None:
                    send_message(control,{'kind':'input','remaining':max(0,deadline-time.monotonic())},deadline)
                    operation=receive_message(control,deadline)
                    if operation!={'kind':'eof'} and (not isinstance(operation,dict) or set(operation)!={'kind','value'} or operation['kind']!='request'):
                        raise AnswerError('session_unavailable')
                    send_message(parent,operation,deadline)
                    input_ended=operation=={'kind':'eof'}
                    if input_ended and evaluation_mode:deadline=time.monotonic()+request_seconds
            elif value.get('kind') == 'result' and phase == 'result' and set(value)=={'kind','result','deadline'}:
                if type(value['deadline']) not in (int,float) or not math.isfinite(value['deadline']):
                    raise AnswerError('session_unavailable')
                delivery_deadline = min(deadline,value['deadline'],time.monotonic()+10)
                raw = (json.dumps(value['result'],ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
                if control is None:write_line(output_fd,raw,delivery_deadline)
                else:
                    send_message(control,{'kind':'result','value':value['result'],
                        'remaining':max(0,delivery_deadline-time.monotonic())},delivery_deadline)
                    if receive_message(control,delivery_deadline)!={'kind':'ack'}:
                        raise AnswerError('session_unavailable')
                send_message(parent,{'kind':'ack'},delivery_deadline)
                phase = 'started'
                deadline = min(time.monotonic()+request_seconds,cleanup_deadline or float('inf'))
            else:
                raise AnswerError('session_unavailable')
    except KeyboardInterrupt:
        code = 130
    except (AnswerError,OSError,ValueError,TypeError):
        code = 1
    finally:
        # The first teardown clock is immutable, including repeated interruption.
        cleanup_deadline = cleanup_deadline or time.monotonic()+45
        for signum in (signal.SIGINT,signal.SIGTERM):
            signal.signal(signum,signal.SIG_IGN)
        try:
            # A child can finish setsid before its handshake reaches the parent.
            # getpgid of our still-unreaped direct child is an ownership check.
            grouped = grouped or os.getpgid(pid) == pid
            if not _stop_child(pid,grouped,min(cleanup_deadline,time.monotonic()+stop_seconds)):
                code = code or 1
            elif process is not None:process.returncode=0
            if factory is None:
                from .runtime import registry_absent
                if not registry_absent(registry):code=code or 1
        except OSError:
            code = code or 1
        finally:
            parent.close()
            for signum,handler in original_handlers.items():
                signal.signal(signum,handler)
    if control is not None:
        try:
            send_message(control,{'kind':'done','code':code},min(cleanup_deadline,time.monotonic()+1))
        except (AnswerError,OSError,ValueError):code=code or 1
    return code


if __name__=='__main__':
    if len(sys.argv)!=5 or sys.argv[1]!='session-worker':raise SystemExit(1)
    with socket.socket(fileno=int(sys.argv[2])) as channel:
        _native_child(None,channel,int(sys.argv[3]),float(sys.argv[4]),240)
