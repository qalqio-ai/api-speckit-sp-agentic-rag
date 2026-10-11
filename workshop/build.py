"""Fresh local application rebuild over the retained pinned dependency image."""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from workshop.seda import BASE_IMAGE, BUNDLE, ROOT

TAG = 'seda-workshop:20261008-rc1'


def main():
    evidence = BUNDLE/'evidence/build.json'
    if evidence.exists():
        raise SystemExit('Build evidence exists; use a separately versioned build script/tag')
    base = subprocess.check_output(['docker', 'image', 'inspect', BASE_IMAGE, '--format', '{{.Id}}'], text=True).strip()
    subprocess.run(['docker', 'image', 'tag', base, 'seda-f3-dependencies:20261007'], check=True)
    with tempfile.TemporaryDirectory(prefix='seda-build-') as folder:
        context = Path(folder)
        shutil.copytree(ROOT/'app', context/'app', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for relative in ('specs/agentic-rag/f1-ingestion/contracts/serialization.schema.json',
                         'specs/002-f2-retrieval/contracts/serialization.schema.json',
                         'specs/003-f3-grounded-rag/contracts/serialization.schema.json'):
            target = context/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/relative, target)
        code = context/'workshop'
        code.mkdir()
        for name in ('constraint-v1-trie.py', 'constraint-v1-worker.py', 'session.py', 'calibration.py'):
            shutil.copy2(BUNDLE/'inputs'/name, code/name)
        dockerfile = ('FROM seda-f3-dependencies:20261007\nWORKDIR /app\n'
                      'COPY app ./app\nCOPY specs ./specs\nCOPY workshop /workshop\n'
                      'LABEL local.seda.candidate="20261008-rc1"\n')
        (context/'Dockerfile').write_text(dockerfile)
        manifest = {str(p.relative_to(context)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in context.rglob('*') if p.is_file()}
        argv = ['docker', 'build', '--pull=false', '--network=none', '--platform', 'linux/amd64',
                '--no-cache', '--progress=plain', '-t', TAG, str(context)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=600, check=False)
        (BUNDLE/'evidence/build.log').write_text(result.stdout+result.stderr)
        image = subprocess.check_output(['docker', 'image', 'inspect', TAG, '--format', '{{.Id}}'], text=True).strip() if result.returncode == 0 else None
        record = {'tag': TAG, 'base_image_id': base, 'image_id': image, 'exit_code': result.returncode,
                  'command': argv[:-1]+['<isolated temporary context>'], 'dockerfile': dockerfile,
                  'context_files': manifest, 'network': 'none', 'dependencies_reused_by_digest': True,
                  'clean_dependency_reinstallation_claimed': False, 'published': False}
        evidence.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record), flush=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
