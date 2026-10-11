"""Runner-owned Qdrant operations through an injectable REST request boundary."""
import json
import time

from .embedding import stop_worker, validate_vectors
from .types import IngestionError
from .validation import validate_endpoint, validate_shape


class Index:
    def __init__(self, client, clock, run_id):
        self.client, self.clock, self.run_id = client, clock, run_id
        self.collection = 'f1_' + run_id
        self.path = '/collections/' + self.collection

    def call(self, method, suffix, body, deadline):
        remaining = deadline - self.clock()
        if remaining <= 0:
            raise IngestionError('deadline_exceeded')
        try:
            result = self.client.request(method, self.path + suffix, body, timeout=min(10, remaining))
            if self.clock() >= deadline:
                raise IngestionError('deadline_exceeded')
            return result
        except IngestionError:
            raise
        except Exception as error:
            raise IngestionError('index_failed') from error

    def create(self, deadline):
        self.call('PUT', '', {'vectors': {'size': 384, 'distance': 'Cosine'}}, deadline)

    def read(self, use_case_id, source_ids, deadline):
        scope = {'must': [{'key': 'use_case_id', 'match': {'value': use_case_id}},
                          {'key': 'source_id', 'match': {'any': source_ids}}]}
        rows, offset, seen = [], None, set()
        while True:
            result = self.call('POST', '/points/scroll', {'filter': scope, 'limit': 128,
                               'with_payload': True, 'with_vector': True, 'offset': offset}, deadline)
            try:
                if not isinstance(result, dict) or not isinstance(result['points'], list):
                    raise IngestionError('index_failed')
                for point in result['points']:
                    record = {**point['payload'], 'vector': point['vector']}
                    if (record['chunk_id'] != str(point['id']) or record['use_case_id'] != use_case_id
                            or record['source_id'] not in source_ids or point['id'] in seen):
                        raise IngestionError('index_failed')
                    validate_shape(record, 'ChunkRecord')
                    validate_vectors([record['vector']])
                    seen.add(point['id'])
                    rows.append(record)
                next_offset = result['next_page_offset']
                if next_offset is not None and type(next_offset) not in (str, int):
                    raise IngestionError('index_failed')
            except (KeyError, TypeError, ValueError, IngestionError) as error:
                raise IngestionError('index_failed') from error
            if next_offset is None:
                return rows
            if next_offset == offset:
                raise IngestionError('index_failed')
            offset = next_offset

    def replace(self, scope, desired, deadline, previous=None):
        if previous is None:
            previous = self.read(scope[0], [scope[1]], deadline)
        points = [{'id': c['chunk_id'], 'payload': {k: v for k, v in c.items() if k != 'vector'},
                   'vector': c['vector']} for c in desired]
        result = self.call('PUT', '/points?wait=true', {'points': points}, deadline)
        if not isinstance(result, dict) or result.get('status') != 'completed':
            raise IngestionError('index_failed')
        desired_ids = {c['chunk_id'] for c in desired}
        obsolete = [c['chunk_id'] for c in previous if c['chunk_id'] not in desired_ids]
        if obsolete:
            removed = self.call('POST', '/points/delete?wait=true', {'points': obsolete}, deadline)
            if not isinstance(removed, dict) or removed.get('status') != 'completed':
                raise IngestionError('index_failed')
        actual = self.read(scope[0], [scope[1]], deadline)
        if {c['chunk_id'] for c in actual} != {c['chunk_id'] for c in desired}:
            raise IngestionError('index_failed')
        wanted = {c['chunk_id']: c for c in desired}
        if any({k: v for k, v in c.items() if k != 'vector'} !=
               {k: v for k, v in wanted[c['chunk_id']].items() if k != 'vector'} for c in actual):
            raise IngestionError('index_failed')
        return actual

    def clear(self, use_case_id, source_ids, deadline):
        rows = self.read(use_case_id, source_ids, deadline)
        if rows:
            removed = self.call('POST', '/points/delete?wait=true',
                                {'points': [c['chunk_id'] for c in rows]}, deadline)
            if not isinstance(removed, dict) or removed.get('status') != 'completed':
                raise IngestionError('cleanup_failed')
        if self.read(use_case_id, source_ids, deadline):
            raise IngestionError('cleanup_failed')
        return 0

    def close(self, deadline):
        self.call('DELETE', '', None, deadline)
        if self.call('GET', '', None, deadline) is not None:
            raise IngestionError('cleanup_failed')
        return True


def _http_request(url, method, path, body, timeout, transport=None):
    import httpx
    with httpx.Client(base_url=url, trust_env=False, follow_redirects=False,
                      transport=transport or httpx.HTTPTransport(retries=0)) as client, \
            client.stream(method, path, json=body, timeout=timeout) as response:
        if response.status_code == 404 and method == 'GET' and '/points' not in path:
            return None
        if not 200 <= response.status_code < 300:
            raise IngestionError('index_failed')
        data = bytearray()
        for block in response.iter_bytes():
            data.extend(block)
            if len(data) > 16 * 1024 * 1024:
                raise IngestionError('index_failed')
        value = json.loads(data)
        if not isinstance(value, dict) or value.get('status') != 'ok':
            raise IngestionError('index_failed')
        return value['result']


class LocalTransport:
    """One supervised REST attempt; no redirects or environment proxies."""
    def __init__(self, url, transport=None):
        validate_endpoint(url)
        self.url, self.transport = url, transport

    def request(self, method, path, body=None, timeout=None):
        try:
            if self.transport is not None:  # deterministic in-process transport only
                return _http_request(self.url, method, path, body, timeout, self.transport)
            return bounded_http(self.url, method, path, body, timeout)
        except IngestionError:
            raise
        except Exception as error:
            raise IngestionError('index_failed') from error

    def close(self):
        if self.transport is not None:
            self.transport.close()


def verify_tmpfs(probe):
    if not isinstance(probe, dict) or probe.get('type') != 'tmpfs' or type(probe.get('size')) is not int or probe['size'] != 268435456:
        raise IngestionError('index_failed', fatal=True)


def _http_worker(url, method, path, body, timeout, buffer, length, status):
    try:
        result = _http_request(url, method, path, body, timeout)
        encoded = json.dumps(result, allow_nan=False).encode()
        if len(encoded) > len(buffer):
            raise IngestionError('index_failed')
        buffer[:len(encoded)] = encoded
        length.value, status.value = len(encoded), 1
    except Exception:  # noqa: BLE001 -- worker protocol exposes only a safe failure code
        status.value = 2


def bounded_http(url, method, path, body, timeout, clock=time.monotonic, context=None):
    """Hard elapsed deadline includes TERM/KILL; shared bytes avoid blocking recv."""
    import multiprocessing
    deadline = clock() + timeout
    context = context or multiprocessing.get_context('spawn')
    buffer = context.RawArray('B', 16 * 1024 * 1024)
    length, status = context.RawValue('i', 0), context.RawValue('i', 0)
    process = context.Process(target=_http_worker,
        args=(url, method, path, body, timeout, buffer, length, status))
    process.start()
    reserve = min(5, max(0, (deadline - clock()) / 2))
    process.join(timeout=max(0, deadline - clock() - reserve))
    if process.is_alive():
        confirmed = stop_worker(process, clock, deadline)
        raise IngestionError('deadline_exceeded', fatal=not confirmed)
    if process.exitcode != 0 or status.value != 1 or not 0 < length.value <= len(buffer):
        raise IngestionError('index_failed')
    result = json.loads(bytes(buffer[:length.value]))
    if clock() >= deadline:
        raise IngestionError('deadline_exceeded')
    return result
