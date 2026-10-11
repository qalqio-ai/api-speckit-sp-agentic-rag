"""Reviewable wrapper configuration; execution remains gated on genuine live readiness."""
import argparse
import ctypes
import json
import math
import os
import re
import select
import signal
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

from .__main__ import input_records, write_line
from .generation import PipeChannel, _stop_child, receive_message, send_message
from .validation import AnswerError


def forward_session(channel,input_fd,output_fd,ready_fd,startup_deadline,*,state=None,evaluation_mode=False):
    input_deadline=[startup_deadline]
    records=input_records(input_fd,lambda:input_deadline[0])
    try:
        return _forward_session(channel,records,input_deadline,output_fd,ready_fd,startup_deadline,state if state is not None else {},evaluation_mode)
    finally:records.close()


def _forward_session(channel,records,input_deadline,output_fd,ready_fd,startup_deadline,state,evaluation_mode):
    """Forward one private message, retaining original deadlines across VM clocks."""
    deadline=startup_deadline
    cleanup_deadline=None
    collection_absent=False
    ready=False
    while True:
        value=receive_message(channel,deadline)
        if not isinstance(value,dict):raise AnswerError('session_unavailable')
        kind=value.get('kind')
        if 'remaining' in value:
            remaining=value['remaining']
            ceiling=120 if kind=='ready' else 45 if kind=='teardown' else 10 if kind=='result' else 240
            if type(remaining) not in (float,int) or not math.isfinite(remaining) or not 0<remaining<=ceiling:
                raise AnswerError('session_unavailable')
            current=min(deadline,time.monotonic()+remaining)
        if kind=='ready' and not ready and set(value)=={'kind','remaining'}:
            write_line(ready_fd,b'F3_READY\n',current)
            send_message(channel,{'kind':'ack'},current)
            ready=True;deadline=time.monotonic()+240
        elif kind=='input' and ready and set(value)=={'kind','remaining'}:
            input_deadline[0]=current
            try:request=next(records)
            except StopIteration:message={'kind':'eof'}
            else:message={'kind':'request','value':request}
            if (message['kind']=='eof' and not evaluation_mode) or isinstance(message.get('value'),dict) and message['value'].get('op')=='close':
                cleanup_deadline=cleanup_deadline or time.monotonic()+45
                state['teardown_deadline']=cleanup_deadline
            state['request_started']=time.monotonic()
            send_message(channel,message,current)
            deadline=time.monotonic()+240 if evaluation_mode and message['kind']=='eof' else current
        elif kind=='case' and ready and evaluation_mode and cleanup_deadline is None and set(value)=={'kind','remaining'}:
            deadline=time.monotonic()+value['remaining']
            state['request_started']=time.monotonic()
        elif kind=='operation' and ready and set(value)=={'kind','remaining'}:
            deadline=current
        elif kind=='result' and ready and set(value)=={'kind','value','remaining'}:
            raw=(json.dumps(value['value'],ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
            write_line(output_fd,raw,current)
            state['requests']=state.get('requests',0)+1
            state['max_latency_ms']=max(state.get('max_latency_ms',0),
                (time.monotonic()-state.get('request_started',time.monotonic()))*1000)
            send_message(channel,{'kind':'ack'},current)
            deadline=time.monotonic()+240 if cleanup_deadline is None else cleanup_deadline
        elif kind=='teardown' and ready and set(value)=={'kind','remaining'}:
            cleanup_deadline=min(cleanup_deadline or float('inf'),time.monotonic()+min(45,value['remaining']))
            state['teardown_deadline']=cleanup_deadline
            deadline=min(deadline,cleanup_deadline)
        elif kind=='collection' and ready and set(value)=={'kind','absent'} and type(value['absent']) is bool:
            collection_absent=value['absent']
        elif kind=='metrics' and ready and set(value)=={'kind','peak_bytes'} and type(value['peak_bytes']) is int and 0<=value['peak_bytes']<=8589934592:
            state['runner_peak_bytes']=value['peak_bytes']
        elif kind=='done' and ready and set(value)=={'kind','code'} and type(value['code']) is int and value['code'] in (0,1,130):
            return value['code'],cleanup_deadline or time.monotonic()+45,collection_absent
        else:raise AnswerError('session_unavailable')


def recover_owned_stack(project,containers,network,deadline,command):
    """Recover an uncertain create reply by unique labels plus exact owned names."""
    if not re.fullmatch('f3-[a-f0-9]{32}',project):return containers,network,False
    recovered=list(containers)
    try:
        for kind,maximum in (('container',2),('network',1)):
            argv=['docker',kind,'ls']+(['--all'] if kind=='container' else [])
            result=command([*argv,'--no-trunc','--filter','label=com.docker.compose.project='+project,
                            '--format','{{.ID}}'],min(deadline,time.monotonic()+2))
            ids=result['stdout'].decode('utf-8','strict').split()
            if result['returncode']!=0 or len(ids)>maximum or len(set(ids))!=len(ids):
                raise AnswerError('session_unavailable')
            for identity in ids:
                if not re.fullmatch('[a-f0-9]{64}',identity):raise AnswerError('session_unavailable')
                result=command(['docker',kind,'inspect',identity],min(deadline,time.monotonic()+2))
                items=json.loads(result['stdout'])
                if result['returncode']!=0 or not isinstance(items,list) or len(items)!=1:
                    raise AnswerError('session_unavailable')
                item=items[0]
                labels=item['Config']['Labels'] if kind=='container' else item['Labels']
                if labels['com.docker.compose.project']!=project:raise AnswerError('session_unavailable')
                if kind=='container':
                    service=labels['com.docker.compose.service']
                    if service not in ('runner','qdrant') or item['Name']!='/'+project+'-'+service:
                        raise AnswerError('session_unavailable')
                    if identity not in recovered:recovered.append(identity)
                else:
                    if item['Name']!=project+'_f3' or network not in (None,identity):
                        raise AnswerError('session_unavailable')
                    network=identity
        return recovered,network,True
    except (AnswerError,OSError,ValueError,KeyError,TypeError):return recovered,network,False


def remove_owned_stack(containers,network,deadline,command):
    """Bound remove and independent absence checks; unknown errors are not absence."""
    ids=[*containers]+([network] if network else [])
    if any(not re.fullmatch('[a-f0-9]{64}',i) for i in ids) or len(set(ids))!=len(ids):
        return False
    success=True
    actions=[]
    if containers:actions.append(['docker','container','rm','--force',*containers])
    if network:actions.append(['docker','network','rm',network])
    for argv in actions:
        try:
            result=command(argv,min(deadline,time.monotonic()+5))
            success=result['returncode']==0 and success
        except (AnswerError,OSError,ValueError):success=False
    for resource,identity in [('container',i) for i in containers]+([('network',network)] if network else []):
        try:
            result=command(['docker',resource,'inspect',identity],min(deadline,time.monotonic()+5))
            error=result['stderr'].decode('utf-8','strict').strip()
            expected={f'Error: No such object: {identity}',f'Error: No such {resource}: {identity}',
                      f'Error response from daemon: No such {resource}: {identity}',
                      f'Error response from daemon: network {identity} not found'}
            success=bool(result['returncode']!=0 and error in expected) and success
        except (AnswerError,OSError,ValueError):success=False
    return success


def child_exited(pid):
    """Observe a direct child without reaping the PID reservation (Linux/macOS)."""
    if hasattr(os,'waitid'):
        value=os.waitid(os.P_PID,pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
        return value is not None and value.si_pid==pid
    if sys.platform!='darwin':raise AnswerError('session_unavailable')
    library=ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True)
    info=ctypes.create_string_buffer(128)
    if library.waitid(1,ctypes.c_uint(pid),ctypes.byref(info),os.WEXITED|os.WNOHANG|os.WNOWAIT)!=0:
        raise AnswerError('session_unavailable')
    return any(info.raw)


def run_command(argv,deadline):
    """Bound process, bytes and group termination without shell/env-file reads."""
    if time.monotonic()>=deadline:raise AnswerError('deadline_exceeded')
    process=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,close_fds=True,start_new_session=True,
        env={'PATH':os.environ.get('PATH',os.defpath)})
    buffers={process.stdout.fileno():bytearray(),process.stderr.fileno():bytearray()}
    active=set(buffers)
    reaped=False
    work_deadline=deadline-min(1,max(0,(deadline-time.monotonic())*.2))
    try:
        for fd in active:os.set_blocking(fd,False)
        while active:
            remaining=work_deadline-time.monotonic()
            if remaining<=0:raise AnswerError('deadline_exceeded')
            readable,_,_=select.select(list(active),[],[],min(1,remaining))
            for fd in readable:
                try:block=os.read(fd,65536)
                except BlockingIOError:continue
                if not block:active.remove(fd);continue
                buffers[fd].extend(block)
                if sum(map(len,buffers.values()))>16777216:raise AnswerError('output_too_large')
        while not child_exited(process.pid):
            if time.monotonic()>=work_deadline:raise AnswerError('deadline_exceeded')
            time.sleep(.005)
        # Kill the reserved group before reaping. A zombie leader cannot be reused;
        # a descendant surviving EOF must be stopped even on the success path.
        try:os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        except PermissionError:
            if sys.platform!='darwin':raise
        code=process.wait(timeout=max(.001,deadline-time.monotonic()))
        reaped=True
        try:os.killpg(process.pid,0)
        except ProcessLookupError:pass
        except OSError as error:raise AnswerError('session_unavailable') from error
        else:raise AnswerError('session_unavailable')
        return {'returncode':code,'stdout':bytes(buffers[process.stdout.fileno()]),
                'stderr':bytes(buffers[process.stderr.fileno()])}
    except subprocess.TimeoutExpired as error:raise AnswerError('deadline_exceeded') from error
    finally:
        if not reaped:
            stopped=_stop_child(process.pid,True,min(deadline,time.monotonic()+5))
            if stopped:process.returncode=1
        process.stdout.close();process.stderr.close()


QDRANT_IMAGE='qdrant/qdrant:v1.19.1@sha256:12364fe851b9f17356fc88189fc06d1b521262e04659ec7345975b00c9246a10'


def execute_stack(plan,input_fd,output_fd,ready_fd,*,command=run_command):
    """Execute only this unique owned stack; no pull, prune or settings change."""
    startup_deadline=time.monotonic()+120
    teardown_deadline=None
    progress={}
    containers=[];network=None;attach=None
    network_attempted=False;container_attempts=0
    code=1;collection_absent=False
    old={}
    def interrupted(_signal,_frame):raise KeyboardInterrupt
    for signum in (signal.SIGINT,signal.SIGTERM):old[signum]=signal.signal(signum,interrupted)
    def checked(argv,deadline=startup_deadline):
        result=command(argv,deadline)
        if result['returncode']!=0:raise AnswerError('session_unavailable')
        return result['stdout']
    def inspect(kind,identity):
        data=json.loads(checked(['docker',kind,'inspect',identity]))
        if not isinstance(data,list) or len(data)!=1:raise AnswerError('session_unavailable')
        return data[0]
    def identity(raw):
        value=raw.decode().strip()
        if not re.fullmatch('[a-f0-9]{64}',value):raise AnswerError('session_unavailable')
        return value
    try:
        # An already built immutable image is required; build/run authorization is
        # preserved, but missing assets/receipts never cause a build or installation.
        runner_image=inspect('image','f3-grounded-rag:local')['Id']
        qdrant_image=inspect('image',QDRANT_IMAGE)['Id']
        net_name=plan['project']+'_f3'
        label=['--label','com.docker.compose.project='+plan['project']]
        network_attempted=True
        network=identity(checked(['docker','network','create','--internal',*label,net_name]))
        container_attempts+=1
        qdrant=identity(checked(['docker','create','--pull=never','--name',plan['project']+'-qdrant',
            *label,'--label','com.docker.compose.service=qdrant','--network',net_name,'--network-alias','qdrant',
            '--memory','1073741824','--memory-swap','1073741824',
            '--tmpfs','/qdrant/storage:size=268435456',qdrant_image]))
        containers.append(qdrant)
        checked(['docker','start',qdrant])
        proof=checked(['docker','exec',qdrant,'stat','-f','-c','%T %S %b','/qdrant/storage']).decode().split()
        if len(proof)!=3 or proof[0]!='tmpfs' or int(proof[1])*int(proof[2])!=268435456:
            raise AnswerError('session_unavailable')
        from app.ingestion.index import verify_tmpfs

        from .validation import bounded_json
        verify_tmpfs(bounded_json(plan['mounts']['/input/tmpfs-proof.json'],16384))
        mounts=[]
        for target,host in plan['mounts'].items():
            # Commas cannot be represented unambiguously in Docker's mount CSV.
            if ',' in host:raise AnswerError('invalid_input')
            mounts+=['--mount',f'type=bind,src={host},dst={target},readonly']
        container_attempts+=1
        runner=identity(checked(['docker','create','--pull=never','--name',plan['project']+'-runner',
            *label,'--label','com.docker.compose.service=runner','--network',net_name,
            '--init','--read-only','--interactive','--memory','8589934592',
            '--memory-swap','8589934592','--cpus','4','--tmpfs','/tmp:size=67108864',
            '--env','HF_HUB_OFFLINE=1','--env','TRANSFORMERS_OFFLINE=1',
            '--env','TOKENIZERS_PARALLELISM=false',*mounts,runner_image,
            *plan['command'],'--private-wire']))
        containers.append(runner)
        attach=subprocess.Popen(['docker','start','--attach','--interactive',runner],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            close_fds=True,start_new_session=True,env={'PATH':os.environ.get('PATH',os.defpath)})
        # Retry only observed not-running startup state; no second work attempt.
        while True:
            observed=inspect('container',runner)
            if observed['State']['Running']:break
            if time.monotonic()>=startup_deadline:raise AnswerError('deadline_exceeded')
            time.sleep(.01)
        observed_q=inspect('container',qdrant)
        observed_n=inspect('network',network)
        verify_runtime(plan,observed,observed_q,observed_n)
        if observed['Image']!=runner_image or observed_q['Image']!=qdrant_image:
            raise AnswerError('session_unavailable')
        channel=PipeChannel(attach.stdout.fileno(),attach.stdin.fileno())
        if 'qdrant' not in observed_q['NetworkSettings']['Networks'][net_name].get('Aliases',[]):
            raise AnswerError('session_unavailable')
        code,teardown_deadline,collection_absent=forward_session(channel,input_fd,output_fd,ready_fd,startup_deadline,
            state=progress,evaluation_mode='--evaluation-cases' in plan['command'])
        measurement=command(['docker','exec',qdrant,'cat','/sys/fs/cgroup/memory.peak'],
                            min(teardown_deadline,time.monotonic()+2))
        peak=int(measurement['stdout'])
        if measurement['returncode']!=0 or not 0<=peak<=1073741824:
            raise AnswerError('session_unavailable')
        progress['qdrant_peak_bytes']=peak
    except KeyboardInterrupt:code=130
    except (AnswerError,OSError,ValueError,KeyError,TypeError):code=1
    finally:
        teardown_deadline=teardown_deadline or progress.get('teardown_deadline') or time.monotonic()+45
        for signum in old:signal.signal(signum,signal.SIG_IGN)
        try:
            if attach is not None:
                if not _stop_child(attach.pid,True,min(teardown_deadline,time.monotonic()+5)):
                    code=code or 1
                else:attach.returncode=0
                attach.stdin.close();attach.stdout.close()
            docker_deadline=min(teardown_deadline,time.monotonic()+30)
            if network_attempted and (network is None or len(containers)<container_attempts):
                containers,network,certain=recover_owned_stack(plan['project'],containers,network,docker_deadline,command)
                if not certain:code=code or 1
            if not remove_owned_stack(containers,network,docker_deadline,command):
                code=code or 1
            if not collection_absent:code=code or 1
            if 'runner_peak_bytes' in progress and 'qdrant_peak_bytes' in progress:
                safe={k:progress[k] for k in ('runner_peak_bytes','qdrant_peak_bytes','max_latency_ms','requests') if k in progress}
                safe.update(mode='local_live',exit_code=code,collection_absent=collection_absent)
                try:
                    write_line(ready_fd,b'F3_METRICS '+json.dumps(safe,allow_nan=False).encode()+b'\n',
                               min(teardown_deadline,time.monotonic()+1))
                except (AnswerError,OSError,ValueError):code=code or 1
        finally:
            for signum,handler in old.items():signal.signal(signum,handler)
    return code

MOUNTS = {
    'approval_manifest':'/input/manifest.json',
    'retrieval_approval':'/input/retrieval.json',
    'answer_approval':'/input/answer.json',
    'grounding_catalog':'/input/catalog.json',
    'embedding_model_dir':'/embedding',
    'generation_model_dir':'/generation',
    'generation_assets':'/input/assets.json',
    'tmpfs_proof':'/input/tmpfs-proof.json',
    'evaluation_cases':'/input/cases.json',
}


def prepare(argv):
    """Validate explicit locations without reading files or granting approval.

    This plan has no execution method: approving sources/model assets and genuine
    F2/F3 readiness is still required. Paths are never taken from environment files.
    """
    parser = argparse.ArgumentParser()
    for name in MOUNTS:
        parser.add_argument('--'+name.replace('_','-'),required=name!='evaluation_cases')
    parser.add_argument('--min-score',required=True,type=float)
    parser.add_argument('--calibration-id',required=True)
    args = vars(parser.parse_args(argv))
    if not math.isfinite(args['min_score']) or not -1 <= args['min_score'] <= 1:
        raise AnswerError('configuration_mismatch')
    if not args['calibration_id'].strip() or len(args['calibration_id'])>128:
        raise AnswerError('configuration_mismatch')
    mounts = {}
    command = ['python','-B','-m','app.answer','session']
    for name,target in MOUNTS.items():
        if args[name] is None:
            continue
        path = Path(args[name])
        if (not path.is_absolute() or any(p.is_symlink() for p in (path,*path.parents))
                or (not path.is_dir() if name.endswith('_dir') else not path.is_file())):
            raise AnswerError('invalid_input')
        mounts[target] = str(path.resolve(strict=True))
        command += ['--'+name.replace('_','-'),target]
    command += ['--min-score',str(args['min_score']),'--calibration-id',args['calibration_id']]
    return {'project':'f3-'+uuid4().hex,'mounts':mounts,'command':command}


def verify_runtime(plan, runner, qdrant, network):
    """Validate captured inspect fields; not proof of kernel cgroup/mount enforcement.

    The eventual wrapper must obtain fresh inspect snapshots, verify the immutable
    runner image, /proc cgroup membership and actual tmpfs mount, then independently
    verify absence after cleanup. These fixture checks do not activate that wrapper.
    """
    try:
        identities = [runner['Id'],qdrant['Id'],network['Id']]
        if any(not isinstance(i,str) or not re.fullmatch('[a-f0-9]{64}',i) for i in identities) or len(set(identities))!=3:
            raise ValueError
        net_name = plan['project']+'_f3'
        if (network['Internal'] is not True
                or network['Labels']['com.docker.compose.project'] != plan['project']
                or set(network['Containers']) != set(identities[:2])):
            raise ValueError
        for item,name,memory,tmpfs in (
            (runner,'runner',8589934592,{'/tmp':'size=67108864'}),
            (qdrant,'qdrant',1073741824,{'/qdrant/storage':'size=268435456'}),
        ):
            labels = item['Config']['Labels']
            state,host = item['State'],item['HostConfig']
            if (labels['com.docker.compose.project'] != plan['project']
                    or labels['com.docker.compose.service'] != name
                    or state['Running'] is not True or state['OOMKilled'] is not False
                    or type(state['Pid']) is not int or state['Pid']<=0
                    or type(host['Memory']) is not int or host['Memory'] != memory
                    or type(host['MemorySwap']) is not int or host['MemorySwap'] != memory
                    or host['Privileged'] is not False or host['PidMode'] != ''
                    or host['NetworkMode'] != net_name or host['Tmpfs'] != tmpfs
                    or (name=='runner' and (host['ReadonlyRootfs'] is not True or host['NanoCpus'] != 4000000000))
                    or set(item['NetworkSettings']['Networks']) != {net_name}
                    or item['NetworkSettings']['Networks'][net_name]['NetworkID'] != network['Id']):
                raise ValueError
            mounts = item['Mounts']
            expected = plan['mounts'] if name=='runner' else {}
            # Docker may report the configured tmpfs alongside bind mounts.
            binds = [m for m in mounts if m['Type']=='bind']
            other = [m for m in mounts if m['Type']!='bind']
            if (len(binds)!=len(expected) or {m['Destination']:m['Source'] for m in binds}!=expected
                    or any(m['RW'] is not False for m in binds)
                    or any(m['Type']!='tmpfs' or m['Destination'] not in tmpfs for m in other)):
                raise ValueError
        return tuple(identities)
    except (KeyError,TypeError,ValueError) as error:
        raise AnswerError('session_unavailable') from error


def cleanup_commands(plan, runner_id, qdrant_id, network_id):
    """Review-only commands for previously verified owned IDs; never execute here."""
    ids = (runner_id,qdrant_id,network_id)
    if (not re.fullmatch('f3-[a-f0-9]{32}',plan['project']) or len(set(ids))!=3
            or any(not isinstance(i,str) or not re.fullmatch('[a-f0-9]{64}',i) for i in ids)):
        raise AnswerError('session_unavailable')
    return [['docker','container','rm','--force',runner_id,qdrant_id],
            ['docker','network','rm',network_id],
            ['docker','container','inspect',runner_id,qdrant_id],
            ['docker','network','inspect',network_id]]

def main():
    try:
        plan=prepare(sys.argv[1:])
        raise SystemExit(execute_stack(plan,0,1,2))
    except (AnswerError,OSError,ValueError):raise SystemExit('session_unavailable') from None

if __name__=='__main__':
    main()
