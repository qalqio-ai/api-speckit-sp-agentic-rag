# Feature Specification: F2 — Retrieve scoped evidence

**Feature Branch**: `reconciled-governance-starter` (existing branch; no branch created)
**Feature ID / directory**: F2 / `specs/002-f2-retrieval`
**Created**: 2026-10-02
**Status**: Draft requirements; ready for planning review, not implementation approval
**Input**: User description: "F2 retrieval"

## Identity and outcome

Stage 2 appends retrieval to the reusable API repository. A local learning-demo
operator needs to see which approved passages relate to a question, including a
paraphrase that does not copy source wording. The outcome is ranked evidence with
source identity, location, revision and a relevance score, or an explicit empty
result or controlled failure. F2 does not compose an answer.

Authority: [agent guidance](../../AGENTS.md), the sole active
[constitution](../../docs/constitution.md), and the
[adoption boundary](../../docs/evolution-path.md). Context:
[roadmap](../agentic-rag/roadmap.md),
[F1 ingestion](../agentic-rag/f1-ingestion/spec.md), and
[R1 catalog contract](../001-list-use-case-sources/spec.md).
The generated constitution placeholder is not an active policy.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find relevant passages (Priority: P1)

As a demo operator, I want to submit a question for one use case and inspect its
best matching passages so I can understand retrieval before adding answers.

**Why this priority**: Inspectable evidence is F2's independent learning outcome.

**Independent Test**: Ingest a reviewed source set in a fresh approved demo, ask a
supported paraphrase, and inspect the bounded ranked evidence. Separately test
ranking with controlled scores and records.

**Acceptance Scenarios**:

1. **Given** ready approved documents, **When** the operator asks a reviewed
   paraphrase, **Then** its expected source appears within the first three results
   in the live acceptance case, with exact source text and provenance.
2. **Given** qualifying passages with unequal scores, **When** the requested limit
   is two, **Then** at most two distinct passages appear in descending score order,
   with their scores and the effective search settings exposed.
3. **Given** tied scores, **When** the same deterministic search repeats against
   unchanged inventory, **Then** passage identity breaks ties consistently.
4. **Given** fewer qualifying passages than requested, **When** retrieval completes,
   **Then** it returns them without invented padding.

### User Story 2 - Keep evidence inside its scope (Priority: P1)

As a demo operator, I want evidence restricted to the selected use case and current
ready revisions so neighboring or superseded material cannot leak into results.

**Why this priority**: Relevant-looking evidence from the wrong corpus is unsafe.

**Independent Test**: Use two approved use cases sharing a source identifier and
control a foreign passage to score higher than local passages. Retrieve after
scoped replacement and clearing and compare exact identities.

**Acceptance Scenarios**:

1. **Given** two ready use cases sharing a source identifier, **When** either is
   searched, **Then** every returned passage belongs to the exact selected use case,
   even if foreign passages would score higher.
2. **Given** missing or unknown scope, **When** retrieval is requested, **Then** it
   is rejected before question processing or search; no default/global scope is used.
3. **Given** a verified replacement revision, **When** retrieval runs, **Then** zero
   obsolete passages from the replaced revision are returned.
4. **Given** a cleared scope, **When** searched, **Then** it returns no passages;
   the neighboring scope's unchanged evidence remains retrievable.
5. **Given** uncertain source readiness anywhere in the selected scope, **When**
   retrieval is requested, **Then** it reports readiness failure with zero evidence.
   Explicit F1 recovery and verification are required before retry.

### User Story 3 - Understand empty results and failures (Priority: P2)

As a demo operator, I want to distinguish no qualifying evidence from invalid input
or dependency failure so failure is not mistaken for absence of information.

**Why this priority**: Clear outcomes are prerequisites for later grounded answers.

**Independent Test**: Control below-threshold scores, invalid input, incompatible
processing settings and dependency failures; assert outcome and zero invented evidence.

**Acceptance Scenarios**:

1. **Given** an empty ready scope or all scores below the effective minimum,
   **When** search completes, **Then** it returns `no_match` and an empty list.
2. **Given** a score equal to the effective minimum, **When** searched, **Then** the
   passage qualifies, subject to ranking and the result limit.
3. **Given** an invalid question or limit, **When** submitted, **Then** it is rejected
   before question processing or search and returns no evidence.
4. **Given** processing/search failure, **When** retrieval cannot complete, **Then**
   it returns controlled failure and zero evidence, never `no_match` or partial success.
5. **Given** a passage instructs the system to enable tools or ignore policy,
   **When** returned, **Then** that instruction remains untrusted document text and
   causes zero actions, permission changes or additional searches.

### Edge Cases

- Blank, whitespace-only, malformed, wrongly typed or over-limit questions.
- Exact case-sensitive scope identifiers, near matches and shared source IDs.
- Empty inventory, fewer results than requested, score-boundary matches and ties.
- Distinct overlapping passages versus duplicate returned passage identities.
- Unicode text and half-open original-character offsets inherited from F1.
- Closed, cleared, incomplete or replaced inventories and stale search results.
- Non-finite scores, foreign scope, missing provenance and text inconsistent with
  verified source inventory; these must fail without exposing partial evidence.
- Question processing that silently truncates input or uses incompatible settings.
- Timeout, missing assets, interrupted session and unconfirmed worker termination.
- Unsupported questions that still have nearest neighbors: closeness alone is not
  proof of support, and relevance calibration is not answer-quality evaluation.

## Requirements *(mandatory)*

### Scope and compatibility

In scope: one question, one exact use case, one semantic search, bounded ranked
passages, provenance, explicit relevance filtering, controlled failures and separate
live/deterministic verification. F1 ingestion, readiness, revision replacement and
verified demo-end clearing remain prerequisites.

Out of scope: generated answers, adaptive query refinement, agents, memory, tools,
external corpus access, hosted question processing, persistent indexes, hybrid search,
reranking, UI, authentication systems, catalog mutation and publication. Transport
and implementation choices belong in the reviewed plan. No public/multi-user
service is authorized by this spec.

Preserve Stage 1's exact identifiers, ordering, titles, empty catalogs, read-only
behavior, health and error contracts under the linked R1 specification, including
its amended unknown-use-case contract. Retrieval is separate from source discovery.

### Functional Requirements

- **FR-001**: Accept a non-whitespace question, exact use-case ID and optional result
  limit. Proposed demo defaults: at most 4,096 UTF-8 question bytes; limit three,
  allowing integers one through ten. Reject invalid types, including boolean limits,
  before question processing or search.
- **FR-002**: Search only a recognized selected use case in the current owned demo
  session. Apply scope restriction during search and independently check every
  returned passage against that scope before exposure.
- **FR-003**: Retrieve by semantic similarity with compatible question/document
  processing identities and settings. Reject incompatible configuration and input
  exceeding the processor's supported length; never silently truncate, switch models,
  download missing assets or route to hosted processing.
- **FR-004**: Execute at most one search per request, with no automatic retry,
  refinement, alternative corpus search or scope fallback.
- **FR-005**: Return at most the requested number of distinct qualifying passages
  ordered by descending finite score, breaking ties by stable passage identity.
  Overlapping distinct passages are allowed; duplicate passage IDs are not.
- **FR-006**: Include exact original passage text, use-case ID, source ID/title,
  revision, source-content fingerprint, passage ID, original-character start/end
  offsets, rank and score. Preserve F1 configuration identity and provenance;
  do not invent source URLs or locations absent from the approved input.
- **FR-007**: Apply an explicit effective minimum relevance score inclusively and
  expose it, the effective limit and scoring/configuration identity. Review and
  record calibration cases and threshold before live acceptance. No numerical
  threshold or measured quality result is approved by this spec.
- **FR-008**: Distinguish `matched`, `no_match`, rejected input and operational
  failure. Completed empty/below-threshold search returns `no_match` and zero
  passages. Failure returns zero passages with a safe cause category, never search success.
- **FR-009**: Return evidence only from verified current ready revisions. If the
  selected scope contains uncertain source state, fail readiness before search.
  Reject stale or malformed results as controlled failure, not partial evidence.
- **FR-010**: Retrieval leaves inventory, readiness and passage identities unchanged.
  Preserve F1 replacement, clear, close and fatal-stop behavior. Refuse search after close.
- **FR-011**: Treat questions and retrieved instructions as data. They cannot override
  scope, authority, settings or search budget, enable tools, alter corpus or trigger generation.
- **FR-012**: Keep question processing and evidence inside the approved local demo
  boundary. Do not persist raw questions, returned text, user memory or new traces.
  Preserve F1's demo-end index retention and owned cleanup. Explicit evidence output
  to the operator is separate from diagnostic telemetry.
- **FR-013**: Expose request identity, outcome, elapsed time, effective limits and
  evidence count. Default diagnostics omit raw question/source text, secrets and
  environment contents. Saving evaluation question/evidence artifacts requires
  an explicit local retention/access/deletion decision first.
- **FR-014**: Enforce a finite total retrieval deadline and bounded shutdown,
  preserving F1 fatal-stop/cleanup when worker termination cannot be confirmed.
  Exact retrieval budget and failure envelope are reviewed planning deliverables;
  implementation does not start until these limits are explicit and approved.
- **FR-015**: Process only explicitly approved synthetic sources. F1 approval covers
  its recorded scope; verify F2 reuse permission and approve each new tuple/hash
  before ingestion or processing. Roadmap product/return/troubleshooting documents
  are proposals, not an approved corpus.
- **FR-016**: Separate deterministic contract tests from real semantic retrieval.
  Label simulated vectors, scores and failures. A passing fake or lone source is
  insufficient evidence of useful live ranking among competing sources.

### Key Entities *(include if feature involves data)*

- **Retrieval request**: Request identity, exact use-case ID, question and result limit.
- **Retrieval configuration**: Effective limits, minimum score, scoring identity and
  compatible question/document processing identity.
- **Evidence passage**: Verified current source relationship, original text/offsets,
  passage identity, finite score and rank. Evidence is never an instruction or answer.
- **Retrieval result**: Outcome, request/configuration identity, passages, count,
  elapsed time and safe failure category when applicable.
- **Reviewed evaluation case**: Approved sources, question, expected source or
  no-match outcome, review attribution and live/deterministic mode. Identify
  calibration cases separately from held-out acceptance cases.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a reviewed live acceptance set with at least two distinct sources
  in the searched use case and a separate isolation use case, each of at least three
  supported paraphrases retrieves its expected source in the first three passages.
  Record each outcome; this is a proposed demo target, not measured quality.
- **SC-002**: All deterministic isolation, replacement and clear cases expose zero
  foreign, obsolete, cleared or unverified passages.
- **SC-003**: Every exposed passage has complete provenance, exact text and verified
  offsets. Every result obeys its limit, has unique passage IDs and follows documented
  score ordering, including ties.
- **SC-004**: All controlled empty/below-threshold cases return `no_match` and zero
  evidence. At least two reviewed unsupported held-out questions return `no_match`
  in the live set under recorded calibrated settings. Failure is reported as failed
  live acceptance, not hidden by adjusting expected outcomes.
- **SC-005**: All invalid-input, unavailable-dependency, incompatible-configuration,
  malformed-result and deadline cases return rejected/failed outcomes and zero
  evidence; none is mislabeled as successful search or absence of information.
- **SC-006**: All retrieval/adversarial cases execute zero generated answers,
  additional searches, tools, corpus mutations or hosted text transfers.
- **SC-007**: Existing Stage 1 and F1 regressions pass and the final local integration
  run verifies owned demo cleanup. Report real semantic outcomes separately from
  deterministic results, failures and unrun checks.

## Assumptions

- Audience: the local demo operator identified in F1; no new access class,
  multi-user service or persistent retention is assumed.
- Directory numbering follows the active sequential setting. Update the roadmap's
  reserved F2 destination to this single spec instead of creating duplicate specs.
- FR-001 limits are proposed learning-demo defaults, reviewable in planning;
  they are not production latency or throughput promises.
- F1's temporary local processing boundary is the baseline. Source, acquisition,
  installation and build/run approvals do not automatically extend to F2.
- Café/orchard fixtures may support boundary tests after reuse approval. They lack
  the roadmap return policy and competing sources within one use case; they alone
  cannot satisfy SC-001/004.
- Scores express ranking under recorded settings, not probabilities or verified
  claim support. Unsupported questions may remain near neighbors even after calibration.
- Tests precede behavior changes and first fail behaviorally, not due to missing
  dependencies. Local regressions follow [release guidance](../../docs/release.md).
  No F2 implementation or evaluation has run.

## Decisions and approval boundaries

| Decision | Owner | Status / actual evidence | Needed before |
| --- | --- | --- | --- |
| F2 specification work | User | `$speckit-specify F2 retrieval` authorizes drafting | This document |
| Requirements and plan review | User | Draft; no implementation approval recorded | Implementation |
| Operator interface and exact validation/failure envelopes | User / planner | Define in reviewed plan within local single-operator scope | Contract tests and implementation |
| F2 source reuse and expanded synthetic evaluation set | Corpus custodian / user | F1 receipt retained; F2 reuse/additions need exact decision evidence | Adding or processing sources |
| Calibration, held-out cases and finite processing/deadline limits | User / evaluator | Targets above are proposed; select and record configuration | Implementation limits and live acceptance |
| Dependencies, assets and local builds/runs | User / operator | Read-only investigation allowed; no acquisition approval inferred | Acquisition, installation or runs requiring approval |
| Retained evaluation artifacts | User / operator | No new persistence/retention approved | Saving evaluation question/evidence artifacts |
| Legal, license and external release | Human release reviewer | Deferred; no new rights or publication authority | External release |

Planning readiness means outcomes and boundaries are specified; it does not claim
approval of these gates, passing runtime results, model quality or publication.
