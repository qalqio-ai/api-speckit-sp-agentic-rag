"""Approval-first ingestion with inspectable provenance and in-memory readiness."""
import hashlib
import json
from dataclasses import asdict
from uuid import uuid4

from .chunking import chunk_document
from .embedding import validate_vectors
from .types import IngestionError, SourceState
from .validation import (
    allowed_ids,
    validate_document,
    validate_manifest,
    validate_shape,
)


class Service:
    def __init__(self, manifest, config, tokenizer, embedder, index, clock):
        self.manifest = validate_manifest(manifest)
        self.config = validate_shape(config, 'RunConfiguration')
        self.tokenizer, self.embedder, self.index, self.clock = tokenizer, embedder, index, clock
        self.states = {}
        self.closed = False
        self.fatal = False
        self.busy = False
        self.cleanup_result = None

    def result(self, op, status, scope=None, data=None, error=None):
        value = {'schema_version': 1, 'request_id': str(uuid4()), 'run_id': self.index.run_id,
                 'op': op, 'status': status, 'scope': scope, 'configuration': self.config if op is not None else None,
                 'data': data, 'error': None if error is None else {'code': error, 'message': error}}
        return validate_shape(value, 'OperationResult')

    def ingest(self, document):
        if self.busy or self.closed or self.fatal:
            return self.result('ingest', 'rejected', error='invalid_input')
        self.busy = True
        try:
            return self._ingest(document)
        finally:
            self.busy = False

    def _ingest(self, document):
        scope = None
        try:
            validate_document(document, self.manifest)
            scope = {'use_case_id': document.use_case_id, 'source_id': document.source_id}
        except IngestionError as error:
            return self.result('ingest', 'rejected', error=error.code)
        key = (document.use_case_id, document.source_id)
        state = self.states.setdefault(key, SourceState())
        state.attempted_revision = document.revision
        deadline = self.clock() + 120
        chunks = None
        try:
            chunks = chunk_document(document, self.tokenizer, self.config)
            desired = self.embedder.encode(chunks, deadline)
            if len(desired) != len(chunks):
                raise IngestionError('embedding_failed')
            validate_vectors([c['vector'] for c in desired])
            if self.clock() >= deadline:
                raise IngestionError('deadline_exceeded')
            previous = self.index.read(key[0], [key[1]], deadline)
        except IngestionError as error:
            self.record_fatal(error)
            return self.result('ingest', 'failed', scope,
                               self.ingest_data(state, len(chunks) if chunks is not None else None), error.code)
        state.source_status, state.ready = 'incomplete', False
        state.expected_count = len(chunks)
        state.expected_ids = {c['chunk_id'] for c in desired}
        try:
            actual = self.index.replace(key, desired, deadline, previous=previous)
            state.expected_payload_hashes = {c['chunk_id']: self.payload_hash(c) for c in actual}
            state.current_verified_revision = document.revision
            state.source_status, state.ready = 'complete', True
            state.expected_count = state.current_count = len(actual)
            return self.result('ingest', 'complete', scope, self.ingest_data(state, len(chunks)))
        except IngestionError as error:
            self.record_fatal(error)
            state.source_status, state.ready, state.current_count = 'incomplete', False, None
            return self.result('ingest', 'incomplete', scope, self.ingest_data(state, len(chunks)), error.code)

    def record_fatal(self, error):
        if error.fatal:
            self.fatal = True
            for state in self.states.values():
                state.ready = False
                if state.source_status == 'complete':
                    state.source_status = 'incomplete'

    @staticmethod
    def payload_hash(record):
        payload = {k: v for k, v in record.items() if k != 'vector'}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    @staticmethod
    def ingest_data(state, intended):
        return {k: asdict(state)[k] for k in ('attempted_revision', 'current_verified_revision',
                'source_status', 'ready', 'current_count')} | {'intended_count': intended}

    def inspect(self, use_case_id, source_id=None):
        scope = {'use_case_id': use_case_id, 'source_id': source_id}
        try:
            ids = allowed_ids(self.manifest, use_case_id, source_id)
            rows = self.index.read(use_case_id, ids, self.clock() + 10)
            sources = []
            for ident in ids:
                records = [c for c in rows if c['source_id'] == ident]
                state = self.states.get((use_case_id, ident))
                if not records and state is None:
                    continue
                ready = bool(state and state.ready
                             and {c['chunk_id'] for c in records} == state.expected_ids
                             and all(self.payload_hash(c) == state.expected_payload_hashes.get(c['chunk_id']) for c in records))
                if state and state.ready and not ready:
                    state.ready, state.source_status = False, 'incomplete'
                sources.append({'use_case_id': use_case_id, 'source_id': ident,
                                'current_verified_revision': state.current_verified_revision if state else None,
                                'attempted_revision': state.attempted_revision if state else None,
                                'source_status': 'complete' if ready else 'incomplete', 'ready': ready,
                                'expected_count': state.expected_count if state else None,
                                'current_count': len(records), 'records': records})
            incomplete = any(not s['ready'] for s in sources)
            return self.result('inspect', 'incomplete' if incomplete else 'complete', scope,
                               {'sources': sources, 'current_count': len(rows)},
                               'incomplete_source' if incomplete else None)
        except IngestionError as error:
            self.record_fatal(error)
            return self.result('inspect', 'rejected' if error.code == 'source_not_approved' else 'failed',
                               None if error.code == 'source_not_approved' else scope,
                               {'sources': None, 'current_count': None}, error.code)

    def clear(self, use_case_id, source_id=None):
        scope = {'use_case_id': use_case_id, 'source_id': source_id}
        try:
            if self.closed or self.fatal or self.busy:
                raise IngestionError()
            ids = allowed_ids(self.manifest, use_case_id, source_id)
            self.index.clear(use_case_id, ids, self.clock() + 10)
            for ident in ids:
                self.states.pop((use_case_id, ident), None)
            return self.result('clear', 'complete', scope, {'remaining_count': 0})
        except IngestionError as error:
            self.record_fatal(error)
            rejected = error.code in ('source_not_approved', 'invalid_input')
            if not rejected:
                for key, state in self.states.items():
                    if key[0] == use_case_id and (source_id is None or key[1] == source_id):
                        state.ready, state.source_status = False, 'incomplete'
            return self.result('clear', 'rejected' if rejected else 'incomplete',
                               None if rejected else scope, {'remaining_count': None},
                               error.code if rejected else 'cleanup_failed')

    def close(self):
        if self.cleanup_result is not None:
            return self.cleanup_result
        self.closed = True
        for state in self.states.values():
            state.ready = False
        deadline = self.clock() + 15
        failed = False
        if hasattr(self.embedder, 'close'):
            failed = not self.embedder.close(min(deadline, self.clock() + 5))
        try:
            self.index.close(min(deadline, self.clock() + 10))
            if failed:
                raise IngestionError('cleanup_failed')
            self.states.clear()
            result = self.result('close', 'complete', data={'collection_removed': True, 'remaining_count': 0})
        except IngestionError:
            result = self.result('close', 'failed', data={'collection_removed': False, 'remaining_count': None}, error='cleanup_failed')
        self.cleanup_result = result
        return result
