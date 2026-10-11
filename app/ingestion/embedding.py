"""Offline CPU loading and validated vectors. Live dependencies stay lazy."""
import hashlib
import math
import os
from pathlib import Path

from .types import IngestionError


def verify_assets(root, hashes):
    root = Path(root).resolve()
    if not root.is_dir() or not hashes:
        raise IngestionError('model_unavailable')
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name != 'f1-model.json'}
    if actual != set(hashes):
        raise IngestionError('model_unavailable')
    for relative, digest in hashes.items():
        path = Path(relative)
        target = root / path
        if path.is_absolute() or '..' in path.parts or target.is_symlink():
            raise IngestionError('model_unavailable')
        try:
            if not target.resolve().is_relative_to(root) or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise IngestionError('model_unavailable')
        except OSError as error:
            raise IngestionError('model_unavailable') from error


def load_model(root, loader=None):
    if not Path(root).is_dir():
        raise IngestionError('model_unavailable')
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    if loader is None:
        from sentence_transformers import SentenceTransformer
        loader = SentenceTransformer
    try:
        return loader(str(root), device='cpu', local_files_only=True, trust_remote_code=False)
    except Exception as error:
        raise IngestionError('model_unavailable') from error


def validate_vectors(vectors):
    if not vectors:
        raise IngestionError('embedding_failed')
    for vector in vectors:
        if (len(vector) != 384 or any(type(v) not in (float, int) or not math.isfinite(v) for v in vector)
                or not any(v != 0 for v in vector)):
            raise IngestionError('embedding_failed')
    return vectors


def stop_worker(process, clock, deadline):
    if not process.is_alive():
        process.join(timeout=0)
        return True
    process.terminate()
    process.join(timeout=max(0, min(2, deadline - clock())))
    if process.is_alive():
        process.kill()
        process.join(timeout=max(0, min(3, deadline - clock())))
    return not process.is_alive()


def _encode_worker(root, texts, buffer, status, hashes=None):
    try:
        verify_assets(root, hashes)
        model = load_model(root)
        if model.get_embedding_dimension() != 384 or model.max_seq_length != 256:
            raise IngestionError('model_unavailable')
        vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False).tolist()
        validate_vectors(vectors)
        if len(vectors) != len(texts):
            raise IngestionError('embedding_failed')
        for i, vector in enumerate(vectors):
            buffer[i * 384:(i + 1) * 384] = vector
        status.value = 1
    except IngestionError as error:
        status.value = 3 if error.code == 'model_unavailable' else 2
    except Exception:  # noqa: BLE001 -- child boundary must return a fixed safe code
        status.value = 2


class ProcessEmbedder:
    """One fresh spawned worker per attempt; shared numeric memory avoids pipe deadlocks."""
    def __init__(self, root, clock, context=None, hashes=None):
        import multiprocessing
        self.root, self.clock = root, clock
        self.context = context or multiprocessing.get_context('spawn')
        self.hashes = dict(hashes or {})
        self.active = None

    def encode(self, chunks, deadline):
        if deadline - self.clock() <= 5:
            raise IngestionError('deadline_exceeded')
        buffer = self.context.RawArray('d', len(chunks) * 384)
        status = self.context.RawValue('i', 0)
        process = self.context.Process(target=_encode_worker,
                    args=(self.root, [c['text'] for c in chunks], buffer, status, self.hashes))
        self.active = process
        process.start()
        process.join(timeout=max(0, deadline - self.clock() - 5))
        if process.is_alive():
            confirmed = stop_worker(process, self.clock, min(deadline, self.clock() + 5))
            if confirmed:
                self.active = None
            raise IngestionError('deadline_exceeded' if confirmed else 'embedding_failed', fatal=not confirmed)
        self.active = None
        if process.exitcode != 0 or status.value == 0:
            raise IngestionError('embedding_failed', fatal=True)
        if status.value != 1:
            raise IngestionError('model_unavailable' if status.value == 3 else 'embedding_failed')
        vectors = [list(buffer[i * 384:(i + 1) * 384]) for i in range(len(chunks))]
        validate_vectors(vectors)
        return [{**chunk, 'vector': vector} for chunk, vector in zip(chunks, vectors)]

    def close(self, deadline):
        if self.active is None:
            return True
        if not stop_worker(self.active, self.clock, deadline):
            return False
        self.active = None
        return True
