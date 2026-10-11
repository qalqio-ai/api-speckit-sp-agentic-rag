"""Original-text slices and canonical UUIDv5 identities (fixed project namespace)."""
import hashlib
import json
from uuid import UUID, uuid5

from .types import IngestionError

NAMESPACE = UUID('995c501a-e20a-5f20-a970-842721084645')


def chunk_document(document, tokenizer, config):
    text = document.text
    offsets = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True,
                        truncation=False)['offset_mapping']
    if not offsets:
        raise IngestionError()
    chunks, position = [], 0
    while position < len(offsets):
        stop = min(position + 200, len(offsets))
        start = offsets[position][0]
        end = offsets[stop - 1][1]
        while len(tokenizer(text[start:end], add_special_tokens=True, truncation=False)['input_ids']) > 256:
            stop -= 1
            if stop <= position:
                raise IngestionError()
            end = offsets[stop - 1][1]
        if not (0 <= start < end <= len(text)) or not text[start:end].strip():
            raise IngestionError()
        identity = {'use_case_id': document.use_case_id, 'source_id': document.source_id,
                    'revision': document.revision,
                    'content_sha256': hashlib.sha256(text.encode()).hexdigest(),
                    'configuration_fingerprint': config['configuration_fingerprint'],
                    'tokenizer_fingerprint': config['tokenizer_fingerprint'],
                    'model_commit': config['model_commit'], 'start': start, 'end': end,
                    'slice_sha256': hashlib.sha256(text[start:end].encode()).hexdigest()}
        ident = str(uuid5(NAMESPACE, json.dumps(identity, sort_keys=True, separators=(',', ':'), ensure_ascii=False)))
        chunks.append({'chunk_id': ident, 'use_case_id': document.use_case_id,
                       'source_id': document.source_id, 'title': document.title,
                       'revision': document.revision, 'content_sha256': identity['content_sha256'],
                       'start': start, 'end': end, 'text': text[start:end],
                       'configuration_fingerprint': config['configuration_fingerprint'],
                       'tokenizer_fingerprint': config['tokenizer_fingerprint'],
                       'model_id': config['model_id'], 'model_commit': config['model_commit']})
        if len(chunks) > 2048:
            raise IngestionError()
        if stop == len(offsets):
            break
        position = max(position + 1, stop - 20)
    covered = bytearray(len(text))
    for chunk in chunks:
        covered[chunk['start']:chunk['end']] = b'\1' * (chunk['end'] - chunk['start'])
    if any(not covered[i] and not char.isspace() for i, char in enumerate(text)):
        raise IngestionError()
    return chunks
