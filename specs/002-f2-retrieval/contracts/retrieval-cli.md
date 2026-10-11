# F2 local retrieval CLI contract

Status: proposed; no executable F2 CLI exists yet. [Schema](serialization.schema.json),
[data model](../data-model.md), [plan](../plan.md).

## Session entry point and configuration

Proposed dedicated wrapper `scripts/f2-demo.sh` accepts absolute paths for
`--approval-manifest`, `--retrieval-approval`, `--model-dir`, required normal-session `--min-score`
and optional `--calibration-id`. It supplies a verified read-only tmpfs receipt and
launches `python -m app.retrieval session` in the dedicated F2 image/internal network.
No caller-selectable collection, arbitrary endpoint, credential or environment file.
The only Qdrant endpoint remains `http://qdrant:6333`. No runtime acquisition.

An F2 CLI supervisor owns the factory/dispatcher session worker and bounds startup
to 120seconds before READY, including model/tokenizer load. The wrapper independently
bounds startup and uses the same owned shutdown policy on timeout.

Startup checks exact F2 receipt/manifest binding and genuine authorization, immutable
model/config hashes, cosine/384 collection and processor compatibility under a
supervised preflight <=120seconds. F2_READY is emitted only after all checks pass;
F2_TEARDOWN begins one 45-second shutdown. No input forwarded before READY.
Do not change the existing F1 CLI or its READY/TEARDOWN markers.

## Input protocol

One strict JSON object per line. Duplicate keys, nonfinite JSON numbers, extra fields,
wrong types and unknown operations are rejected without echoing raw input. No null
question/limit/scope and no identity normalization. F2 UTF-8 line cap512KiB accommodates the F1 source-size ceiling with worst-case
JSON escaping plus bounded metadata. Reject oversize lines with bounded draining
rather than unbounded allocation. Delegated F1 operations obey their original
field/envelope contracts inside this F2 transport limit; the original F1 CLI is unchanged.

Retrieve example (synthetic question, not a result claim):

```json
{"op":"retrieve","use_case_id":"learning-a","question":"Where does the café keep its blue notebooks?","top_k":3}
```

Required: op, use_case_id, question. Optional: top_k only. Threshold is startup
configuration, not question-controlled. Scope comes from the approved manifest,
not Stage 1's static catalog. Question <=4,096 UTF-8 bytes and <=256 tokenizer tokens
with specials; whitespace-only rejected. Original question bytes are not normalized.
Token overflow returns `question_too_long` before encoding/search. A verified empty
scope still validates token length, then skips semantic encoding/search.

The F2 dispatcher also accepts unchanged F1 ingest/inspect/clear/close requests and
returns their unchanged version1 envelopes. Retrieval/unknown/malformed requests use
version2 envelopes; the separate schema accepts both without modifying F1's schema.

## Output envelope

All fields required: `schema_version`=2, request_id, run_id, op, status, use_case_id,
configuration, elapsed_ms, evidence_count, evidence, error. UUIDs lower-case canonical.
`op`=retrieve for recognized retrieve requests, null for malformed/unknown operations.
Scope null if scope could not be validated. Configuration null until a valid retrieve
request and startup settings exist. elapsed_ms is finite nonnegative; no raw question.

| Status | Evidence | Error |
| --- | --- | --- |
| matched | 1..top_k verified ranked passages; evidence_count equals length | null |
| no_match | [] and count0 | null |
| rejected | [] and count0 | fixed safe code/message |
| failed | [] and count0 | fixed safe code/message |

Evidence fields are F1 payload fields plus rank and score; no vector or invented URI.
Configuration exposes mode, top_k, min_score, calibration_id, query_encoding,
scoring, model_configuration and all operating budgets/caps. Mode is deterministic
or local_live; fake mode never claims real semantic retrieval. calibration_id may
be null for an explicitly configured normal session; it is provenance only, never an approval flag.

Codes/messages are identical fixed strings: invalid_input, unknown_operation,
unknown_use_case, question_too_long, configuration_mismatch, scope_not_ready,
scope_too_large, model_unavailable, embedding_failed, index_failed,
invalid_search_result, deadline_exceeded, session_unavailable. Do not leak exceptions.

Rejected categories: input/op/scope/question length/session unavailable. Failed:
configuration/readiness/cap/model/embedding/index/result/deadline. Verified empty is
no_match, not unknown scope. Scope-too-large is failure without corpus truncation.
Schema shapes do not enforce calendar validity, finite numeric values, bool-vs-int
Python rules, byte length, exact scope, cross-field lengths or real authorization;
these are mandatory semantic checks.

## Search and readiness contract

Read-only scope verification precedes semantic encoding. Do not call mutating F1
inspect as the verifier. All represented states must be complete/ready; approved
never-ingested/cleared sources may be empty if exhaustive read confirms absence.
Reject any unregistered row or mismatch with the verified current registry.

One query: POST owned collection `/points/query`, query=384-vector, params.exact=true,
filter.must includes exact use_case_id, approved source IDs, and has_id=current verified
IDs; limit=N, with_payload=true, with_vector=false. No threshold on server, no prefetch,
lookup, offset, retry/refinement or second query. Empty N skips query. N<=2,048.
Existing LocalTransport unwraps result; expect a points array in its returned object.
Validate all candidate IDs/payloads/scores and require full snapshot set equality.
No filtering of malformed foreign rows to conceal a compromised response.

Then include scores >=effective minimum, sort `(-score, chunk_id)` over all candidates,
slice user top_k and assign contiguous ranks. Distinct overlapping passages remain
allowed. Exact search over full bounded N supports the required tie behavior; it
is not a production scale search plan. Unsupported-topic no-match must be measured.

## Deadlines, failures and exit

Total request <=120seconds, inventory <=10 aggregate, query worker <=90 including
load/tokenization/hash verification/termination, search <=10; all also <=remaining
original deadline. Validation/serialization remain inside total. Reserve TERM2/KILL3
inside active worker stage; transport's hard timeout remains supervised, not merely
inactivity-based. Serialization size is bounded by top_k and F1 chunk bounds.

Nonfatal failed request sets eventual session exit1 but may accept explicit later
requests. Rejected request and no_match alone do not set nonzero exit. Fatal worker
exit/protocol failure/unconfirmed termination stops input, marks run unavailable and
performs existing cleanup. EOF/close cleans up; interrupt exit130; cleanup uncertainty
retains nonzero status. Close returns unchanged F1 close envelope.
One 45-second teardown: worker<=5, collection<=10, Docker<=30. No repeated-signal reset,
global prune, shared volume removal or secure-erasure claim. Explicit fresh run is
recovery after fatal stop or lost registry.

## F2 source-use approval

Keep the original F1 manifest shape unchanged. A separate read-only F2ApprovalReceipt
binds its exact SHA-256 to purpose f2_local_retrieval, owner/reviewer/real decision/date,
local operator access and demo-end owned deletion. This receipt adds no sources and
does not broaden redistribution. Every new source needs its own exact tuple/hash in
an actually approved manifest. A valid receipt schema or test fixture cannot grant consent.

## Owned process hierarchy and bounded IPC

The CLI parent supervisor stays outside a dedicated owned process group. Its session
factory/dispatcher is group leader; all query and storage worker descendants inherit
that group and must not detach. Record the group identity and descendant ownership
before startup/READY. Leader death alone never proves descendant termination. Session
exit, broken/stalled IPC or unconfirmed worker stop is fatal: stop input and signal
only the recorded owned group, even if its leader has died. Verify all recorded
processes and group descendants are absent; ownership mismatch or unverifiable
residue remains a cleanup failure. The wrapper independently checks process and
owned container/network absence. Never signal an unrelated or reused group.

IPC uses strict JSON framed bytes, never pickle, with a 16 MiB maximum message and
64 KiB maximum frame. Validate length before allocation; bound cumulative assembly
and reads/writes by the remaining startup/request/teardown deadline. Oversize or
stalled transport is fatal with a fixed safe error, without partial output. Existing
512 KiB input-line limit still applies; delegated F1 envelopes retain their shape
inside this F2-only transport ceiling. The original F1 CLI is unchanged.
One original 45-second teardown covers whole-group TERM2/KILL3 within worker5,
collection10 and Docker30. Repeated signals, leader death or failed IPC never reset
that deadline. Cleanup uncertainty preserves nonzero exit status.

## Evaluation case format and consumer

`EvaluationCaseSet` and `EvaluationCase` are closed schema definitions. The set has
schema_version=2, kind=evaluation_case_set, case_set_id, manifest_sha256,
configuration_fingerprint, review_attribution and cases. Each case has case_id,
split=calibration|held_out, exact use_case_id, question and expected. Expected is
one of {status:matched, source_ids:[...]} (nonempty unique IDs) or {status:no_match}
(with no source_ids). No free-form expectation, null or extra field is permitted.

Case file is capped at16 MiB and256 cases before allocation; the schema caps case
count, while byte limits and bounded reads are semantic checks. Semantic preflight
rejects duplicate case IDs, unknown scopes/source IDs, expected
sources outside that exact scope, mismatching manifest/config fingerprints and
contradictory expectations. Apply the same question byte limits without normalization; tokenize only selected-split
questions during execution under their individual deadlines. Both supported and unsupported calibration cases are required;
held-out has >=3 supported and >=2 unsupported cases. Review attribution records
real owner/reviewer/decision_reference/approved_at; schema validity grants no consent.
Freeze the case-file SHA-256 with corpus/config/threshold before held-out execution.

Planned `app/retrieval/evaluation.py` exposes
`evaluate_cases(service, case_set, split, deadline)` to an already-ready owned session.
The dedicated wrapper additionally accepts `--evaluation-cases ABSOLUTE_PATH` and
`--evaluation-split calibration|held_out`; both are required together. In evaluation
mode stdin accepts only approved F1 ingest requests, returning unchanged envelopes;
on EOF, stop ingest, evaluate the selected split sequentially in that same session,
then always tear down. Any failed ingest prevents evaluation. No reopen/resume,
question logging or evaluator control operation in normal session JSONL.

Calibration mode rejects --min-score/--calibration-id and needs no invented threshold:
shared pipeline returns full validated candidates internally, then emits bounded
summaries containing only case_id, candidate_count, maximum_candidate_score,
best_expected_source_score and best_expected_source_rank (nullable when absent).
candidate_count is integer0–2,048; maximum_candidate_score is null only for empty
candidates; best expected score/rank are null for negatives or absent expected sources.
These summaries use internal verified model/config settings, not a
RetrievalConfiguration with a fabricated min_score. Scores are finite; ranks follow (-score, chunk_id) across all N; no questions,
vectors, passage text or full candidate dump. Each case has the original120-second
budget. Missing expected-source candidate, rank>3, empty negative scope or pipeline
failure fails calibration. Compare the largest negative maximum with the smallest
positive expected-source score; nonseparation fails, never silently filters samples.

Held-out mode requires reviewed --min-score and --calibration-id, uses normal
retrieval with top_k=3 and emits its unchanged result plus a case_id association in
an evaluation-only record. A positive passes if any expected source appears among
first3; a negative passes only on no_match with zero evidence. Rejected/failed is
failed evaluation. Selected-split execution never tunes threshold or consumes held-out
scores for calibration. Both modes use the same approval/startup/ownership/cleanup
and separately approved evidence retention gates as the normal session.
