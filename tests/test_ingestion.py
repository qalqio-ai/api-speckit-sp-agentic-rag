"""Deterministic F1 checks. Fakes never establish real embeddings or storage."""
import copy
import json
import re
from pathlib import Path

import pytest

from app.ingestion.types import IngestionError, SourceDocument
from app.ingestion.validation import (
    parse_request,
    strict_json,
    validate_document,
    validate_manifest,
)

FIXTURES = Path(__file__).parent / "fixtures/f1"


def manifest():
    return json.loads((FIXTURES / "approval.json").read_text())


def document(name="original.txt"):
    return SourceDocument(
        "learning-b" if name == "isolation.txt" else "learning-a",
        "shared-guide",
        "Fictional orchard guide" if name == "isolation.txt" else "Fictional café guide",
        "v2" if name == "shorter.txt" else "v1",
        (FIXTURES / name).read_text(),
    )


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class FakeTokenizer:
    """Word offsets plus special tokens; deterministic, not the model tokenizer."""
    def __call__(self, text, add_special_tokens=True, return_offsets_mapping=False,
                 truncation=False, **kwargs):
        assert truncation is False
        offsets = [m.span() for m in re.finditer(r"\S+", text)]
        result = {"input_ids": list(range(len(offsets) + (2 if add_special_tokens else 0)))}
        if return_offsets_mapping:
            result["offset_mapping"] = offsets
        return result


class FakeEmbedder:
    def __init__(self):
        self.error = None
        self.calls = 0

    def encode(self, chunks, deadline):
        self.calls += 1
        if self.error:
            raise self.error
        return [{**c, "vector": [1.0] + [0.0] * 383} for c in chunks]


class FakeClient:
    """Qdrant's external call boundary, with exhaustive two-record pages."""
    def __init__(self):
        self.records = {}
        self.calls = []
        self.fail = None
        self.clock = None
        self.present = True

    def request(self, method, path, body=None, timeout=None):
        self.calls.append((method, path, copy.deepcopy(body), timeout))
        if self.fail:
            raise self.fail
        if self.clock:
            self.clock.now += 1
        if path.endswith("/points/scroll"):
            wanted = body["filter"]["must"]
            def matches(p):
                return all(p[k["key"]] == k["match"]["value"] if "value" in k["match"]
                           else p[k["key"]] in k["match"]["any"] for k in wanted)
            rows = [r for r in self.records.values() if matches(r["payload"])]
            start = body.get("offset") or 0
            page = rows[start:start + 2]
            return {"points": copy.deepcopy(page),
                    "next_page_offset": start + 2 if start + 2 < len(rows) else None}
        if method == "PUT" and path.split("?")[0].endswith("/points"):
            for p in body["points"]:
                self.records[p["id"]] = copy.deepcopy(p)
            return {"status": "completed"}
        if path.split("?")[0].endswith("/points/delete"):
            for ident in body["points"]:
                self.records.pop(ident, None)
            return {"status": "completed"}
        if method == "DELETE":
            self.records.clear()
            self.present = False
            return True
        if method == "GET":
            return True if self.present else None
        return True


def test_approved_manifest_and_exact_source_are_accepted():
    approved = validate_manifest(manifest())
    assert validate_document(document(), approved) == document()


@pytest.mark.parametrize("field,value", [
    ("owner", " "), ("approved_at", "2026-02-30T00:00:00Z"),
    ("approved_at", "2026-10-02T00:00:00"), ("schema_version", True),
    ("retention", "forever"), ("access_scope", "everyone"),
    ("approved", True), ("allowed_sources", []),
])
def test_invalid_manifest_is_rejected(field, value):
    probe = manifest()
    probe[field] = value
    with pytest.raises(IngestionError):
        validate_manifest(probe)


def test_conflicting_approval_tuple_is_rejected():
    probe = manifest()
    probe["allowed_sources"].append({**probe["allowed_sources"][0], "content_sha256": "a" * 64})
    with pytest.raises(IngestionError):
        validate_manifest(probe)


@pytest.mark.parametrize("field,value", [
    ("use_case_id", "Learning-a"), ("use_case_id", " learning-a"),
    ("source_id", "shared-guide "), ("title", " "),
    ("revision", "missing"), ("text", ""), ("text", " \n"),
    ("text", "é" * 32769), ("text", "changed"), ("text", 123),
])
def test_invalid_or_unapproved_document_is_rejected(field, value):
    values = vars(document()).copy()
    values[field] = value
    with pytest.raises(IngestionError):
        validate_document(SourceDocument(**values), manifest())


@pytest.mark.parametrize("raw", ['{"op":"close","op":"inspect"}', '{"op":NaN}',
                                  '{"op":Infinity}', '{broken', '[]'])
def test_non_strict_json_is_rejected(raw):
    with pytest.raises(IngestionError):
        strict_json(raw)


@pytest.mark.parametrize("operation", [
    {"op": "inspect", "use_case_id": "learning-a", "source_id": None},
    {"op": "close", "collection": "foreign"}, {"op": "unknown"},
    {"op": "ingest", "use_case_id": "learning-a"},
])
def test_request_shape_rejects_unknown_missing_or_null_fields(operation):
    with pytest.raises(IngestionError):
        parse_request(operation)


def test_omitted_source_scope_and_close_are_valid_shapes():
    assert parse_request({"op": "inspect", "use_case_id": "learning-a"}) == {
        "op": "inspect", "use_case_id": "learning-a"}
    assert parse_request({"op": "close"}) == {"op": "close"}

# US1: removing approval-before-processing, offset preservation or read-back must fail these.
from app.ingestion.chunking import chunk_document
from app.ingestion.embedding import load_model, validate_vectors, verify_assets
from app.ingestion.index import Index
from app.ingestion.service import Service
from app.ingestion.validation import SCHEMA, validate_shape


def configuration():
    cfg = {k: v['const'] for k, v in SCHEMA['$defs']['RunConfiguration']['properties'].items() if 'const' in v}
    cfg.update(model_commit='1' * 40, model_file_sha256={'config.json': '2' * 64},
               tokenizer_fingerprint='3' * 64, configuration_fingerprint='4' * 64)
    return cfg  # explicit schema probe, not actual model identities


def service():
    clock = FakeClock()
    client = FakeClient()
    index = Index(client, clock, '00000000-0000-4000-8000-000000000001')
    return Service(manifest(), configuration(), FakeTokenizer(), FakeEmbedder(), index, clock), client


def test_chunk_offsets_windows_unicode_and_trailing_coverage():
    doc = document()
    chunks = chunk_document(doc, FakeTokenizer(), configuration())
    assert len(chunks) == 3
    assert chunks[0]['start'] == 0
    assert chunks[-1]['end'] == len(doc.text)
    assert all(c['text'] == doc.text[c['start']:c['end']] for c in chunks)
    covered = {i for c in chunks for i in range(c['start'], c['end'])}
    assert all(i in covered for i, char in enumerate(doc.text) if not char.isspace())
    assert all(len(FakeTokenizer()(c['text'])['input_ids']) <= 256 for c in chunks)
    assert chunks == chunk_document(doc, FakeTokenizer(), configuration())
    other = SourceDocument('learning-b', doc.source_id, doc.title, doc.revision, doc.text)
    assert not {c['chunk_id'] for c in chunks} & {c['chunk_id'] for c in chunk_document(other, FakeTokenizer(), configuration())}


@pytest.mark.parametrize('vector', [[], [0.0] * 384, [1.0] * 383, [float('nan')] * 384,
                                    [float('inf')] * 384, [True] * 384])
def test_invalid_vectors_are_rejected(vector):
    with pytest.raises(IngestionError):
        validate_vectors([vector])


def test_vector_validation_accepts_only_valid_dimension_and_norm():
    assert validate_vectors([[1.0] + [0.0] * 383]) == [[1.0] + [0.0] * 383]


def test_offline_loader_options_and_missing_assets(tmp_path):
    options = []
    def loader(path, **kwargs):
        options.append(kwargs)
        return 'local-model'
    assert load_model(tmp_path, loader) == 'local-model'
    assert options == [{'device': 'cpu', 'local_files_only': True, 'trust_remote_code': False}]
    with pytest.raises(IngestionError):
        load_model(tmp_path / 'absent', loader)


def test_model_hashes_and_paths_are_verified_before_loading(tmp_path):
    import hashlib
    (tmp_path / 'config.json').write_text('{}')
    hashes = {'config.json': hashlib.sha256(b'{}').hexdigest()}
    assert verify_assets(tmp_path, hashes) is None
    for probe in ({'../outside': '2' * 64}, {'/absolute': '2' * 64}, {'config.json': '2' * 64}):
        with pytest.raises(IngestionError):
            verify_assets(tmp_path, probe)


def test_ingest_inspect_round_trip_has_verified_provenance():
    svc, client = service()
    result = svc.ingest(document())
    assert result['status'] == 'complete'
    assert result['data']['ready'] is True
    assert result['data']['intended_count'] == result['data']['current_count'] == 3
    validate_shape(result, 'OperationResult')
    inventory = svc.inspect('learning-a', 'shared-guide')
    validate_shape(inventory, 'OperationResult')
    records = inventory['data']['sources'][0]['records']
    assert len(records) == 3
    assert records[-1]['text'].endswith('End of original guide.')
    for record in records:
        assert record['text'] == document().text[record['start']:record['end']]
        assert record['use_case_id'] == 'learning-a'
        assert record['source_id'] == 'shared-guide'
        assert len(record['vector']) == 384
    assert len([c for c in client.calls if c[1].endswith('/points/scroll')]) >= 4


def test_bad_document_never_calls_embedder_or_storage():
    svc, client = service()
    result = svc.ingest(SourceDocument('learning-a', 'shared-guide', 'title', 'v1', 'bad'))
    assert result['status'] == 'rejected'
    assert svc.embedder.calls == 0
    assert client.calls == []

from app.ingestion.embedding import ProcessEmbedder, stop_worker


class FakeProcess:
    def __init__(self, clock, gone_after_kill=True):
        self.clock, self.gone_after_kill = clock, gone_after_kill
        self.events = []
        self.alive = True
        self.exitcode = None

    def is_alive(self):
        return self.alive

    def terminate(self):
        self.events.append('TERM')

    def kill(self):
        self.events.append('KILL')
        self.alive = not self.gone_after_kill

    def join(self, timeout):
        self.events.append(timeout)
        self.clock.now += timeout


def test_worker_shutdown_escalates_within_one_reserved_budget():
    clock = FakeClock()
    process = FakeProcess(clock)
    assert stop_worker(process, clock, 5) is True
    assert process.events == ['TERM', 2, 'KILL', 3]
    assert clock.now == 5


def test_worker_shutdown_cannot_claim_unconfirmed_termination():
    clock = FakeClock()
    process = FakeProcess(clock, False)
    assert stop_worker(process, clock, 5) is False
    assert clock.now == 5


def test_process_embedder_reserves_stop_window_and_fatal_on_unexpected_exit(tmp_path):
    # A worker with unexpected exit must not produce fake/live success.
    import multiprocessing
    class Exited:
        exitcode = 7
        def start(self): pass
        def join(self, timeout): assert timeout <= 115
        def is_alive(self): return False
    class Context:
        def RawArray(self, *args): return multiprocessing.RawArray(*args)
        def RawValue(self, *args): return multiprocessing.RawValue(*args)
        def Process(self, **kwargs): return Exited()
    worker = ProcessEmbedder(tmp_path, FakeClock(), Context())
    with pytest.raises(IngestionError) as error:
        worker.encode([{'text': 'synthetic'}], 120)
    assert error.value.fatal is True

# US2: preparation must preserve readiness; mutations must invalidate it.
def test_repeat_and_shorter_replacement_remove_obsolete_ids():
    svc, client = service()
    assert svc.ingest(document())['status'] == 'complete'
    initial = set(client.records)
    assert svc.ingest(document())['status'] == 'complete'
    assert set(client.records) == initial
    result = svc.ingest(document('shorter.txt'))
    assert result['status'] == 'complete'
    assert result['data']['current_count'] == 1
    assert not initial & set(client.records)
    assert svc.inspect('learning-a')['data']['sources'][0]['records'][0]['text'] == 'The fictional café keeps one blue notebook.'


@pytest.mark.parametrize('failure', [IngestionError('embedding_failed'), IngestionError('deadline_exceeded')])
def test_preparation_failure_preserves_old_revision_and_explicit_retry(failure):
    svc, client = service()
    svc.ingest(document())
    old = copy.deepcopy(client.records)
    svc.embedder.error = failure
    result = svc.ingest(document('shorter.txt'))
    assert result['status'] == 'failed'
    assert result['data']['ready'] is True
    assert result['data']['current_verified_revision'] == 'v1'
    assert result['data']['attempted_revision'] == 'v2'
    assert client.records == old
    svc.embedder.error = None
    assert svc.ingest(document('shorter.txt'))['status'] == 'complete'


def test_preparation_failure_of_new_source_stays_unseen():
    svc, client = service()
    svc.embedder.error = IngestionError('embedding_failed')
    result = svc.ingest(document())
    assert result['status'] == 'failed'
    assert result['data']['source_status'] == 'unseen'
    assert result['data']['current_count'] == 0
    assert result['data']['ready'] is False
    assert client.calls == []


def test_partial_storage_failure_is_incomplete_unknown_count_and_no_retry():
    svc, client = service()
    request = client.request
    def fail_write(method, path, body=None, timeout=None):
        if method == 'PUT':
            client.calls.append((method, path, body, timeout))
            raise OSError('simulated storage capacity exhaustion')
        return request(method, path, body, timeout)
    client.request = fail_write
    result = svc.ingest(document())
    assert result['status'] == 'incomplete'
    assert result['error']['code'] == 'index_failed'
    assert result['data']['ready'] is False
    assert result['data']['current_count'] is None
    assert len(client.calls) == 2
    client.request = request
    assert svc.ingest(document())['status'] == 'complete'


def test_elapsed_embedding_budget_does_not_start_mutation():
    svc, client = service()
    class LateEmbedder(FakeEmbedder):
        def encode(self, chunks, deadline):
            svc.clock.now = 121
            return super().encode(chunks, deadline)
    svc.embedder = LateEmbedder()
    result = svc.ingest(document())
    assert result['status'] == 'failed'
    assert result['error']['code'] == 'deadline_exceeded'
    assert client.calls == []


def test_storage_timeout_cap_uses_remaining_time_and_no_extra_attempt():
    clock = FakeClock()
    client = FakeClient()
    client.clock = clock
    idx = Index(client, clock, '00000000-0000-4000-8000-000000000001')
    assert idx.read('learning-a', ['shared-guide'], 3) == []
    assert client.calls[0][3] == 3
    with pytest.raises(IngestionError):
        idx.read('learning-a', ['shared-guide'], 1)
    assert len(client.calls) == 1


def test_readback_metadata_mismatch_never_marks_ready():
    svc, client = service()
    original = client.request
    def corrupt(method, path, body=None, timeout=None):
        result = original(method, path, body, timeout)
        if path.endswith('/points/scroll') and result['points']:
            result['points'][0]['payload']['revision'] = 'corrupt'
        return result
    client.request = corrupt
    result = svc.ingest(document())
    assert result['status'] == 'incomplete'
    assert result['data']['ready'] is False

# US3: exact authorized scope must reach every inventory request.
def test_shared_source_id_scopes_remain_isolated_on_replacement():
    svc, client = service()
    svc.ingest(document())
    svc.ingest(document('isolation.txt'))
    neighbor = copy.deepcopy(svc.inspect('learning-b')['data'])
    svc.ingest(document('shorter.txt'))
    assert svc.inspect('learning-b')['data'] == neighbor
    assert svc.inspect('learning-a')['data']['current_count'] == 1
    assert svc.inspect('learning-b')['data']['current_count'] == 1
    assert len(client.records) == 2


@pytest.mark.parametrize('scope', ['Learning-a', 'learning-a ', ' learning-a', 'missing'])
def test_unapproved_scopes_never_reach_storage(scope):
    svc, client = service()
    result = svc.inspect(scope)
    assert result['status'] == 'rejected'
    assert result['scope'] is None
    assert client.calls == []


def test_whole_use_case_inventory_excludes_unapproved_source_ids():
    svc, client = service()
    svc.ingest(document())
    first = copy.deepcopy(next(iter(client.records.values())))
    first['id'] = '00000000-0000-4000-8000-000000000099'
    first['payload']['chunk_id'] = first['id']
    first['payload']['source_id'] = 'foreign-source'
    client.records[first['id']] = first
    result = svc.inspect('learning-a')
    assert result['data']['current_count'] == 3
    assert all(c['source_id'] == 'shared-guide' for c in result['data']['sources'][0]['records'])


def test_parallel_update_is_rejected_without_mutating_neighbor_attempt():
    svc, client = service()
    class Reentrant(FakeEmbedder):
        def encode(self, chunks, deadline):
            inner = svc.ingest(document('shorter.txt'))
            assert inner['status'] == 'rejected'
            return super().encode(chunks, deadline)
    svc.embedder = Reentrant()
    assert svc.ingest(document())['status'] == 'complete'
    assert len(client.records) == 3


def test_changed_inventory_cannot_reuse_stale_ready_flag():
    svc, client = service()
    svc.ingest(document())
    next(iter(client.records.values()))['payload']['revision'] = 'mixed'
    result = svc.inspect('learning-a')
    assert result['status'] == 'incomplete'
    assert result['data']['sources'][0]['ready'] is False

# US4: clearing/EOF/fatal errors cannot broaden deletion or claim uncertain cleanup.
def test_clear_is_scoped_and_verified_then_close_removes_owned_collection():
    svc, _client = service()
    svc.ingest(document())
    svc.ingest(document('isolation.txt'))
    assert svc.clear('learning-a')['data']['remaining_count'] == 0
    assert svc.inspect('learning-b')['data']['current_count'] == 1
    result = svc.close()
    assert result['status'] == 'complete'
    assert result['data'] == {'collection_removed': True, 'remaining_count': 0}
    assert svc.ingest(document())['status'] == 'rejected'


def test_cleanup_failure_preserves_unknown_count():
    svc, client = service()
    svc.ingest(document())
    client.fail = OSError('cannot delete')
    result = svc.close()
    assert result['status'] == 'failed'
    assert result['data']['remaining_count'] is None
    assert result['data']['collection_removed'] is False


def test_fatal_worker_failure_invalidates_prior_ready_and_stops_input():
    svc, _client = service()
    svc.ingest(document())
    svc.embedder.error = IngestionError('embedding_failed', fatal=True)
    result = svc.ingest(document('shorter.txt'))
    assert result['status'] == 'failed'
    assert result['data']['ready'] is False
    assert svc.ingest(document())['status'] == 'rejected'
    assert svc.fatal is True


def test_unverified_collection_absence_cannot_report_success():
    svc, client = service()
    # Fake server acknowledges delete but still reports a collection.
    original = client.request
    def undeleted(method, path, body=None, timeout=None):
        return True if method == 'GET' else original(method, path, body, timeout)
    client.request = undeleted
    assert svc.close()['status'] == 'failed'


def test_model_hash_manifest_cannot_leave_unreviewed_assets(tmp_path):
    import hashlib
    (tmp_path / 'config.json').write_text('{}')
    (tmp_path / 'unreviewed.py').write_text('not approved')
    with pytest.raises(IngestionError):
        verify_assets(tmp_path, {'config.json': hashlib.sha256(b'{}').hexdigest()})


@pytest.mark.parametrize('probe', [None, {'type': 'ext4', 'size': 268435456},
                                  {'type': 'tmpfs', 'size': 999}, {'type': 'tmpfs'}])
def test_tmpfs_capacity_must_be_verified_before_startup(probe):
    from app.ingestion.index import verify_tmpfs
    with pytest.raises(IngestionError):
        verify_tmpfs(probe)


def test_verified_tmpfs_capacity_is_accepted():
    from app.ingestion.index import verify_tmpfs
    assert verify_tmpfs({'type': 'tmpfs', 'size': 268435456}) is None


def test_global_teardown_deadline_never_resets_and_caps_phases():
    from app.ingestion.lifecycle import Teardown
    clock = FakeClock()
    cleanup = Teardown(clock)
    cleanup.begin()
    assert cleanup.phase(5) == 5
    clock.now = 12
    cleanup.begin()
    assert cleanup.remaining() == 33
    assert cleanup.phase(30) == 42
    clock.now = 44
    assert cleanup.phase(30) == 45
    clock.now = 46
    assert cleanup.remaining() == 0


def test_hung_cleanup_command_is_killed_without_unbounded_wait():
    from app.ingestion.lifecycle import guarded_command
    clock = FakeClock()
    import subprocess
    class Hung(FakeProcess):
        def communicate(self, timeout):
            self.clock.now += timeout
            if self.alive:
                raise subprocess.TimeoutExpired('owned-test', timeout)
            return ('', '')
        @property
        def returncode(self): return 0 if not self.alive else None
    process = Hung(clock)
    def factory(*args, **kwargs):
        return process
    # command timeout includes TERM/KILL guards, never extends phase.
    with pytest.raises(IngestionError):
        guarded_command(['owned-test'], 5, clock=clock, factory=factory)
    assert clock.now <= 5
    assert 'KILL' in process.events

# Review remediation: these catch real protocol/error branches, not mock existence.
def test_prewrite_inventory_outage_preserves_prior_verified_source():
    svc, client = service()
    svc.ingest(document())
    old = copy.deepcopy(client.records)
    client.fail = OSError('read unavailable before mutation')
    result = svc.ingest(document('shorter.txt'))
    assert result['status'] == 'failed'
    assert result['data']['ready'] is True
    assert result['data']['current_verified_revision'] == 'v1'
    assert client.records == old


@pytest.mark.parametrize('reply', [{}, {'points': [{}], 'next_page_offset': None},
                                  {'points': [{'id': 'broken'}], 'next_page_offset': None},
                                  {'points': 'not-records', 'next_page_offset': None}])
def test_malformed_inventory_returns_controlled_failure(reply):
    svc, client = service()
    def broken(*args, **kwargs): return reply
    client.request = broken
    result = svc.inspect('learning-a')
    assert result['status'] == 'failed'
    assert result['error']['code'] == 'index_failed'
    assert result['data']['current_count'] is None


def test_partially_accepted_upsert_never_preserves_old_ready():
    svc, client = service()
    original = client.request
    def partial(method, path, body=None, timeout=None):
        if method == 'PUT' and '/points' in path:
            client.records[body['points'][0]['id']] = copy.deepcopy(body['points'][0])
            raise OSError('receipt lost after accepting one point')
        return original(method, path, body, timeout)
    client.request = partial
    result = svc.ingest(document())
    assert result['status'] == 'incomplete'
    assert result['data']['ready'] is False
    assert result['data']['current_count'] is None
    assert len(client.records) == 1
    client.request = original
    assert svc.ingest(document())['status'] == 'complete'
    assert len(client.records) == 3


def test_embedding_worker_rechecks_expected_hashes_before_reloading(tmp_path, monkeypatch):
    import hashlib
    import multiprocessing

    import app.ingestion.embedding as module
    (tmp_path / 'config.json').write_text('changed')
    expected = {'config.json': hashlib.sha256(b'original').hexdigest()}
    class Model:
        max_seq_length = 256
        def get_sentence_embedding_dimension(self): return 384
        def get_embedding_dimension(self): return 384
        def encode(self, *args, **kwargs):
            class Vectors:
                def tolist(self): return [[1.0] + [0.0] * 383]
            return Vectors()
    monkeypatch.setattr(module, 'load_model', lambda *_: Model())
    buffer, status = multiprocessing.RawArray('d', 384), multiprocessing.RawValue('i', 0)
    module._encode_worker(tmp_path, ['synthetic'], buffer, status, expected)
    assert status.value == 3
    assert list(buffer) == [0.0] * 384


def test_hard_storage_deadline_stops_slow_progress_worker():
    import multiprocessing

    from app.ingestion.index import bounded_http
    clock = FakeClock()
    process = FakeProcess(clock)
    class Context:
        def RawArray(self, *args): return multiprocessing.RawArray(*args)
        def RawValue(self, *args): return multiprocessing.RawValue(*args)
        def Process(self, **kwargs):
            process.start = lambda: None
            return process
    with pytest.raises(IngestionError) as error:
        bounded_http('http://qdrant:6333', 'GET', '/collections/owned', None, 10,
                     clock=clock, context=Context())
    assert error.value.code == 'deadline_exceeded'
    assert clock.now <= 10
    assert process.alive is False


def test_slice_retokenization_shrinks_oversize_boundary_without_truncating():
    class ExpandingTokenizer(FakeTokenizer):
        def __call__(self, text, add_special_tokens=True, **kwargs):
            value = super().__call__(text, add_special_tokens=add_special_tokens, **kwargs)
            if add_special_tokens:
                value['input_ids'] = value['input_ids'] * 2
            return value
    chunks = chunk_document(document(), ExpandingTokenizer(), configuration())
    assert len(chunks) > 3
    assert chunks[-1]['text'].endswith('End of original guide.')
    assert all(len(ExpandingTokenizer()(c['text'])['input_ids']) <= 256 for c in chunks)


@pytest.mark.parametrize('operation', ['inspect', 'clear'])
def test_unconfirmed_storage_worker_stop_ends_session(operation):
    svc, _client = service()
    assert svc.ingest(document())['status'] == 'complete'
    def unconfirmed(*args, **kwargs):
        raise IngestionError('deadline_exceeded', fatal=True)
    svc.index.read = unconfirmed
    result = getattr(svc, operation)('learning-a')
    assert result['status'] in ('failed', 'incomplete')
    assert svc.fatal is True
    assert all(not state.ready for state in svc.states.values())
    assert svc.ingest(document())['status'] == 'rejected'
