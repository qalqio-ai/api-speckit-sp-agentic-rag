# Feature Specification: F3 — Grounded answers with citations

**Feature Branch**: `reconciled-governance-starter` (preserved; no branch created)
**Feature ID / directory**: F3 / `specs/003-f3-grounded-rag`
**Created**: 2026-10-02
**Status**: Question/claim boundary clarified on 2026-10-03; remaining design review pending; no implementation or runtime approval
**Input**: User description: "F3", resolved against the reconciled learning roadmap

## Identity and outcome

Stage 2 appends ordinary question → evidence → answer behavior to the existing
repository. A local learning-demo operator needs a concise factual answer whose
claims can be checked against approved passages from the current request. This
F3 slice uses the user-selected boundary of exact reviewed question aliases and reviewed claim
wording in a closed-domain grounding catalog. An unseen alias is outside the supported
question boundary even when passages might answer it; it receives unsupported_question
with zero generation attempts. The user selected this requirements boundary on
2026-10-03; detailed design and implementation still require approval. This is not
general semantic question answering. When
those passages do not support an answer, the operator receives explicit insufficient
evidence. A failed dependency must remain distinguishable from insufficient evidence.

Authority: [AGENTS.md](../../AGENTS.md), the sole active
[constitution](../../docs/constitution.md) and [adoption boundary](../../docs/evolution-path.md).
Context: [roadmap](../agentic-rag/roadmap.md),
[runbook learning ladder](../../docs/Foundational_Multiuse_API_SpecKit_Superpowers_Runbook.md),
[F2 requirements](../002-f2-retrieval/spec.md),
[F2 design](../002-f2-retrieval/plan.md),
[F1 ingestion](../agentic-rag/f1-ingestion/spec.md) and
[R1 contract](../001-list-use-case-sources/spec.md).
The generated constitution placeholder remains inactive.

## Clarifications

### Session 2026-10-03

- Q: Should F3 answer only pre-reviewed question wording, or also new paraphrases that its retrieved evidence supports? → A: Option A (user replied "recommended"): support exact reviewed question aliases and claim wording; unseen questions abstain without generation. This selects the requirements boundary only, not implementation or model/corpus runs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect a supported cited answer (Priority: P1)

As a demo operator, I want an answer to a supported question with citations attached
to its factual claims so I can inspect both what was said and why it is supported.

**Why this priority**: This is the ordinary-RAG learning outcome beyond F2 evidence.

**Independent Test**: Use controlled retrieved passages and a controlled answer to
verify claims/citation validation independently; subsequently run reviewed paraphrases
with real retrieval and generation, reviewing every factual claim against its cited text.

**Acceptance Scenarios**:

1. **Given** approved current passages that support a reviewed return question,
   **When** the operator asks a paraphrase, **Then** the answer preserves every
   applicable supported condition and each factual claim cites its supporting passage.
2. **Given** several retrieved passages, **When** only some support the answer,
   **Then** citations reference those supporting passages, not merely the first result
   or an unrelated passage with a valid identifier.
3. **Given** a changed source revision, **When** the next question is answered,
   **Then** only current evidence from that request is cited; prior answers or obsolete
   passages do not supply facts.
4. **Given** identical source identifiers in neighboring use cases, **When** one
   exact use case is selected, **Then** its answer and citations contain no facts or
   passages from its neighbor.

### User Story 2 - Recognize insufficient or conflicting evidence (Priority: P1)

As a demo operator, I want the system to state when it cannot support an answer,
including when relevant-looking passages omit the requested fact or disagree.

**Why this priority**: A plausible invented policy defeats the grounding boundary.

**Independent Test**: Provide empty evidence, unrelated high-scoring passages,
partially supported requests and conflicting current claims; inspect abstention and
verify no unsupported factual answer is exposed. Live unsupported cases are separate.

**Acceptance Scenarios**:

1. **Given** successful retrieval with no qualifying passages, **When** answering is
   requested, **Then** the result is insufficient_evidence with no factual answer or
   citations, and no generation is attempted.
2. **Given** a return policy but no shipping policy, **When** asked about international
   shipping, **Then** the result is insufficient_evidence; it does not infer a shipping
   restriction or permission from silence, even if retrieval found the return policy.
3. **Given** evidence for only part of a multi-part question, **When** the complete
   question is evaluated, **Then** it abstains for the request rather than silently
   omitting an unsupported part or mixing supported and invented claims.
4. **Given** current passages that conflict on a fact required by the question,
   **When** answering is requested, **Then** it reports conflicting_evidence as the
   insufficient-evidence reason, without choosing a policy unsupported by an explicit
   approved precedence rule. Unrelated disagreement does not itself force abstention.
5. **Given** the model explicitly declines for insufficient support, **When** its
   response is validated, **Then** the result is insufficient_evidence, not a fabricated
   answer, dependency failure or assertion that the real-world policy does not exist.

6. **Given** evidence that could answer an unseen question alias, **When** submitted,
   **Then** it returns unsupported_question with zero generation and clearly identifies
   the selected catalog limitation.

### User Story 3 - Understand controlled failure and trust boundaries (Priority: P2)

As a demo operator, I want invalid input, failed dependencies and invalid model
responses reported safely, with clear mode and budget information.

**Why this priority**: Controlled failure and untrusted-content handling make the
baseline inspectable before adding the F4 agent loop.

**Independent Test**: Inject invalid input, forged citations, valid IDs with unsupported
claims, malformed/overlarge responses, source instructions, timeouts and uncertain
worker cleanup. Count retrieval/generation attempts and inspect safe outcomes.

**Acceptance Scenarios**:

1. **Given** missing/unknown scope or an invalid question, **When** submitted,
   **Then** it is rejected before retrieval or generation, without falling back to a
   different scope. F2's question limits apply without relaxing them.
2. **Given** failed retrieval or unavailable generation, **When** answering is
   requested, **Then** it reports failed with zero answer claims/citations; failure is
   never labeled insufficient_evidence.
3. **Given** malformed model output, unknown/foreign/stale citation IDs, or a claimed
   answer that fails grounding validation, **When** checked, **Then** it reports failed
   with a fixed safe reason and emits no partial answer. It does not retry or repair.
4. **Given** instructions embedded in retrieved text or a question that requests
   secrets, tools, scope changes or policy overrides, **When** processed, **Then** the
   system performs zero such actions and preserves its answer/abstention boundary.
5. **Given** deterministic test mode, **When** a scripted response passes,
   **Then** the result is labeled deterministic and is not evidence of live generation.
6. **Given** timeout, interrupt, close or uncertain descendant termination,
   **When** work stops, **Then** no further input is accepted after a fatal failure;
   owned resources are removed or cleanup uncertainty is explicitly reported.

### Edge Cases

- Nonblank Unicode questions, whitespace-only input and the exact F2 byte/token limits.
- Empty verified scope versus unknown, incomplete or unavailable scope.
- Relevant-looking passages with no support for the requested proposition.
- Conditions split across passages, overlapping text and duplicate citation references.
- Correct citation identity attached to an unrelated or contradictory claim.
- Missing citations, invented identifiers, altered quote/location or an obsolete revision.
- Unsupported extra detail inside an otherwise supported answer; no partial emission.
- Multiple requested facts with only partial support; conservative whole-request abstention.
- Source text instructing the model to answer without evidence or contact another service.
- Context or output over the approved bound; no silent truncation that changes meaning.
- Model requests another search/tool or emits an action instead of a final answer.
- Dependency failure, original deadline exhaustion, stalled output and uncertain cleanup.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Accept one nonblank question and one exact approved use-case identity
  per request; preserve F2 input limits/validation and reject invalid input without
  retrieving, generating or using a default scope.
- **FR-002**: Perform one F2 retrieval operation, with at most one evidence search,
  over the current ready approved scope. Preserve F2's threshold, ranking, provenance,
  revision, readiness and failure rules. No second search, refinement or reranking.
- **FR-003**: Supply generation with only the question, governing answer rules and
  verified evidence returned for this request. Use no other corpus, previous answer,
  session history or model recollection as factual evidence.
- **FR-004**: If retrieval succeeds with no qualifying evidence, return
  insufficient_evidence without invoking generation. If retrieval fails, return failed
  without invoking generation; an invalid request returns rejected.
- **FR-005**: With nonempty verified evidence, make at most one generation attempt
  to produce either a concise answer or insufficient_evidence for a reviewed supported
  alias whose complete support passes catalog checks. Unknown aliases and failed
  coverage/conflict preflight abstain without generation. No automatic retry,
  model-selected action, query rewrite or repair call is allowed.
- **FR-006**: An answered result MUST consist of at most five factual claims, each
  supported by one or more citations attached to that claim. Claim wording MUST
  exactly match its reviewed catalog rendering; unseen aliases are outside this
  slice even if the passages might answer them. Preserve material
  conditions, quantities, exceptions and uncertainty in the supporting evidence.
  Unsupported extra facts or unsupported portions of a request prevent an answer.
- **FR-007**: Each citation MUST resolve to a passage returned in this same request,
  with exact use-case/source/chunk identity, title, revision, content fingerprint and
  original location. Deduplicate references without losing claim-to-passage links.
  Do not invent a source URI or treat a retrieval score as proof of claim support.
- **FR-008**: Assess claim support as well as citation identity before exposing an
  answered result. A valid ID attached to unrelated evidence MUST fail validation.
  The selected boundary uses reviewed catalog claim/coverage rules and current
  supporting passages. Detailed validation design and its limitations require planning review;
  citation checks or historical evaluation results alone cannot supply this check.
- **FR-009**: Return insufficient_evidence with a bounded reason of no_evidence,
  unsupported_question or conflicting_evidence when a valid completed request lacks
  full support, falls outside the reviewed alias boundary, or contains a material
  unresolved evidence conflict. conflicting_evidence requires runtime-verified relevant
  opposing support or a reviewed negative alias bound to matching current source
  rules; a model-only conflict allegation fails as invalid_model_response. Emit no factual
  answer claims or citations with this status. Do not assert that absent policy does
  not exist; operator review may resolve uncertainty outside this request.
- **FR-010**: Distinguish answered, insufficient_evidence, rejected and failed in a
  closed, validated result. Malformed output, invalid citation/grounding, exceeded
  bounds or dependency failure yield failed with no partial claims/citations and a
  fixed safe reason. Expose no raw model response or exception in failure output.
- **FR-011**: Treat the question and source text as untrusted data. Neither can
  change scope, governing rules, budgets, model destination or permissions. Tools,
  browsing, executable source instructions and consequential actions are unavailable.
- **FR-012**: Bound the entire request, including retrieval, generation, validation,
  output transfer and serialization, to 240 seconds. Preserve F2's stage ceilings
  within the remaining original deadline; reserve termination time rather than
  resetting a deadline or extending it after a signal. Stop fatal sessions and apply
  one owned cleanup deadline of at most 45 seconds, reporting unverifiable residue.
- **FR-013**: Fail closed on context/output limits before exposing a partial answer.
  Planning MUST define numeric input, context, output, memory and generation-stage
  ceilings compatible with the reviewed local model and 240-second total. No silent
  evidence/question truncation, resource acquisition or fallback to a different model.
- **FR-014**: Keep generation local for this slice and acquire/run no new model or
  dependency without specific approval. No hosted transfer, credentials, runtime
  download or paid service. Missing approved assets remain unavailable, not a reason
  to substitute scripted output or silently widen permissions.
- **FR-015**: Retain questions, answer context and model output only in request/run
  memory until request/run disposal; persistent end-user memory remains disabled.
  Preserve the approved temporary index lifecycle. Do not log raw questions, source
  text, model output or secrets. Any retained cases/results/traces require explicit
  access, retention, correction/deletion, expiry and destination decisions first.
- **FR-016**: Expose request/run identity, mode, effective limits, retrieval settings,
  actual model/configuration identity when available, attempt counts, elapsed time
  and controlled outcome so operators can distinguish deterministic and local_live
  evidence. Metadata never supplies source-use, model or retention authorization.
- **FR-017**: Use only actually approved synthetic source tuples/revisions and
  separately reviewed question/expected-claim cases. Existing F1/F2 approvals do not
  automatically approve new data, F3 processing or model use. Freeze corpus,
  retrieval settings, model configuration and expected claims before live acceptance.
- **FR-018**: Preserve Stage 1, F1 and F2 public behavior, tests, environment and
  approval boundaries. Add no RAG behavior to the existing API request path or health
  checks. R1 unknown scope retains HTTP404 with exactly
  `{"detail":{"code":"unknown_use_case"}}`. No installation, commit, push, PR or
  publication is authorized by this specification.

### Key Entities *(include if feature involves data)*

- **AnswerRequest**: Exact use-case identity and one question; no conversation history
  or caller-supplied evidence/model destination.
- **RequestEvidence**: F2 passages and retrieval outcome/settings from this request,
  tied to approved current source identity and original location.
- **AnswerClaim**: One factual statement and references to the evidence supporting
  it; material conditions remain part of its support assessment.
- **Citation**: Exact pointer to a current returned passage and its provenance,
  associated with one or more supported claims.
- **AnswerResult**: Controlled outcome, claims/citations only when answered, bounded
  abstention/failure reason and safe execution metadata.
- **EvaluationCase**: Reviewed question/scope, expected supported claims or abstention
  reason, acceptable evidence identities and frozen source/model/settings versions.
- **ExecutionLimits**: Original request deadline, attempt counts and reviewed resource
  ceilings; no model or source can modify them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least three reviewed supported paraphrases in local live evaluation
  produce answers containing all required expected claims/conditions, with every
  factual claim supported by its cited evidence and zero unsupported extra claims.
  These are observed outcomes for frozen reviewed exact question aliases, assessed
  claim by claim. Accepted factual claim wording must match its reviewed catalog
  rendering exactly; different question paraphrases still require actual generation.
- **SC-002**: For every answered deterministic and live acceptance case, 100% of
  citation references resolve to the current returned passage in the selected scope,
  and 100% of factual claims have supporting citations. Correct IDs alone do not pass
  SC-001 or semantic grounding review.
- **SC-003**: At least two reviewed unsupported live questions, including missing
  international-shipping policy, yield insufficient_evidence with zero factual claims
  or citations; deterministic empty, partial-support and material-conflict cases also
  abstain under the specified reason. An unseen but otherwise answerable question
  also abstains as unsupported_question with zero generation; report this as the
  catalog restriction, not proof of general semantic abstention.
- **SC-004**: Every deterministic invalid-output, dependency-failure and grounding-
  failure case returns rejected/failed as appropriate, with zero partial answer
  claims/citations and no raw input, model output, exception or secret disclosure.
- **SC-005**: Every request in deterministic budget/adversarial cases uses at most
  one retrieval search and one generation attempt; empty evidence and retrieval
  failure use zero generation attempts; all cases use zero tools, refinements,
  hosted transfers or persistent memory writes.
- **SC-006**: In controlled clock/stall/interrupt cases, each request completes or
  fails within 240 seconds and owned teardown within 45 seconds from its original
  start; no timeout or repeated signal resets a budget. Record actual live elapsed
  times and cleanup results separately; historical passes prove neither.
- **SC-007**: Cross-scope/shared-ID, replacement and clearing acceptance cases expose
  zero foreign, obsolete or unverified facts/citations. Unchanged Stage 1/F1/F2
  regressions pass before acceptance, and every owned resource is confirmed absent
  or explicitly reported as unresolved cleanup failure.
- **SC-008**: Every reported acceptance result identifies deterministic or local_live
  mode and the tested source/model/configuration/expected-case identities. If real
  generation cannot run, live outcomes are reported unverified; test fixtures,
  citation shape and successful packaging are never counted as live grounding proof.

## Assumptions

- "F3" means the roadmap's Grounded RAG slice, not F4's agent loop. The fictional
  return/shipping scenario is a proposed learning case, not approved source content
  or real policy. Exact sources and expected claims still need actual approval.
- A local operator is the initial audience. Local-only generation follows the existing
  local learning boundary; a hosted model would change this spec and require explicit
  data-access/cost review. No model or generation runtime is selected here.
- Proposed small-demo limits are five factual claims and a 240-second whole-request
  ceiling, allowing retrieval's existing maximum without claiming measured latency.
  Numeric generation/resource limits belong to the model compatibility plan and
  require review before implementation; the whole-request ceiling cannot be relaxed
  silently. Shared 45-second cleanup remains unchanged.
- F2 is designed and has 46 unexecuted tasks, not an implemented or accepted dependency.
  F3 may be specified now; integrated F3 live acceptance requires verified F2 first.
  Controlled seams can test contracts but cannot establish predecessor completion.
- Supported questions are exact unnormalized (use case, question) aliases in the
  reviewed catalog, as selected by the user on 2026-10-03; approved claim renderings
  define accepted output wording. Broader
  question/claim paraphrasing or a semantic verifier requires a reviewed scope/design
  revision. These document edits do not supply implementation or corpus approval.
- Full-question support is required. Partial answers, interactive clarification,
  external policy resolution, agent decisions, session memory, tools, UI, new public
  HTTP routes, runtime migration and publication are outside this slice.
- Plan the operator interface, closed answer/model contracts and grounding assessment
  before building. Do not assume an existing embedding model can generate answers.

## Decisions and approval gates

| Decision | Owner | Status / actual approval evidence | Needed before |
| --- | --- | --- | --- |
| Requirements and proposed demonstration limits | User / maintainer | Draft from `$speckit-specify F3`; not implementation approval | Implementation planning approval |
| Local model/runtime, compatibility, resource caps and model rights | User / runtime reviewer | Unselected; no acquisition/reuse/run decision inferred | Final plan and any acquisition/run |
| Supported question/claim boundary | User | Option A selected on 2026-10-03 via "recommended": exact reviewed aliases/renderings; unseen aliases abstain without generation | Resolved requirements decision; no execution approval |
| Interface, closed answer contract and grounding assessment mechanism | User / design reviewer | Catalog requirements boundary selected; concrete design and failure limitations still need review | Implementation |
| Exact synthetic source/case approval, classification/access/redistribution and F3 purpose | Actual source owner / user | Pending; no corpus or approval receipt created | Source creation/reuse/processing |
| Expected claims, insufficiency/conflict cases and frozen acceptance settings | User / evaluator | Criteria specified; approved cases and observed outcomes absent | Live acceptance |
| Retained evidence access/location/expiry/correction/deletion | User / data owner | No retention authorization inferred | Any stored cases/results/traces |
| F2 acceptance and F3 implementation/build/run authorization | User / maintainer | F2 unimplemented; F3 documentation only authorized | Relevant implementation/live gates |

## Acceptance and verification boundaries

Write/run new behavioral tests before production changes; confirm failures describe
missing behavior rather than a broken environment. Cover each scenario and edge
case, including valid citations with unsupported claims. Preserve and rerun relevant
R1/F1/F2 tests. Approved live evaluation separately reviews retrieval, each claim's
semantic support, exact provenance, abstention, latency and cleanup. Human acceptance
review does not replace runtime grounding checks. No successful outcome is claimed
by this document or its quality checklist. [Local release guidance](../../docs/release.md)
remains authoritative; no build, live evaluation or external action occurs here.
