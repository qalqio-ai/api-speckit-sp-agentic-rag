"""Owned-stack orchestration with injected Docker/protocol fixtures only."""
import json
import tempfile
import time

import pytest

from app.answer import demo


class FakeChannel:
    def __init__(self,messages):self.messages=iter(messages);self.sent=[]


def test_private_wrapper_preserves_result_and_acks_only_after_delivery(monkeypatch):
    channel=FakeChannel([{'kind':'ready','remaining':120}, {'kind':'input','remaining':240},
                         {'kind':'result','value':{'status':'complete','op':'inspect'},'remaining':10},
                         {'kind':'input','remaining':240},{'kind':'teardown','remaining':45},
                         {'kind':'collection','absent':True},{'kind':'done','code':0}])
    monkeypatch.setattr(demo,'receive_message',lambda c,d:next(c.messages))
    monkeypatch.setattr(demo,'send_message',lambda c,v,d:c.sent.append(v))
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output,tempfile.TemporaryFile() as ready:
        source.write(b'{"op":"inspect"}\n');source.seek(0)
        code,cleanup_deadline,absent=demo.forward_session(channel,source.fileno(),output.fileno(),ready.fileno(),time.monotonic()+120)
        output.seek(0);ready.seek(0)
        assert json.loads(output.read())=={'status':'complete','op':'inspect'}
        assert ready.read()==b'F3_READY\n'
    assert code==0 and absent and cleanup_deadline<=time.monotonic()+45
    assert channel.sent==[{'kind':'ack'},{'kind':'request','value':{'op':'inspect'}},{'kind':'ack'},{'kind':'eof'}]


def test_wrapper_repeated_teardown_cannot_extend_original_clock(monkeypatch):
    channel=FakeChannel([{'kind':'ready','remaining':120},{'kind':'teardown','remaining':.1},
                         {'kind':'teardown','remaining':45},{'kind':'done','code':1}])
    monkeypatch.setattr(demo,'receive_message',lambda c,d:next(c.messages))
    monkeypatch.setattr(demo,'send_message',lambda *args:None)
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output,tempfile.TemporaryFile() as ready:
        _,deadline,_=demo.forward_session(channel,source.fileno(),output.fileno(),ready.fileno(),time.monotonic()+120)
    assert deadline<=time.monotonic()+.1


def test_output_break_does_not_ack_or_emit_second_record(monkeypatch):
    import os
    channel=FakeChannel([{'kind':'ready','remaining':120},
                         {'kind':'result','value':{'status':'complete'},'remaining':10}])
    monkeypatch.setattr(demo,'receive_message',lambda c,d:next(c.messages))
    monkeypatch.setattr(demo,'send_message',lambda c,v,d:c.sent.append(v))
    read,write=os.pipe();os.close(read)
    try:
        with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as ready,pytest.raises(ValueError):
            demo.forward_session(channel,source.fileno(),write,ready.fileno(),time.monotonic()+120)
    finally:os.close(write)
    assert channel.sent==[{'kind':'ack'}]


def test_owned_stack_cleanup_attempts_all_exact_resources_even_after_failure():
    calls=[]
    def command(argv,deadline):
        calls.append((argv,deadline))
        if argv[1:3]==['container','rm']:return {'returncode':1,'stdout':b'','stderr':b''}
        if argv[1:3]==['network','rm']:return {'returncode':0,'stdout':b'','stderr':b''}
        return {'returncode':1,'stdout':b'','stderr':b'permission denied'}
    assert not demo.remove_owned_stack(['a'*64,'b'*64],'c'*64,time.monotonic()+30,command)
    assert any(a[1:3]==['network','rm'] for a,d in calls)
    assert any(a[1:3]==['container','inspect'] for a,d in calls)
    assert any(a[1:3]==['network','inspect'] for a,d in calls)
    assert all('prune' not in a for a,d in calls)


def test_teardown_clock_survives_forwarding_exception(monkeypatch):
    channel=FakeChannel([{'kind':'ready','remaining':120},{'kind':'teardown','remaining':.1},
                         {'kind':'invalid'}])
    monkeypatch.setattr(demo,'receive_message',lambda c,d:next(c.messages))
    monkeypatch.setattr(demo,'send_message',lambda *args:None)
    state={}
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output,tempfile.TemporaryFile() as ready,pytest.raises(ValueError):
        demo.forward_session(channel,source.fileno(),output.fileno(),ready.fileno(),time.monotonic()+120,state=state)
    assert state['teardown_deadline']<=time.monotonic()+.1


def test_evaluation_eof_does_not_start_cleanup_or_request_more_input(monkeypatch):
    channel=FakeChannel([{'kind':'ready','remaining':120},{'kind':'input','remaining':.01},
                         {'kind':'case','remaining':240},
                         {'kind':'result','value':{'case_id':'one'},'remaining':10},
                         {'kind':'case','remaining':240},
                         {'kind':'result','value':{'case_id':'two'},'remaining':10},
                         {'kind':'teardown','remaining':45},{'kind':'collection','absent':True},
                         {'kind':'done','code':0}])
    state={}
    def receive(c,d):
        value=next(c.messages)
        if value['kind']=='case':
            time.sleep(.02)
            assert 'teardown_deadline' not in state and d>time.monotonic()
        if value['kind']=='result':assert d>time.monotonic()+200
        return value
    monkeypatch.setattr(demo,'receive_message',receive)
    monkeypatch.setattr(demo,'send_message',lambda c,v,d:c.sent.append(v))
    with tempfile.TemporaryFile() as source,tempfile.TemporaryFile() as output,tempfile.TemporaryFile() as ready:
        assert demo.forward_session(channel,source.fileno(),output.fileno(),ready.fileno(),
            time.monotonic()+120,state=state,evaluation_mode=True)[0]==0
        output.seek(0)
        assert len(output.readlines())==2
    assert channel.sent==[{'kind':'ack'},{'kind':'eof'},{'kind':'ack'},{'kind':'ack'}]


def test_owned_qdrant_create_has_the_storage_endpoint_alias():
    calls=[]
    def command(argv,deadline):
        calls.append(argv)
        if argv[1:3]==['image','inspect']:
            return {'returncode':0,'stdout':json.dumps([{'Id':'sha256:'+'d'*64}]).encode(),'stderr':b''}
        if argv[1:3]==['network','create'] or argv[1]=='create':
            return {'returncode':0,'stdout':('a'*64 if argv[1]=='create' else 'b'*64).encode(),'stderr':b''}
        return {'returncode':1,'stdout':b'','stderr':b'permission denied'}
    assert demo.execute_stack({'project':'f3-'+'c'*32},0,1,2,command=command)==1
    create=next(a for a in calls if a[1]=='create')
    assert create[create.index('--network-alias')+1]=='qdrant'


def test_command_stops_descendants_before_releasing_leader_pid(monkeypatch):
    import os
    import sys

    from app.answer.validation import AnswerError
    calls=[]
    original=os.killpg
    def stop(pid,signum):
        if not signum:return original(pid,signum)
        calls.append((pid,signum))
        assert os.getpgid(pid)==pid
        return original(pid,signum)
    monkeypatch.setattr(os,'killpg',stop)
    # Child closes inherited pipes, so leader/EOF alone cannot establish absence.
    code='import os,time; p=os.fork(); (os.close(1),os.close(2),time.sleep(.4)) if p==0 else None'
    try:demo.run_command([sys.executable,'-c',code],time.monotonic()+3)
    except AnswerError:pass  # Remaining orphan zombies make absence uncertain.
    assert calls and calls[0][1]!=0


def test_lost_create_reply_recovers_only_verified_owned_resources():
    project='f3-'+'d'*32
    def command(argv,deadline):
        if argv[2]=='ls':
            assert 'label=com.docker.compose.project='+project in argv
            return {'returncode':0,'stdout':(('a'*64 if argv[1]=='container' else 'b'*64)+'\n').encode(),'stderr':b''}
        record={'Config':{'Labels':{'com.docker.compose.project':project,'com.docker.compose.service':'qdrant'}},'Name':'/'+project+'-qdrant'} if argv[1]=='container' else {'Labels':{'com.docker.compose.project':project},'Name':project+'_f3'}
        return {'returncode':0,'stdout':json.dumps([record]).encode(),'stderr':b''}
    containers,network,certain=demo.recover_owned_stack(project,[],None,time.monotonic()+30,command)
    assert (containers,network,certain)==(['a'*64],'b'*64,True)
