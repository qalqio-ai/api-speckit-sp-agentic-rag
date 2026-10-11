"""Deterministic JSONL/endpoint checks; these never load a live model."""
import io
import json

import pytest

from app.ingestion.__main__ import session
from app.ingestion.types import IngestionError
from app.ingestion.validation import validate_endpoint, validate_shape


def test_inspection_jsonl_envelope_and_safe_malformed_lines():
    from test_ingestion import service
    svc, _ = service()
    output, errors = io.StringIO(), io.StringIO()
    code = session(['session', '--approval-manifest', 'explicit', '--model-dir', 'explicit'],
                   factory=lambda *_: svc,
                   stdin=io.StringIO('{bad\n{"op":"unknown"}\n{"op":"inspect","use_case_id":"learning-a"}\n'),
                   stdout=output, stderr=errors)
    rows = [json.loads(line) for line in output.getvalue().splitlines()]
    assert len(rows) == 3
    assert rows[0]['op'] is None and rows[0]['status'] == 'rejected'
    assert rows[1]['op'] is None and rows[1]['status'] == 'rejected'
    assert rows[2]['op'] == 'inspect' and rows[2]['data']['current_count'] == 0
    assert len({r['request_id'] for r in rows}) == 3
    assert len({r['run_id'] for r in rows}) == 1
    for row in rows:
        validate_shape(row, 'OperationResult')
    assert code == 0
    assert '{bad' not in errors.getvalue()


@pytest.mark.parametrize('url', ['http://localhost:6333', 'http://127.0.0.1:6333',
                                'https://qdrant:6333', 'http://qdrant:6334',
                                'http://user:pass@qdrant:6333', 'http://qdrant:6333/',
                                'http://qdrant:6333?x=1', 'http://qdrant:6333#frag',
                                'http://remote.example:6333'])
def test_endpoint_rejected_before_factory_or_text_reads(url):
    class ForbiddenInput:
        def __iter__(self):
            raise AssertionError('input must not be read')
    def forbidden_factory(*args):
        raise AssertionError('client/model must not be constructed')
    errors = io.StringIO()
    assert session(['session', '--approval-manifest', 'absent', '--model-dir', 'absent',
                    '--qdrant-url', url], factory=forbidden_factory,
                   stdin=ForbiddenInput(), stdout=io.StringIO(), stderr=errors) != 0
    assert errors.getvalue().strip() == 'endpoint_not_allowed'


def test_literal_endpoint_only():
    assert validate_endpoint('http://qdrant:6333') == 'http://qdrant:6333'
    with pytest.raises(IngestionError):
        validate_endpoint(' http://qdrant:6333')


def test_eof_cleanup_has_no_fabricated_stdout_line_and_failure_is_nonzero():
    from test_ingestion import service
    svc, client = service()
    client.fail = OSError('cannot clear')
    out, err = io.StringIO(), io.StringIO()
    code = session(['session', '--approval-manifest', 'explicit', '--model-dir', 'explicit'],
                   factory=lambda *_: svc, stdin=io.StringIO(''), stdout=out, stderr=err)
    assert code != 0
    assert out.getvalue() == ''
    assert 'cleanup_failed' in err.getvalue()


def test_explicit_close_has_one_result_and_stops_later_input():
    from test_ingestion import service
    svc, client = service()
    original = client.request
    def removed(method, path, body=None, timeout=None):
        if method == 'GET' and path == svc.index.path:
            return None
        return original(method, path, body, timeout)
    client.request = removed
    out = io.StringIO()
    code = session(['session', '--approval-manifest', 'explicit', '--model-dir', 'explicit'],
                   factory=lambda *_: svc,
                   stdin=io.StringIO('{"op":"close"}\n{"op":"inspect","use_case_id":"learning-a"}\n'),
                   stdout=out, stderr=io.StringIO())
    rows = [json.loads(x) for x in out.getvalue().splitlines()]
    assert code == 0
    assert len(rows) == 1 and rows[0]['op'] == 'close'
    assert rows[0]['status'] == 'complete'


def test_transport_does_not_follow_redirects_or_use_proxies(monkeypatch):
    import httpx

    from app.ingestion.index import LocalTransport
    seen = []
    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(307, headers={'location': 'https://forbidden.example/'})
    monkeypatch.setenv('HTTP_PROXY', 'http://forbidden.example:8080')
    client = LocalTransport('http://qdrant:6333', transport=httpx.MockTransport(handler))
    with pytest.raises(IngestionError):
        client.request('PUT', '/collections/owned/points', {'points': []}, timeout=3)
    assert seen == ['http://qdrant:6333/collections/owned/points']


def test_fatal_error_stops_following_operations_and_exits_nonzero():
    from test_ingestion import document, service
    svc, _client = service()
    svc.embedder.error = IngestionError('embedding_failed', fatal=True)
    out = io.StringIO()
    line = json.dumps({'op': 'ingest', **vars(document())})
    code = session(['session', '--approval-manifest', 'explicit', '--model-dir', 'explicit'],
                   factory=lambda *_: svc, stdin=io.StringIO(line+'\n'+line+'\n'),
                   stdout=out, stderr=io.StringIO())
    assert code != 0
    assert len(out.getvalue().splitlines()) == 1
    assert svc.closed is True


def test_wrapper_refuses_foreign_project_before_destructive_command():
    from test_ingestion import FakeClock

    from app.ingestion.demo import remove_owned
    clock = FakeClock()
    seen = []
    def command(argv, deadline, **kwargs):
        seen.append(argv)
        if 'ps' in argv:
            return 'owned-id\n'
        if 'inspect' in argv:
            return 'unrelated-project\n'
        raise AssertionError('must not destroy unrelated resource')
    with pytest.raises(IngestionError):
        remove_owned(['owned-id'], [], 'f1-owned', clock, 30, command)
    assert all('kill' not in c and 'rm' not in c for c in seen)


def test_wrapper_scopes_every_kill_remove_and_absence_check():
    from test_ingestion import FakeClock

    from app.ingestion.demo import remove_owned
    clock = FakeClock()
    present = {'owned-id'}
    seen = []
    def command(argv, deadline, **kwargs):
        seen.append(argv)
        assert deadline <= 30
        if 'ps' in argv:
            return 'owned-id\n' if present else ''
        if 'inspect' in argv:
            if argv[-1] not in present:
                raise IngestionError('cleanup_failed')
            return 'f1-owned\n'
        if 'rm' in argv:
            present.discard(argv[-1])
        return ''
    assert remove_owned(['owned-id'], [], 'f1-owned', clock, 30, command) is True
    assert present == set()
    assert all('prune' not in c and 'foreign' not in c for c in seen)
