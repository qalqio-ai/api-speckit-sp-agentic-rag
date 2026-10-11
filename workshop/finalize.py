"""Run only the named, authorized local workshop finalization steps."""
import argparse
import json
from pathlib import Path

from workshop.seda import BUNDLE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', required=True, choices=('fresh-v2', 'rehearse-v2', 'environment'))
    args = parser.parse_args()
    if args.step in ('fresh-v2', 'rehearse-v2'):
        from workshop.seda_v2 import BUNDLE as bundle
        from workshop.seda_v2 import run
        image = json.loads((BUNDLE/'evidence/build.json').read_text())['image_id']
        mode = 'fresh' if args.step == 'fresh-v2' else 'rehearsal'
        destination = bundle/'evidence'/('fresh-v2-live.json' if mode == 'fresh' else 'rehearsal.json')
        raise SystemExit(run(mode, image, destination))
    if args.step == 'environment':
        import subprocess
        data = {}
        commands = {
            'docker_version': ['docker','version','--format','{{.Client.Version}} {{.Server.Version}} {{.Server.Os}} {{.Server.Arch}}'],
            'compose_version': ['docker','compose','version'],
            'docker_resources': ['docker','info','--format','{{.MemTotal}} {{.NCPU}} {{.OperatingSystem}} {{.KernelVersion}}'],
            'host_os': ['sw_vers'],
            'host_arch': ['uname','-m'],
            'host_memory': ['sysctl','-n','hw.memsize'],
            'host_cpu': ['sysctl','-n','machdep.cpu.brand_string'],
            'docker_desktop': ['defaults','read','/Applications/Docker.app/Contents/Info','CFBundleShortVersionString'],
        }
        for name, command in commands.items():
            result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
            data[name] = {'exit_code':result.returncode,'value':result.stdout.strip(),'error':result.stderr[:256]}
        target = Path('workshop/seda-20261008/evidence/environment.json')
        with target.open('x') as output:
            json.dump(data,output,indent=2)
        print(json.dumps(data),flush=True)


if __name__ == '__main__':
    main()
