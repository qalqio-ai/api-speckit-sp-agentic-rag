# F3 answer and local session contract

Design only; no F3 executable exists. [Schema](serialization.schema.json),
[data model](../data-model.md), [research](../research.md).
The user selected the exact reviewed question/claim boundary on 2026-10-03
(Option A: "recommended"); see [clarification](../spec.md#session-2026-10-03).
Detailed design and implementation/source/model/run permissions remain separate gates.

## Entry point and input

Proposed wrapper scripts/f3-demo.sh launches python -m app.answer session. Required
absolute read-only paths: --approval-manifest, --retrieval-approval, --answer-approval,
--grounding-catalog, --embedding-model-dir, --generation-model-dir, --generation-assets.
Require reviewed finite --min-score and --calibration-id for F2 provenance. No caller
endpoint, collection, credentials, env file or model fallback. Qdrant only at the
owned internal http://qdrant:6333. Preflight<=120seconds before F3_READY verifies actual
approvals, source/catalog hash binding, asset allowlist/hash/config and supervised
local tokenizer compatibility. No forward input before READY or runtime acquisition.

Strict JSONL,512KiB/line with bounded draining; no duplicate keys/nonfinite values.
Answer request: {op:answer,use_case_id:exact_string,question:nonblank_string}; all
required, no extra field or top_k. F2 validation applies including4,096UTF8 bytes and
256 embedding-token limit incl specials. Answer always retrieves top_k3. Delegated
F1 ingest/inspect/clear/close and F2 retrieve keep their original request/result shapes
and settings. Original CLI entry points and markers remain unchanged. Unknown/malformed
F3 requests use version3 safe envelope with op=null. No model action protocol.

## Reviewed catalog and runtime grounding

Catalog is bounded1MiB, <=64 claims, <=128 aliases, <=32 source_rules. Actual owner/
reviewer/decision/date attribution and F3 receipt bind exact manifest/catalog hashes;
shape does not grant approval. Each SourceRule binds exact approved scope/source/
revision/content SHA256 and a reviewed full-source assessment. Cover every represented
source tuple in the selected scope; missing/stale/mismatched rules fail configuration.
A reviewer must explicitly establish completeness, relevant contradictions and all
material conditions; this is a human-authored domain boundary, not automatic proof.

Each CatalogClaim has an exact complete factual rendering, scope/claim_id, supporting
alternatives and conflicting_claim_ids. Every alternative is a nonempty list of spans
that must ALL be present; alternatives are OR. Spans bind source/revision/hash, exact
original-character start/end and exact quote. A span must fit wholly inside a current
returned passage and equal its text at those offsets. Review ensures span meaning,
conditions/exceptions and rendering match; equality alone is not semantic validation.
References/claim IDs unique in scope, offsets valid, no unapproved source/claim.
Reject duplicate aliases, unknown/conflicting claim references, source-rule duplicates
and catalog/manifest mismatch. Scope keys are exact strings; support sources must
belong to that claim scope. Question expected_claim_ids nonempty iff reason=null;
negative question entries have empty IDs and supported reason.

QuestionCoverage exact unnormalized (scope,question) maps to all required claim IDs
or a reviewed unsupported/conflict reason. Each known question's full requested
meaning must be reviewed; do not infer unseen multipart coverage, normalize aliases,
use keywords, similarity or a model to choose a catalog question. Unknown questions
abstain unsupported_question after F2 validation/retrieval with zero generation.
This can reject genuinely answerable unseen questions and cannot claim general QA.

After F2 returns:
1. Failed/rejected result maps to failed/rejected without generation; successful empty
   result -> no_evidence. No fallback/retry/refinement.
2. Verify catalog/current source coverage, then exact question alias. Reviewed negative
   aliases abstain with their specified reason. Positive alias requires all claims'
   complete support in current returned evidence; otherwise unsupported_question.
3. For each required claim inspect its reviewed relevant opposing claims. If complete
   opposing support is also returned -> conflicting_evidence. If an opposing claim
   has supporting sources present in the current scope but its complete spans are not
   returned, conflict cannot be ruled out: abstain unsupported_question. Unrelated
   conflicts do not force abstention. Never query again or fetch extra evidence.
4. Only eligible reviewed renderings whose complete supporting spans were verified
   from returned evidence may appear in generation rules, with their claim IDs and
   allowed supporting chunk IDs. Evidence text is the factual source; catalog supplies
   reviewed validation constraints. Send question, governing rules and current evidence
   only; no prior history, extra source facts or expected evaluation outcomes.
5. One actual model attempt emits closed ModelResponse. Answered requires every exact
   expected claim ID/text once, no extra claim/prose, and current supporting chunk IDs.
   Every claim's cited passages must cover a complete reviewed support alternative;
   valid but irrelevant citation fails grounding. No synthesizing an answer from catalog
   when model output fails. Model-declared insufficiency must be well-formed and uses
   unsupported_question only. A model-declared conflicting_evidence or no_evidence
   fails invalid_model_response: preflight would already have stopped on a verified
   material conflict, and model allegations cannot establish one. Reviewed negative
   conflicting_evidence aliases require exact matching current source rules; they are
   application decisions with zero model attempts, not model verdicts.

Exact rendering restricts paraphrase variety; approved different question paraphrases
can still produce genuine model-generated answers. No same-output determinism or
semantic accuracy claim follows from greedy sampling or schema-valid output.

## Output and error semantics

AnswerResult version3 required fields: request_id/run_id lower-case UUID, op answer/null,
status, use_case_id/configuration nullable, elapsed_ms, retrieval_searches,
generation_attempts, claims, citations, reason, error. No raw question/model/vector.
Configuration includes mode deterministic/local_live, F2 settings, proposed generation
identity/config and fixed operating ceilings. Until validated settings exist it is null.
Never report live model use if an injected fake supplied the response. In deterministic
mode the model/config fields identify the simulated target, not an observed loaded
model; local_live requires actual verified asset/config identities.

answered:1–5 claims, all cited; reason/error null. Citations are unchanged F2
EvidencePassage objects, deduplicated by chunk_id and only from this request.
insufficient_evidence: empty claims/citations; reason no_evidence|unsupported_question|
conflicting_evidence; error null. rejected/failed: empty claims/citations; reason null;
error fixed code==message. Counts are actual attempted searches/generate invocations,
not task completions; integer0–1 excluding bool. F2 causes propagate via error
retrieval_failed and safe cause_code from F2 enum; no raw exception.

Other errors: invalid_input, unknown_operation, unknown_use_case, question_too_long,
configuration_mismatch, catalog_mismatch, context_too_large, model_unavailable,
generation_failed, invalid_model_response, invalid_citation, grounding_failed,
output_too_large, deadline_exceeded, session_unavailable. Rejected categories are
input/op/scope/question/session unavailable; all others failed. No partial output.
Schema plus semantic validation enforce counts/lengths, equality, UUID/date validity,
finite numbers, UTF8 byte limits, approved provenance and actual decisions.

## Generation and hard ceilings

Propose SmolLM2-360M-Instruct revision a10cc1512eabd3dde888204e902eca88bddb4951.
GenerationAssetManifest binds model ID/revision and relative allowlisted filenames /
SHA256: config.json, model.safetensors, tokenizer.json, tokenizer_config.json,
special_tokens_map.json and generation_config.json when actually needed. No symlink,
path traversal, unlisted file use, weights pickle/custom code or training artifacts.
Freeze effective chat template, EOS/pad IDs and configuration fingerprint; referenced
files must exist and hash-match. Use CPU FP32, local-files-only, no remote code/token,
no custom hooks, batch1, greedy, beams1, threads4/interop1. No new runtime dependency.

Prompt<=64KiB before tokenization, <=2,048 generation tokens after chat template;
completion<=384new tokens and<=16KiB decoded bytes. Verify model context supports
prompt plus reserved output<=8,192; never truncate question/evidence to fit. Require
legitimate reviewed EOS; reaching token cap without stop fails output_too_large.
Slice away prompt token IDs before decode; parse exactly one JSON value with no trailing
prose. No substring JSON extraction/repair/second call. Unicode/whitespace costs,
template expansion and EOS identity must be tested against approved local assets.

Runner cgroup hard memory8GiB including supervisor/session/model descendants,4CPUs;
Qdrant hard memory1GiB,256MiB index tmpfs; runner tmpfs64MiB. These are enforcement
ceilings, not measured need. All workers remain in the runner cgroup and owned
process group; no child escape. OOM/unconfirmed stop is fatal. No periodic RSS check
claimed as hard limit, no swap-dependent growth, no automatic enlargement. Docker
capacity probe/build/mount/cgroup verification require actual authorization.

Original request240seconds. F2 stage max120 incl inventory10/query90/search10; each
stage is capped by remaining original deadline. Post-retrieval support/validation plus
final serialization max10 aggregate. Generation110 includes fresh hash/load, template,
tokenization, decode/transfer and reserved worker stop5 (TERM2/KILL3). Every substage
uses min(stage remaining, total remaining). Startup120 is separate from per-request.
Supervised parent enforces wall deadlines; model max_time/socket inactivity do not.

## Process ownership, shutdown and session exit

Parent outside owned session process group; factory/dispatcher and every query/
generation/storage descendant inside. Record ownership before READY. Strict framed
JSON IPC max16MiB/message/64KiB frame, lengths checked before allocation; bounded
cumulative assembly and remaining-time reads/writes. Delegated F1/F2 envelopes keep
shape inside this F3-only transport ceiling. AnswerResult additionally capped128KiB;
cap before stdout emission. No pickle or raw prompt/model diagnostics.

Fatal session/worker exit, stalled/broken IPC, unconfirmed termination or ownership
mismatch stops input; invalidate readiness and cleanup exact recorded group even when
leader died. Verify descendants and owned container/network absence independently.
Protect against reused identity; unknown residue is failure, never a global signal/prune.
One45-second teardown: group5 (TERM2/KILL3), collection10, Docker30. No repeated-signal
reset. Nonfatal failure sets eventual exit1; rejected/insufficient alone exit0; interrupt
exit130; cleanup uncertainty nonzero. EOF/close disposes run. No reopen/resume.

F3 outer dispatcher lock serializes every delegated operation across the entire
answer. Inside it F2 acquires/releases its existing busy guard normally; after retrieval
F3 holds the same service busy flag during grounding/generation/output. No callback,
mutation entry point or concurrent thread can enter during the handoff. Check registry
generation before output. Do not call F2 while its busy flag is already owned by F3.

## Evaluation cases and consumer

EvaluationCaseSet version3 has case_set_id, manifest/catalog/generation-config/case
fingerprints and actual review attribution, with <=128 closed cases. Cases bind exact
scope/question, expected_status answered|insufficient_evidence, expected_claim_ids,
expected_reason and acceptable_source_ids. Positive expects1–5 known claims/null
reason; negative empty claim IDs/non-null reason. Require >=3 positives and>=2 negatives
including shipping, no duplicate IDs, frozen expectations before execution. Case-set JSON<=1MiB, generation asset manifest<=64KiB, F3 receipt<=16KiB; enforce
bounded reads before allocation. Asset manifest file paths must be unique. Case-set
file SHA256 is computed externally (not a self-referential field); schema uses no
self hash. Bind catalog/model/retrieval configuration and manifest before execution.

Proposed evaluation.py consumes ready service and approved cases, calls normal answer
once per case, records case_id and actual AnswerResult without tuning. Wrapper
--evaluation-cases requires ingest-only stdin until EOF; after all successful approved
ingest requests, run selected frozen cases sequentially and always teardown. Ingestion
failure prevents evaluation. Missing/extra claim, wrong reason, failed/rejected,
invalid citation or unsupported claim fails case. Do not feed expected claims into
model as evaluation data or count catalog lookup as live generation. Capture only at
separately approved evidence location with access/expiry/deletion established.

## Internal F2 integration port (not a new public envelope)

Proposed library signature:
`retrieve_with_receipt(request, *, request_started_at, deadline) -> RetrievalReceipt`.
F3 supplies its original monotonic start/deadline; F2 computes its effective deadline
as min(supplied deadline, request_started_at+120), applies existing stage ceilings and
runs the exact existing validation/inventory/encode/single-search pipeline once.
F2 public retrieve continues to use that same pipeline and returns only its unchanged
RetrievalResult; F3 uses the internal receipt. Never perform a second retrieval,
mutating inspect, snapshot reconstruction from top_k or additional storage read.

Receipt contains result (unchanged F2 RetrievalResult), scope_snapshot nullable,
retrieval_searches integer0–1 and retrieval_deadline monotonic numeric. Snapshot is
immutable/request-memory only: exact use_case_id, registry_fingerprint SHA256 and
represented_sources of source_id/revision/content_sha256 for every represented
complete current source state, including zero-chunk represented states. Sources
never ingested/fully removed are absent. Include no text/vector/full candidates.
F3's catalog ceiling allows<=32 represented source bindings; excess fails closed
catalog_mismatch without truncation. This cap belongs only to the F3 consumer:
F2 public retrieval never validates against the F3 receipt schema or gains a new
source-count cap. F3 startup verifies its catalog covers the approved manifest within
its own32-rule limit; runtime scope inconsistency fails closed. Duplicate/missing/foreign
bindings fail validation.

The query dispatch counter increments immediately before the sole Qdrant query send,
including a send that times out or fails. Inventory reads are not evidence-search
attempts. Empty verified scope or failure before query has count0; failure after
query dispatch has count1. Failed/rejected result may have null snapshot; successful
matched/no_match requires a complete verified snapshot. Missing required receipt,
unknown counter or invalid snapshot fails configuration_mismatch, never guesses counts.
Fatal loss of transport makes the session unavailable and cleanup takes precedence
rather than fabricating a delivered request record. Compare registry_fingerprint
before output under the existing outer lock/guard, without fetching new evidence.

The internal bridge belongs in the future F2 service/index integration, requires
explicit implementation dispositions and unchanged F2 regressions. F2 artifacts and
code are not changed by this F3 documentation remediation. T041 must verify actual
port compatibility before real F3 composition; injected receipts are not integration proof.

## Final output delivery and backpressure

Serialize a complete bounded line before delivery; retain at most one output message
(max16MiB for delegated envelopes, max128KiB for AnswerResult). Parent stdout writes
and wrapper forwarding use nonblocking file descriptors, bounded partial-write loops
and readiness waits capped by the remaining original operation deadline. Answer
serialization and delivery share the10-second aggregate validation budget and240-second
original request ceiling. Delegated F1/F2 operations retain their applicable original
operation deadlines; F3 adds no new budget by forwarding their output. Startup/control
markers use remaining startup/teardown time. Never use an unbounded blocking flush,
queue, thread join or synchronous pipe write. The wrapper tracks deadline metadata on
its private supervisor control channel; it does not add fields to public envelopes.

Blocked stdout deadline, closed consumer or broken pipe stops input and is fatal.
Do not try to emit an error on the same failed channel. A partially transmitted JSONL
line is incomplete and must never be accepted as a result; receiver discards it at EOF.
No protocol promises atomic multi-byte pipe writes or delivered JSON after consumer
failure. Internal outcome is undelivered/nonzero exit, safe stderr marker only when
that channel is independently writable within remaining time. Cleanup always proceeds
under its own original45-second deadline without waiting on stdout/stderr. Wrapper
must terminate/verify the recorded CLI parent and owned group even when the parent is
stuck; ownership checks protect unrelated processes. No repeated-signal reset.
