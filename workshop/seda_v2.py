"""Isolated SEDA wrapper. No image publication, downloads or production changes."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from uuid import uuid4

from app.answer.demo import (
    QDRANT_IMAGE,
    recover_owned_stack,
    remove_owned_stack,
    run_command,
    verify_runtime,
)

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT/'workshop/seda-20261008-v2'
BASE_IMAGE = 'sha256:139a1f015734889f0bef40f66a4db65a1addc1a3dc5dc41f6bc82fe9d936757f'


def verify_bundle(directory):
    directory = Path(directory).resolve()
    files = json.loads((directory/'frozen.json').read_text())['files']
    for name, expected in files.items():
        path = (directory/name).resolve()
        if directory not in path.parents or not path.is_file():
            raise ValueError('bundle_mismatch')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('bundle_mismatch')
    return True


def result_passes(report):
    return (bool(report.get('cases')) and all(c.get('passed') is True for c in report['cases'])
            and report.get('collection_absent') is True and report.get('stack_absent') is True
            and report.get('lifecycle_pass', True) is True
            and report.get('ownership_consistent', True) is True)


def run(mode, image, destination):
    verify_bundle(BUNDLE)
    destination = Path(destination).resolve()
    if destination.exists() or BUNDLE/'evidence' not in destination.parents:
        raise ValueError('new_local_evidence_destination_required')
    destination.parent.mkdir(parents=True, exist_ok=True)
    project = 'f3-'+uuid4().hex
    netname = project+'_f3'
    containers, network = [], None
    deadline = time.monotonic()+1500
    report = {'project': project, 'command_mode': mode, 'acceptance_claimed': False,
              'bundle_sha256': hashlib.sha256((BUNDLE/'frozen.json').read_bytes()).hexdigest()}
    labels = ['--label', 'com.docker.compose.project='+project]
    def checked(argv, end=deadline):
        value = run_command(argv, end)
        if value['returncode'] != 0:
            report['failed_operation'] = argv[:3]
            report['diagnostic'] = value['stderr'][:1024].decode('utf-8', 'replace')
            raise RuntimeError('docker_command_failed')
        return value['stdout']
    def inspect(kind, identity):
        return json.loads(checked(['docker', kind, 'inspect', identity]))[0]
    try:
        start = time.monotonic()
        runnerimage = inspect('image', image)['Id']
        qimage = inspect('image', QDRANT_IMAGE)['Id']
        report.update(runtime_image_id=runnerimage, qdrant_image_id=qimage)
        network = checked(['docker', 'network', 'create', '--internal', *labels, netname]).decode().strip()
        q = checked(['docker', 'create', '--pull=never', '--name', project+'-qdrant',
                     *labels, '--label', 'com.docker.compose.service=qdrant', '--network', netname,
                     '--network-alias', 'qdrant', '--memory', '1073741824', '--memory-swap',
                     '1073741824', '--tmpfs', '/qdrant/storage:size=268435456', qimage]).decode().strip()
        containers.append(q)
        checked(['docker', 'start', q])
        mounts = {'/fixtures': str(BUNDLE/'fixtures'), '/input': str(BUNDLE/'inputs'),
                  '/embedding': str(ROOT/'local-data/f1-models/1110a243fdf4706b3f48f1d95db1a4f5529b4d41'),
                  '/generation': str(ROOT/'local-data/f3-models/a10cc1512eabd3dde888204e902eca88bddb4951')}
        arguments = []
        for target, host in mounts.items():
            arguments += ['--mount', f'type=bind,src={host},dst={target},readonly']
        script = 'calibration.py' if mode == 'calibration' else 'session.py'
        code = f'import runpy,sys;sys.argv=["{script}","{mode}"];runpy.run_path("/input/{script}",run_name="__main__")'
        runner = checked(['docker', 'create', '--pull=never', '--init', '--read-only',
                          '--name', project+'-runner', *labels, '--label', 'com.docker.compose.service=runner',
                          '--network', netname, '--memory', '8589934592', '--memory-swap', '8589934592',
                          '--cpus', '4', '--tmpfs', '/tmp:size=67108864', *arguments, runnerimage,
                          'python', '-B', '-c', code]).decode().strip()
        containers.append(runner)
        checked(['docker', 'start', runner])
        r, qr, nr = inspect('container', runner), inspect('container', q), inspect('network', network)
        verify_runtime({'project': project, 'mounts': mounts}, r, qr, nr)
        proof = checked(['docker', 'exec', q, 'stat', '-f', '-c', '%T %S %b', '/qdrant/storage']).decode().split()
        if proof[0] != 'tmpfs' or int(proof[1])*int(proof[2]) != 268435456:
            raise ValueError('tmpfs_mismatch')
        report['host_startup_to_verified_stack_ms'] = (time.monotonic()-start)*1000
        exit_code = checked(['docker', 'wait', runner]).strip()
        logs = run_command(['docker', 'logs', runner], deadline)
        lines = logs['stdout'].splitlines()
        if len(lines) == 1:
            report.update(json.loads(lines[0]))
        else:
            report['bounded_stderr_tail'] = logs['stderr'][-2048:].decode('utf-8', 'replace')
        report['runner_exit_code'] = int(exit_code)
        report['qdrant_peak_bytes'] = int(checked(['docker', 'exec', q, 'cat', '/sys/fs/cgroup/memory.peak']))
        report['elapsed_host_ms'] = (time.monotonic()-start)*1000
    except (RuntimeError, ValueError, OSError, KeyError) as error:
        report['wrapper_error'] = str(error)[:512]
    finally:
        cleanup_start = time.monotonic()
        containers, network, recovered = recover_owned_stack(project, containers, network, cleanup_start+10, run_command)
        report['ownership_consistent'] = recovered
        report['stack_absent'] = recovered and remove_owned_stack(containers, network, cleanup_start+30, run_command)
        report['cleanup_ms'] = (time.monotonic()-cleanup_start)*1000
        if mode == 'calibration':
            passed = report.get('collection_absent') is True and report['stack_absent'] and 'calibration_cases' in report
        else:
            passed = result_passes(report) and report.get('runner_exit_code') == 0
        report['exit_code'] = 0 if passed else 1
        with destination.open('x') as output:
            json.dump(report, output, indent=2)
            output.write('\n')
    print(json.dumps({'report': str(destination), 'exit_code': report['exit_code'],
                      'stack_absent': report['stack_absent']}), flush=True)
    return report['exit_code']


def main():
    parser = argparse.ArgumentParser(description='Local SEDA constrained-selection workshop wrapper')
    parser.add_argument('--mode', required=True, choices=('fresh', 'rehearsal', 'regression', 'calibration'))
    parser.add_argument('--image', default=BASE_IMAGE)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.mode, args.image, args.output))


if __name__ == '__main__':
    main()
