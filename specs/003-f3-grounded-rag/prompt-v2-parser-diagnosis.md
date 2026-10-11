# V2 parser diagnosis

The original v2 run discarded raw output and exception detail. This is one separate
unchanged synthetic diagnostic replay, not recovered historical output or acceptance.
Original and replay proposal/system/context hashes, prompt tokens/bytes/settings,
43newtokens/EOS2/157bytes match. Historical byte identity cannot be proved.
[Replay](prompt-v2-parser-replay-report.json), [findings](prompt-v2-parser-findings.json).

Exact complete raw output (157 UTF8 bytes):

```json
{"status":"answered","claims":[{"claim_id":"returns","text":"Synthetic returns: unused items may be returned within 7 days with a receipt."}], "reason":null}
```

Strict JSON succeeds. Production validate_shape raises `AnswerError: invalid_input`;
decode_once translates it to `invalid_model_response`. Inspection of the unchanged
JSON Schema identifies exactly `/claims/0`: **'chunk_ids' is a required property**.
No JSON syntax, wrong type, extra property or trailing text failure.

Expected closed contract:exactly status/claims/reason. Answered requires1–5claims
and null reason; each claim requires nonempty claim_id/text and chunk_ids containing
1–3 unique lowercase UUID strings. Insufficient_evidence requires claims[] and
reason unsupported_question. No extra fields. Separate grounding requires exact
reviewed text and current returned evidence with full support/provenance checks.

V2 explicitly requests the same keys, answered/null reason and supporting chunk_ids.
Its angle-bracket example strings are placeholders, not literal citation UUIDs.
The model omitted an explicitly required field; no structural prompt/parser
contract mismatch. It also copied source text instead of reviewed rendering:
`Unused items may be returned within 7 days with a receipt.`. That visible mismatch would fail exact grounding, but production
stopped at schema validation and never reached grounding/citation validation.

Smallest evidence-backed correction proposal:clarify the prompt mapping to use
matching rules[].text verbatim and require chunk_ids from actual supporting
evidence[].chunk_id. This addresses both observed issues, but remains an untested
hypothesis. No silent text repair, citation insertion/fabrication, parser loosening
or weaker claim validation. No change applied.

Actual checks:cached pinned F3 build and diagnostic replay exit0 (measurement/cleanup,
not quality success); read-only parsing/shape reproduction and exact JSON Schema
inspection exit0. Replay total31.959s; collection/owned stack absent. Exact schema
inspection first found jsonschema absent from .venv; used its already-installed
system Python copy without installing anything. 136 existing app/test/docs/spec
files unchanged, including original failures and frozen inputs; diffcheck exit0.
Only new diagnostic capture/findings/narrative and ignored helpers created. No
acceptance runs, prompt/model/parser/limits/expectation changes, threshold tuning,
commits/pushes/publication. No full gate repeated for read-only diagnosis.
