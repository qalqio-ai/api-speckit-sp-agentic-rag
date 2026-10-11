"""Sequential JSONL session with approval-first offline startup and bounded cleanup."""
import argparse
import json
import signal
import sys
import time
from pathlib import Path
from uuid import uuid4

from .embedding import ProcessEmbedder, load_model, verify_assets
from .index import Index, LocalTransport, verify_tmpfs
from .service import Service
from .types import IngestionError, SourceDocument
from .validation import (
    parse_request,
    strict_json,
    validate_endpoint,
    validate_manifest,
    validate_shape,
)


def live_factory(manifest_path, model_dir, url, proof_path):
    try:
        approved = validate_manifest(strict_json(Path(manifest_path).read_text()))
        proof = strict_json(Path(proof_path).read_text())
        verify_tmpfs(proof)
        root = Path(model_dir)
        config = validate_shape(strict_json((root / 'f1-model.json').read_text()), 'RunConfiguration')
        verify_assets(root, config['model_file_sha256'])
        model = load_model(root)
        if model.get_embedding_dimension() != 384 or model.max_seq_length != 256:
            raise IngestionError('model_unavailable')
        clock = time.monotonic
        transport = LocalTransport(url)
        index = Index(transport, clock, str(uuid4()))
        svc = Service(approved, config, model.tokenizer, ProcessEmbedder(root, clock, hashes=config['model_file_sha256']), index, clock)
        try:
            index.create(clock() + 10)
        except IngestionError:
            svc.close()
            transport.close()
            raise
        return svc
    except IngestionError:
        raise
    except (OSError, ValueError, TypeError) as error:
        raise IngestionError('model_unavailable') from error


def session(argv=None, factory=None, stdin=None, stdout=None, stderr=None):
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout
    stderr = stderr if stderr is not None else sys.stderr
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['session'])
    parser.add_argument('--approval-manifest', required=True)
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--qdrant-url', default='http://qdrant:6333')
    parser.add_argument('--tmpfs-proof', help='Read-only mount receipt produced by the owned-stack wrapper')
    args = parser.parse_args(argv)
    try:
        validate_endpoint(args.qdrant_url)
        svc = factory(args.approval_manifest, args.model_dir, args.qdrant_url) if factory else live_factory(
            args.approval_manifest, args.model_dir, args.qdrant_url, args.tmpfs_proof)
    except IngestionError as error:
        print(error.code, file=stderr, flush=True)
        return 1
    print('F1_READY', file=stderr, flush=True)
    exit_code = 0
    old_handler = signal.getsignal(signal.SIGTERM)
    def interrupted(signum, frame):
        raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM, interrupted)
    cleanup = None
    try:
        for line in stdin:
            value = None
            try:
                value = strict_json(line)
                operation = parse_request(value)
                op = operation['op']
                if op == 'ingest':
                    result = svc.ingest(SourceDocument(**{k: v for k, v in operation.items() if k != 'op'}))
                elif op == 'inspect':
                    result = svc.inspect(operation['use_case_id'], operation.get('source_id'))
                elif op == 'clear':
                    result = svc.clear(operation['use_case_id'], operation.get('source_id'))
                else:
                    print('F1_TEARDOWN', file=stderr, flush=True)
                    cleanup = result = svc.close()
            except IngestionError as error:
                known = value.get('op') if isinstance(value, dict) else None
                known = known if known in ('ingest', 'inspect', 'clear', 'close') else None
                result = svc.result(known, 'failed' if known == 'close' else 'rejected', error=error.code)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False), file=stdout, flush=True)
            if result['status'] in ('failed', 'incomplete'):
                exit_code = 1
            if svc.fatal or cleanup is not None:
                break
    except KeyboardInterrupt:
        exit_code = 130
    except (OSError, UnicodeError) as error:
        del error
        exit_code = 1
    finally:
        signal.signal(signal.SIGTERM, old_handler)
        if cleanup is None:
            print('F1_TEARDOWN', file=stderr, flush=True)
            cleanup = svc.close()
        if cleanup['status'] != 'complete':
            exit_code = exit_code or 1
        if svc.fatal:
            exit_code = exit_code or 1
        print('cleanup_complete' if cleanup['status'] == 'complete' else 'cleanup_failed', file=stderr, flush=True)
        if hasattr(svc.index.client, 'close'):
            svc.index.client.close()
    return exit_code


if __name__ == '__main__':
    raise SystemExit(session())
