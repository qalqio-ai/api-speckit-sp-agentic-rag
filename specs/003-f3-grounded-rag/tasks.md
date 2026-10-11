# Tasks: F3 — Grounded answers with citations

**Input**: [spec](spec.md), [plan](plan.md), [research](research.md),
[data model](data-model.md), [CLI contract](contracts/answer-cli.md),
[schema](contracts/serialization.schema.json), [quickstart](quickstart.md).
**Created**: 2026-10-02. **Updated**: 2026-10-03.
**Status**: F3 runtime integration/factory/wrapper/cleanup/evaluation code wired; live acceptance pending. Task markers retain full observed-criteria boundaries; see the latest ledger below.
**Branch**: `reconciled-governance-starter`; no branch change/commit authorized.
**Authority**: [AGENTS.md](../../AGENTS.md) and sole active
[constitution](../../docs/constitution.md); generated constitution placeholder is inactive.
**Authorization**: `$speckit-tasks F3` authorizes this document only. It does not
approve detailed design or authorize implementation. The requirements boundary was
already selected in [Clarifications](spec.md#session-2026-10-03): exact reviewed
question aliases/claim wording; unseen aliases abstain with zero generation.
**Tests**: Explicitly required by spec/repository: behavioral RED before production code,
then GREEN and unchanged regressions. Existing passing safeguards remain regression evidence.

## Format: `[ID] [P?] [Story] Description`

Sequential IDs; completion markers reflect observed task criteria. Story labels only in story phases. `[P]` denotes distinct-file
work after stated prerequisites, not authority to spawn agents, install or execute.
Every task gives repository-relative paths; missing product paths are future deliverables.

## Path conventions and preservation

Future product code is `app/answer/`; tests `tests/test_answer.py` and
`tests/test_answer_cli.py`; packaging `Dockerfile.f3`, `compose.f3.yaml`,
`scripts/f3-demo.sh`; approved future data only in `tests/fixtures/f3/` or an explicitly
reviewed read-only operator asset location. Preserve all Stage1/F1/F2 source, tests,
fixtures, schemas, packaging, locks and native venv; preserve governance and existing
F3 spec/plan/research/data model/contracts/checklist. Do not silently revise inputs to
make tasks pass. R1 unknown scope remains HTTP404 with exactly
`{"detail":{"code":"unknown_use_case"}}`.
No new HTTP route, agent loop, refinement, NLI runtime, tools, hosted transfer,
persistent user memory, dependency installation/upgrade, corpus upload, branch switch,
commit, push, PR or publication. Actual scope/design changes require review.

## Phase 1: Setup — decisions, proposals and baseline

**Purpose**: Make review concrete; record actual decisions before gated execution.
T001/T002 reviews and proposals are read-only. T001 verifies the recorded Option A
requirements decision rather than asking for it again. Catalog-dependent implementation
requires separate detailed-design/implementation approval. A future request for broader
semantic verification requires reviewed replacement design/tasks; this invocation
supplies no execution consent.

- [X] T001 Review `specs/003-f3-grounded-rag/spec.md`, `plan.md`, `research.md` and this `tasks.md`; verify the recorded 2026-10-03 Option A decision (user reply "recommended"): exact reviewed question aliases and claim wording, zero-generation abstention for unseen aliases even when evidence could answer them. Do not re-ask the selected boundary or infer broader semantic QA. Prepare the concrete detailed-design/implementation review and working-tree create/preserve/update/omit dispositions in `specs/003-f3-grounded-rag/tasks.md`; record actual separate approval before coding, preserving input files otherwise. Record in-place/worktree decision without assuming branch authorization. Broader semantic verification needs explicitly reviewed replacement artifacts; the clarification and this task-generation request supply no implementation/model/source/run approval.
- [X] T002 Prepare an exact synthetic source/catalog/case proposal in `specs/003-f3-grounded-rag/tasks.md`: current tuple/revision/hash, complete reviewed conditions/support spans and relevant conflicts, >=3 supported question aliases and >=2 unsupported including shipping, same-source-ID neighbor, replacement/clear scenario; propose owner/classification/access/redistribution, F3 purpose and capture location/access/expiry/correction/deletion. Create no corpus or consent receipt while preparing review.
- [X] T003 After actual exact-content/F3-purpose/retention approval, record decision evidence in `specs/003-f3-grounded-rag/tasks.md` and create only approved `tests/fixtures/f3/approval.json`, `grounding-catalog.json`, `answer-approval.json`, `evaluation-cases.json` and approved source/ingest JSONL files under `tests/fixtures/f3/`. Preserve F1 manifest shape and genuine F2 receipt boundary; bind exact manifest/catalog SHA256. Apply F3ApprovalReceipt constraint "Real separately reviewed F3 use decision; does not add sources or broaden rights". No schema-valid fixture supplies consent.
- [X] T004 Prepare and record actual proposed model/locked-stack reuse, model rights, capacity, local build/run and retained-result approval in `specs/003-f3-grounded-rag/tasks.md`; model `HuggingFaceTB/SmolLM2-360M-Instruct` revision `a10cc1512eabd3dde888204e902eca88bddb4951`, no fallback. Verify approved existing asset paths/observed hashes and create `generation-assets.json` only at the approved location after that decision. No installation/download/acquisition is implied; absent approved assets/capacity stop live gates.
- [X] T005 Establish fresh unchanged Stage1/F1 baseline with `.venv/bin/python -B -m pytest tests/test_sources.py tests/test_ingestion.py tests/test_ingestion_cli.py -q -p no:cacheprovider`; record exact commands/exits/warnings and protected-file SHA256 values in `specs/003-f3-grounded-rag/tasks.md`. This uses existing authorized fixtures only, grants no F3 reuse consent and does not claim F2 is implemented.
- [X] T006 After T001 implementation approval and T005, create importable signatures/explicit NotImplementedError stubs only in `app/answer/__init__.py`, `validation.py`, `grounding.py`, `generation.py`, `service.py`, `__main__.py`, `demo.py`, `evaluation.py`; define injectable clock/F2/tokenizer/model/process/transport seams in `tests/test_answer.py` and `tests/test_answer_cli.py`. No functional behavior, real source processing/model load/search or live factory yet; record import check in `specs/003-f3-grounded-rag/tasks.md`.

**Checkpoint**: T001/T005/T006 gate deterministic foundation. T003/T004 may remain
pending for synthetic in-memory shape/fake work, but gate actual new/reused source
processing, model reuse, builds/runs and retained evidence. Nothing executes here.

## Phase 2: Foundational — closed records and composition ports

**Purpose**: Shared contract validation and fixed injectable interfaces before stories.
**Dependencies**: T001 verification of recorded Option A plus actual detailed-design/implementation approval, T005 and T006;
T003/T004 only where their source/runtime/retention action is actually involved.

- [ ] T007 Write shared closed-record tests in `tests/test_answer.py` and shape/dispatch probes in `tests/test_answer_cli.py` against stubs: every F3 schema required/extra/null/type/enum/const/max/unique field, all F1/F2 external refs, duplicate-key/nonfinite/trailing JSON, bool-vs-int, canonical UUID, finite elapsed/counts and real calendar date. Include manifest/catalog/asset/case fingerprint binding and all cross-field invariants. Apply AnswerRequest constraint "Closed; F2 question256-token/4,096-byte limit; no normalization/history/evidence override"; AnswerResult constraint "Answered1–5 claims only; other outcomes zero claims/citations; safe metadata/no question/vector". Shape probes are visibly synthetic memory data, never approval/source fixtures. Include RetrievalReceipt/ScopeSnapshot shape and semantic tests; these internal records are not public session messages.
- [ ] T008 Run T007 before functional validators and record exact behavioral failures in `specs/003-f3-grounded-rag/tasks.md`; resolve collection/import/environment errors separately. Existing schema shape passes are not behavioral RED for missing production validators.
- [ ] T009 Implement shared parsing/record/result/config/receipt/asset/case validation in `app/answer/validation.py` after T008 with stdlib/existing helpers, no schema dependency. Require version3 closed envelopes, exact IDs, finite values, correct nullable config/scope, code==message, safe F2 cause enum and count0–1 excluding bool. Enforce runtime semantic invariants beyond schema; receipt shape never supplies approval. Enforce bounded reads before allocation: catalog/cases1MiB, asset manifest64KiB, F3 receipt16KiB; catalog<=64 claims/128 aliases/32 source rules; no symlink/path traversal/unlisted/duplicate asset paths. No claim-support or generation behavior before story RED.
- [X] T010 Test then implement F3 composition/outer dispatcher-lock interfaces in `app/answer/service.py` using injected F2 service in `tests/test_answer.py`: RequestEvidence constraint "Current exact scope; top_k3; internal request memory only"; F2 acquires/releases normal busy guard for retrieval, F3 owns same service guard afterwards, no callback/concurrent mutation in handoff. Supply F2 deadline=min(original request deadline, request start+120), retain actual counters and snapshot generation; no F2 call while F3 already owns its guard, no mutating inspect/reopen or public F2 contract edits. Record new behavioral RED/GREEN in `specs/003-f3-grounded-rag/tasks.md` before each port behavior. Implement/test retrieve_with_receipt contract and injected complete represented-source bindings, registry fingerprint, pre-send counter0/1 on failure and deadline clamp; never infer full scope/counts from top_k/status or add a read/search. Any future internal bridge changes in app/retrieval/service.py/index.py require T001 explicit implementation dispositions and actual F2 integration/regressions at T041; F1/F2 public behavior remains unchanged.
- [X] T011 Rerun shared foundation tests, unchanged Stage1/F1 tests and scoped Ruff; record commands/exits/warnings in `specs/003-f3-grounded-rag/tasks.md`. Keep actual semantic generation and live factory unavailable; injected F2 seams do not establish predecessor acceptance.

**Checkpoint**: Closed records and composition seams verified; no live path enabled.

## Phase 3: User Story 1 — Inspect a supported cited answer (Priority: P1)

**Goal**: Validated current evidence supports all reviewed claims from one genuine
model response; bounded exact citations accompany the answer.
**Independent Test**: Controlled eligible spans/conditions, model response and current
citations produce a valid answer; unrelated valid citation, omitted condition or extra
claim fails. Final approved live gates separately prove actual supported generation.
**Dependencies**: T011; tests use fixed shared seams and distinct files.

- [X] T012 [P] [US1] Write positive support/model tests in `tests/test_answer.py`: exact reviewed scope/question, complete material conditions, OR alternatives of AND spans, Unicode start/end/quote, split supports, duplicate/unknown claims, missing/extra/altered rendering, valid IDs with irrelevant support and no answer synthesized from catalog on model failure. Quote CatalogClaim constraint "Complete reviewed proposition including conditions; each alternative requires all spans; <=5 requested claims"; SupportSpan constraint "Entire span inside a current returned passage; quote/source-boundaries validated; no fragment semantic inference" (FR-003/006/007/008; SC-001/002).
- [X] T013 [P] [US1] Write successful injected-session/citation tests in `tests/test_answer_cli.py`: version3 answered envelope, claim-to-passage links, deduplication/no unused citations, actual one-search/one-generation counts, top_k3 and frozen retrieval settings, deterministic label versus simulated target identity, original F1/F2 delegated envelopes. Apply Citation constraint "Deduplicated chunk IDs from actual request; every citation used and every claim supported" (FR-002/007/016/018; SC-002/005/008).
- [X] T014 [US1] Run T012/T013 and record expected behavioral failures in `specs/003-f3-grounded-rag/tasks.md` before grounding/model/answer behavior; do not manufacture failures by removing existing safeguards.
- [X] T015 [P] [US1] Implement reviewed positive support validation in `app/answer/grounding.py` after T014: GroundingCatalog constraint "Reviewed validation rules, not alternative factual evidence or consent; frozen exact file hash"; SourceRule constraint "Covers every approved source tuple in selected scope; stale/missing/unreviewed tuples fail". Verify each selected current source tuple/catalog binding and complete approved support span alternative in actual returned passages; semantic correctness comes from actual reviewed rules plus current support, not equality alone. No new evidence/search, scope inference or source-state writes.
- [X] T016 [P] [US1] Implement injected generation adapter in `app/answer/generation.py` after T014: context only question/rules/current evidence with verified eligible labels/renderings; one invocation, no expected evaluation outcomes/history/other-source facts. Apply ModelResponse constraint "Strict JSON; exact approved rendering; all requested claims; no unrelated extras or free prose". Slice completion from prompt token count, parse one strict JSON value/no trailing prose, no JSON extraction/repair/retry. Live load stays unavailable until US3 supervision (FR-003/005/006/010).
- [X] T017 [US1] Implement supported answer orchestration in `app/answer/service.py` after T015/T016: one F2 retrieve top_k3, outer-lock/guard handoff, current snapshot, complete reviewed requested claims, at most one model attempt, post-model exact text/claim/support/citation validation and safe envelope/counters. Recheck registry generation before output, attach unchanged current provenance, emit no partial answer or fabricated result. Existing rejection/failure boundaries remain safe pending US2/US3 hardening.
- [X] T018 [US1] Implement injected-only JSONL dispatch in `app/answer/__main__.py` after T017: answer uses version3; delegate F1 operations and F2 retrieve unchanged, exact scopes, no model-controlled actions, no new HTTP behavior. Keep live factory explicitly unavailable until T034–T036; do not bypass original F2 readiness or busy semantics.
- [X] T019 [US1] Rerun US1/foundation tests and unchanged Stage1/F1 tests plus scoped Ruff; record actual provenance/coverage/count/mode assertions in `specs/003-f3-grounded-rag/tasks.md`. Record simulated identity as simulated, never observed model load or live semantics.
- [X] T020 [US1] Run independent deterministic supported-answer scenario through `tests/test_answer.py` and `tests/test_answer_cli.py`; record every required condition/citation validation and one model-adapter invocation in `specs/003-f3-grounded-rag/tasks.md`. This is the deterministic MVP, not full F3/live acceptance or authority to enable its live factory.

**Checkpoint**: US1 independently testable with controlled seams; US2/US3 required
before any live demonstration. Catalog-dependent work still requires T001 detailed-design/implementation approval.

## Phase 4: User Story 2 — Recognize insufficient or conflicting evidence (Priority: P1)

**Goal**: Safe whole-request abstention, relevant conflict detection and exact current
scope/revision handling without treating dependency failure as missing evidence.
**Independent Test**: Empty, unknown alias, unrelated/nonempty, partial supports and
relevant/irrelevant/potential conflicts; zero forbidden generation and zero invented facts.
**Dependencies**: T020. Shared grounding/service files make story implementation sequential.

- [X] T021 [P] [US2] Write insufficiency/conflict tests in `tests/test_answer.py`: no_evidence, exact unknown/case/whitespace alias, known unsupported with nonempty evidence, full multipart coverage, missing condition/span, relevant opposing support, potential opposition not returned, unrelated conflict and reviewed source-rule completeness/staleness. Apply QuestionCoverage constraint "Exact aliases only; answered expectations require nonempty claims and null reason; unsupported/conflict expectations require empty claims and explicit reason" (FR-004/008/009; SC-003/005). Add otherwise answerable unseen-alias zero-generation abstention and reject fabricated model conflicting_evidence/no_evidence; reviewed negative conflict aliases require matching current source-rule bindings.
- [ ] T022 [P] [US2] Write session isolation/abstention tests in `tests/test_answer_cli.py`: same-source-ID neighbor, shorter replacement, cleared scope, catalog revision mismatch and exact F1/F2 envelopes, model-declared well-formed insufficiency versus failed retrieval/model, zero answer claims/citations/no false real-world policy absence. Verify generation zero on empty/unknown/missing support (FR-002/004/007/009/010/018; SC-003/007).
- [X] T023 [US2] Run T021/T022 and record newly failing assertions versus already passing regressions in `specs/003-f3-grounded-rag/tasks.md`; correct only demonstrated gaps after behavioral RED.
- [X] T024 [US2] Implement/harden question coverage/relevant conflict and source-rule checks in `app/answer/grounding.py` after T023: exact aliases only; required complete claims, reviewed negative reason, current-source-covered opposition returned→conflicting_evidence, potentially relevant opposing source present without full returned support→unsupported_question, unrelated conflicts ignored. Unknown or stale source-rule bindings fail configuration. No second search, extra fetched evidence, keyword/NLI inference or normalization.
- [X] T025 [US2] Implement/harden outcome mapping in `app/answer/service.py` after T023/T024: successful empty→no_evidence/no model; unknown/full-support-missing→unsupported_question/no model; reviewed conflict→conflicting_evidence/no model; explicit well-formed model insufficiency has no claims/citations and unsupported_question reason only; model-only conflict/no_evidence is invalid_model_response. Retrieval/dependency/invalid grounding remains failed; unsupported extra model claims never become a partly valid answer. Only application-verified preflight/reviewed negative conflict rules can yield conflicting_evidence; do not normalize an invalid model reason or make another adjudication call.
- [ ] T026 [US2] Execute independent deterministic scope/replacement/clear/partial/conflict scenario with `tests/test_answer.py` and `tests/test_answer_cli.py`; compare source state/inventory/generation snapshots and neighbor preservation, record zero foreign/obsolete facts/citations in `specs/003-f3-grounded-rag/tasks.md`. Do not modify F1/F2 or create new source data without T003.
- [X] T027 [US2] Rerun US1/US2/foundation and unchanged Stage1/F1 plus available implemented F2 regressions; lint scoped files and record exact commands/exits/warnings in `specs/003-f3-grounded-rag/tasks.md`. If F2 tests/code are absent, report unavailable explicitly rather than treating fake composition as accepted F2.
- [X] T028 [US2] Review deterministic insufficiency results in `specs/003-f3-grounded-rag/tasks.md` against FR-009/SC-003: unknown aliases demonstrate catalog restriction, not broad semantic abstention; separately identify reviewed unsupported aliases, missing full support and actual model-declared insufficiency probes. Preserve prior passing guards while recording remaining US3 work.

**Checkpoint**: Independent abstention/isolation checks pass; live remains closed.

## Phase 5: User Story 3 — Controlled failure and trust boundaries (Priority: P2)

**Goal**: Bounded local supervised execution, safe failures and independently verified
owned cleanup without new permissions, hidden retries or false live mode.
**Independent Test**: Inject malformed/oversize/model/stall/OOM/IPC/leader-death/signal
failures; verify original budgets, safe outcome, attempt counts and all owned descendants.
**Dependencies**: T028. Unit and CLI test files are separate; lifecycle edits sequential.

- [ ] T029 [P] [US3] Write model/resource/deadline/adversarial tests in `tests/test_answer.py`: hashes/allowlist/local-only CPU FP32/no remote code, prompt64KiB/2,048 tokens with template, completion384/16KiB legitimate EOS, five claims, output128KiB, original240/retrieval120/generation110/validation10, reserved TERM2/KILL3, count0–1, no source/question instructions/tools/history/fallback. Include bool/nonfinite/trailing JSON, wrong citations and no partial diagnostics (FR-010–016; SC-004/005/006).
- [ ] T030 [P] [US3] Write supervisor/wrapper/evaluation tests in `tests/test_answer_cli.py`: startup120/READY gating,512KiB drain,16MiB message/64KiB frame and remaining-time IPC, parent outside session group/all descendants inside, leader death during active child, OOM/stalled transfer/reused ownership, repeated signals/no deadline reset, worker5/collection10/Docker30 within45 cleanup, exit0/1/130, uncertain residue and no subsequent fatal-session input (FR-011–016/018; SC-004–008). Test stdout stopped reader/partial write/broken pipe and wrapper forwarding stalls (including delegated envelopes), bounded one-message queue, incomplete-line discard/no second error, original deadlines and independently progressing cleanup.
- [ ] T031 [US3] Run T029/T030 before lifecycle changes; record exact behavioral RED/environment distinctions in `specs/003-f3-grounded-rag/tasks.md`, retaining existing regression passes.
- [ ] T032 [US3] Harden failed/rejected/count/config/error/output semantics in `app/answer/validation.py` and `service.py` after T031: fixed code==message/cause enum, no question/model/vector leaks, original monotonic total and aggregate validation/serialization deadline, output128KiB cap before emission, safe nullable metadata and actual counters, no repair/retry/partial answer. Assert new failures before changes and record in `specs/003-f3-grounded-rag/tasks.md`.
- [ ] T033 [US3] Implement supervised local model worker in `app/answer/generation.py` after T031/T032: exact model revision/hash asset manifest, safe read-only allowlist/safetensors/no custom hooks, offline flags before imports/local_files_only/trust_remote_code=False/token=False, CPU FP32/batch1/greedy beams1/threads4 interop1. Bound hash/load/template/tokenize/generate/decode/IPC/stop within110 and remaining240, reserve TERM2/KILL3; verify <=2,048+384 within native8,192, no truncation. Unexpected exit/stalled protocol/unconfirmed termination fatal; never substitute catalog/scripted answer or load model in parent.
- [ ] T034 [US3] Implement live owned factory/session in `app/answer/__main__.py` after T033: actual approval/hash/config preflight, supervised tokenizer startup<=120 before F3_READY, same F1/F2 readiness and outer serialization lock, no reopen; parent outside recorded owned group, all worker descendants inside same group/cgroup. Strict bounded JSON IPC/remaining-time reads/writes, no pickle; whole-group cleanup even after leader death, ownership/reuse verification and original45 teardown. Preserve F1/F2 envelopes and nonfatal/fatal/interrupt exit semantics. Implement complete-line bounded serialization followed by nonblocking stdout/readiness waits capped by remaining original/validation deadlines; blocked consumer/broken pipe fatal, no blocking flush/join or error on failed channel. Count delivery only on complete line, partial stream is invalid/undelivered.
- [ ] T035 [US3] Implement owned-stack wrapper in `app/answer/demo.py` and `scripts/f3-demo.sh` after T034: explicit absolute paths/reviewed threshold/calibration ID, no env-file/credential reads/runtime pulls/builds, verified read-only mounts/internal network/tmpfs/cgroup resource identity before input. Independently verify processes/collection/container/network absence; unknown residue nonzero; no global prune/shared-volume removal or repeated-signal reset. Forward stdout under private remaining-deadline metadata without changing public envelopes; no blocked consumer may prevent independent wrapper termination/ownership verification of CLI parent plus group or cleanup. Bound safe diagnostics separately.
- [ ] T036 [US3] Create separate `Dockerfile.f3` and `compose.f3.yaml` after T035 using exact F1 base/Qdrant/locked-stack identities without changing F1/F2 files; runner8GiB hard memory including descendants/four CPUs/no swap-dependent enlargement, Qdrant1GiB hard memory/256MiB index tmpfs, runner64MiB tmpfs. Exclude model/corpus/receipts/env/secrets from image; lazily read approved mounted assets. Review rendered config with deterministic probes first; actual Docker builds/runs require T004 and approved host capacity. Necessary `.dockerignore` updates only under T001 implementation disposition.
- [ ] T037 [US3] Test then implement `app/answer/evaluation.py` and integrate `--evaluation-cases` flow in `app/answer/__main__.py`/`demo.py`: EvaluationCaseSet constraint "Separate approved frozen expectations; no quality assertion from shape". Validate <=128 cases/1MiB, >=3 positives/>=2 negatives incl shipping, unique case IDs/known scoped claims/sources/status-reason relationships and manifest/catalog/model/retrieval fingerprints. Approved ingest-only stdin to EOF, abort on any ingest failure, then normal answer once/case in same ready session; output case_id+actual result and teardown. Never send evaluation expectations as model context or tune settings; write/run failing tests in `tests/test_answer.py` and `tests/test_answer_cli.py` before consumer behavior.
- [X] T038 [US3] Rerun all F3 deterministic tests, unchanged Stage1/F1 and available F2 tests plus scoped Ruff; record commands/exits/warnings/deadline/ownership/cgroup/outcome assertions in `specs/003-f3-grounded-rag/tasks.md`. No model/Docker source processing solely to satisfy deterministic gate.
- [ ] T039 [US3] Perform deterministic adversarial/output review through `tests/test_answer.py` and `tests/test_answer_cli.py`: instructions cannot widen scope/destination/claims/limits/actions, zero tools/refinements/hosted transfer/persistent writes, no raw question/model/source diagnostics and no secret reads. Record actual review/results in `specs/003-f3-grounded-rag/tasks.md`; do not create retained traces or approval evidence without T003/T004.
- [ ] T040 [US3] Execute independent deterministic controlled-failure/lifecycle scenarios and verify exact owned fake resource/descendant registry snapshots, interruption/EOF/close/nonfatal/fatal behavior and zero partial answer in `tests/test_answer_cli.py`; record original240/45 budget evidence and unrun actual runtime gate in `specs/003-f3-grounded-rag/tasks.md`.

**Checkpoint**: Full deterministic F3 validated. Live execution additionally requires
actual T003/T004 source/runtime/capacity/retention approvals and verified F2 (T041).

## Phase 6: Polish and cross-cutting acceptance

**Purpose**: Verified predecessor, actual local model/semantic evidence and review.
**Dependencies**: T040 for execution; T003/T004 and T041 for live portions. Documentation
proposals/read-only reviews may proceed without inventing approval. No publication.

- [ ] T041 Read `specs/002-f2-retrieval/tasks.md` and actual F2 acceptance evidence when available; independently verify required F2 tests/runtime/source/config/calibration/cleanup under its own approvals and record predecessor status in `specs/003-f3-grounded-rag/tasks.md`. F2 implementation belongs to its own workflow; if unbuilt/unverified, mark F3 integrated live gate pending instead of implementing or claiming it within F3. Verify actual retrieve_with_receipt fields, count-at-dispatch, current complete source bindings, registry fingerprint and original deadline behavior against unchanged F2 regressions before real F3 composition; absent port remains an integration gate, not inferred compatibility.
- [ ] T042 Under actual T003/T004/T041 gates, probe pinned approved local model/tokenizer/locked runtime and rendered `compose.f3.yaml`/`Dockerfile.f3`: observe asset/config identities, special/chat/EOS behavior, strict single-output limits, actual cgroup/tmpfs/network enforcement, capacity/latency/memory and supervised stop. Record commands/exits/warnings in `specs/003-f3-grounded-rag/tasks.md`; incompatibility/missing assets/insufficient capacity fails, no install/fallback/enlargement without fresh review.
- [ ] T043 Run frozen supported live cases using `scripts/f3-demo.sh` and approved `tests/fixtures/f3/evaluation-cases.json` after T042: >=3 reviewed exact question paraphrases, actual model invocation, every expected claim/material condition and current citation checked, zero unsupported extra facts. Record actual source/catalog/model/config/case hashes, per-case response/latency/counts and claim-by-claim human semantic assessment in `specs/003-f3-grounded-rag/tasks.md` or approved evidence location. Matching scripted/catalog answers do not supply live SC-001/002.
- [ ] T044 Run >=2 approved frozen unsupported live cases incl missing shipping policy through `scripts/f3-demo.sh`; record exact reason/zero claims/citations and actual zero/one attempt counts in `specs/003-f3-grounded-rag/tasks.md`. Distinguish catalog preflight abstention from model-declared insufficiency; separately run reviewed controlled explicit-model-insufficiency probe in `tests/test_answer.py`. Unknown aliases never prove broad semantic abstention; failed cases remain failed, no held-out tuning.
- [ ] T045 Run approved same-session shared-source-ID isolation, shorter replacement, clearing/neighbor preservation and ordinary EOF/close cleanup via `scripts/f3-demo.sh`; inspect exact recorded current source/catalog binding and owned process/container/network absence within original45 seconds. Record actual outcomes/residue in `specs/003-f3-grounded-rag/tasks.md`; stale catalog correctly fails until separately approved matching catalog/source rules are used, never rewrite review evidence on the fly.
- [X] T046 Run final all relevant F3/Stage1/F1/F2 pytest and Ruff gates and unchanged local `scripts/ci-local.sh` only under actual Docker authorization; record exact commands/exits/warnings/tested snapshot and cleanup in `specs/003-f3-grounded-rag/tasks.md`. Local checks are not remote CI or image release; unrun/missing/failed checks stay explicit.
- [ ] T047 After real implementation, update `README.md` navigation and `specs/003-f3-grounded-rag/quickstart.md` with actual runnable commands/model/source/retention gates and observed limitations; distinguish reviewed aliases/exact wording from unrestricted grounded QA. Preserve Stage1/F1/F2 instructions and original requirement/checklist criteria; reviewed design deviations require explicit reconciliation.
- [X] T048 Create `specs/003-f3-grounded-rag/validation.md` from observed evidence only: actual approval references, code/source/catalog/model/config/image/case identities, RED/GREEN/deterministic/live outcomes, per-claim support, citation/abstention/mode/budget/cleanup, exact command exits/warnings, protected hashes, unrun checks and risks. Store no raw sensitive content or results outside approved retention/access/expiry policy.
- [X] T049 Conduct requirements/contract/security/code review against `specs/003-f3-grounded-rag/spec.md` and actual changes; record findings/disposition in `specs/003-f3-grounded-rag/validation.md`. Implement only approved in-scope fixes after fresh behavioral failing tests as appropriate; rerun affected checks. No reviewer role or checklist supplies human approval or authority for commit/PR.
- [ ] T050 Compare final protected Stage1/F1/F2/governance file hashes and owned-resource residue with T005 baseline, audit all actual task evidence and remaining decisions in `specs/003-f3-grounded-rag/validation.md`; report changed paths/rationale, commands/exits/failures/warnings, deterministic versus live/unverified outcomes and external actions. Do not mark complete if predecessor/approval/semantic/cleanup gates remain pending; no commit, push, PR or publication.

## Dependencies and execution order

```text
Read-only T001/T002 -> verify recorded Option A + actual design/implementation approval T001
T001 + T005 baseline -> T006 stubs -> T007 -> T008 -> T009 -> T010 -> T011
T011 -> US1 T012/T013 -> T014 -> T015/T016 -> T017 -> T018 -> T019 -> T020
T020 -> US2 T021/T022 -> T023 -> T024 -> T025 -> T026 -> T027 -> T028
T028 -> US3 T029/T030 -> T031 -> T032 -> T033 -> T034 -> T035 -> T036 -> T037 -> T038 -> T039 -> T040
T002 + actual source/catalog/retention approval -> T003 -> actual source processing
Actual model/reuse/capacity/build/run/retention decision T004 -> relevant live actions
T040 + T003 + applicable T004 + verified F2 T041 -> T042 -> T043 -> T044 -> T045 -> T046
T046 -> T047 -> T048 -> T049 -> T050
```

F2 absence blocks integrated live gates, not authorized injected F3 contract work.
T003/T004 apply to each actual action; neither is a blanket prerequisite for synthetic
memory probes. T001 verification of recorded Option A and separate design/implementation approval remain mandatory.
US1→US2→US3 share files; independent scenarios do not imply whole-story parallelization.
No live/demo factory before US3 completion and all applicable approvals. Missing behavior
gets RED/fix; already passing safety stays intact without manufactured regressions.

## Parallel opportunities and examples

Eight `[P]` tasks form four separate-file pairs after fixed seams/prerequisites:

- US1 tests T012 `tests/test_answer.py` / T013 `tests/test_answer_cli.py` after T011.
- US1 implementation T015 `app/answer/grounding.py` / T016 `app/answer/generation.py` after T014.
- US2 tests T021 `tests/test_answer.py` / T022 `tests/test_answer_cli.py` after T020.
- US3 tests T029 `tests/test_answer.py` / T030 `tests/test_answer_cli.py` after T028.

Examples describe scheduling, not authorization to spawn agents. Fixed signatures
from foundation are shared; adaptive dependent work and tasks.md result recording
remain sequential. Packaging/evaluation touch supervisor files and are not parallel pairs.

## Implementation strategy

1. Verify the recorded grounding boundary; obtain separate detailed-design/implementation approval and preserve user work.
2. Prepare specific source/model/capacity/retention proposals without processing data.
3. Establish baseline, importable stubs and tested closed foundation with lazy live imports.
4. Deliver US1 deterministic cited-answer MVP, including strict complete support checks.
5. Add independent US2 abstention/isolation then US3 deadline/resource/ownership hardening.
6. Verify F2 and actual applicable approvals; run real pinned-runtime/frozen live cases.
7. Report observed acceptance, limitations/residue and review findings; no deployment.

## Requirement and outcome traceability

| Requirement | Tasks |
| --- | --- |
| FR-001 input | T007–T009, T013/T018, T021/T029/T032 |
| FR-002 one scoped retrieval | T010/T013/T017, T022/T026/T041/T045 |
| FR-003 context boundary | T012/T015–T017, T029/T033/T039 |
| FR-004 no-evidence/failure | T021/T022/T025/T028/T044 |
| FR-005 one generation | T012/T016/T017, T029/T033/T040/T043 |
| FR-006 complete claims | T012/T015/T017, T021/T024/T043 |
| FR-007 current citations | T012/T013/T015/T017, T022/T026/T043/T045 |
| FR-008 semantic support | T001/T002/T012/T015/T017/T024/T043 |
| FR-009 abstention/conflicts | T021–T028/T044 |
| FR-010 controlled outcome | T007–T009/T016/T025/T029–T034/T040 |
| FR-011 untrusted content | T029/T030/T033/T039 |
| FR-012 deadlines/cleanup | T010/T029–T036/T040/T042/T045/T046 |
| FR-013 resource limits | T007/T009/T029–T036/T042 |
| FR-014 local model/permissions | T004/T029/T033–T036/T039/T042 |
| FR-015 memory/retention | T002–T004/T029/T030/T039/T048 |
| FR-016 modes/metadata | T007/T009/T013/T019/T029/T032/T043/T048 |
| FR-017 approved frozen inputs | T002–T004/T007/T009/T037/T041–T045 |
| FR-018 preservation | T001/T005/T010/T013/T018/T022/T027/T041/T046–T050 |
| SC-001 real supported claims | T002/T003/T012/T015/T020/T042/T043 |
| SC-002 exact supporting citations | T012/T013/T015/T017/T019/T026/T043/T045 |
| SC-003 insufficiency | T021–T028/T037/T044 |
| SC-004 safe failure | T007–T009/T012/T016/T025/T029–T034/T040 |
| SC-005 counts/actions | T010/T013/T016/T017/T021/T025/T029/T033/T039/T044 |
| SC-006 original time/cleanup | T029–T036/T040/T042/T045 |
| SC-007 regressions/isolation | T005/T011/T019/T022/T026/T027/T038/T041/T045/T046/T050 |
| SC-008 genuine mode evidence | T013/T019/T020/T027/T028/T041–T044/T048/T050 |

Every schema required/optional/null/enum/type/const/array field is covered by T007/T009;
calendar validity, UTF8 limits, boolean rejection, finite values, exact approved scope,
all cross-field relations/current support and actual approval remain semantic checks.
All twelve data-model constraint cells are quoted verbatim above. At initial generation, all tasks were unexecuted; current progress is in the implementation ledger.

## Initial generation verification record (historical)

| Check | Actual result / exit | Limit |
| --- | --- | --- |
| `bash .specify/scripts/bash/setup-tasks.sh --json` | Exit0; active F3 path/template and four optional doc entries resolved | Host C.UTF-8 locale warning; no execution approval |
| `python3 /tmp/audit_f3_tasks.py` | Exit0:50 sequential unchecked tasks; US1=9/US2=8/US3=12/shared-final=21; eight parallel tasks;12 verbatim constraints;26 coverage rows;79 protected hashes unchanged | Initial audit exit1 counted the table separator as an entity; corrected audit parser and reran successfully; no design change |
| `git diff --check` and full tasks.md whitespace/link audit | Exit0 | Untracked task file checked directly; no product/runtime result |
| Pre/post `.specify/extensions.yml` check | Absent; no hooks | No external action |
| Runtime tests / behavioral RED/GREEN | Not run | Future implementation tasks, actual T001 approval pending |
| Real model/Docker/semantic/corpus evaluation | Not run | T003/T004/T041 gates pending; no measured outcome |

Record execution only when observed. The catalog choice was pending at initial generation;
the 2026-10-03 clarification subsequently resolved it. F2 remains unimplemented and
model compatibility/capacity/source/retention/run approvals remain unverified. Current
reconciliation below supersedes historical pending-choice wording without implying
implementation or live acceptance.

## Remediation verification — 2026-10-03

User requested concrete edits for I1/U1/U2/I2/U3. Updated nine F3 requirement/design/
checklist/task/schema files only. No product code, data fixture or approval record.
`python3 /tmp/verify_f3_remediation.py`: exit0;50 sequential unchecked tasks, eight
parallel markers,26 requirement/outcome coverage rows, verbatim original constraint
cells, local links/whitespace;71 other snapshotted files unchanged, including F1/F2,
governance, locks and feature pointer. Three Draft2020-12 schemas conform;22 F3
definitions; offline positive/negative model-reason/receipt shape probes pass.
`git diff --check`: exit0. These are structural/shape/consistency checks, not actual
F2 bridge, stdout deadline, semantic generation or owned cleanup verification.
Runtime/API/product tests, corpus/model processing, Docker builds/runs and external
actions not performed. The requirements boundary was subsequently selected in clarification;
explicit detailed-design/implementation/source/model/run/retention approvals remain
pending; no model/receipt schema supplies them.

## Clarified-plan reconciliation — 2026-10-03

The requirements boundary is selected, not an open choice: exact reviewed question
aliases and claim renderings; unseen aliases abstain with zero generation. T001
verifies that existing decision and prepares separate detailed-design/implementation
review. All50 IDs, unchecked status, story phases, eight parallel markers and existing
behavioral RED/GREEN sequencing are preserved. No task was executed or marked done.

The five remediations remain explicit: selected closed-domain scope; one internal F2
receipt carrying full source bindings/fingerprint/actual dispatch count/original deadline;
bounded stdout and wrapper forwarding with independent cleanup; verified F2 prerequisite
for real composition rather than injected seams; and application-only conflict decisions
with invalid model conflict/no-evidence reasons rejected. No public F2 contract change.

Deterministic MVP is US1 after approved foundation, with controlled supported answers
and complete current support/citation validation. US2 independently tests insufficiency,
conflicts and scope isolation; US3 independently tests bounded failures and owned cleanup.
US2/US3 and verified F2 are required before integrated live demonstration. Unmeasured
model compatibility/capacity and action-specific source/model/build/run/retention gates
remain unresolved. No new source, model, dependency or production behavior is introduced.

### Refresh verification record

- `bash .specify/scripts/bash/setup-tasks.sh --json`: exit0; absolute active F3
  directory/template and four optional document entries resolved. C.UTF-8 locale
  warning only; no setup or document-resolution failure.
- `python3 /tmp/audit_f3_tasks_refresh.py`: exit0;50 sequential unchecked tasks,
  US1=9/US2=8/US3=12/shared-final=21, eight parallel markers,12 verbatim data-model
  constraints,26 requirement/outcome rows and10 local Markdown links/anchors.
  Checklist format/story phases/file paths/whitespace and preserved remediation
  markers pass;79 protected file hashes unchanged. Only this tasks.md changed.
- `git diff --check`: exit0; direct whitespace audit covers the untracked task file.
  Pre/post `.specify/extensions.yml` absent; no hooks dispatched.
- No API/runtime tests, behavioral RED/GREEN, model/Docker/corpus processing or live
  semantic acceptance performed for this documentation refresh. No installation,
  commit, push, PR, publication or other external action. Actual execution gates
  remain pending; generated task counts are not completed implementation evidence.

## Implementation ledger — 2026-10-03

Authorization: the user explicitly invoked `$speckit-implement F3`, authorizing
local implementation of this reviewed design. Option A remains selected. Work in
the current non-main branch checkout after the optional worktree question; no branch
change, commit, installation or external action authorized.

Dispositions: create app/answer modules, tests/test_answer.py and tests/test_answer_cli.py;
create separate F3 packaging/evidence documentation when appropriate; update this
task ledger and necessary ignore patterns; preserve all existing source/test/spec/plan/
schema/governance/locks/fixtures; omit approved-source fixtures, asset acquisition,
model processing, actual Docker runs and external actions until specifically approved.
Ruling: injected deterministic seams do not require a built F2; real composition
requires T041 verification. No fake supplies predecessor acceptance or live approval.

T002 proposal (not an approved corpus): literal synthetic source text
"Synthetic returns: unused items may be returned within 7 days with a receipt."
proposed scope f3-synthetic, source policy, revision v1. Reviewed claim proposal
"Unused items may be returned within 7 days with a receipt." and exact aliases
"What is the return policy?", "How long do I have to return an unused item?",
"Is a receipt required for a return?". Negatives "What is the shipping policy?"
and "Can used items be returned?". Neighbor scope f3-neighbor with same policy ID;
replacement revision v2 shorter text and clear scenario need a matching separately
reviewed catalog. Owner/classification/access/redistribution/F3 purpose/retention
are unresolved; no fixture/approval JSON written, no source processed.

T004 proposal: retain plan's immutable SmolLM2 revision and locked Linux CPU stack.
Existing approved generation asset location, observed hashes, rights, host/Docker
capacity, build/run and evidence capture policy are unknown; no manifest created.
T003/T004 action gates remain unchecked and block their actual asset/content actions.

T005 observed: `.venv/bin/python -B -m pytest tests/test_sources.py tests/test_ingestion.py tests/test_ingestion_cli.py -q -p no:cacheprovider`
exit0:113 passed, one existing Starlette HTTPX integration deprecation warning.
Protected SHA256 baseline recorded in /tmp/f3-implementation-before.json; no
historical pass used as current evidence. Checklist requirements.md:16/16 pass,
read-only; generated constitution remains inactive. No extension hooks exist.

T006: eight importable modules/signature stubs created; no functional behavior or live factory.

Implementation progress (partial; unchecked tasks retain unmet criteria):
- T001/T002/T005/T006 complete: reviewed recorded boundary and explicit implement
  instruction/dispositions; prepared synthetic proposal without processing; fresh
  baseline passed; importable stubs and seams created. T003/T004 remain gated.
- T007/T009 validators and tests are implemented in part, with strict closed shapes,
  local F1/F2 references, semantic catalog/source/span/alias/receipt/result checks,
  bounded JSON files, asset hash allowlists and case-set shape/relationship checks.
  Exhaustive field mutation and complete approval/config fingerprint binding remain.
- Behavioral RED:29 failures/2 non-object-definition skips against validators' stubs,
  then20 new failures against catalog/receipt/grounding stubs; after validators, six
  grounding stubs still failed as expected. Two initial positive sample-generator
  errors (dictionary additionalProperties and nullable conditional merge) were
  corrected separately; they are fixture defects, not behavioral RED evidence.
- Grounding/injected service/generation/dispatcher components cover portions of
  T010/T012–T028: exact alias, OR-of-AND spans, exact rendering, valid-but-irrelevant
  IDs, partial support, relevant/potential/unrelated conflicts, one actual injected
  adapter attempt, model-only reason rejection, no catalog substitution, private
  error text suppression, actual receipt counts and serialized busy handoff.
- Session tests first failed11 times for absent AnswerService/adapter behavior;
  behavior then passed. New guard-release test failed, then passed after holding the
  guard through final validation. Failure receipt probe initially used a nonexistent
  F2 search_failed code; corrected to actual index_failed separately.
- Output primitive/execute portions of T030/T034 tested: three initial stub failures,
  then partial writes/stopped consumers/broken pipes passed. Two callback/delivery
  stub failures and a serialization-deadline-reset failure were observed and fixed.
  Initial unrealistic1e20 selector timeout failed on host; bounded polling fixed it.
  This is an injected single-operation transport, not an owned live session supervisor.
- No genuine tokenizer/model loading, factory readiness, framed worker IPC, cgroup
  enforcement, descendant identity registry, actual wrapper, F3 image or live
  evaluation exists yet. Synchronous injected adapters rely on caller discipline;
  they are not hard wall-time supervision and may never be labeled local_live.
- Checklists remain unchanged. Git ignore verification adds Python/editor/temp
  exclusions only; existing deny-by-default Docker context already excludes
  model/corpus/credentials, so .dockerignore is preserved.

T002 exact proposed source SHA256: `50e85780308baf9945671e2c05be5ef4fa3e02ccd805babd2b6809ee52eb841d`.

### Final checks for this partial implementation snapshot

- Focused F3 pytest: exit0,91 tests passed. Full `.venv/bin/python -B -m pytest -q -p no:cacheprovider`: exit0,204 passed, one existing Starlette HTTPX deprecation warning.
- `.venv/bin/python -m ruff check app/answer tests/test_answer.py tests/test_answer_cli.py`: exit0. Earlier scoped lint failures were import order, unused test bindings and local style issues, corrected and rerun.
- `git diff --check`: exit0. Direct untracked-file whitespace/preservation audit: exit0;79 protected hashes unchanged. Only new F3 modules/tests, .gitignore and this ledger changed; validation.md added as a partial evidence report.
- Read-only code review reproduced four implemented-boundary defects and one follow-up order defect. Fresh RED/GREEN tests fixed original start/deadline propagation and bounded lock waits, invocation-local busy ownership, receipt embedding provenance/score validation, full-question support before conflict checks and order-independent opposing-claim classification. No live components were reviewed or asserted.
- Pre/post extension hook checks: absent. No actual F2 code, F3 corpus fixture, model acquisition/load, Docker/cgroup/descendant run, semantic evaluation, install, commit, push, PR or publication.
- T003/T004 need actual exact-content/F3-purpose/rights/capacity/build/run/retention decisions. T041 reports F2 unbuilt; no real receipt bridge/regressions. Remaining deterministic criteria and live infrastructure are still unbuilt; no whole-feature acceptance or all-task completion claimed.
- See [partial validation report](validation.md). Existing unchecked tasks are the continuation queue; do not redo the four completed setup tasks.


### 2026-10-03 continuation: completion request

The user requested `speckit-implement F3 complete`. Local F3 code changes and
synthetic in-memory/native process probes are authorized. No reply has yet supplied
the source/model/F2/Docker/retention decisions requested in [approval-request.md](approval-request.md).
These missing decisions are not inferred from the completion request. Preserve
Stage1/F1/F2 and the selected exact-alias boundary; no corpus fixture/receipt created.

Completed deterministic tasks are reconciled above: T010–T021 (excluding the
still-partial foundation schema criteria), T023–T025, T027/T028 and observed evidence
T048/T049. T007–T009 remain unchecked for exhaustive mutation criteria; runtime/story
tasks with untested subcriteria remain unchecked. T022/T026 still require complete
faithful predecessor inventory/envelope scenario coverage; partial snapshot probes
are not a genuine F2 state machine. Do not redo completed native grounding work.

Continuation changes:
- Shape tests now mutate field types/nullability/max array counts across all F3
  definitions; validation binds manifest/catalog/F3 receipt/asset/config/case hashes.
  Catalog source tuples must be approved and every approved source identity covered;
  approved future replacement revisions do not replace current catalog rules.
- Fresh fork/exec workers use bounded JSON frames (16MiB total/64KiB frame), safe
  errors and actual attempt controls. Local worker enforces reviewed file hashes,
  no unlisted snapshot files, offline/local-only/safetensors/no custom code, pinned
  runtime/CPU/config/chat/EOS; probe precedes model weights, greedy decode validates
  prompt/template/token/EOS/completion limits. Actual live load remains unverified.
- Native transport now drains oversize JSONL, rejects malformed records, discards
  incomplete EOF, stops on close/output failure and calls independent cleanup.
  Injected evaluation consumes ingest-only input to EOF, aborts any non-complete
  F1 ingest, then issues one normal answer per frozen case. Expectations are not
  model context. These consumers are cooperative/injected, not a live supervisor.
- Dockerfile.f3/compose.f3.yaml reuse exact F1 identities and locked requirements;
  .dockerignore permits only required schemas in the deny-by-default context.
  Read-only Compose rendering with /dev/null env file succeeds. No build/run or
  resource enforcement is claimed; wrapper/factory/owned cgroup registry unbuilt.

Observed failures and corrections (not acceptance results):
- Four transport tests failed with NotImplementedError; implemented input/consumer
  behavior then passed. One evaluation test failed because successful F1 ingest
  status is `complete`, not `ingested`; consumer corrected, exact contract preserved.
  A test initially used nonexistent `ok` and a renamed variable caused NameError;
  those fixture errors were corrected separately, not counted as behavioral RED.
- Independent review reproduced unlisted optional tokenizer-file acceptance. Three
  new tests failed (optional map/config/custom file); exact snapshot allowlist fix
  made them pass. Two new tests exposed FIFO/parent-symlink acceptance and passed
  after bounded-file validation rejected those paths before opening.
- Native group cleanup initially failed twice with macOS EPERM on zombie-only
  groups. An escalated rerun reproduced the same two failures. Cleanup now requires
  verified group absence after reap; a short timer fixture was increased to allow
  actual KILL/reap scheduling. No signal denial or leader exit is treated as proof.
- Fake decode and attempt-control tests passed; no model result or model rights
  approval exists. A fresh exec platform/invalid-asset probe reported ownership,
  zero generation attempts and fixed model_unavailable, then verified owned stop.

Latest actual checks: full pytest exit0,255 passed/one existing Starlette HTTPX
integration deprecation warning. Focused F3 and scoped Ruff checks are reported in
validation.md. Docker compose --env-file /dev/null -f compose.f3.yaml config
--no-interpolate --format json exit0; no daemon action. git diff --check exit0.
Earlier lint-only findings were an unbound loop closure and unused test bindings;
corrected without changing requirements. Extension hooks absent.

T027/T028 assessment: unknown/case/whitespace aliases show catalog restriction,
not broad semantic abstention. Reviewed negative/missing support/application
conflict probes have zero adapter calls; valid model insufficiency has one. Actual
receipt count0/1 is preserved through injected failure boundaries. Full-question
coverage precedes conflict classification and all relevant opponents are checked.

T041 predecessor assessment: app/retrieval and its tests/acceptance/bridge remain
absent. This is a live integration blocker under its own workflow, not permission
to build F2 inside F3. T003/T004/T041–T045 remain pending. T029–T040 have partial
code/tests but lack complete supervisor/wrapper/resource/fatal-state verification.
T046 Docker local CI unrun. No all-task/full-F3 completion claim is made.


Final follow-up review: empty/incomplete stdin incorrectly triggered frozen cases.
Two new regression tests failed with exit0 instead of1; consumer now requires at
least one successful complete ingest. Final full pytest exit0:257 passed (144 F3,
113 unchanged Stage1/F1), one existing Starlette warning. Scoped Ruff exit0.
67 protected snapshot hashes unchanged, listed with final code/config identities
in validation.md. Checklist markers unchanged; no extension hooks.23/50 tasks
checked;27 remain pending/partial, no all-task completion claim.


### User approved recommendations — native F2 prerequisite continuation

Actual user response: “Proceed with your recommendations”. F2 implementation
and proposed local capacity/build/run checks, safe repository metadata default
now authorized. The F2 native core/receipt bridge is implemented under its own
tasks ledger; actual F1/F2/F3 classes compose in a synthetic memory test. T041
remains unchecked: no F2 live worker/factory/wrapper/calibration/acceptance proof.
No source owner/reviewer name or generation directory/acquisition values supplied;
those questions remain pending. Additional exact F2 competing-source/case proposal
prepared and presented; no corpus/consent fixture created or approved by inference.

Host capacity read-only probe exit0:64GiB; Docker about3.8GiB/16CPUs. F3's8GiB
runner plus1GiB Qdrant cannot fit; no limits or Desktop settings changed. Local
Docker build/run stays gated by actual capacity and completed owned-runtime code.
F3 demo module now fails closed with session_unavailable when invoked; three new
unready module-entry tests first failed with exit0, then passed with exit1/noREADY.
No actual F3 live gate enabled. New final suite exit0:324 passed/one existing
Starlette warning; scoped F2/F3 Ruff exit0. F2 hashes/evidence in its validation.md.
The prior67-hash/F3 identity report remains a historical snapshot, not a claim
that intentionally updated F2 task documentation or F3 demo remain identical.

### 2026-10-04 deterministic continuation

Latest authorization: implement/verify unfinished F3 work using existing deterministic
fixtures; no models downloaded, unapproved sources processed, Docker settings changed,
commits or publication. Read project guidance/spec/contract and preserve existing
dirty work. Apply implementation/TDD and final read-only code review skills.
Dispositions: create native lifecycle and wrapper tests/helpers plus decision report;
update F3 consumer/generator/service/error handling and F3 evidence; preserve Stage1,
API/F1, F2, governance, specs/plans/schemas, approved fixtures, locks and packaging.

T030/T031/T034 deterministic portion:15 new behavioral RED failures against a
supervisor stub/consumer exit defects, followed by green native owned-group probes.
Factory constructs fixtures only after setsid, parent stays outside group; framed
startup gating precedes READY/input, one output acknowledged after complete transfer,
hard request/output timeout and native owned stop progress independently. Broken
readiness/output, failed startup, stalled dispatch and group ownership tested.
SIGTERM-handler restoration regression failed exit1 vs130, then passed; teardown
ignores repeated interrupts without changing the original deadline. This is not
the genuine fresh-exec factory, cgroup enforcement or collection/Docker cleanup.

T035 deterministic portion:22 wrapper helper stub failures, then green explicit
absolute/nonsymlink locations, finite threshold/calibration, optional evaluation
arguments, captured memory/swap/CPU/mount/internal-network ownership checks and
review-only exact-ID cleanup command plans. A realistic additional network metadata
fixture failed before acceptance of endpoint details while preserving exact owned
network identity. No Docker command was executed by these helpers; runner image,
kernel cgroup and actual tmpfs/absence checks remain required.

Review corrections, each with observed behavioral RED then green: actual request
start rather than subtracting240 from shortened fixture budgets; evaluation mismatch
sets exit1 via frozen case_matches without sending expectations to model; fatal
adapter session transport sets fatal state, stops input and propagates before any
public record (last zero-output regression failed before the correction). Consumer
retains nonfatal failed/incomplete status through EOF/close; cleanup False/exception
forces nonzero status. Actual F2 ingestion fatal state also stops input.

Ruling: source/model approvals gate live actions, not local deterministic code.
The genuine F2 runtime interfaces are still unbuilt/unverified; a fixture factory
and review-only wrapper helpers must not be promoted to the live path. T033–T037
remain unchecked for their unmet execution/integration criteria. No unchecked task
is marked complete merely because these added probes pass.

Final observed checks: full pytest exit0,367 passed/one existing Starlette HTTPX
deprecation; scoped F2/F3 Ruff exit0; git diff --check exit0;104 protected hashes
unchanged and extension hook absent. Independent read-only reviewer confirmed
final fatal-output/network fixes;42 native lifecycle/wrapper tests exit0. Detailed
commands/limits in validation.md; exact sources/model sizes/memory derivation and
remaining code/approvals in continuation-decisions.md. No live F3 acceptance claimed.


### 2026-10-04 authorized runtime wiring and local build/run

Latest user explicitly authorizes all unblocked local F3 implementation and
previously authorized build/run; no renewed generic approval. Specific source,
model acquisition, catalog/case/calibration and setting/host changes remain
separate. Dispositions: create F3 runtime and runtime/stack tests, executable
F3 wrapper script and review-only download manifest; update F3 service/generation/
consumer/lifecycle/wrapper plus its task/evidence/quickstart/decision records;
preserve Stage1/API/F1/F2, all governance, specs/plans/contracts/checklists,
locks, native environment and existing packaging. No official internals edited.

Implementation queue T033–T037 is wired. F3-owned fresh workers preserve the
unchanged F1 embedding/chunk/index and F2 inventory/search/receipt algorithms.
Factory verifies actual kernel caps plus approvals/hashes/config/case bindings
before tokenizer/model startup or input; READY is private until those checks pass.
Typed live query/generation adapters share the outer F2 lock. Search count is
recorded immediately before actual HTTP query send, generation count before actual
model.generate. Parent independently records worker start identity/group/cgroup;
original absence is checked after stop, reused PIDs are never signaled.

Owned wrapper creates only a unique internal two-container stack from existing
image IDs with explicit read-only mounts and unchanged caps. Actual tmpfs and
storage DNS alias are verified. It keeps full-line output acknowledgments and
original host/VM deadline bounds. Delegated stage reductions reach the hard
supervisor. Immutable teardown survives forwarding exceptions/repeated signals;
collection, group, container/network absence uncertainty is nonzero. Lost create
replies are recovered only by exact unique labels plus owned names and verified
IDs inside the same Docker30 cleanup budget; no global prune. Optional case
mounts and preflight are implemented. Ingest EOF moves to a distinct bounded
case phase; five native frozen-case fixtures produce six actual envelopes after
one ingest, without stdin replay or expectations in model context.

Observed REDs: eight kernel-limit stub failures, approval mismatch reaching model
startup, outer count1 versus actual worker count0, wrapper stubs, missing storage
alias, evaluation EOF entering teardown, lost teardown clock, discarded original
registry identity, missing lost-create recovery and delayed first evaluation case
under an expired input deadline. Corrected then GREEN. Missing test imports/
configuration hooks were fixture errors, not behavioral RED. Review reproduced
leader reaping before descendant stop; regression verifies KILL while direct PID
remains reserved. Official Linux/macOS WNOWAIT observation precedes reap. Scoped
native failures/absence are still not actual Linux model/Docker proof.

T038 local deterministic checks and T046 local CI now observed, marked complete.
T033–T037 retain unchecked whole-task markers where live enforcement/integration
observations are unrun; this is no longer a queue of unbuilt factory/wrapper code.
T003/T004/T041–T045 remain acceptance/approval gates. Exhaustive foundation/adversarial
subcriteria elsewhere remain explicitly unchecked, not inferred from a suite count.
README navigation is preserved; quickstart now describes the implemented CLI,
required tmpfs proof and actual optional evaluation/measurement flow.

Official CPU Torch2.14.1+cpu CPython3.12 manylinux_2_28 x86_64 wheel and
Transformers5.18.0 Python>=3.10/universal wheel verified before Docker installation.
Official Transformers SHA256 matches unchanged requirements.f1.lock. Authorized
hashed-lock F3 image build succeeded; source-free read-only/network-none container
observed Python3.12.15/Linuxx86_64/glibc2.41/Torch2.14.1+cpu/Transformers5.18.0,
threads4/interop1, no weights loaded or sources processed. No native install.
Ten GiB remains a planning allocation, not a physical minimum. Runner/Qdrant peak
and transport-latency measurement code exists; selected-model measurements wait
for acquisition and reviewed source/evaluation gates. No capacity enlargement.

Actual final commands, tested identities, warnings, preservation and unrun live
checks are recorded in validation.md. Independent final read-only review and
controlled fixtures do not claim live quality/acceptance. Only local images and
container dependencies acquired; no model/source acquisition/processing, license
grant, Docker settings, commit, push, PR or publication.


### 2026-10-04 EDM approval, acquisition and genuine state measurements

EDM confirmed owner/reviewer/contact and approved all prepared proposals; evidence
in session-approval.json. T004 approval/asset/hash criteria now observed: approved
six-file generation snapshot acquired, upstream identities distinguished from local
SHA256, generation-assets.json verified; unchanged Docker caps and approved runtime
used. T003 remains partial: exact sources, F1 manifest, catalog and genuine F2/F3
purpose receipts created; evaluation-cases.proposal.json remains a proposal until
the newly measured numerical separator/configuration/case binding is reviewed.
Do not treat the older source decision reference as approval of a future fingerprint.

Calibration full candidate sets: four fixed cases, exit0, search1each; minimum
supported0.7199879, maximum negative0.19230622; proposed midpoint
0.45614706000000005/calibration EDM-f2-20261004-v1. Specific review requested per
unchanged F2 plan before held-out/F3 acceptance. No held-out or generation outputs
were used to tune expectations. Genuine same-session neighbor isolation, approved
shorter replacement, obsolete IDs absence, selected scope clear, neighbor preserved,
collection/stack absence all pass; state check search0/generation0. T041 retains
whole-task marker pending reviewed held-out and wrapper-level predecessor acceptance.

Real pinned-model offline tokenizer and FP32 load pass:15.93s/2.72GiB; calibration
runner1.08GiB/Qdrant0.39GiB with8.13–8.27s per search. Selected-model full-stack
answer-generation peak/latency not measured; ten GiB remains a planning estimate.
T042–T045 remain live acceptance criteria, not unfinished local wiring. Resource
criteria FR/SC trace remains in the table above; actual cap checks/probe observations
are partial evidence only, not inferred timeout/OOM/generation/citation acceptance.

Latest checks:389pytest tests pass, one existing warning, Ruff and diffcheck exit0;
100 protected original paths unchanged. Full details, failed temporary measurement
attempts, cleanup and safe metadata in validation.md; current concise decision table
in continuation-decisions.md. No production code changes in this continuation; only
approved fixtures, acquisition assets/receipts and F3 evidence/status documents.
No Docker setting changes, native installs, commits/pushes/publication.


### 2026-10-05 frozen provisional candidate and actual acceptance failures

User explicitly froze0.45614706000000005/calibrationEDM-f2-20261004-v1 as a
provisional evaluation candidate and authorized held-out/F3 evaluation. T003's
approved final case/manifest/catalog/configuration bindings are created; threshold
candidate remains frozen and original proposal/cases preserved. All expected
results remain unchanged. Protected spec/plan/contracts/governance untouched.

Actual F2 held-out4/5:proof false negative, other supported rank1, both negatives
no_match; no foreign-scope evidence. T041 remains incomplete due failed retrieval
acceptance. Under explicit user evaluation authorization, genuine F3 factory and
normal wrapper tested the same frozen cases: supported0/3/output_too_large after
exactly one search/generation each; negative2/2 with zero generation. T043 remains
failed, grounding/citation acceptance unproven. T044's two live negatives observed
pass; no broad semantic abstention claim. No expectation weakening/retries/repair.
T042 selected generation peaks observed~3.03GiB; unchanged caps and real cleanup
verified. T045 retains wider fault/current-answer scope criteria not claimed from
state-only checks. Collection/stack absent, fresh389tests/Ruff/diff checks pass;
100 protected original paths unchanged. Full times/memory/actual exits/proposed
corrections in evaluation-results.md. No production fixes, downloads, settings,
commits/pushes/publication in this evaluation.
