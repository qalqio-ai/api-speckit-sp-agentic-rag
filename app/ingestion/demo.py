"""Local Docker supervision. All destructive steps verify the unique owned project."""
import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from uuid import uuid4

from .index import verify_tmpfs
from .lifecycle import Teardown, guarded_command
from .types import IngestionError


def present(kind, identity, deadline, command=guarded_command):
    argv = ['docker', 'ps', '-a', '--no-trunc'] if kind == 'container' else ['docker', 'network', 'ls', '--no-trunc']
    found = command(argv + ['--filter', 'id=' + identity, '--format', '{{.ID}}'], deadline)
    return bool(found.strip())


def verify_owned(kind, identity, project, deadline, command=guarded_command):
    if not present(kind, identity, deadline, command):
        return False
    label = command(['docker', kind, 'inspect', '--format',
                     '{{index .Config.Labels "com.docker.compose.project"}}' if kind == 'container'
                     else '{{index .Labels "com.docker.compose.project"}}', identity], deadline).strip()
    if label != project:
        raise IngestionError('cleanup_failed')
    return True


def remove_owned(containers, networks, project, clock, deadline, command=guarded_command):
    # Exact recorded IDs only. Ownership is rechecked before both kill and removal.
    kill_end = min(deadline, clock() + 5)
    for identity in containers:
        if verify_owned('container', identity, project, kill_end, command):
            command(['docker', 'kill', identity], kill_end)
    remove_end = min(deadline, clock() + 5)
    for identity in containers:
        if verify_owned('container', identity, project, remove_end, command):
            command(['docker', 'rm', '--force', identity], remove_end)
    for identity in networks:
        if verify_owned('network', identity, project, remove_end, command):
            command(['docker', 'network', 'rm', identity], remove_end)
    verify_end = min(deadline, clock() + 5)
    return not any(present('container', identity, verify_end, command) for identity in containers) and not any(
        present('network', identity, verify_end, command) for identity in networks)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--approval-manifest', required=True)
    parser.add_argument('--model-dir', required=True)
    args = parser.parse_args(argv)
    approved, model = Path(args.approval_manifest).resolve(), Path(args.model_dir).resolve()
    if not approved.is_file() or not model.is_dir():
        print('invalid_input', file=sys.stderr)
        return 1
    repo = Path(__file__).resolve().parents[2]
    project = 'f1-' + uuid4().hex[:12]
    runner_name = project + '-runner'
    containers, networks = [], []
    teardown = Teardown()
    ready, triggered = threading.Event(), threading.Event()
    process = None
    status, cleanup_ok = 0, False
    interrupted = False
    temp = tempfile.TemporaryDirectory(prefix='f1-mount-proof-')
    proof_file = Path(temp.name) / 'tmpfs-proof.json'
    env = os.environ.copy()
    env.update(F1_MODEL_DIR=str(model), F1_MANIFEST=str(approved), F1_TMPFS_PROOF=str(proof_file))
    compose = ['docker', 'compose', '--env-file', '/dev/null', '--project-name', project,
               '-f', str(repo / 'compose.f1.yaml')]
    def command(argv, deadline):
        return guarded_command(argv, deadline, factory=lambda *a, **k: subprocess.Popen(*a, **k, env=env))
    def trigger(signum=None, frame=None):
        nonlocal interrupted
        interrupted = signum is not None or interrupted
        teardown.begin()
        triggered.set()
        if signum is not None and process is not None and process.poll() is None:
            process.send_signal(signal.SIGTERM)
    old = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
    for s in old:
        signal.signal(s, trigger)
    print(json.dumps({'project': project, 'runner_name': runner_name, 'mode': 'local_live'}), file=sys.stderr, flush=True)
    try:
        # No build/pull/runtime acquisition. T033 must have supplied both images.
        command(['docker', 'image', 'inspect', '--format', '{{.Id}}', 'f1-ingestion:local'], time.monotonic() + 5)
        command(compose + ['up', '-d', '--no-build', '--pull', 'never', 'qdrant'], time.monotonic() + 45)
        container = command(compose + ['ps', '-q', 'qdrant'], time.monotonic() + 5).strip()
        if not container:
            raise IngestionError('index_failed')
        containers.append(container)
        network = command(['docker', 'network', 'ls', '--filter', 'label=com.docker.compose.project=' + project,
                           '--format', '{{.ID}}', '--no-trunc'], time.monotonic() + 5).strip()
        if not network or '\n' in network:
            raise IngestionError('index_failed')
        networks.append(network)
        if not verify_owned('container', container, project, time.monotonic() + 5, command):
            raise IngestionError('index_failed')
        internal = command(['docker', 'network', 'inspect', '--format', '{{.Internal}}', network], time.monotonic() + 5).strip()
        if internal != 'true':
            raise IngestionError('index_failed')
        mount = command(['docker', 'exec', container, 'stat', '-f', '-c', '%T %S %b', '/qdrant/storage'], time.monotonic() + 10).split()
        probe = {'type': mount[0], 'size': int(mount[1]) * int(mount[2])}
        verify_tmpfs(probe)
        proof = {**probe, 'project': project, 'container': container, 'network': network}
        proof_file.write_text(json.dumps(proof))
        print(json.dumps({'verified_mount': proof}), file=sys.stderr, flush=True)
        process = subprocess.Popen(compose + ['run', '--name', runner_name, '--no-deps', '--pull', 'never', '-T', 'runner',
                     'python', '-m', 'app.ingestion', 'session', '--approval-manifest', '/input/approval.json',
                     '--model-dir', '/models', '--tmpfs-proof', '/input/tmpfs-proof.json'],
                     env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def output(stream, target, controls=False):
            for line in iter(stream.readline, b''):
                if controls and line.strip() == b'F1_READY':
                    ready.set()
                if controls and line.strip() == b'F1_TEARDOWN':
                    trigger()
                target.buffer.write(line)
                target.buffer.flush()
        for stream, target, controls in ((process.stdout, sys.stdout, False), (process.stderr, sys.stderr, True)):
            threading.Thread(target=output, args=(stream, target, controls), daemon=True).start()
        preflight_end = time.monotonic() + 120
        while not ready.wait(.05):
            if process.poll() is not None or time.monotonic() >= preflight_end or triggered.is_set():
                raise IngestionError('model_unavailable')
        runner_id = command(['docker', 'inspect', '--format', '{{.Id}}', runner_name], time.monotonic() + 5).strip()
        containers.append(runner_id)
        for identity in containers:
            if not verify_owned('container', identity, project, time.monotonic() + 5, command):
                raise IngestionError('index_failed')
            attached = command(['docker', 'inspect', '--format',
                                 '{{range $name, $value := .NetworkSettings.Networks}}{{$name}}{{"\\n"}}{{end}}', identity], time.monotonic() + 5).split()
            if attached != [project + '_f1']:
                raise IngestionError('index_failed')
        def feed():
            try:
                for line in sys.stdin.buffer:
                    process.stdin.write(line)
                    process.stdin.flush()
            except (OSError, ValueError):
                pass
            finally:
                try:
                    process.stdin.close()
                except OSError:
                    pass
        threading.Thread(target=feed, daemon=True).start()
        while process.poll() is None:
            if triggered.is_set() and time.monotonic() >= min(teardown.deadline, teardown.deadline - 30):
                process.terminate()
                status = 1
                break
            time.sleep(.05)
        status = status or process.poll() or 0
        if interrupted:
            status = 130
    except (IngestionError, OSError, ValueError, IndexError) as error:
        print(error.code if isinstance(error, IngestionError) else 'index_failed', file=sys.stderr, flush=True)
        status = status or 1
    finally:
        trigger()
        # Collection/worker cleanup already shares the first 15 seconds of this deadline.
        docker_end = min(teardown.deadline, time.monotonic() + 30)
        try:
            # Startup may have failed before IDs were collected; discover only this unique project.
            if not containers:
                rows = command(['docker', 'ps', '-a', '--no-trunc', '--filter',
                                'label=com.docker.compose.project=' + project, '--format', '{{.ID}}'], docker_end)
                containers.extend(rows.split())
            if not networks:
                rows = command(['docker', 'network', 'ls', '--no-trunc', '--filter',
                                'label=com.docker.compose.project=' + project, '--format', '{{.ID}}'], docker_end)
                networks.extend(rows.split())
            down_end = min(docker_end, time.monotonic() + 15)
            for identity in containers:
                verify_owned('container', identity, project, down_end, command)
            for identity in networks:
                verify_owned('network', identity, project, down_end, command)
            try:
                command(compose + ['down', '--timeout', '10', '--remove-orphans'], down_end)
            except IngestionError:
                status = status or 1
            cleanup_ok = remove_owned(containers, networks, project, time.monotonic, docker_end, command)
        except (IngestionError, OSError):
            status = status or 1
        if not cleanup_ok:
            status = status or 1
        for s, handler in old.items():
            signal.signal(s, handler)
        # No unbounded subprocess/thread join, even if Docker is unresponsive.
        if process is not None and process.poll() is None:
            process.kill()
        print(json.dumps({'project': project, 'containers': containers, 'networks': networks,
                          'owned_resources_absent': cleanup_ok, 'residue_unknown': not cleanup_ok,
                          'teardown_seconds': round(45 - teardown.remaining(), 3), 'exit_status': status}),
              file=sys.stderr, flush=True)
        temp.cleanup()
    return status


if __name__ == '__main__':
    raise SystemExit(main())
