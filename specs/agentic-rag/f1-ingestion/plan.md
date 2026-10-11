# F1 ingestion implementation plan

Status: **Complete for approved F1 scope; local gates passed**. Date: 2026-10-02.
Actual git branch: `reconciled-governance-starter` (preserved).
Spec Kit feature identifier: `f1-ingestion` (setup script fallback, not a git branch).
Spec: [F1](spec.md). Roadmap: [learning ladder](../roadmap.md).

## Input and approval

The user requested `$speckit-plan F1` and answered **“use temporary/local”** on
2026-10-02. D1 means temporary demo indexing cleared at demo end; D2 means local
embedding computation without document-text transfer to a hosted provider. These
are planning decisions, not corpus approval, package installation, or implementation
approval. The [spec checklist](checklists/requirements.md) records the distinction.

The user subsequently requested `$speckit-implement F1` and explicitly stated on
2026-10-02: **“I've approved the requirements.”** These are requirements approval and
implementation intent, separate from corpus/model/package acquisition and publication.
Readiness gaps were reconciled. The user renewed `$speckit-implement F1` on 2026-10-02;
T002/T003 proposals were subsequently explicitly approved: “I approve. Proceed.”
The approval and actual acquisition records are in tasks.md; current checks are in
[validation.md](validation.md).

Stage 2 appends ingestion and inspection only. Stage 1's source catalog, fixtures,
health readiness, exact IDs/order, JSON/OpenAPI, and HTTP 404 with exactly
`{"detail":{"code":"unknown_use_case"}}` remain unchanged. Inspect `app/main.py`,
`app/sample_data.py`, `tests/test_sources.py`, `pyproject.toml`, `compose.yaml`, and
`scripts/ci-local.sh` before implementation. These paths were reviewed in the F0 audit.

### Technical context

- Existing runtime: Python 3.10+ / FastAPI; current venv Python 3.10.10. Preserve it.
- Live F1 runtime: local Linux CPU container, Python 3.12; no hosted embedding API.
- Proposed live-only dependencies: `sentence-transformers==6.1.0`,
  `qdrant-client==1.19.1`; Qdrant server `qdrant/qdrant:v1.19.1`.
  Resolve/review transitive locks and image digests in the separately authorized build;
  version availability is documented, installation/compatibility is not verified.
- Proposed model: reviewed local snapshot of `sentence-transformers/all-MiniLM-L6-v2`,
  384 dimensions, cosine distance. Record actual snapshot commit and file hashes at
  authorized acquisition; missing or mismatched assets fail closed, not auto-download.
- Storage: dedicated Qdrant Compose service; tmpfs at `/qdrant/storage` capped at
  **256 MiB (268,435,456 bytes)**, with mount option `size=268435456`;
  no named persistent volume. This deliberately departs from the runbook's named-volume
  proposal to implement the user's temporary-index decision. Validate tmpfs on Docker
  Desktop; if unavailable, report failure instead of silently persisting data on disk.
  This is a proposed filesystem capacity for the small learning corpus, not measured
  sufficiency or a cap on total container/model RAM. Verify the actual mount limit
  before accepting input. Reject startup if the limit cannot be verified. Exhaustion
  during mutation/read-back returns `incomplete` with `index_failed`, `ready: false`,
  and unknown counts as null; do not auto-resize, retry, or fall back to disk. An
  operator may clear approved scopes or close and start a fresh approved run before
  explicit retry. Failed cleanup remains visible and requires isolated stack teardown.
- Interfaces: local JSON-lines CLI session, not new HTTP routes. Storage is reachable
  only on the dedicated Compose network; the runner has no published port. Runtime
  accepts only the literal `http://qdrant:6333` service URL, validated before any
  client construction, connection, or source processing. The runner and Qdrant join
  only their isolated Compose network with `internal: true`; no host networking,
  additional network, endpoint fallback, proxy use, or HTTP redirect following.
  The wrapper verifies that the Qdrant service belongs to its recorded project.
  Downloads/builds occur separately under their approvals, never inside the runtime.
- Testing: existing pytest/Ruff; injected tokenizer/embedder/index fakes for deterministic
  native tests, plus a separately labeled local live container demonstration.
- Scope: sequential approved plain-text documents across two synthetic use cases.
  No source fixtures or approval records are created by this planning command.
- Proposed operating limits: 64 KiB UTF-8 text per source; at most 2,048 chunks per
  source; 120 seconds per ingestion including embedding/index operations; individual
  storage requests capped at 10 seconds or remaining deadline, whichever is shorter.
  No automatic retry; operator-triggered retry is explicit and idempotent. These are
  design limits for review, not measured latency targets. Cleanup has a 10-second
  request cap within a 10-second total collection-cleanup budget; unsuccessful cleanup
  is visible and blocks a success report. Final teardown has a 45-second total budget:
  worker shutdown <=5 seconds, collection cleanup <=10 seconds, owned Docker teardown
  <=30 seconds. See the contract's bounded shutdown policy; phase caps share remaining
  overall time and do not restart on additional signals or errors.

### Constitution check — before research and after design

Authority remains [docs/constitution.md](../../../docs/constitution.md), v1.0.0.
The unfilled Spec Kit scaffold was inspected and supplies no active project values.
The project-owned plan template controls this document under AGENTS.md; setup's
resolved tool template was read, then adapted without changing its versioned source.

| Principle / gate | Design evidence | Result |
| --- | --- | --- |
| Intent and human authority (1, 4, 10) | D1/D2 recorded; design only; separate corpus, dependency, execution, and publication gates | Satisfied for planning |
| Evidence and untrusted documents (2, 3) | Source revisions/offsets, inspectable chunks; text cannot execute or change permissions | Satisfied for design |
| Least privilege and memory (5, 6) | Local operator, approved digests, scoped operations, temporary storage; memory disabled | Satisfied for design |
| Testability and simplicity (7, 8) | CLI ingestion/inspection, narrow adapters, no agents/generation; AC mapping below | Satisfied for design |
| Observability (9) | IDs/status/counts and timing; no raw-text telemetry or secrets; inspection is explicit | Satisfied for design |
| Preserve Stage 1 | Existing files/contracts retained; F1 adapters never loaded by R1 requests | Satisfied for design; fresh regression evidence in validation.md |
| Local-only checks | No GitHub Actions or Docker Hub automated builds; release excluded | Satisfied for design |

No governance exception or principle removal is proposed. Corpus/model acquisition,
installation, live checks, and implementation remain gated; this is not a runtime
compliance claim. Phase 0 decisions are in [research.md](research.md); Phase 1 entities,
interfaces, and validation are in [data-model.md](data-model.md),
[contracts/ingestion-cli.md](contracts/ingestion-cli.md), and [quickstart.md](quickstart.md).
The proposed serialized manifest/request/result shapes are defined in the project-owned
[JSON Schema](contracts/serialization.schema.json); the CLI contract supplies its
cross-field, authorization, and lifecycle rules. Schema validation grants no approval.

## Approach

### Components and data flow

Run `python -m app.ingestion session` in a dedicated local runner. It receives a
read-only approval manifest/model directory and sequential operations on stdin.
The manifest binds each permitted exact use-case/source/revision tuple to a content
SHA-256, classification, access/redistribution scope, and a real human approval record.
A caller flag alone cannot assert approval. The runner validates the manifest and
content before tokenization or embedding; the plan does not manufacture that record.

A tokenizer-based chunker makes original-text slices of at most 200 content wordpieces
with 20-wordpiece overlap and character offsets. It re-tokenizes each actual slice
with special tokens, without truncation, and requires it to fit the loaded model's
256-token limit. Adjust slice boundaries or reject rather than truncate silently;
cover all non-whitespace source content, including trailing content. Chunk configuration
and tokenizer/model identities participate in deterministic UUIDv5 identities.

The embedding adapter loads only the reviewed local model directory with CPU execution,
`local_files_only=True`, `trust_remote_code=False`, and offline hub mode. It validates
384 finite vector values and rejects zero-norm/incompatible vectors. Run embedding in
an interruptible worker process; the parent enforces the ingestion deadline and can
terminate the worker. Do not rely on a non-cancellable background thread for timeout.

The index adapter handles scoped Qdrant operations. Each runner session owns a fresh
collection named `f1_<run_uuid>` and an in-memory source-state registry. Source identity
is `(use_case_id, source_id)`, revision is the current approved revision, and every
inspection or mutation carries both exact scope fields when operating on a source.
No caller may choose an arbitrary collection name. Whole-run cleanup is confined to
that runner-owned collection; no database-wide purge or development-volume deletion.

Validate and compute the full desired set before mutation. Mark the source incomplete,
upsert desired UUIDs with completed writes, remove scoped obsolete UUIDs, then exhaust
scroll pagination and verify the exact final ID set, metadata, and vector dimensions.
Only then mark it complete. Input rejection returns `rejected` without changing the
prior source state. A preparation/embedding error, invalid vector, or controlled
embedding deadline returns attempt status `failed` without index mutation; prior
readiness remains unchanged (`unseen` for a new source). Expected deadline termination
of an embedding worker is recoverable; a later explicit retry uses a fresh worker.
Once mutation begins, any storage/write/read-back error or deadline returns attempt
status `incomplete` and marks the source incomplete, with unknown counts as null.
Operator retry recomputes and reconciles the full desired set. An unexpected worker
exit, broken worker protocol, or inability to terminate the worker is fatal: report
`failed`, stop accepting input, clean up the whole run, and exit nonzero. Recovery
then means a fresh run and approved re-ingestion, never resuming old readiness.
This is not an atomic transaction.
Inspection exposes incomplete state and cannot represent mixed records as ready evidence.
Future F2 must consume only complete-source inventories, not query Qdrant bypassing
that guard. Restart creates a new run/collection and invalidates earlier readiness;
resuming abandoned source state is outside F1.

`clear` deletes only a selected source's data (or exact use-case scope when source ID
is omitted), verifies absence, and removes matching registry state. Session close,
EOF, interrupts, and fatal worker failure trigger whole-run cleanup. Recoverable
preparation errors and expected deadline termination leave the session open for
explicit retry; they do not trigger whole-run deletion. The outer demo wrapper
attempts bounded stop/removal only of its dedicated Qdrant stack; verified removal
discards its tmpfs contents even if source cleanup failed. Report cleanup errors;
do not claim successful clearing on
uncertain deletion. SIGKILL/host failure can bypass traps: document recovery and do
not equate tmpfs with secure erasure or guaranteed cleanup under every failure.

### Implementation path manifest

This manifest defines the implemented scope; lifecycle.py and demo.py also provide
shared bounded teardown and owned-stack supervision.

| Disposition | Paths | Responsibility |
| --- | --- | --- |
| Create | `app/ingestion/types.py`, `validation.py`, `chunking.py` | Typed records, approval/input validation, provenance and deterministic chunking |
| Create | `app/ingestion/embedding.py`, `index.py`, `service.py` | Lazy live adapters, scoped storage operations, deadline/source-state orchestration |
| Create | `app/ingestion/__init__.py`, `__main__.py` | Local session interface; no automatic adapter import from Stage 1 |
| Create | `tests/test_ingestion.py`, `tests/test_ingestion_cli.py` | Deterministic AC tests and CLI failures/cleanup |
| Create after corpus approval | `tests/fixtures/f1/` | Approved synthetic corpus, replacement/isolation inputs and manifest |
| Create | `compose.f1.yaml`, `Dockerfile.f1`, `.dockerignore`, `scripts/f1-demo.sh` | Isolated live runner/storage; narrow context, no models/corpus/secrets baked into image |
| Update after dependency approval | `pyproject.toml`, `uv.lock` | Optional live extra/locked Linux CPU dependencies; preserve Stage 1 base dependencies |
| Update after implementation | `README.md` | Link local F1 validation and required cleanup |
| Preserve | `app/main.py`, `app/sample_data.py`, `tests/test_sources.py`, `compose.yaml`, `scripts/ci-local.sh`, `scripts/api_smoke.py` | Stage 1 contracts, environment and local gate |
| Preserve | `AGENTS.md`, `docs/constitution.md`, roadmap, existing feature artifacts | Authority and earlier scope |
| Omit | GitHub Actions, persistent memory/index, hosted provider, query/agent/tool routes, image publication | Outside F1 |

### Interfaces and isolation

Core service methods: `ingest(document: SourceDocument) -> IngestionResult`,
`inspect(use_case_id: str, source_id: str | None) -> InspectionResult`,
`clear(use_case_id: str, source_id: str | None) -> ClearResult`, and `close() -> CleanupResult`.
`Embedder.encode(chunks: list[Chunk], deadline: float) -> list[EmbeddedChunk]` and
`IndexStore.replace(scope: SourceScope, desired: list[EmbeddedChunk], deadline: float)`
are injected ports. Clock, tokenizer, approval manifest, and source registry are
injected too, making boundary tests independent of real models and storage services.

This is local application isolation, not multi-user authentication. Use one runner
at a time; reject parallel source updates. No generation model, memory, or tool registry
is loaded. No secret is read from environment files or credentials; runtime receives
explicit non-secret model/storage paths and read-only approved inputs.

### Alternatives and recovery

A new ingestion HTTP route adds authentication and API-contract questions with no
learning benefit yet; defer it. Embedded storage would avoid a service but diverge
from the guide's Compose boundary. A retained named volume violates the temporary
choice. Native Intel embedding installation risks an older PyTorch stack; use the
local Linux CPU runner, preserving native deterministic tests. See research sources.

Fail closed for missing approval/model assets and incompatible vector configuration.
Recover a failed replacement by explicit same-source retry or scoped clearing; a
fresh run re-ingests approved data. Recovery after lost application state requires
stopping the old dedicated stack, not trusting old records as complete.

## Verification

No implementation tests or live demonstrations run during planning. Future tests
must first fail behaviorally, then pass after the minimal implementation.

| Test cycle / deliverable | First failing assertions and boundary cases | AC coverage |
| --- | --- | --- |
| Validation/chunk records | Reject unapproved hash, whitespace, missing metadata, oversize text before adapter calls; preserve Unicode, full trailing content and stable IDs | AC-001/002/003/006 |
| Ingestion/replacement | Same input twice gives equal sets; shorter source/config change removes obsolete IDs; invalid vectors/preparation failure preserve prior readiness; injected storage outage after mutation leaves source incomplete; explicit retry converges | AC-001/003/005 |
| Inspection/isolation | Same source ID across two use cases does not collide; pagination exhausts all pages; exact scope filters required; incomplete records never report ready | AC-001/004/005 |
| Lifecycle and CLI | Scoped clear verifies zero records without changing neighbors; controlled worker timeout preserves pre-mutation readiness and permits fresh-worker retry; fatal worker failure stops input and cleans the run; EOF/interrupt cleanup; unknown op/malformed JSON produces controlled errors | AC-004/005/006 |
| Local endpoint boundary | Reject nonliteral URLs, credentials, alternate ports/paths, redirects, proxies and endpoint fallback before text transfer; verify only the dedicated internal network is attached | AC-006 |
| Serialization and capacity | Missing/unknown fields, invalid types/enums/nulls and conflicting approval tuples fail closed; capacity errors never report ready or resize/fall back; actual tmpfs mount limit is verified separately | AC-002/005/006 |
| Regression and live proof | Native R1 suite unchanged; real offline CPU vectors/index inspection labeled live; cleanup failure reported; no text/provider transfer | AC-007/008 |

Review focus: tokenizer truncation at boundaries; partial writes with uncertain timeout;
final scroll page skipped; collection cleanup outside owned scope; offline loading
silently fetching assets. Each has explicit tests in the corresponding cycle above.

Local commands after implementation: `.venv/bin/python -m pytest`,
`.venv/bin/python -m ruff check .`, the existing `bash scripts/ci-local.sh`, and the
`bash scripts/f1-demo.sh` under its documented approvals. Record actual revision,
commands, exit status, warnings, dependency/model hashes, fixture revision, inspected
IDs/counts, and cleanup results. No remotely triggered build or quality gate.

The full fresh Stage 1 Docker gate remains a prerequisite for integrated acceptance.
The live runner must pass import/one-vector/container-storage checks before
claiming Intel-host/Linux-container compatibility. F1 does not evaluate retrieval or
answer quality. Legal rights and publication approvals are not granted here.

## Open decisions

D1/D2 user decisions are resolved; no unresolved design choice remains in Phase 0.
The following are execution prerequisites, not inferred approvals:

| Gate | Decision owner | Needed before | Status |
| --- | --- | --- | --- |
| Requirements approval / readiness reconciliation | User / human reviewer | Requirements gate / implementation | User approval recorded above; current document remediation addresses CHK012/031/032; no runtime result inferred |
| Corpus owner/classification/access/redistribution and exact approved digests | Corpus owner/human reviewer | Creating/ingesting corpus | Approved exact synthetic fixtures; real manifest in tests/fixtures/f1/approval.json |
| Package/model acquisition, exact model snapshot/hash and resolved dependency lock | Human reviewer/operator | Downloads/install/build | Specifically approved; actual hashes/locks/digests in tasks.md |
| Platform compatibility/tmpfs/dependency checks | Implementer with authorized local environment | Live acceptance | See actual local checks in validation.md |
| Implementation intent | User | Implementation | Renewed `$speckit-implement F1` recorded; T002/T003 explicitly approved; implementation authorization is not missing |
| F0 full local gate | Human reviewer / local operator | F0 acceptance / integrated F1 acceptance | Fresh full Docker gate recorded in validation.md |
| External release/legal/registry decisions | Human release reviewer | Any publication | Deferred outside F1 |

[tasks.md](tasks.md) exists and was reconciled after cross-artifact analysis. The
requirements review and the separate source/acquisition/build decisions are approved.
Implementation follows the task ledger; final acceptance is supported only by actual
checks in [validation.md](validation.md). Checklist criteria are preserved.
