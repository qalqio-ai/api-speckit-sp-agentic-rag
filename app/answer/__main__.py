"""Bounded injected JSONL consumer. No live F3 factory is enabled."""
import json
import os
import select
import time

from .validation import AnswerError, strict_json, validate_cases

OPERATION_CEILINGS={'ingest':120,'retrieve':120,'inspect':10,'clear':10,'close':45}


def dispatch(service, request):
    if not isinstance(request, dict):
        return service.reject('invalid_input')
    if request.get('op') == 'answer':
        return service.answer(request)
    if request.get('op') in ('ingest', 'inspect', 'clear', 'close', 'retrieve'):
        return service.dispatch(request)
    return service.reject('unknown_operation')


def input_records(fd, deadline):
    """Bounded JSONL input transport, including oversize-line drain."""
    original = os.get_blocking(fd)
    pending = bytearray()
    oversized = False
    current = deadline() if callable(deadline) else deadline
    try:
        os.set_blocking(fd, False)
        while True:
            remaining = current-time.monotonic()
            if remaining <= 0:
                raise AnswerError('deadline_exceeded')
            if not select.select([fd],[],[],min(remaining,1))[0]:
                continue
            try:
                block = os.read(fd,65536)
            except BlockingIOError:
                continue
            if not block:
                return  # Incomplete records at EOF are never dispatched.
            for piece in block.split(b'\n')[:-1]:
                # Re-add LF only for complete fragments; CR is JSON whitespace.
                piece += b'\n'
                pending.extend(piece)
                while b'\n' in pending:
                    line,_,tail = pending.partition(b'\n')
                    if oversized or len(line)>524288:
                        value = None
                    else:
                        try:
                            value = strict_json(bytes(line))
                            if not isinstance(value,dict):
                                value = None
                        except ValueError:
                            value = None
                    pending = bytearray(tail)
                    oversized = False
                    yield value
                    current = deadline() if callable(deadline) else deadline
                if len(pending)>524288:
                    pending.clear()
                    oversized = True
            pending.extend(block.rsplit(b'\n',1)[-1])
            if len(pending)>524288:
                pending.clear()
                oversized = True
    finally:
        try:os.set_blocking(fd,original)
        except OSError:pass  # The caller may already have disposed its input descriptor.


def consume_session(service, input_fd, output_fd, *, cleanup, cases=None,
                    delivery=None, started=None, request_seconds=240,records=None,
                    begin_teardown=None,case_started=None,operation_started=None):
    """Injected consumer with cleanup uncertainty reflected in the exit status."""
    try:
        code = _consume_session(service, input_fd, output_fd, cases=cases,
                                delivery=delivery, started=started,
                                request_seconds=request_seconds,records=records,
                                begin_teardown=begin_teardown,case_started=case_started,operation_started=operation_started)
    except KeyboardInterrupt:
        code = 130
    except (AnswerError, OSError, ValueError):
        code = 1
    try:
        if cleanup(time.monotonic()+45) is False:
            code = code or 1
    except KeyboardInterrupt:
        code = 130
    except Exception:  # noqa: BLE001 -- cleanup failures must force a safe nonzero exit
        code = code or 1
    return code


def _consume_session(service, input_fd, output_fd, *, cases, delivery, started,
                     request_seconds,records,begin_teardown,case_started,operation_started):
    """Injected session consumer; no live readiness or factory authorization."""
    record_deadline = [0]
    record_started = [0]
    successful_ingests = 0
    exit_code = [0]
    def next_deadline(evaluation=False):
        record_started[0] = time.monotonic()
        record_deadline[0] = record_started[0]+request_seconds
        callback=case_started if evaluation else started
        if callback is not None:
            callback(record_deadline[0])
        return record_deadline[0]
    def emit(result,deadline):
        actual = result.get('result',result)
        if actual.get('status') in ('failed','incomplete'):
            exit_code[0] = 1
        if delivery is not None:
            delivery(result,min(deadline,record_deadline[0]))
            return
        raw = (json.dumps(result,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
        write_line(output_fd,raw,min(deadline,record_deadline[0]))
    try:
        if cases is not None:
            validate_cases(cases,service.catalog)
        source=input_records(input_fd,next_deadline) if records is None else records(next_deadline)
        for request in source:
            if cases is not None and (not isinstance(request,dict) or request.get('op')!='ingest'):
                return 1
            if isinstance(request,dict) and request.get('op')=='answer':
                service.answer(request,emit=emit,request_started_at=record_started[0],
                               deadline=record_deadline[0])
            else:
                if isinstance(request,dict) and request.get('op') in ('ingest','retrieve','inspect','clear','close'):
                    ceiling=OPERATION_CEILINGS[request['op']]
                    record_deadline[0]=min(record_deadline[0],record_started[0]+ceiling)
                    if operation_started is not None:
                        operation_started(record_deadline[0])
                    if request['op']=='close' and begin_teardown is not None:
                        begin_teardown()
                remaining = record_deadline[0]-time.monotonic()
                if remaining<=0 or not service.lock.acquire(timeout=remaining):
                    raise AnswerError('deadline_exceeded')
                try:
                    result = dispatch(service,request)
                    emit(result,min(record_deadline[0],time.monotonic()+10))
                finally:
                    service.lock.release()
                if cases is not None and result.get('status')!='complete':
                    return 1
                if cases is not None:
                    successful_ingests += 1
                if isinstance(request,dict) and request.get('op')=='close':
                    return exit_code[0]
            predecessor = getattr(service.retrieval,'ingestion',None)
            if getattr(service,'fatal',False) or getattr(service.retrieval,'fatal',False) or getattr(predecessor,'fatal',False):
                return 1
        if cases is not None:
            if not successful_ingests:
                return 1
            for case in cases['cases']:
                next_deadline(evaluation=True)
                def case_emit(result,deadline,current_case=case):
                    from .evaluation import case_matches
                    if not case_matches(current_case,result):
                        exit_code[0] = 1
                    emit({'case_id':current_case['case_id'],'result':result},deadline)
                service.answer({'op':'answer','use_case_id':case['use_case_id'],'question':case['question']},
                               emit=case_emit,request_started_at=record_started[0],
                               deadline=record_deadline[0])
                if getattr(service,'fatal',False) or getattr(getattr(service.retrieval,'ingestion',None),'fatal',False):
                    return 1
        return exit_code[0]
    except KeyboardInterrupt:
        return 130
    except (AnswerError,OSError,ValueError):
        return 1


def main():
    import sys

    from .generation import PipeChannel
    from .lifecycle import supervise_factory
    from .runtime import platform_gate
    try:
        argv=sys.argv[1:]
        if not argv or argv[0]!='session':raise AnswerError('session_unavailable')
        platform_gate()
        private='--private-wire' in argv
        if private:argv.remove('--private-wire')
        code=supervise_factory(None,0,1,2,argv=argv[1:],
            control=PipeChannel(0,1) if private else None)
        raise SystemExit(code)
    except (AnswerError,OSError,ValueError):
        raise SystemExit('session_unavailable') from None


def write_line(fd, raw, deadline):
    """Bound partial writes by an original deadline; never retry an error envelope."""
    if not isinstance(raw, bytes) or len(raw) > 16777216 or not raw.endswith(b'\n'):
        raise AnswerError('output_too_large')
    blocking = os.get_blocking(fd)
    try:
        os.set_blocking(fd, False)
        position = 0
        while position < len(raw):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AnswerError('deadline_exceeded')
            if not select.select([], [fd], [], min(remaining, 1))[1]:
                continue
            try:
                written = os.write(fd, memoryview(raw)[position:])
            except BlockingIOError:
                continue
            if written <= 0:
                raise AnswerError('session_unavailable')
            position += written
    except (BrokenPipeError, OSError) as error:
        raise AnswerError('session_unavailable') from error
    finally:
        try:
            os.set_blocking(fd, blocking)
        except OSError:
            pass


if __name__ == '__main__':
    main()


def execute(service, request, output_fd, *, cleanup, deadline):
    """Injected single-operation transport; cleanup does not depend on output success.

    This is not a live session supervisor or proof of actual owned-resource cleanup.
    The caller supplies independently bounded cleanup of its injected resources.
    """
    def emit(result, remaining_deadline):
        raw = (json.dumps(result, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
        write_line(output_fd, raw, min(deadline, remaining_deadline))

    try:
        if isinstance(request, dict) and request.get('op') == 'answer':
            return service.answer(request, emit=emit, deadline=deadline)
        remaining = deadline-service.clock()
        if remaining <= 0 or not service.lock.acquire(timeout=remaining):
            raise AnswerError('deadline_exceeded')
        try:
            if service.clock() >= deadline:
                raise AnswerError('deadline_exceeded')
            result = dispatch(service, request)
            emit(result, deadline)
            return result
        finally:
            service.lock.release()
    finally:
        cleanup(time.monotonic() + 45)
