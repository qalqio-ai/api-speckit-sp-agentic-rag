# Tasks: F2 — Retrieve scoped evidence

**Input**: [spec](spec.md), [plan](plan.md), [research](research.md),
[data model](data-model.md), [CLI contract](contracts/retrieval-cli.md),
[serialization schema](contracts/serialization.schema.json), [quickstart](quickstart.md).
**Created**: 2026-10-02. **Status**: Generated; all tasks unexecuted.
**Branch**: `reconciled-governance-starter`; no branch switch or commit authorized.
**Authority**: [AGENTS.md](../../AGENTS.md) and the sole active
[constitution](../../docs/constitution.md); generated constitution placeholder is inactive.
**Authorization**: `$speckit-tasks F2` authorizes this task artifact, not implementation,
source creation/processing, retained evidence, asset acquisition or local Docker runs.
**Tests**: Required by the spec and repository guidance; run behavioral RED before code changes.
**Organization**: Setup, shared foundation, US1/US2/US3 in priority order, then final gates.

## Format: `[ID] [P?] [Story] Description`

All tasks use unchecked boxes, sequential IDs, exact paths and story labels only
in story phases. `[P]` denotes separate-file work after the stated prerequisites;
it grants no authorization to delegate, install or execute external actions.

## Path conventions and preservation

All task paths are repository-relative. New product code belongs in `app/retrieval/`;
new deterministic tests are `tests/test_retrieval.py` and `tests/test_retrieval_cli.py`.
Approved future fixtures belong in `tests/fixtures/f2/`. Only approved implementation
may update `.dockerignore`/README for F2 build inputs/navigation.

Preserve `app/ingestion/`, F1 schemas/tests/fixtures/locks, `Dockerfile.f1`,
`compose.f1.yaml`, `scripts/f1-demo.sh`, Stage 1 app/data/tests/Compose/local gate,
the native venv, F2 design/checklist inputs and governance. R1 unknown use cases
retain HTTP404 with exactly `{"detail":{"code":"unknown_use_case"}}`.
No new HTTP route, hosted provider, persistent memory/index, generation, agent,
tool, package upgrade, corpus upload, commit, push, PR or publication is included.

## Phase 1: Setup (shared authorization and baseline)

**Purpose**: Prepare reviewable proposals and record actual decisions before code or data changes.
T001/T002 are preparatory; do not wait for permission to make their review concrete.
Do not infer an answer or broaden the F1 approval receipt. Execution tasks are gated
by actual approval evidence; no checked box can supply it.

- [X] T001 Review `specs/002-f2-retrieval/spec.md`, `plan.md` and this `tasks.md`; record actual requirements/plan/120-second limits and implementation authorization, working-tree create/preserve/update/omit dispositions and in-place/worktree decision in the verification record of `specs/002-f2-retrieval/tasks.md`; preserve existing work and do not claim approval from this invocation.
- [X] T002 Prepare a concrete source-use and evaluation proposal in `specs/002-f2-retrieval/tasks.md`: exact proposed source text/tuple/hash, at least two competing sources in one use case, neighbor sharing a source ID, shorter replacement, separate calibration and held-out cases (>=3 supported and >=2 unsupported held-out questions); propose owner/classification/access/redistribution, retention/deletion and local evaluation evidence destination without inventing approval or creating corpus fixtures.
- [ ] T003 After the user approves the exact proposal, record the real decision/date/reviewer in `specs/002-f2-retrieval/tasks.md`, then create only approved files under `tests/fixtures/f2/`, `tests/fixtures/f2/approval.json`, `tests/fixtures/f2/retrieval-approval.json` and `tests/fixtures/f2/evaluation-cases.json`; preserve F1 manifest shape and bind the F2 receipt to its actual SHA-256. Apply F2ApprovalReceipt constraint verbatim: "Real decision evidence binds exact read-only F1 manifest; timestamp calendar-valid; does not add sources or grant redistribution". No draft field or schema-valid receipt supplies consent. Validate evaluation-cases.json against EvaluationCaseSet plus semantic invariants before approved processing.
- [ ] T004 Record separate existing-model/locked-stack reuse, local F2 build/run and retained evaluation evidence authorization in `specs/002-f2-retrieval/tasks.md`; preserve native venv and pin the observed F1 model/server/base identities. Do not install/download/upgrade packages; missing approved assets stop the relevant live gate. Define retained evidence access, correction/deletion, location and expiry before capture.
- [X] T005 Run unchanged Stage 1/F1 baseline via `.venv/bin/python -B -m pytest tests/test_sources.py tests/test_ingestion.py tests/test_ingestion_cli.py -q -p no:cacheprovider`; record command/exit/warnings and protected-file SHA-256 values in `specs/002-f2-retrieval/tasks.md`. Establish actual baseline instead of citing historical passes.
- [X] T006 After implementation authorization, create importable signatures/explicit NotImplementedError behavior stubs only in `app/retrieval/__init__.py`, `validation.py`, `embedding.py`, `index.py`, `service.py`, `evaluation.py`, `__main__.py`, `demo.py`; add deterministic clock/tokenizer/encoder/index/service seams in `tests/test_retrieval.py` and `tests/test_retrieval_cli.py`. No functional validation, model load, search, supervisor or data processing yet; confirm imports without live dependencies and record in `specs/002-f2-retrieval/tasks.md`.

**Checkpoint**: Record evidence for each applicable prerequisite before its dependent task;
pending T003/T004 do not block authorized synthetic in-memory shape/fake work.

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: Closed records, shared safety boundary and injectable ports before stories.
**Dependencies**: T001 implementation authorization, T005 fresh baseline and T006 stubs.
T002 is a read-only proposal; T003 gates actual new/reused source processing, while
T004 gates actual model reuse/build/live run and retained evidence. These decisions
may remain pending during authorized deterministic shape/fake work. Genuine corpus
approval applies to any source processing;
schema probes use visibly synthetic in-memory shape data, never invented consent.

- [ ] T007 Write shared schema/input/receipt/result tests in `tests/test_retrieval.py` and CLI-shape probes in `tests/test_retrieval_cli.py` against importable stubs; cover every required/extra/null/enum field from `specs/002-f2-retrieval/contracts/serialization.schema.json`, strict duplicate-key/nonfinite JSON, booleans, exact untrimmed scope, valid timestamp, manifest binding, missing threshold and cross-field invariants. Include every F1 external schema reference without changing F1 validation. Include closed EvaluationCaseSet/expectation shape probes, duplicate case IDs, wrong-scope sources, fingerprint mismatches, contradictory expectations and split minima.
- [ ] T008 Run T007 tests before functional record/validation code and record expected behavioral failures with exact commands/exits in `specs/002-f2-retrieval/tasks.md`; resolve import/collection/environment failures separately. Tests that already pass are regression evidence, not RED.
- [ ] T009 Implement shared record/config/result validation in `app/retrieval/validation.py` and `service.py` after T008 using existing stdlib/F1 validators with separate F2 dispatch, no new schema dependency. Preserve RetrievalRequest constraint "Strict closed object; question nonblank <=4,096 UTF-8 bytes; top_k integer 1–10, default3; no booleans"; RetrievalConfiguration constraint "Mode deterministic/local_live explicit; generic F1-compatible encode, cosine exact; model_configuration is unchanged F1 RunConfiguration; threshold finite [-1,1]"; RetrievalResult constraint "matched nonempty; no_match empty; rejected/failed empty with fixed error; no raw question or vector". Require version2, canonical run/request UUIDs, op retrieve/null, validated scope/config nullable only as contracted, finite elapsed_ms>=0, evidence_count 0–10 equal length and error code==message from the fixed enum. Enforce receipt fields/real decision evidence separately from shape; do not implement story behavior before its RED. Validate EvaluationCaseSet semantic invariants per CLI contract independently of consent; use identical question limits.
- [X] T010 Define and implement tested shared scope-verification foundation in `app/retrieval/index.py` and `service.py` after T008: recognized approved scope, represented complete states, exhaustive read under one aggregate10-second deadline, accumulation fails at2,049 rows, expected IDs/counts/payload/config/finite384-vectors and no unknown stored rows. Add missing first-failing assertions in `tests/test_retrieval.py` before each new behavior. Preserve ReadyScopeSnapshot constraint "Internal memory only; at most2,048 total passages; unknown stored rows or incomplete states fail; no source-state writes on nonfatal retrieval failure". Snapshot registry generation through an F2-owned fingerprint/guard without modifying F1; never invoke mutating F1 inspect as retrieval verification.
- [ ] T011 Rerun foundation tests, unchanged `tests/test_sources.py`, `tests/test_ingestion.py`, `tests/test_ingestion_cli.py`, and scoped Ruff; record RED/GREEN, command/exit/warnings in `specs/002-f2-retrieval/tasks.md`. Leave semantic encoding/search/dispatcher unimplemented until their story tests fail behaviorally.

**Checkpoint**: Complete this phase under its explicit gates and record actual evidence before its dependent tasks.

## Phase 3: User Story 1 — Find relevant passages (Priority: P1)

**Goal**: One question produces bounded ranked verified evidence with exact provenance.
**Independent test**: Controlled scores rank unequal/tied passages, preserve IDs/text,
apply user limits and expose settings; after final authorized live gates, reviewed
paraphrases retrieve expected competing sources in first3. This phase alone is a
deterministic MVP; no live demonstration before US3 lifecycle and final approvals.
**Dependencies**: T011; T012/T013 share fixed foundation interfaces but edit different files.

- [ ] T012 [P] [US1] Write positive ranking/query-worker tests in `tests/test_retrieval.py`: immutable no-prompt generic encode compatibility, 384 finite nonzero vector, special-token<=256 with truncation=False and byte<=4,096, exact query/fullN<=2,048, ties larger than user k, fewer-than-k, overlap without duplicate IDs, Unicode offsets and complete provenance/settings. Reject changed hashes, prompts/router/config or token overflow before semantic encoding/search (FR-001/003/004/005/006/007; SC-001/003). Add full-candidate calibration tests where expected sources lie below a prospective threshold or outside top_k, missing expected candidates, rank>3, empty negatives and nonseparation; assert one search per case.
- [ ] T013 [P] [US1] Write US1 successful retrieval/CLI envelope tests in `tests/test_retrieval_cli.py` with injected services: default3/limits1–10, version2 fields, threshold/calibration provenance, no vectors/questions in output, contiguous ranks/counts and unchanged delegated F1 envelopes. Assert separate deterministic/live labels and no user-controlled threshold/collection/endpoint (FR-013/016; SC-003/006).
- [ ] T014 [US1] Run T012/T013 before query/ranking/dispatcher behavior and record expected failures in `specs/002-f2-retrieval/tasks.md`; preserve regression passes and separate harness errors from behavioral RED.
- [ ] T015 [P] [US1] Implement supervised query processing in `app/retrieval/embedding.py` after T014: per-worker exact asset verification/local CPU/no remote code, no effective prompt/router differences, tokenizer with specials/no truncation, <=256 tokens before generic encode, validated384 vector; validation-only mode for empty scopes. Query worker <=90seconds including cold load/hash/tokenization and reserved TERM2/KILL3, capped by remaining original120-second request deadline. No persistent worker/model/provider change.
- [ ] T016 [P] [US1] Implement one scoped exact query and complete candidate validation in `app/retrieval/index.py` after T014: POST owned `/points/query`, query384, exact=true, use-case AND source-ID AND has_id allowlists, limit=N, payload on/vectors off, no server threshold/prefetch/offset/retry. Existing transport unwraps result; require points array with complete expected ID set and matching payloads/finite scores; reject malformed/omitted/duplicate/foreign results before exposing evidence (FR-002/004/005/006/009).
- [ ] T017 [US1] Implement retrieval orchestration/ranking in `app/retrieval/service.py` after T015/T016: validate request/scope, acquire shared busy guard, verify current snapshot, query worker, one search, inclusive minimum score, sort (-score, canonical_chunk_id), slice k and produce required metadata. Preserve EvidencePassage constraint "Rank1-based contiguous; score finite; exact scope/config/revision/offsets/text; known IDs; verify payload hash against snapshot". No source mutations/repair, extra search or raw-text diagnostics; semantic failure paths remain controlled pending US3 hardening. Extract the shared complete validated candidate pipeline for retrieval and app/retrieval/evaluation.py; test then implement evaluate_cases consumption and summaries before filtering/top_k. Implement both split modes, including held-out normal top_k3, case_id association and failed-case handling; no separate search implementation.
- [ ] T018 [US1] Implement deterministic/injected F2 JSONL dispatch in `app/retrieval/__main__.py` after T017: retrieve uses F2 schema; delegate ingest/inspect/clear/close through the same F1 Service and preserve original envelopes; bounded512KiB input/draining and safe malformed/unknown envelopes. Keep live factory explicitly unavailable until supervised startup/teardown tasks pass; never reopen a lost readiness registry.
- [ ] T019 [US1] Rerun US1/foundation and unchanged Stage 1/F1 tests, lint `app/retrieval/` and test files; record results/provenance/tie/limit/count assertions in `specs/002-f2-retrieval/tasks.md`. Verify deterministic MVP without claiming live semantic search or full F2 acceptance.

**Checkpoint**: Complete this phase under its explicit gates and record actual evidence before its dependent tasks.

## Phase 4: User Story 2 — Keep evidence inside its scope (Priority: P1)

**Goal**: No foreign, obsolete, cleared or unverified passage reaches the operator.
**Independent test**: Two same-source-ID corpora, higher-scoring foreign candidates,
replacement/clear, incomplete state and stale snapshot; assert zero leaks and preserved neighbors.
**Dependencies**: T019. This hardens shared index/service files, so whole stories are sequential.
Existing correct scope checks must remain regression evidence rather than be rewritten for RED.

- [ ] T020 [P] [US2] Write scope/revision tests in `tests/test_retrieval.py`: exact/case-sensitive and shared source IDs, foreign candidate above local scores, scalar-vs-array scope payload, unknown/unregistered/never-ingested/cleared state, incomplete states, pages beyond128, repeated pagination offsets/cycles, >2,048 total rows, config/payload mutation, registry-generation changes and no readiness writes on nonfatal failure (FR-002/009/010; SC-002/003).
- [ ] T021 [P] [US2] Write same-session delegated ingest-repeat-shorter-replacement-clear-retrieve sequences in `tests/test_retrieval_cli.py`; assert exact current IDs, no obsolete/foreign text, unchanged neighbor and F1 result schema, invalid scope before question processing and reentrant/concurrent retrieval rejection. Close/fatal cases remain explicit US3 tests (FR-002/010; SC-002/007).
- [ ] T022 [US2] Run T020/T021 and record new failing behavior plus existing passing isolation regressions in `specs/002-f2-retrieval/tasks.md` before hardening; do not manufacture failures if prior phases already satisfy a case.
- [ ] T023 [US2] Resolve only demonstrated inventory/filter/pagination gaps in `app/retrieval/index.py` after T022; verify every page, cycle/cap/deadline handling, exact current expected set/config/payload and independent returned scalar scope. Never drop corrupt rows, truncate scope, resize storage, widen filters, repair corpus or call F1 inspect. If all related assertions pass already, record preserved implementation instead of redundant changes.
- [ ] T024 [US2] Resolve demonstrated same-session state/guard gaps in `app/retrieval/service.py` and `__main__.py` after T022/T023: detect snapshot generation change and reject stale evidence, share busy guard with delegated F1 mutations, preserve neighbor/current identities and nonfatal readiness. Approved never-ingested/cleared empty scope is distinct from unknown/incomplete scope; no F1 code or schema edits.
- [ ] T025 [US2] Run independent US2 isolation/replacement/clear scenario with deterministic seams from `tests/test_retrieval.py` and `tests/test_retrieval_cli.py`; compare before/after inventory/state snapshots and test zero foreign/obsolete/unverified records; record exact procedure/results in `specs/002-f2-retrieval/tasks.md`.
- [ ] T026 [US2] Rerun US1/US2/foundation and complete unchanged Stage 1/F1 regressions plus scoped Ruff; record commands/exits/warnings and SC-002 evidence in `specs/002-f2-retrieval/tasks.md`. Do not claim live corpus isolation from fake scores.

**Checkpoint**: Complete this phase under its explicit gates and record actual evidence before its dependent tasks.

## Phase 5: User Story 3 — Understand empty results and failures (Priority: P2)

**Goal**: Separate completed no-match from invalid input/dependency failure and clean up safely.
**Independent test**: Empty/below/equal threshold, malformed dependency replies, timeouts,
unconfirmed worker stop, EOF/close/interrupt and owned-resource cleanup with deterministic transports.
**Dependencies**: T026. T027/T028 are independent separate-file tests after this checkpoint.

- [ ] T027 [P] [US3] Write no-match/failure/deadline tests in `tests/test_retrieval.py`: empty scope still token-validates but skips encode/search, equality/below threshold, invalid question/limit, missing asset/config, malformed finite/vector/search payload, total120/inventory10/query90/search10 caps with remaining-time checks through serialization, confirmed/unconfirmed worker termination and preserved nonfatal state; errors return zero evidence and never false no_match (FR-007/008/014; SC-004/005).
- [ ] T028 [P] [US3] Write supervisor/session/wrapper tests in `tests/test_retrieval_cli.py`: startup<=120/F2_READY gating,512KiB draining, frozen startup threshold, EOF/close/interrupt130, failed request eventualexit1 versus rejected/no_match exit0, fatal stop/no further input, shared45-second teardown, TERM2/KILL3, worker5/collection10/Docker30, repeated-signal deadline stability, ownership mismatch/residue and zero secret/env/raw-text output (FR-011/012/013/014; SC-005/006/007). Cover leader death during active query/storage child work, inherited process-group membership, stalled/oversize IPC, reused ownership identity and descendant residue after leader exit; prove original deadlines survive repeated signals.
- [ ] T029 [US3] Run T027/T028 before lifecycle/failure changes and record expected behavioral failures in `specs/002-f2-retrieval/tasks.md`; retain passes as regression evidence and correct harness failures separately.
- [ ] T030 [US3] Implement/harden outcome/error/deadline semantics in `app/retrieval/service.py` and `validation.py` after T029: fixed contract categories/code==message, no partial evidence, empty valid/no_match distinct from unavailable dependency, status-dependent nullable config/scope, inclusive boundary and finite elapsed/count fields. All stages and final validation/serialization share original deadline; no automatic retry and no question logging.
- [ ] T031 [US3] Implement/harden query-worker fatal protocol and termination in `app/retrieval/embedding.py` after T029: reserve stop time inside90/remaining120, unexpected exit/broken protocol/unconfirmed stop fatal, controlled timeout permits only explicit later retry with fresh worker; validate-only empty mode rejects overlength without semantic encode. Propagate fatal state to existing F1 invalidation and owned cleanup without corpus repair.
- [ ] T032 [US3] Implement supervised live factory/session in `app/retrieval/__main__.py` after T030/T031: CLI parent supervises owned factory/dispatcher worker startup<=120 before F2_READY; model/tokenizer/F1 Service remain in that worker; real receipt/manifest/hash/config preflight, no unsupervised second load, shared session/busy guard, delegated F1 operations unchanged, EOF/close/interrupt/fatal exit rules and cleanup outcome preservation. Bound worker IPC/result transfer; do not add unsafe pickle model transport or unbounded joins. Parent stays outside the recorded owned session process group; all worker descendants remain inside. Implement whole-group TERM/KILL even after leader death with ownership verification and no reused-group signaling. Strict JSON IPC max16MiB/message and64KiB/frame, bounded cumulative allocation and remaining-time reads/writes; broken/stalled transport is fatal. Implement separate evaluation startup flags and ingest-only-until-EOF evaluation flow per CLI contract.
- [ ] T033 [US3] Implement dedicated owned-stack wrapper in `app/retrieval/demo.py` and `scripts/f2-demo.sh` after T032: explicit absolute model/manifest/receipt and finite min-score/optional calibration ID for normal sessions, no env-file reads/runtime pulls/builds, mount/network/project ownership proof before forwarding input, F2 image/entrypoint/markers, one45-second teardown and independently verified absence/unknown residue. Reuse F1 policy/helpers without altering F1 wrapper behavior. Support paired evaluation flags, calibration without threshold and held-out requiring reviewed threshold/ID. Independently verify owned descendant processes as well as containers/network; uncertain residue fails cleanup under the same deadline.
- [ ] T034 [US3] Create `Dockerfile.f2` and `compose.f2.yaml`, narrowly update `.dockerignore` after T033: reuse exact pinned F1 base/server/lock/model identities, internal-only network, no published ports/host networking, read-only assets/approval receipts/tmpfs proof,256MiB storage, runtime offline flags/pull never. Package local F1 and F2 schema refs; no corpus/model/secrets in image and no dependency changes. Write files only; live build/run waits for authorization.
- [ ] T035 [US3] Run all US3/lifecycle/wrapper tests plus US1/US2 and unchanged regressions; run Ruff, `bash -n scripts/f2-demo.sh` and approved parsing-only Compose validation with explicit non-secret placeholders and `--env-file /dev/null`; record commands/exits/warnings and exact rejected-vs-failed-vs-no_match/fatal cleanup assertions in `specs/002-f2-retrieval/tasks.md`.
- [ ] T036 [US3] Run deterministic adversarial/operator-output review using `tests/test_retrieval.py` and `tests/test_retrieval_cli.py`: instructions cannot change scope/threshold/search count/permissions, no generation/tools/hosted transfer, raw question/source/secret diagnostic exclusions, no vectors in evidence and no retained traces. Record results and FR-011/012/013/016 coverage in `specs/002-f2-retrieval/tasks.md`; authorize no new retention policy.

**Checkpoint**: Complete this phase under its explicit gates and record actual evidence before its dependent tasks.

## Phase 6: Polish and cross-cutting acceptance

**Purpose**: Approved real compatibility/calibration/held-out acceptance and final review.
**Dependencies**: T036; T004 actual local build/run authorization; T003 real approved
source/case receipts; retained evidence policy before any redirected/captured output.
Do not promote deterministic MVP to real semantic acceptance or silently tune held-out cases.

- [ ] T037 Run full native pytest/Ruff and `git diff --check`, compare protected Stage 1/F1/authority/F2 design hashes and confirm native F1 live packages remain absent; record commands/exits/warnings and any changes in `specs/002-f2-retrieval/tasks.md`. Broaden checks only for new changes/failures.
- [ ] T038 After T004 approval, build `Dockerfile.f2` as f2-retrieval:local using the existing hash lock/base; record actual image digest/build warnings in `specs/002-f2-retrieval/tasks.md`. Run offline model/query compatibility and actual pinned Qdrant1.19.1 query-response/filter/fullN probes under `compose.f2.yaml`; missing assets or incompatible API stop acceptance, no silent upgrades/downloads.
- [ ] T039 Under the actual approved source/retention/run gates, use `scripts/f2-demo.sh` and `tests/fixtures/f2/evaluation-cases.json` to measure separate calibration positives/negatives; record actual source/config/case fingerprints and required per-case score/rank summaries in `specs/002-f2-retrieval/tasks.md` or the approved evidence location. Apply EvaluationCase constraint "Future approved synthetic case set; held-out expectations frozen before threshold evaluation". If max unsupported >=min supported expected-source score, report nonseparation, not an invented threshold. Use --evaluation-cases/--evaluation-split calibration: evaluate_cases measures complete validated candidates before threshold/top_k, records maximum negative and best expected-source score/full rank, and fails missing candidates/rank>3/empty negatives. Never reconstruct scores from normal filtered output.
- [ ] T040 Present the measured candidate threshold/configuration/calibration record in `specs/002-f2-retrieval/tasks.md` for actual user review before acceptance; choose a reproducible finite separator only when calibration supports it, record decision evidence and freeze exact corpus/config/cases/threshold. Do not tune on held-out questions or treat calibration_id as approval.
- [ ] T041 Run frozen held-out live acceptance via `scripts/f2-demo.sh` using `tests/fixtures/f2/evaluation-cases.json`: >=3 supported paraphrases retrieve expected competing sources in first3, >=2 unsupported questions produce no_match/zero evidence, repeat/ties as applicable, shared-source-ID isolation, shorter replacement, clearing/neighbor preservation and exact provenance. Record each actual result in `specs/002-f2-retrieval/tasks.md`; failed SC-001/004 remains failed acceptance. Consume the schema-defined case set through --evaluation-split held_out with reviewed threshold/ID; validate frozen case-file SHA-256 and manifest/config fingerprints. A supported case passes if any expected source appears among first3; rejected/failed cases fail evaluation.
- [ ] T042 Run final Stage 1 gate using `COMPOSE_DISABLE_ENV_FILE=1 COMPOSE_ENV_FILES=/dev/null bash scripts/ci-local.sh`, then final F2 close/EOF/local cleanup and independent exact-project container/network absence checks for `compose.f2.yaml`; record actual commands/exits/warnings/digests/timing/residue in `specs/002-f2-retrieval/tasks.md`. Keep deterministic outage tests separate from unrun live crash/capacity/host-failure checks.
- [ ] T043 Update `README.md` navigation and `specs/002-f2-retrieval/quickstart.md` only after implementation with real runnable commands, necessary approval gates/calibration IDs and actual limitations. Preserve original spec/design/requirements-checklist criteria; any design deviation requires review rather than side-effect edits.
- [ ] T044 Create actual acceptance record `specs/002-f2-retrieval/validation.md` from verified evidence: code/source/model/config/image identities, RED/GREEN and live outcomes, all command exits/warnings, calibration decisions, cleanup/residue, protected-file checks, unrun checks and pending approvals. Separate public documentation research, deterministic, local live and external-action evidence; no claim of answer quality or release.
- [ ] T045 Review final implementation against FR-001–FR-016, SC-001–SC-007 and all data/CLI constraints in `specs/002-f2-retrieval/tasks.md`; reproduce important findings with behavioral tests in `tests/test_retrieval.py`/`tests/test_retrieval_cli.py` before fixes and rerun affected/full final gates as justified. Do not spawn review agents without specific authorization and do not weaken criteria to close findings.
- [ ] T046 Verify `specs/002-f2-retrieval/tasks.md` completion markers and `validation.md` evidence, local Markdown links/whitespace/schema references and post-implement hooks if applicable; report changed paths/rationale, actual commands/exits/warnings, unrun checks/remaining decisions/risks and external actions. Mark complete only after real gates pass; leave unmet live/approval tasks unchecked. No staging, commit, push, PR or publication.

**Checkpoint**: Complete this phase under its explicit gates and record actual evidence before its dependent tasks.

## Dependencies and execution order

```text
T001 -> T002 -> T003 (real source approval)
T001 -> T004 (real asset/build/run/retention approval)
T001 + approved implementation -> T005 -> T006
T001 implementation approval + T005 + T006 -> foundation T007 -> T008 -> T009 -> T010 -> T011
T011 -> US1 T012/T013 -> T014 -> T015/T016 -> T017 -> T018 -> T019
T019 -> US2 T020/T021 -> T022 -> T023 -> T024 -> T025 -> T026
T026 -> US3 T027/T028 -> T029 -> T030 -> T031 -> T032 -> T033 -> T034 -> T035 -> T036
T002 -> actual source approval -> T003 -> source creation/processing tasks
T003 + applicable T004 + T036 -> live T038
T036 -> deterministic T037; T038 -> T039 -> T040 (human calibration review) -> T041 -> T042
T042 -> T043 -> T044 -> T045 -> T046
```

T003/T004 may remain pending while authorized synthetic shape/fake preparation is
possible; do not process new/reused source bytes without their specific permission.
No story can bypass the T001 implementation review. Within a paired independent
branch, the execution ledger remains serially maintained to avoid shared-file edits.

Stories share service/index/dispatcher code and therefore execute US1 -> US2 -> US3;
independent testing means each story has its own controlled scenario, not that its
code can be implemented out of order. No live demo before US3 owned lifecycle.
If US2/US3 tests pass already, preserve those safeguards; only new missing behavior
requires a RED/fix cycle. Do not remove existing safety behavior to manufacture RED.

## Parallel opportunities and examples

There are four separate-file pairs after shared prerequisites, totaling eight [P] tasks:

- US1: T012 `tests/test_retrieval.py` and T013 `tests/test_retrieval_cli.py`, after T011;
  T015 `app/retrieval/embedding.py` and T016 `app/retrieval/index.py`, after T014.
- US2: T020 `tests/test_retrieval.py` and T021 `tests/test_retrieval_cli.py`, after T019.
- US3: T027 `tests/test_retrieval.py` and T028 `tests/test_retrieval_cli.py`, after T026.

Examples are work scheduling, not tool/delegation authorization. Keep fixed injectable
interfaces from T006/T009; adaptively dependent changes and test-result recording stay
sequential. No all-story parallelization or same-file concurrent edits are proposed.

## Implementation strategy

1. Prepare concrete source/runtime/retention proposals; obtain actual applicable
   decisions, preserve work and establish fresh baseline.
2. Complete importable stubs then tested foundation, keeping all live imports lazy.
3. Deliver US1 deterministic MVP: ranked bounded passages with exact provenance,
   stable cutoff ties and explicit settings. It is not full/live acceptance.
4. Add US2's independent lifecycle/isolation verification, then US3 outcome/deadline/
   startup/session/owned-wrapper checks before opening the live path.
5. Under actual approvals, verify pinned runtime, calibrate on separate cases, obtain
   threshold review, freeze settings and run held-out live criteria. Report failures.
6. Run final regressions/owned cleanup, document real evidence and review findings.
   No deployment/publication follows completion.

## Requirement and outcome traceability

| Requirement | Task coverage |
| --- | --- |
| FR-001 input limits | T007–T009, T012–T015, T027/T030 |
| FR-002 exact scope | T010, T016/T017, T020–T026 |
| FR-003 compatible offline processing | T012/T015, T027/T031/T032, T038 |
| FR-004 one search | T012/T016/T017, T027/T036 |
| FR-005 bounds/tie order | T012/T016/T017/T019 |
| FR-006 full provenance | T010/T012/T016/T017, T020/T025/T041 |
| FR-007 inclusive calibrated score | T009/T012/T017, T027/T030, T039–T041 |
| FR-008 safe outcomes | T007/T009, T027–T030/T035 |
| FR-009 verified ready revisions | T010/T016, T020–T026 |
| FR-010 unchanged corpus/lifecycle | T010/T017, T021–T026, T032/T042 |
| FR-011 untrusted content | T028/T036/T041 |
| FR-012 local/retention boundary | T003/T004/T015, T028/T033/T034/T036 |
| FR-013 safe metadata/diagnostics | T007/T009/T013, T028/T030/T036 |
| FR-014 hard deadlines/cleanup | T010/T015, T027–T035/T042 |
| FR-015 real source approvals | T001–T004/T007/T009/T032, T039/T041 |
| FR-016 deterministic/live separation | T005/T019/T025/T026/T036–T046 |
| SC-001 supported live paraphrases | T002/T003/T012/T019/T038–T041 |
| SC-002 zero foreign/obsolete/unverified | T010/T016/T020–T026/T041 |
| SC-003 provenance/order/bounds | T007/T009/T012–T019/T025/T041 |
| SC-004 no-match live negatives | T027/T030/T035/T039–T041 |
| SC-005 rejected/failed zero evidence | T007/T009/T027–T035 |
| SC-006 zero extra actions/transfers | T012/T015/T016/T028/T036/T041 |
| SC-007 regressions/owned cleanup | T005/T011/T019/T026/T035/T037/T042–T046 |

Serialized required/null/type/enum constraints come from the linked schemas unchanged;
T007/T009 validate every property, plus calendar validity, UTF-8 bytes, finite values,
strict Python integer types, known current approval/scope/provenance and cross-field
consistency that schema shape alone does not prove. All tasks are unexecuted.

## Verification record

| Stage | Exact command/procedure | Actual result / exit status | Evidence |
| --- | --- | --- | --- |
| Task setup | `bash .specify/scripts/bash/setup-tasks.sh --json` | Exit0; active F2 directory; template and four optional document entries resolved | Host C.UTF-8 locale warning; no runtime action |
| Task document audit | Native Python format/phase/path/link/constraint/traceability checks | Exit0:46 sequential unchecked tasks; US1=8, US2=7, US3=10, shared/final=21; eight parallel markers | All seven verbatim entity constraints and FR-001–016/SC-001–007 coverage checked |
| Preservation audit | SHA-256 comparison of11 existing F2/design/governance inputs and16 saved F1 snapshot files | Pass; zero existing-file changes | Only tasks.md created |
| Whitespace | `git diff --check` plus full tasks.md trailing-whitespace check | Exit0 | No whitespace errors |
| Extension hooks | Check `.specify/extensions.yml` before/after generation | Absent; no hooks dispatched | No external action |
| Implementation / behavioral RED/GREEN | Future tasks above | Not run | None; not approved by generation |
| Real semantic calibration / held-out / Docker | Future T038–T042 | Not run | No measured scores or runtime result |

Record execution results here only when observed. Checked tasks, role labels, schemas
and templates never establish approval, ownership, measured quality or publication.


## Implementation ledger — 2026-10-03 user approval

User: “Proceed with your recommendations”, following the concrete F3 approval
request, authorizes the existing F2 plan/tasks and internal retrieve_with_receipt
bridge, native implementation and proposed local capacity/build/run checks. This
is a separate explicit prerequisite action, not approval inferred from F3 roles.
Retained reports: safe metadata/claim checks in repository only, no raw traces.
Source owner/reviewer and any generation acquisition remain pending concrete values.

Dispositions: create app/retrieval, retrieval tests and separate packaging; update
this ledger/evidence and necessary ignore/navigation paths; preserve Stage1/F1
implementation/tests/contracts/lock/governance. Work in existing non-main checkout;
no branch change, commit, push/publication or dependency install.
Preflight: F2 receipt bridge produces complete represented-source bindings and
actual query-dispatch count, consumed by F3 with original deadline; never derive
source scope from returned top_k. Retrieval guard is shared with F1; F3 acquires it
only after retrieval releases. No live factory until owned startup/cleanup proven.
Capacity observed: host68719476736bytes (64GiB), Docker4101435392bytes/16CPUs.
F3 budgets cannot fit current Docker capacity; no silent budget enlargement or
Desktop settings change. Initial sandbox capacity commands denied; escalated
read-only reruns exit0. Missing source ownership means no corpus fixtures created.


### Observed native prerequisite implementation

T005 baseline exit0:113 passed/one existing Starlette HTTPX warning. Protected
Stage1/F1/constitution/locks baseline saved /tmp/f2-approved-start.json and verified
unchanged. T006 importable eight signatures and synthetic memory seams created;
functional validators/search/service followed behavioral RED, not import failures.
No corpus fixtures, consent record, model reuse receipt or assets created.

Initial shape/behavior run:11 stub failures and18 sample-generator path errors.
Fixture references corrected separately; rerun exit1 with29 NotImplementedError
behavioral failures. Implemented closed F2/F1 schema resolution, bounds/semantic
results, typed inputs, ready scope verification, current registry/payload/config
checks, pagination cycle/cap, empty token-validation and one exact fullN query.
First GREEN28/29; expired-original-deadline failure finalized safely then29/29.
Actual F1/F2/F3 class composition added; one reentrant inspect test failed, then
passed after F2 prevented delegated inspect during the shared busy guard.
Initial combined gate40/40, not real semantic or predecessor acceptance.

Scope/paging/cap/malformed current-state probes added. Independent review and
native probes reproduced premature query count and malformed server scalar payload
acceptance. Count now increments only after remaining-time checks at actual client
request boundary; expired dispatch count0, query failure count1. Search candidate
payload receives strict shape/type validation before exact snapshot comparison;
malformed dependency values map failed/invalid_search_result, not rejected input.
Inventory malformed shape similarly maps failed/index_failed. No F1 code changed.
F2 scope keeps its2,048-chunk limit; a failing33-source probe removed an accidental
F3-only32-source restriction from ordinary F2. F3 enforces its own receipt/catalog
limit and does not infer all source bindings from top_k.

Four calibration helper probes failed against stubs, then passed: full expected
source rank/score before threshold/top_k, no separator on missing source/rank>3,
empty negatives/nonseparation. These are arithmetic probes, not measured calibration,
and are not wired as a live evaluation consumer. Eight frozen case-binding/minima
probes failed against a validation stub; validator implemented. Review found one
contradiction plus cross-split question reuse; new regressions failed then passed.
Valid synthetic case questions made distinct; fixture contradictions not approved
as real evaluation evidence. No quality result or threshold review fabricated.

Three unready module-entry probes failed because empty stubs exited0. F2 CLI/demo
and F3 demo now exit1 session_unavailable without output or READY. Actual factory,
supervision/wrapper and live evaluator consumer remain unbuilt; do not call these
fail-closed gates runnable sessions. No source ingestion or live query/weights run.

Latest full gate: `.venv/bin/python -B -m pytest -q -p no:cacheprovider --tb=short`
exit0:324 passed (67 new retrieval,144 F3,113 Stage1/F1), one existing Starlette
HTTPX deprecation warning. Scoped Ruff exit0. Independent read-only review fixed
query count, strict returned scalar types and contradictory expectation findings
with fresh RED/GREEN; no reviewer role supplies corpus/model approval.
T007–T040 remain partial where full criteria/lifecycle/integration are unmet; only
T001/T005/T006 are fully marked. Never equate67 probes with full F2 acceptance.
Actual safe evidence and unrun checks recorded in validation.md.


### T002 concrete corpus/case proposal — not processed or approved

Classification: synthetic/nonpersonal; local operator only; no upload or
redistribution; index lifetime ends at demo teardown. Safe metadata only retained
in validation.md; raw questions/passages/results not captured. Owner/reviewer name
and exact new-source approval pending. These literals extend the previously
proposed F3 source into an F2 competing-source demonstration; no fixtures created.

| Scope | Source | Revision | Exact UTF-8 text (no trailing newline) | SHA256 |
| --- | --- | --- | --- | --- |
| f2-synthetic | returns | v1 | Synthetic returns: unused items may be returned within 7 days with a receipt. | `50e85780308baf9945671e2c05be5ef4fa3e02ccd805babd2b6809ee52eb841d` |
| f2-synthetic | hours | v1 | Synthetic opening hours: the shop opens Monday through Friday from 9 am to 5 pm. | `f19298916273b5ad01a43fdaa740eba1c37596049e59059f6141df6b69baa03d` |
| f2-neighbor | returns | v1 | Synthetic neighbor: unopened items may be returned within 3 days with an order number. | `17a36a6f7e0ca4f4d90a57dc56feb5bf151e654fd57101989df5b0fe42037f18` |
| f2-synthetic | returns | v2 | Synthetic returns: unused items require a receipt. | `42e29fd89ba570415acadc4555e6249e8d00c0a511e982f8abfea0bdc31ac324` |

Calibration positives: “How many days can an unused product be returned?”
(expected returns) and “What are the shop opening times?” (expected hours).
Calibration negatives: “How much does international shipping cost?” and
“Does the shop sell car insurance?” (expected no_match).
Held-out positives: “What is the deadline for returning an unused item?”
(expected returns), “What proof should accompany a return?” (expected returns),
“Can I visit the shop at four on a Tuesday?” (expected hours).
Held-out negatives: “Is overnight delivery free?” and “Is battery repair offered?”
(expected no_match). All scope f2-synthetic; exact strings and expectations frozen
before live calibration/held-out. Neighbor uses the shared returns source ID;
replacement v2 then clear f2-synthetic must preserve f2-neighbor. A separately
reviewed matching F3 catalog remains required for any replacement answer scenario.
No numerical threshold is recommended until observed calibration separates scores.
No shape-valid fixture supplies owner consent or a live relevance result.
