# Implementation Plan: F2 — Retrieve scoped evidence

**Branch**: `reconciled-governance-starter` | **Date**: 2026-10-02 | **Spec**: [F2](spec.md)
**Setup feature identifier**: `002-f2-retrieval`; setup's BRANCH value is a feature
identifier, not proof of a Git branch switch.
**Status**: Phase 0 research and Phase 1 design complete; proposed implementation,
not approved execution. `$speckit-plan F2` authorizes planning of the written spec.
No requirements approval, source permission or implementation approval is invented.

## Summary

Compose a separate local F2 JSONL session around the existing F1 ingestion service.
Verify the entire selected ready scope, encode one question offline with the same
MiniLM snapshot, issue one exact scoped Qdrant query for all bounded candidates,
validate each candidate, filter inclusively by the explicit minimum score, sort by
score then chunk identity, and expose at most the user's requested number of passages.
No HTTP route or Stage 1 change; no generated answers or autonomous actions.

Research decisions and alternatives are in [research.md](research.md). Serialized
contracts and semantic rules are in [retrieval CLI](contracts/retrieval-cli.md) and
[serialization schema](contracts/serialization.schema.json). No tasks are generated here.

## Technical Context

**Language/Version**: Native Python 3.10+ deterministic checks; dedicated Linux
Python 3.12 CPU runner, preserving the native Stage 1 environment.
**Primary Dependencies**: Existing hash-locked F1 stack: sentence-transformers 6.1.0,
transformers 5.18.0, Torch CPU and HTTPX; existing Qdrant 1.19.1 pinned server image.
No package/version change is proposed. Verify locked API compatibility during implementation.
**Storage**: Fresh runner-owned `f1_<run_uuid>` Qdrant collection, Cosine/384,
verified 256 MiB tmpfs; in-process F1 readiness registry; no restart resume or new persistence.
**Testing**: pytest, deterministic tokenizer/embedder/index/clock seams, CLI contract
checks; separate approved real semantic and integrated Docker checks.
**Target Platform**: Existing Intel macOS host with Docker Desktop; Linux CPU live runner.
**Project Type**: Local CLI/library composition; single sequential operator.
**Performance Goals**: Bounded completion/failure, not a measured speed promise:
120 seconds/request; inventory verification at most 10 seconds total; query encoding
at most 90 seconds including cold load and worker stop; one search at most 10 seconds.
Each stage is also capped by the original remaining total deadline. Final validation
and serialization must complete inside it. Reserve worker TERM/KILL within stage budgets.
**Constraints**: Question <=4,096 UTF-8 bytes AND <=256 tokens with special tokens;
limit default 3, integer 1–10; selected scope <=2,048 total passages. Refuse over-cap
scope, do not truncate it. REST responses <=16 MiB, inherited from F1.
**Scale/Scope**: Synthetic demo only. One exact search, no retries/refinement;
zero tools, generation, hosted processing, memory or corpus changes during retrieval.
The bounded full-scope query is deliberately unsuitable for large production corpora.

## Constitution Check

Authority is [docs/constitution.md](../../docs/constitution.md), not the untouched
placeholder under `.specify/memory`. Both were inspected. Exactly one active authority
is retained; no tool-policy migration or new constitution is part of F2.

| Principle | Pre-research design gate | Post-design gate |
| --- | --- | --- |
| 1 User intent | F2 outcomes/scope specified; planning explicitly requested | Local evidence-only interface and reviewable limits defined |
| 2 Evidence | Preserve F1 approved provenance; no answers | Full inventory/candidate verification; no fabricated locations |
| 3 Untrusted content | Document/question instructions have no authority | Typed request; fixed filter/settings; no tool or model-decision loop |
| 4 Human authority | Source/build/release decisions remain human gates | No execution/approval inferred from planning |
| 5 Least privilege | Local owned collection; synthetic sources only | Internal network, read-only assets, scoped filter and demo-end cleanup |
| 6 Memory | No persistent memory or new trace retention | Registry/process state only; artifact retention separate approval |
| 7 Testability | Behavioral tests before implementation | Contract, isolation, ties, deadlines and held-out live criteria mapped |
| 8 Simplicity | Reuse F1; avoid new HTTP/auth/provider concerns | One exact dense search; no reranker/hybrid search |
| 9 Telemetry | No raw question/text diagnostic logs | Safe result metadata; explicit operator evidence only |
| 10 Reviewability | Preserve work; preview dispositions | Six design artifacts, explicit gates, actual validation record |

Result: planning gates pass, no constitutional exception requested. Execution gates
below are pending actual human decisions; they do not block producing a proposal.
No unresolved technical clarification remains after Phase 0; empirical calibration
and permissions are explicitly future execution evidence, not fabricated research results.

## Project Structure

### Documentation (this feature)

```text
specs/002-f2-retrieval/
  spec.md
  plan.md
  research.md
  data-model.md
  quickstart.md
  checklists/requirements.md
  contracts/retrieval-cli.md
  contracts/serialization.schema.json
```

`tasks.md` is a later `$speckit-tasks` artifact and is not created by this command.

### Source Code (proposed, not created)

```text
app/retrieval/
  __init__.py
  __main__.py          # independent JSONL dispatcher, composed F1 service
  validation.py        # F2 schema/semantics; F1 validator remains intact
  embedding.py         # supervised query tokenizer/encoder, no truncation
  index.py             # bounded inventory verification and one exact search
  service.py           # read-only request lifecycle and result envelope
  evaluation.py        # approved case consumer; shared full-candidate calibration
  demo.py              # owned F2 stack supervision
scripts/f2-demo.sh
Dockerfile.f2
compose.f2.yaml
tests/test_retrieval.py
tests/test_retrieval_cli.py
tests/fixtures/f2/    # only after exact-source approval
```

**Structure Decision**: F2 owns its request/results and supervised query worker.
It instantiates F1 Service/Index in the same process and delegates approved ingest,
inspect, clear and close unchanged. A second process cannot recover F1's in-memory
ready registry. F2 wrapper follows existing ownership/mount/network/45-second teardown
logic, but selects the F2 CLI and its own image; no F1 wrapper behavior is changed.

## Input, disposition and approvals

| Disposition | Paths | Rationale |
| --- | --- | --- |
| Create now | This plan, research, data model, quickstart and two contracts | Authorized Phase 0/1 design |
| Create after implementation review | Proposed `app/retrieval/`, tests, Dockerfile/Compose/wrapper | Retrieval functionality isolated from F1 |
| Create after source approval | `tests/fixtures/f2/`, exact manifest and F2 reuse receipt | No invented consent or new corpus now |
| Update after implementation | `.dockerignore`, README navigation | Permit only F2 Dockerfile/schema build inputs; document interface |
| Preserve | All `app/ingestion/`, F1 schemas/tests/fixtures/wrapper/Compose/Dockerfile/locks | F1 strict protocol and offline behavior unchanged |
| Preserve | Stage 1 app/data/tests/Compose/local gate, native venv, governance/checklists | Stable API and sole constitution |
| Omit | New HTTP routes, package upgrades, downloads, hosted processing, persistence, publication | Outside authorized design |

No secret/environment-file read, acquisition, install, runtime corpus processing,
Docker action, commit, push or publication occurs during planning. Read-only research
accessed public official technical documentation only.

## Approach and integration

1. Startup validates F1 manifest plus a separate real F2 source-use decision receipt
   binding its exact manifest SHA-256, and explicit `--min-score` for normal retrieval
   or held-out evaluation (calibration mode has no threshold). Approval shape is
   not actual permission. An optional calibration identifier is provenance, not approval.
2. A dedicated F2 factory uses the same verified immutable model and F1 configuration.
   The F2 CLI supervisor starts the factory and dispatcher together in an owned
   session worker. Its model/tokenizer startup has a 120-second wall deadline before
   READY; the loaded tokenizer stays with F1 Service in that worker. This avoids
   copying live model objects or loading again in an unsupervised parent. The wrapper
   also bounds startup and verifies worker/service stop on timeout.
3. Sequential dispatch rejects concurrent/reentrant operations. Retrieval holds the
   shared F1 `busy` guard; delegates set/clear that guard according to F1 semantics.
4. Validate question bytes/type/limit/scope before question processing. Snapshot F1
   source states without calling `Service.inspect`, which mutates readiness and
   creates its own deadline. Any represented non-ready source causes readiness failure.
5. Exhaustively read only approved source IDs in the exact use case, under one
   10-second inventory deadline; stop accumulation at 2,049 rows and fail over-cap.
   Compare expected IDs/counts/payload hashes/configuration, strict record shape and
   finite nonzero vectors. Allow approved but never-ingested sources to be absent;
   unexpected stored rows without complete state fail. Empty verified inventory is
   eligible for `no_match` after question token-length validation.
6. Supervised query worker verifies hashes, loads local CPU model, asserts dimension,
   max length and no effective prompts/router specialization, tokenizes untruncated
   with specials, rejects >256 tokens before encode, and uses F1-compatible generic
   encode. For empty inventory use validation-only worker mode: verify question
   token length, then return `no_match` without semantic encoding or search.
7. One exact query uses use-case match AND allowed source IDs AND verified passage IDs.
   Request limit is verified scope size N, no server threshold/prefetch/offset;
   include payload, omit vectors. Require exactly the expected ID set in the response.
8. Validate every candidate payload against the verified snapshot, reject malformed,
   duplicate, foreign or stale results; apply `score >= min_score`, sort by
   `(-score, canonical_chunk_id)`, take user k, and emit verified payload plus rank/score.
9. Failures expose zero passages. Nonfatal read-only failures preserve source readiness;
   fatal worker/stop failures follow F1 session invalidation and owned cleanup. This
   existing fatal transition is the exception already required by FR-010/014, not a
   corpus write. No retrieval repair or automatic ingestion is performed.

Use existing literal endpoint `http://qdrant:6333`, no credentials, proxies,
redirects, retry or alternate endpoint. F2 image reuses exact F1 dependency/model/server
identities; add F2 schema to the narrow build context but never corpus/model bytes.
Reuse unchanged F1 collection cleanup 10 seconds and worker stop 5 seconds inside
one 45-second whole-demo teardown, with Docker reserved 30 seconds. Report unknown residue.

## Verification and calibration

Behavioral RED/GREEN order: validation/envelope; inventory/readiness and isolation;
query token/asset/worker policy; exact search and global tie handling; empty/failure
outcomes; CLI/owned cleanup. Establish unchanged Stage 1/F1 baseline first.

| Check | Requirements / outcomes |
| --- | --- |
| Strict input/schema, scope, booleans, bytes, token overflow | FR-001/002/003; SC-005 |
| Query/document identity, hash recheck, local-only loading | FR-003/012; SC-006 |
| Exact filter, exhaustive pages, cap, payload/current state | FR-002/006/009/010; SC-002/003 |
| One query, full N, tied group larger than k, duplicate/omitted IDs | FR-004/005; SC-003/006 |
| Inclusive minimum; empty scope validates tokens but skips encode/search | FR-007/008; SC-004 |
| Read timeout, malformed response, fatal/unconfirmed stop | FR-008/014; SC-005/007 |
| Diagnostics, injection and retention exclusions | FR-011/012/013; SC-006 |
| Real competing-source paraphrases and held-out negatives | FR-015/016; SC-001/004 |
| Existing regressions, final Docker/local cleanup | FR-010/016; SC-007 |

Calibration uses separately approved fixed calibration and held-out case sets.
Use the internal evaluator and shared retrieval pipeline defined in the CLI contract:
scope verification, question encoding and at most one exact search per case. Inspect
the complete validated candidate set before threshold/top-k; never reconstruct scores
from the normal filtered result. Compute the best expected-source score and its full
rank for each supported calibration case and maximum candidate score for each
unsupported case. Missing expected-source candidates, rank >3 or empty negative
candidate sets fail calibration; they cannot establish a separator. If max negative <
min supported expected-source score, propose a threshold strictly above the former
and at/below the latter (midpoint is a reproducible candidate), then obtain review.
If not separable, report calibration failure; do not fabricate a threshold or weaken
held-out expectations. Freeze corpus/configuration/cases/threshold before acceptance.
At least three supported held-out paraphrases and two unsupported held-out questions
must then meet SC-001/004; also validate competing-source ranking, isolation and clearing.
This small demonstration does not establish general retrieval quality or answer support.

Future commands and result-recording rules are in [quickstart](quickstart.md).
No F2 runtime tests, model probe, Docker gate or calibration executed in planning.

## Open decisions and execution gates

| Gate | Owner | Status / needed before |
| --- | --- | --- |
| Written requirements/plan/operating limits | User | Planning requested; implementation review still needed |
| Exact F2 corpus/reuse and case set | Corpus custodian / user | Record exact bytes/hashes, owner/classification/access/redistribution and source-use receipt before processing |
| Threshold and calibration record | User / evaluator | Explicit threshold required; calibrated value/results not yet measured; freeze before live acceptance |
| Local F2 build/run and existing assets reuse | User / operator | Specific authorization required; no new dependency proposal |
| Retained evaluation artifacts | User / operator | Access, lifetime/deletion and destination before any output capture |
| License/rights/publication | Release reviewer | Deferred outside F2 |

No technical design unknown is concealed by these human gates. F2 implementation
must not infer approval from generated documents, roles or checked checklist items.

## Actual planning checks — 2026-10-02

- Setup script `bash .specify/scripts/bash/setup-plan.sh --json`: exit0; resolved
  F2 spec/plan/directory and feature identifier002-f2-retrieval. Existing Git branch
  remains reconciled-governance-starter. Host emitted the existing C.UTF-8 locale warning.
- `git diff --check`: exit0.
- Native Python document/schema structural audit: exit0; all six generated design
  artifacts present; local Markdown links and whitespace checked; 13 local schema
  references resolved; closed object/required-field shapes checked; version2 retrieval
  envelope and vector exclusions checked. This is not full JSON Schema conformance.
- Saved F1 SHA-256 comparison: exit0; all16 application/test/packaging/source snapshot
  hashes in the existing validation record unchanged. No existing F1 file edited.
- Pre/post extension hooks: `.specify/extensions.yml` absent; none dispatched.
- `tasks.md` not created; specification and quality checklist preserved.
- Not run: F2 behavioral tests, full runtime regressions, Docker builds/runs, pinned
  API compatibility probe, source processing, threshold calibration or live acceptance.
  No runtime behavior changed. JSON Schema conformance engine absent; none installed.
- External actions: read-only official public documentation research. No installation,
  acquisition, corpus upload, secret read, commit, push, PR or publication.

## Remediation boundaries

The detailed process hierarchy/IPC and evaluation input/consumer contracts in
[retrieval-cli.md](contracts/retrieval-cli.md) are mandatory for T007/T009,
T012/T017, T028/T032/T033 and T039/T041. Calibration summaries are internal evaluation
records, not normal RetrievalResult envelopes; normal retrieval keeps mandatory
threshold and top_k limits. The evaluator and normal retrieval share the same search
implementation. No additional search, model, corpus, service or persistent worker.
Foundation implementation depends on T001 implementation authorization, T005 baseline
and T006 stubs. T003/T004 gate actual corpus processing, model reuse, live builds/runs
and retained evidence respectively; synthetic in-memory shape/fake work does not
require pretending those decisions are complete. All execution remains unapproved.
