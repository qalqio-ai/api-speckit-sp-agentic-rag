# Implementation Plan: F3 — Grounded answers with citations

**Branch**: `reconciled-governance-starter` (unchanged) | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)
**Input**: `specs/003-f3-grounded-rag/spec.md`; `$speckit-plan F3` authorizes design only.
**Status**: Planning reconciled on 2026-10-03 with clarified catalog requirements;
detailed design/execution approval pending; no implementation.
The setup script reports feature identifier003-f3-grounded-rag as BRANCH; actual git
branch above is unchanged. Sole constitution is [docs/constitution.md](../../docs/constitution.md).

## Summary

Compose one F2 retrieval with at most one real local generation attempt. Validate
current provenance, reviewed whole-question support, exact accepted claims and citations
before returning answered. No evidence/unknown coverage/material conflict abstains;
dependency or invalid model output fails safely. Preserve Stage1/F1/F2 behavior.

The user-selected grounding boundary supports only reviewed exact question aliases
and claim wording. The [2026-10-03 clarification](spec.md#session-2026-10-03) records
Option A (user reply: "recommended"). Unseen aliases abstain without generation, even
when evidence might answer them. This is a closed-domain limitation, not general
semantic verification. Requirements selection does not approve detailed design,
implementation, model/corpus processing or live runs. Research and alternatives are in
[research](research.md); detailed algorithm/schema are in [contracts](contracts/answer-cli.md).

## Technical Context

**Language/Version**: Native Stage1 Python3.10 environment unchanged; dedicated Linux
Python3.12 runner reuses F1 base identity and hash-locked dependency stack.
**Primary Dependencies**: Existing Transformers5.18.0, Torch2.14.1+cpu, embedding stack
and Qdrant1.19.1; proposed SmolLM2-360M-Instruct revision
`a10cc1512eabd3dde888204e902eca88bddb4951`. No new schema/NLI/serving dependency.
**Storage**: Existing owned256MiB Qdrant tmpfs; request memory only. Immutable approved
model/catalog/cases mounted read-only; no retained content by default.
**Testing**: Native pytest/Ruff with injected clocks/tokenizers/model/F2 seams, then
separately approved actual pinned CPU runtime and semantic acceptance.
**Target Platform**: Linux x86_64 CPU container; Intel host observed, available host
RAM unknown. No native model installation or migration.
**Project Type**: Separate local CLI/library composition, no new HTTP endpoint.
**Performance Goals**: Whole request240seconds; F2 retrieval120 within remaining total;
generation110 including cold load/hash/tokenization/decode/IPC/stop; grounding and
final validation/serialization share10seconds after retrieval plus remaining total.
**Constraints**: Prompt64KiB and2,048 generation tokens (template included), completion384
new tokens/16KiB, <=5 claims; runner8GiB cgroup memory incl descendants, four CPUs;
Qdrant1GiB cgroup memory and256MiB storage tmpfs. These ceilings are proposals, not
observed memory needs. Fail unavailable on insufficient approved host/Docker capacity.
**Scale/Scope**: One operator, sequential operations, reviewed question aliases and
approved synthetic sources; one search/one generation, zero retries/tools/memory.

## Constitution Check

Gate review before research and after design uses the sole project constitution;
generated Spec Kit placeholder is inactive. No policy exceptions are proposed.

| Principle | Pre-research gate | Post-design disposition |
| --- | --- | --- |
| User intent | F3 ordinary RAG only | Exact-alias/exact-claim boundary selected in clarification; detailed design and execution remain gated |
| Evidence before answers | Current F2 provenance required | Complete reviewed support rules plus actual model output validation; no citation-only proof |
| Untrusted content | Sources are data | Closed protocol, no actions, only reviewed claims and exact evidence allowed |
| Human authority | No execution inferred | Specific source/model/runtime/retention approvals remain gated |
| Least privilege | Local synthetic learning scope | Offline no credentials/downloads; owned network/tmpfs and resource ceilings |
| Explicit memory | No persistent user memory | Request memory and index lifetime separated; no content logging |
| Testability | Deterministic plus actual live evidence | Semantic support, citations, abstention and attempt counters evaluated separately |
| Simplicity | Fixed baseline | No agent loop, NLI, persistent model worker, tool or reranker |
| Minimal observability | Safe IDs/budgets only | No raw question/model/context diagnostics; capture policy before retention |
| Reviewability | Preserve all existing work | Spec unchanged; six design artifacts; pending decisions visible |

Documentation/research and post-design constitution gates pass for the selected
requirements boundary. Implementation gate is closed pending detailed requirements/
design approval and source/model/cost/capacity/retention decisions
for the applicable action. Verified F2 and its internal receipt integration additionally
gate real F2 composition and integrated/live acceptance; they do not block separately
authorized synthetic injected F3 implementation. No active constitution is altered or duplicated.

## Project Structure

### Documentation (this feature)

```text
specs/003-f3-grounded-rag/
  spec.md                         # preserved requirements
  checklists/requirements.md       # preserved quality review
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/answer-cli.md
  contracts/serialization.schema.json
```

### Source Code (repository root; proposed only)

```text
app/answer/
  __init__.py
  __main__.py      # owned supervisor/session and JSONL dispatch
  validation.py   # closed records and limits
  grounding.py    # catalog/coverage/current-support validation
  generation.py   # fresh local model worker
  service.py      # F2 composition; original deadlines/shared busy guard
  demo.py         # owned stack wrapper
  evaluation.py   # frozen cases consumer
scripts/f3-demo.sh
Dockerfile.f3
compose.f3.yaml
tests/test_answer.py
tests/test_answer_cli.py
tests/fixtures/f3/ # only after exact content/purpose/retention approval
```

**Structure Decision**: Separate F3 code and packaging; compose F2 service without
editing its public contract. Proposed paths do not exist and are not created here.

## Approach, boundaries and dispositions

1. Freeze actual approved manifest, F2 retrieval receipt, F3 purpose receipt, model
   asset manifest and GroundingCatalog. Approval shape never supplies consent.
2. Parent supervisor stays outside owned session process group; factory, F1/F2
   service and all query/generation/storage descendants stay inside. Startup<=120
   includes model asset validation and a supervised tokenizer/config probe. Fresh
   generation worker hashes/loads model per request; parent never loads live weights.
3. An F3 outer dispatcher lock covers answer from retrieval through output validation;
   F2 owns its normal busy guard during retrieval, then F3 holds that service guard
   for generation/output. No concurrent entry point or callback can mutate the registry
   during handoff; do not call F2 while F3 already owns its busy flag.
   Adapt F2 with deadline=min(request start+120, original F3 deadline); no fresh hidden
   stage budget, mutating inspect, reopen or extra search. Nonfatal failures preserve
   source readiness; fatal failures use existing invalidation and owned cleanup.
4. Retrieve top_k3 under reviewed threshold/calibration settings. Validate exact
   reviewed question coverage and all support/conflict rules against the selected
   scope/current returned passages. Unreviewed source revision/catalog coverage fails
   closed. Do not use catalog facts as alternative evidence.
5. When complete support exists, send only question, rules and verified evidence
   with eligible claim labels/renderings derived from that evidence to one model call.
   No standalone catalog fact enters context unless its entire reviewed support is
   present in current returned passages. Missing support abstains; input/context
   overflow fails without truncation. Algorithm is normative in the CLI contract.
6. Parse strict complete JSON, validate all claim texts/IDs/citations and full coverage;
   no unapproved prose or partial answer. Reject semantically unsupported controlled
   outputs even when citation IDs are valid. Never fabricate a model result from catalog.
7. Preserve one original240-second deadline and owned45-second teardown. Bound IPC,
   output and resource allocation; verify processes and exact owned Docker resources
   even after leader death. No repeated-signal reset or shared/global cleanup.

Create these six documentation files only. Preserve spec/checklist, active feature
pointer, R1/F1/F2 app/tests/fixtures/schema/locks/packaging, native venv and governance.
Future approved implementation may create listed source/packaging/tests and update
README/.dockerignore for F3 only. Omit installs/downloads, corpus/catalog fixtures,
model manifests/receipts, tasks.md, branch changes, commits, pushes, PRs and publication.

## Verification and implementation sequencing

After actual implementation authorization: establish fresh unchanged Stage1/F1 and
available implemented F2 regressions when present; define importable behavior
stubs/injected seams independently of F2 availability; write/run
behaviorally failing tests before functional code. Corpus/runtime approvals need not
block synthetic in-memory shape/fake tests, but they gate any actual source processing,
model reuse, builds/runs and retained results.

Tests cover every schema property and semantic invariant; unknown aliases, absent
support/conditions, relevant versus irrelevant conflicts, altered quote/location,
valid IDs with unsupported claims, foreign/revision/stale catalog, missing/extra
claims, explicit model abstention, zero-generation no-evidence/unknown cases, attempt
counts, context/output limits, malicious instructions, failure/timeout/IPC/leader-death
and group/cgroup cleanup. Regression safeguards remain passing evidence, not invented RED.

Live gate requires verified F2; exact approved sources and frozen aliases/cases/catalog;
model asset hashes/runtime/config; approved capacity/build/run/retention. Record >=3
supported real-generation paraphrases and >=2 unsupported questions including shipping;
review each expected claim/condition and citation. Catalog rules and test output never
prove live generation. Unknown aliases are not evidence of broad semantic abstention.
Assess known unsupported aliases with nonempty evidence and explicit model abstention
through separate controlled probes; no scripted live result. Keep retrieval calibration
frozen; do not tune on held-out F3 cases. Report small-model invalid JSON/quality failure.

## Open decisions and actual verification

| Decision / gate | Status |
| --- | --- |
| Supported question/claim boundary | Resolved: Option A selected on 2026-10-03; exact reviewed aliases/renderings, zero generation for unseen aliases; no broader semantic verifier |
| Specific implementation/source F3 purpose/catalog/cases approvals | Pending; no content or consent invented |
| Model acquisition/reuse/rights and Linux runtime compatibility | Proposed pin; no assets acquired or runtime probe |
| Host/Docker capacity and local build/run | Unknown/unapproved; ceilings are hard constraints, not measured fit |
| Evidence retention/access/expiry/correction/deletion | Pending; operator output only unless separately approved |
| F2 implementation and acceptance | Unexecuted task list; no integrated F3 acceptance possible yet |

Setup command: `bash .specify/scripts/bash/setup-plan.sh --json`, exit0 with host
C.UTF-8 locale warning. Official template copied into active F3 directory. Research
used read-only repository and primary public documentation. Host RAM probe denied
by sandbox; no capacity result claimed. No API/runtime tests, model/Docker gate or
semantic evaluation run. Structural/preservation verification is recorded in the
completion report, not substituted for implementation or quality proof.

## Planning verification record

- Structural/link/schema-reference/preservation audit: exit0; six intended design
  artifacts,20 definitions,32 local refs and73 existing-file hashes verified. Spec,
  checklist, F1/F2/governance/locks and active feature pointer unchanged.
- JSON Schema conformance/shape probes: native Python Draft202012Validator with
  installed RefResolver and offline local store, exit0 for F3/F2/F1 schemas and
  positive/negative AnswerRequest/ModelResponse probes. Initial newer referencing
  API import failed because that optional API package is absent; installed legacy
  resolver used successfully without installation or network schema fetch.
- git diff --check: exit0. Full generated-file trailing whitespace checked separately
  because new files are untracked. No pre/post extension hooks exist.
- Host RAM probe: denied by sandbox; capacity unknown. No runtime, API/product tests,
  model load, Docker build/run, semantic grounding/corpus evaluation, installation,
  branch change, commit, push, PR or publication performed.
- At the initial planning run the grounding choice was pending. This historical gate
  was resolved by the user's 2026-10-03 clarification; detailed design/execution gates
  remain separate. Current reconciliation is recorded below.

## F3 analysis remediation — 2026-10-03

I1: Spec/SC-001/SC-003 use the exact-alias/exact-claim catalog boundary, including
answerable unseen-question abstention. The user subsequently selected that boundary
on 2026-10-03; detailed design approval remains required. No runtime is approved.
I2: T001/T005/T006 gate authorized deterministic implementation; verified F2 and the
bridge below gate real composition/live acceptance, with action-specific data/model gates.
U1: The normative internal retrieve_with_receipt port in the CLI contract supplies
current represented source bindings, registry fingerprint, actual dispatch count and
clamped original deadline from one F2 pipeline execution. Synthetic port tests may be
written now only after implementation approval; actual F2 internal bridge changes and
integration require explicit approved dispositions. Public F2 envelopes stay unchanged.
U2: Parent and wrapper stdout forwarding use nonblocking deadline-aware delivery,
including delegated envelopes, with bounded queues and fatal broken-pipe/stall handling.
No result is claimed delivered until the complete line transfers. Independent cleanup
never waits for output delivery or resets its original deadline.
U3: ModelResponse accepts only unsupported_question for insufficiency. Application
conflicting_evidence remains available only from verified preflight/reviewed negative
rules bound to current sources; fabricated model conflict reasons fail validation.
See CLI contract for exact rules, schema and task descriptions for implementation/tests.

## Clarification reconciliation — 2026-10-03

Phase0 reuses the pinned-model/runtime/source research and the reviewed alternatives:
clarification resolves the only open scope choice, introducing no new technology,
source data, resource ceiling or dependency. A targeted read-only research review
checks stale decision wording; no new model/source acquisition or runtime probe.
Phase1 reconciles research, data model, CLI contract and quickstart to selected Option A.
Serialization schema already enforces the matching exact-claim/closed-output design
and remains unchanged. The internal F2 receipt, bounded output delivery, application-
only conflict decision and deterministic/live gates from remediation remain normative.

Pre/post-design constitution review passes for documentation: selected scope is
explicit, approved current evidence is required, content is untrusted, consequential
permissions remain human-controlled, memory/telemetry remain minimized, behavior is
testable and changes are reviewable. No policy exception or second constitution.
Implementation needs separate approval; real F2 composition needs verified internal
port/regressions; source/model/build/run/retention approvals and empirical results
remain pending for their actions. These are execution gates, not unanswered technical
clarifications or permission to re-ask the already selected requirements boundary.

Preserve spec/clarification/checklist and existing tasks.md. A later speckit-tasks
refresh must replace its pending-choice wording with verification of the recorded
Option A decision, while retaining actual detailed-design/implementation approval
and data/model/live gates. No new tasks or product artifacts are created by this run.

### Refresh verification record — 2026-10-03

- `python3 /tmp/verify_f3_plan_refresh.py`: exit0. Exactly five intended design
  documents changed;75 protected file hashes unchanged, including spec, checklist,
  schema, tasks, F1/F2, governance, product code/tests and locks. All18 local Markdown
  links/anchors, required plan sections and document whitespace checks passed.
  Installed Draft202012Validator checked the unchanged F3 schema successfully.
- Targeted read-only research review confirmed the selected boundary introduces no
  new technical unknown; stale current choice statements were reconciled. Historical
  initial-planning and remediation evidence remains identifiable as historical.
- `git diff --check`: exit0; direct whitespace checks also cover untracked artifacts.
  No pre/post extension hooks exist. Setup exit0 with C.UTF-8 locale warning;
  setup preserved the existing plan during this refresh.
- Actual git branch remains `reconciled-governance-starter`; setup reports the F3
  feature identifier `003-f3-grounded-rag`, not a git branch change.
- No API/runtime tests or live grounding acceptance run for this documentation
  refresh. No assets acquired, corpus processed, model loaded, capacity measured,
  Docker build/run, installation, commit, push, PR or publication performed.
