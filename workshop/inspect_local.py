"""Bounded metadata and independent absence checks for recorded owned runs."""
import json
import subprocess

from workshop.seda import ROOT


def main():
    data={'commands':{},'owned_projects':{}}
    commands={
        'docker_version':['docker','version','--format','{{.Client.Version}} {{.Server.Version}} {{.Server.Os}} {{.Server.Arch}}'],
        'compose_version':['docker','compose','version'],
        'docker_resources':['docker','info','--format','{{.MemTotal}} {{.NCPU}} {{.OperatingSystem}} {{.KernelVersion}}'],
        'host_os':['sw_vers'],'host_arch':['uname','-m'],
        'host_memory':['sysctl','-n','hw.memsize'],
        'host_cpu':['sysctl','-n','machdep.cpu.brand_string'],
        'docker_desktop':['defaults','read','/Applications/Docker.app/Contents/Info','CFBundleShortVersionString'],
    }
    def execute(command):
        result=subprocess.run(command,capture_output=True,text=True,timeout=30,check=False)
        return {'command':command,'exit_code':result.returncode,'stdout':result.stdout[:2048].strip(),'stderr':result.stderr[:512]}
    for name,command in commands.items():data['commands'][name]=execute(command)
    projects=set()
    for directory in ('seda-20261008','seda-20261008-v2'):
        for path in (ROOT/'workshop'/directory/'evidence').glob('*.json'):
            value=json.loads(path.read_text())
            if isinstance(value,dict) and isinstance(value.get('project'),str):projects.add(value['project'])
    for project in sorted(projects):
        data['owned_projects'][project]={kind:execute(['docker',kind,'ls',*(['--all'] if kind=='container' else []),
            '--filter','label=com.docker.compose.project='+project,'--format','{{.ID}}']) for kind in ('container','network')}
    smoke=json.loads((ROOT/'workshop/seda-20261008/evidence/api-smoke.json').read_text())
    data['api_smoke_absence']=execute(['docker','container','ls','--all','--filter','label=local.seda.smoke='+smoke['name'],'--format','{{.ID}}'])
    checks=[v for resources in data['owned_projects'].values() for v in resources.values()]+[data['api_smoke_absence']]
    data['independent_absence_pass']=all(v['exit_code']==0 and not v['stdout'] for v in checks)
    path=ROOT/'workshop/seda-20261008-v2/evidence/independent-inspection.json'
    with path.open('x') as stream:json.dump(data,stream,indent=2)
    print(json.dumps({'report':str(path),'owned_projects':len(projects),'independent_absence_pass':data['independent_absence_pass']}))
    raise SystemExit(0 if data['independent_absence_pass'] else 1)


if __name__=='__main__':main()
