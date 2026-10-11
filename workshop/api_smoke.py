"""Stage 1 smoke on the freshly rebuilt candidate, with owned cleanup."""
import json
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener
from uuid import uuid4

from workshop.seda import BUNDLE


def main():
    record = BUNDLE/'evidence/api-smoke.json'
    if record.exists():
        raise SystemExit('Existing smoke record preserved')
    image = json.loads((BUNDLE/'evidence/build.json').read_text())['image_id']
    name = 'seda-api-'+uuid4().hex
    report = {'image_id': image, 'name': name, 'checks': []}
    started = time.monotonic()
    identity = None
    code = 1
    try:
        identity = subprocess.check_output(['docker', 'run', '--pull=never', '--detach', '--init',
                                           '--name', name, '--label', 'local.seda.smoke='+name,
                                           '--read-only', '--memory', '536870912', '--memory-swap', '536870912',
                                           '--publish', '127.0.0.1::8000', image, 'python', '-m', 'uvicorn',
                                           'app.main:app', '--host', '0.0.0.0', '--port', '8000'],
                                          text=True, timeout=30).strip()
        address = subprocess.check_output(['docker', 'port', identity, '8000'], text=True, timeout=10).strip()
        opener = build_opener(ProxyHandler({}))
        def request(path):
            try:
                response = opener.open('http://'+address+path, timeout=3)
            except HTTPError as error:
                response = error
            with response:
                return response.status, response.headers.get_content_type(), json.load(response)
        end = time.monotonic()+60
        while True:
            try:
                if request('/health') == (200, 'application/json', {'status': 'ok'}):
                    break
            except (URLError, OSError, ValueError):
                pass
            if time.monotonic() >= end:
                raise RuntimeError('readiness_failed')
            time.sleep(.2)
        report['readiness_ms'] = (time.monotonic()-started)*1000
        for path, expected_status, expected in [
            ('/health', 200, {'status': 'ok'}),
            ('/v1/use-cases/sample-use-case/sources', 200, {'use_case_id': 'sample-use-case', 'sources': [{'source_id': 'sample-source-1', 'title': 'Sample source'}]}),
            ('/v1/use-cases/empty-use-case/sources', 200, {'use_case_id': 'empty-use-case', 'sources': []}),
            ('/v1/use-cases/missing-use-case/sources', 404, {'detail': {'code': 'unknown_use_case'}}),
        ]:
            actual = request(path)
            passed = actual == (expected_status, 'application/json', expected)
            report['checks'].append({'path': path, 'passed': passed, 'status': actual[0], 'body': actual[2]})
            if not passed:
                raise RuntimeError('contract_failed')
        code = 0
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        report['error'] = str(error)[:512]
    finally:
        if identity:
            removed = subprocess.run(['docker', 'container', 'rm', '--force', identity], capture_output=True, timeout=15, check=False)
            absent = subprocess.run(['docker', 'container', 'ls', '--all', '--filter', 'label=local.seda.smoke='+name, '--format', '{{.ID}}'], capture_output=True, timeout=10, check=False)
            report['container_absent'] = removed.returncode == 0 and absent.returncode == 0 and not absent.stdout.strip()
        else:
            report['container_absent'] = False
        report['exit_code'] = code if report['container_absent'] else 1
        record.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report), flush=True)
    raise SystemExit(report['exit_code'])


if __name__ == '__main__':
    main()
