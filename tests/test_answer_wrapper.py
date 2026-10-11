"""No Docker daemon, assets or source processing: inspect fixture checks only."""
import copy
from pathlib import Path

import pytest

from app.answer.demo import MOUNTS, cleanup_commands, prepare, verify_runtime


def wrapper_plan(tmp_path, **overrides):
    args = []
    for name in MOUNTS:
        if name == 'evaluation_cases':
            continue
        path = tmp_path/name
        if name.endswith('_dir'):
            path.mkdir()
        else:
            path.write_text('{}')
        args += ['--'+name.replace('_','-'),str(path)]
    args += ['--min-score',str(overrides.get('score',.5)),'--calibration-id','reviewed-calibration']
    return prepare(args)


def inspected(plan):
    def container(name,memory,tmpfs):
        return {'Id': ('a' if name=='runner' else 'b')*64,
                'Config':{'Labels':{'com.docker.compose.project':plan['project'],
                                  'com.docker.compose.service':name}},
                'State':{'Running':True,'OOMKilled':False,'Pid':100 if name=='runner' else 101},
                'HostConfig':{'Memory':memory,'MemorySwap':memory,'ReadonlyRootfs':name=='runner',
                              'NanoCpus':4000000000 if name=='runner' else 0,
                              'Tmpfs':tmpfs,'Privileged':False,'PidMode':'','NetworkMode':plan['project']+'_f3'},
                'Mounts':([{'Type':'bind','Source':host,'Destination':target,'RW':False}
                           for target,host in plan['mounts'].items()] if name=='runner' else []),
                'NetworkSettings':{'Networks':{plan['project']+'_f3':{'NetworkID':'c'*64}}}}
    runner=container('runner',8589934592,{'/tmp':'size=67108864'})
    qdrant=container('qdrant',1073741824,{'/qdrant/storage':'size=268435456'})
    network={'Id':'c'*64,'Internal':True,'Labels':{'com.docker.compose.project':plan['project']},
             'Containers':{runner['Id']:{},qdrant['Id']:{}}}
    return runner,qdrant,network


def test_prepare_freezes_explicit_readonly_paths_and_normal_cli(tmp_path):
    plan=wrapper_plan(tmp_path)
    assert set(plan['mounts'])==set(MOUNTS.values())-{'/input/cases.json'}
    assert all(Path(p).is_absolute() for p in plan['mounts'].values())
    assert plan['command'][:5]==['python','-B','-m','app.answer','session']
    assert '--min-score' in plan['command'] and '0.5' in plan['command']
    assert plan['project'].startswith('f3-')


@pytest.mark.parametrize('score',[float('nan'),float('inf'),2,-2])
def test_prepare_rejects_invalid_threshold(tmp_path,score):
    with pytest.raises(ValueError):
        wrapper_plan(tmp_path,score=score)


def test_prepare_rejects_symlink_before_reading_content(tmp_path):
    plan=wrapper_plan(tmp_path)
    path=Path(plan['mounts']['/input/catalog.json'])
    path.unlink()
    path.symlink_to(tmp_path/'answer_approval')
    argv=[]
    for name,target in MOUNTS.items():
        if target in plan['mounts']:
            argv+=['--'+name.replace('_','-'),plan['mounts'][target]]
    with pytest.raises(ValueError):
        prepare(argv+['--min-score','.5','--calibration-id','reviewed'])


def test_inspect_verifies_owned_limits_mounts_and_internal_network(tmp_path):
    plan=wrapper_plan(tmp_path)
    runner,qdrant,network=inspected(plan)
    assert verify_runtime(plan,runner,qdrant,network)==(runner['Id'],qdrant['Id'],network['Id'])


def test_inspect_accepts_normal_network_details_without_extra_networks(tmp_path):
    plan=wrapper_plan(tmp_path)
    runner,qdrant,network=inspected(plan)
    for item in (runner,qdrant):
        next(iter(item['NetworkSettings']['Networks'].values())).update(IPAddress='172.20.0.2',Aliases=['runner'])
    assert verify_runtime(plan,runner,qdrant,network)==(runner['Id'],qdrant['Id'],network['Id'])


@pytest.mark.parametrize('mutation',[
    lambda r,q,n:r['HostConfig'].update(Memory=0),
    lambda r,q,n:r['HostConfig'].update(MemorySwap=-1),
    lambda r,q,n:r['HostConfig'].update(NanoCpus=0),
    lambda r,q,n:r['HostConfig'].update(ReadonlyRootfs=False),
    lambda r,q,n:r['HostConfig'].update(Privileged=True),
    lambda r,q,n:r['State'].update(OOMKilled=True),
    lambda r,q,n:r['Mounts'][0].update(RW=True),
    lambda r,q,n:r['Mounts'][0].update(Source='/other/model'),
    lambda r,q,n:r['Mounts'].append({'Type':'bind','Source':'/host','Destination':'/host','RW':True}),
    lambda r,q,n:q['HostConfig'].update(Tmpfs={'/qdrant/storage':'size=999999999'}),
    lambda r,q,n:n.update(Internal=False),
    lambda r,q,n:n['Containers'].update({'foreign':{}}),
    lambda r,q,n:r['Config']['Labels'].update({'com.docker.compose.project':'other'}),
    lambda r,q,n:r['NetworkSettings']['Networks'].update({'external':{'NetworkID':'external'}}),
])
def test_inspect_fails_closed_on_runtime_mutation(tmp_path,mutation):
    plan=wrapper_plan(tmp_path)
    runner,qdrant,network=copy.deepcopy(inspected(plan))
    mutation(runner,qdrant,network)
    with pytest.raises(ValueError):
        verify_runtime(plan,runner,qdrant,network)


def test_cleanup_plan_targets_exact_ids_with_no_global_prune(tmp_path):
    plan=wrapper_plan(tmp_path)
    runner,qdrant,network=inspected(plan)
    ids=verify_runtime(plan,runner,qdrant,network)
    commands=cleanup_commands(plan,*ids)
    assert commands==[['docker','container','rm','--force',ids[0],ids[1]],
                      ['docker','network','rm',ids[2]],
                      ['docker','container','inspect',ids[0],ids[1]],
                      ['docker','network','inspect',ids[2]]]
    with pytest.raises(ValueError):
        cleanup_commands(plan,'--all',ids[1],ids[2])
