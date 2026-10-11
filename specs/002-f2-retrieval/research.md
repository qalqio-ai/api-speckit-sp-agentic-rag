# F2 research decisions

Date: 2026-10-02. Read-only repository inspection and two research agents under the
explicit speckit-plan research workflow; official public documentation consulted.
No runtime evaluation, source upload, installation or new model acquisition occurred.

## R1 — Interface and integration

**Decision**: Separate local `app.retrieval` session composing F1 Service/Index and
unchanged ingest/inspect/clear/close protocol. No new HTTP route.
**Rationale**: F1 strict schema rejects new operations; readiness is process memory,
so querying a separate reopened session cannot establish current ready evidence.
**Alternatives considered**: Extend F1 schema (breaks its closed protocol); HTTP route
(adds startup/readiness/access concerns); reopen collection (loses readiness/ownership).
Evidence: `app/ingestion/__main__.py`, `service.py` and the F1 serialization contract.

## R2 — Compatible offline question processing

**Decision**: Preserve F1 generic encode and exact reviewed MiniLM snapshot/config;
check absence of prompts/default prompt/router specialization. Tokenize without
truncation including special tokens; reject over 256 tokens before encode. Hash-check
assets in each fresh supervised query worker; CPU, local-files-only, no remote code.
**Rationale**: Bytes do not bound tokens and default model encoding can truncate.
Query/document methods can introduce distinct prompts/tasks on other models; generic
encode preserves this repository's existing document-processing identity.
**Alternatives considered**: Blind encode_query migration, truncation, new model/provider
or native dependency installation; all add incompatibility or unauthorized scope.
Primary sources: [Sentence Transformers usage](https://www.sbert.net/docs/sentence_transformer/usage/usage.html),
[model reference](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html),
[MiniLM card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2),
[tokenizer controls](https://huggingface.co/docs/transformers/main_classes/tokenizer).
Documentation informs the design; locked-runtime compatibility still needs an actual probe.

## R3 — One exact bounded search and deterministic ties

**Decision**: Qdrant POST `/collections/{owned}/points/query`, dense 384-vector,
`params.exact=true`, mandatory scalar use-case match plus source/ID allowlists,
`limit=N` for every verified scope passage; payload on, vectors off. No prefetch,
lookup, retry, offset or server threshold. Application filters inclusively, sorts
all scores descending with chunk-ID ties, then slices user k.
**Rationale**: This is a design inference: fetching server top-k alone cannot enforce
an application identity tie-break on omitted tied candidates. Full N avoids cutoff
ambiguity while preserving one search. Local `>=` defines equality explicitly.
**Alternatives considered**: Approximate top-k, fixed overfetch or an extra search
for tied candidates; these do not satisfy the specified stable ties/one-search boundary.
Primary sources: [Query API](https://api.qdrant.tech/api-reference/search/query-points),
[search and exact search](https://qdrant.tech/documentation/search/search/),
[filter semantics](https://qdrant.tech/documentation/search/filtering/).
Current API docs were readable; version-specific 1.19 reference was not. Exercise
the exact request/response on the pinned 1.19.1 image during implementation; no server
compatibility test has run here. Existing transport unwraps `result`, so adapter sees
`{points:[...]}`. Require all expected IDs; omitted/duplicate/foreign/malformed rows fail.

## R4 — Bound the whole scope, verify readiness without mutations

**Decision**: Cap selected scope at 2,048 total passages; refuse over-cap without
truncation. Exhaustive read-only scoped inventory under one 10-second stage budget,
then compare F1 complete-state IDs/counts/payload hashes and compatible configuration.
**Rationale**: F1's 2,048 bound is per source, not per use case. Calling F1 inspect
would allocate a fresh deadline and mutate readiness on mismatch. Independent
verification can fail closed while preserving read-only state, except required fatal-stop.
**Alternatives considered**: Assume scope bounded by source bound; silently drop sources;
trust query acknowledgments or stale state alone; all violate evidence/limit requirements.
The 16 MiB F1 transport limit stays in place, even if it rejects an otherwise under-cap
inventory. Caps are operating ceilings, not promises to fit every corpus.

## R5 — Deadline, lifecycle and packaging

**Decision**: 120-second retrieval budget; aggregate inventory 10, query worker 90,
search 10, all <=remaining total; worker TERM2/KILL3 reserved inside stages. Separate
F2 image/Compose/wrapper uses same pinned stack, tmpfs and ownership policy, preserving
45-second teardown and no runtime builds/pulls. Supervise startup preflight too.
**Rationale**: F1 uses cold model workers; an arbitrary short warm-only latency goal
would not fit this architecture. Existing synchronous startup must not become an
unbounded F2 query/startup path. No measured latency or compatibility result is claimed.
**Alternatives considered**: Persistent worker, native install, shared F1 image tag or
relaxing internal network; more lifecycle risk or changes to preserved behavior.

## R6 — Calibration and execution permissions

**Decision**: No built-in relevance threshold; require finite `--min-score` in [-1,1]
for normal retrieval/held-out; internal calibration has no threshold.
Use distinct reviewed calibration/held-out sets and freeze corpus/configuration/threshold.
Try a separator between unsupported maximum and supported expected-source minimum
only if calibration scores separate. Nonseparation is reported as failure, not guessed
quality. Real source-use receipt required independently of manifest schema validity.
**Rationale**: No model score establishes relevance universally. Existing F1 fixtures
lack competing sources within one scope and cannot establish SC-001/004. This phase
can choose protocol and calibration method, but cannot create empirical results or consent.
**Alternatives considered**: Arbitrary 0.5 default, tuning on held-out questions or
claiming useful ranking from one source; all provide misleading acceptance evidence.
Proposed corpus follows the roadmap learning scenario (product/return/troubleshooting
and a second isolation corpus), but exact text/hash/reviewer approval is a future gate.

## Resolution ledger

All technical unknowns identified at setup are resolved as proposed decisions R1–R6:
interface, compatible processing, exact/tied ranking, total scope limits, lifecycle,
packaging and calibration method. Numeric calibrated scores, real approvals and live
results are unavailable execution evidence, explicitly pending in the plan; they
are not replaced by placeholders or claimed as completed research.

## R5/R6 remediation detail

The parent supervisor is outside the owned session process group; session and all
query/storage descendants stay inside it. Leader death requires whole-group cleanup
and independent absence verification, not merely joining the leader. Strict bounded
JSON IPC (16 MiB/message,64 KiB/frame) uses remaining-time reads/writes; all failures
share the original45-second teardown. See CLI contract for ownership and signals.

Normal retrieval still requires --min-score. Separate calibration evaluation has no
threshold: its internal shared pipeline examines complete validated candidates before
filtering/top_k with one search/case. Best expected-source full rank must be <=3;
missing/empty candidates or nonseparation fail. Closed EvaluationCaseSet schema and
ready-session evaluate_cases consumer bind real reviewed cases to manifest/config
fingerprints. Held-out uses frozen normal top_k3 retrieval. These are proposed design
resolutions, not empirical measurements, actual approvals or runtime evidence.
