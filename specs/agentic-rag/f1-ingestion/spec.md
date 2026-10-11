# Feature Specification: F1 — Ingest approved learning documents

## Identity and outcome

- Feature: F1 / ingest-learning-documents. Created: 2026-10-02.
- Status: Requirements approved by the user on 2026-10-02: “I've approved the requirements.”
  Prior `$speckit-implement F1` requests authorize implementation subject to separate
  prerequisites. The subsequent “I approve. Proceed.” authorizes the exact source/acquisition
  proposals and in-place execution. F1 is implemented; local gates passed; see validation.md.
  Requirements approval alone does not authorize corpus/acquisition; the subsequent
  explicit T002/T003 approval does. Publication remains outside scope.
- Stage: Stage 2, appended to the existing Stage 1 reusable API.
- Input: `$speckit-specify F1`, resolved against the reconciled learning roadmap.
- Decision owner: project owner/human reviewer; a named person is not designated.
- Intended users: workshop participants and the local demo operator inspecting how
  approved text becomes evidence-ready indexed chunks.
- Outcome: ingest approved learning documents and inspect chunk text, stable IDs,
  numerical representations, source references, and use-case separation. Repeating
  ingestion does not create duplicates; updating a source reconciles its old chunks.
- Authority: [existing constitution](../../../docs/constitution.md) and
  [AGENTS.md](../../../AGENTS.md). No constitution migration or amendment occurs.
- Sources: [F1 roadmap](../roadmap.md), the runbook's complete
  [governance reconciliation and Stage 2](../../../docs/Foundational_Multiuse_API_SpecKit_Superpowers_Runbook.md),
  [initial scope](../../001-initial-scope/spec.md), and
  [R1 contract](../../001-list-use-case-sources/spec.md).
- Template: [project-owned feature specification](../../../docs/templates/feature-spec.md),
  as required by repository guidance while tooling adoption remains unresolved.

## Scope and scenarios

### In scope

Approved plain-text learning documents; validation; deterministic chunk identity;
chunking; embedding; source-scoped indexing and replacement; use-case isolation;
operator inspection; controlled failures; and the index lifecycle selected in D1.
The input associates a document with an exact use-case ID, source ID, title, and
source revision. Each chunk retains a location reference into its source.

### Out of scope

Document crawling or URL fetching, PDF/Office/OCR parsing, production or private
corpora, semantic question search (F2), generated answers/citations (F3), agent actions
(F4), session memory (F5), calculator/tools (F6), and publishing (F7 follow-up).
No new authentication system, persistent end-user memory, broad ingestion pipeline,
hybrid retrieval, reranking, UI, or Stage 1 catalog mutation is introduced.
Full historical source-version storage and a general source-deletion product are
deferred; reconciliation of removed chunks from an updated source is required now.

### Compatibility guarantees

Stage 1's existing source catalog and sample fixtures remain unchanged. Exact,
case-sensitive IDs, ordered `source_id`/`title` fields, successful empty results,
read-only configuration, JSON/OpenAPI contracts, and `/health` readiness are preserved.
Unknown catalog IDs remain HTTP 404 with exactly
`{"detail":{"code":"unknown_use_case"}}`. F1 indexing neither creates nor updates
catalog entries and adds no model/storage dependency to an R1 request. Any new F1
entry point or dependency-readiness contract is separately reviewed in its plan.

### User Story 1 — Inspect an ingested source (Priority: P1)

As a workshop participant, I want to inspect a document's chunks and provenance so
I can understand what evidence later retrieval will be able to return.

**Independent verification:** Use one approved synthetic text and predetermined
chunking configuration; inspect its indexed records without any question or answer.

1. **Given** an approved non-empty document with complete metadata, **when** the
   operator ingests it, **then** each indexed chunk exposes its text, chunk ID,
   use-case/source IDs, title, revision, source location, embedding identity, and
   numerical representation, and the result reports the indexed chunk count.
2. **Given** text containing Unicode and quotation marks, **when** it is chunked,
   **then** inspected chunk text and location references correspond to the original
   text without silently replacing those characters.
3. **Given** empty or whitespace-only input, missing required metadata, or an input
   outside the approved plain-text boundary, **when** ingestion is attempted,
   **then** it is rejected with a reason and creates no indexed chunks.

### User Story 2 — Repeat and update a source safely (Priority: P1)

As the demo operator, I want a source to have one current chunk set so repeats and
updates do not leave duplicate or obsolete evidence in later retrieval.

**Independent verification:** Ingest the same source twice, then ingest a shorter
revision with the same exact use-case/source identity; compare inspected records.

1. **Given** a successfully indexed source, **when** the same text, identity, revision,
   and chunking/embedding configuration are ingested again, **then** the chunk ID set
   and count remain unchanged and no duplicate indexed chunks exist.
2. **Given** a revised source with removed text, **when** replacement completes,
   **then** the inspected current chunk set exactly represents the new revision;
   obsolete chunks are absent and another source's records are unchanged.
3. **Given** an embedding or indexing failure, **when** ingestion stops,
   **then** the operator sees a bounded failure, no complete-success result is
   reported, and retrying the same approved source can converge to its intended
   chunk set without duplicates. The result identifies whether the source is complete
   or incomplete; incomplete source state is not reported as ready evidence.

### User Story 3 — Inspect only the selected use case (Priority: P1)

As a participant, I want independently indexed corpora to remain separate so
identical source IDs do not expose or replace another use case's evidence.

**Independent verification:** Use two approved synthetic corpora sharing a source ID;
inspect and replace that source in one use case, then compare both inventories.

1. **Given** separate use cases with the same source ID, **when** either is ingested
   or inspected, **then** identities are scoped to both use case and source, and
   inspection returns only chunks from the exact selected use case.
2. **Given** two indexed use cases, **when** a source is replaced or cleared within
   one approved scope, **then** the other use case's text, IDs, and counts are unchanged.

### User Story 4 — Respect approval and lifecycle boundaries (Priority: P2)

As the local operator, I want ingestion and inspection restricted to the approved
demo inputs and lifecycle so the learning exercise does not silently retain or
transmit documents beyond their approved use.

**Independent verification:** Test an unapproved synthetic input, then the selected
lifecycle's clear/expiry behavior, without accessing real data or a hosted provider.

1. **Given** no recorded source approval or lifecycle configuration, **when** ingestion
   is requested, **then** it is refused before document text is embedded or indexed.
2. **Given** the lifecycle selected in D1, **when** its end/expiry/clear condition
   occurs, **then** the scoped source text, chunks, metadata, and numerical
   representations are removed and inspection confirms absence.
3. **Given** instructions embedded inside approved source text, **when** it is ingested,
   **then** those instructions remain document data and cannot change source approval,
   data routing, policy, tools, or index scope.

### Edge cases

- Whitespace-only documents; missing/blank IDs, title, or revision; unsupported input.
- Exact IDs differing by case or surrounding whitespace are not silently merged.
- A document shorter than one chunk; a document crossing a chunk boundary; Unicode.
- Repeated input; changed text under the same source; removed final chunks.
- A changed chunking/embedding configuration requires replacement of that source's
  old chunk set; incompatible representations must not be mixed silently.
- Embedding timeout, indexing outage, or malformed numerical representation: return
  an explicit failure/incomplete state, not successful indexing.
- Same source ID in separate corpora; inspection of an unknown use case returns no
  unrelated chunks. Its new F1 error contract is defined separately from R1.
- Clear/expiry and re-ingestion after clearing; an interrupted or failed source update.

## Requirements and trust boundaries

### Functional requirements

- **FR-001:** The system MUST accept only explicitly approved plain-text learning
  sources with non-blank use-case ID, source ID, title, and revision. It MUST reject
  invalid/unapproved input before embedding or indexing and report the reason.
- **FR-002:** The system MUST split accepted text into non-empty inspectable chunks,
  preserving source text and an unambiguous location reference into that revision.
  The effective chunking configuration MUST be identifiable in the inspection result.
- **FR-003:** Identical source input and effective chunking/embedding configuration
  MUST produce the same indexed chunk IDs and count. Identity MUST include the
  selected use case and source scope; collisions across scopes MUST NOT merge data.
- **FR-004:** Each indexed chunk MUST retain use-case ID, source ID, title, revision,
  chunk ID, location reference, text, and embedding model/configuration identity.
- **FR-005:** Each chunk MUST have a valid non-empty numerical representation produced
  by the selected embedding configuration. Invalid or incompatible representations
  MUST be rejected and MUST NOT be reported as successfully indexed.
- **FR-006:** Re-ingesting identical input MUST NOT create duplicate chunks. Completing
  a replacement MUST leave exactly the current source's new chunk set, removing its
  obsolete chunks without changing another source or use case.
- **FR-007:** Inspection and lifecycle operations MUST use an explicit exact use-case
  scope; source operations MUST also use the exact source scope. Inspection MUST
  expose only that scope's text, records, counts, provenance, and completion state.
- **FR-008:** The ingestion result MUST distinguish complete, rejected, and failed/
  incomplete outcomes and expose affected source identity and chunk counts. Failures
  MUST NOT claim complete success; retry MUST permit convergence without duplicates.
- **FR-009:** An embedding/index dependency failure MUST terminate within configured
  timeouts/retry ceilings and return a controlled outcome. Those limits MUST be
  reviewed and configured before running F1; no unlimited retry behavior is permitted.
- **FR-010:** Before indexing, a recorded lifecycle MUST identify who can ingest,
  inspect, and clear the selected index, its retention condition, and deletion scope.
  Data MUST be removed at the selected end/expiry/clear condition (D1).
- **FR-011:** Document text MUST follow the embedding data-flow boundary selected in
  D2. No document transfer to a hosted service is permitted without separate source
  access/data-handling and cost approval; this spec is not such approval.
- **FR-012:** Documents MUST be treated as untrusted evidence; text MUST NOT execute
  instructions, enable tools, amend policy, or change the approved ingestion scope.
- **FR-013:** F1 MUST preserve the Stage 1 compatibility guarantees above and MUST NOT
  mutate the catalog or introduce its dependencies into existing catalog requests.
- **FR-014:** F1 MUST provide deterministic local tests without external services and
  a separately labeled live ingestion/inspection demonstration with real embeddings
  and an actual index. Both modes MUST NOT claim generation or semantic retrieval.

### Approved inputs and governance gates

The runbook's proposed three fictional guides and separate isolation corpus are
candidates, not approved files. Owner, classification, access, redistribution, and
approval evidence must be recorded before creating/ingesting their content. Existing
Stage 1 catalog fixtures do not authorize a new corpus or provider transfer.

The local operator is the proposed F1 audience. Authorization mechanisms and a new
entry-point contract belong in the plan; remote/multi-user ingestion is outside F1.
No route, dependency installation, storage deployment, or provider is created here.
The runbook proposes Qdrant as a separate Compose service; its exact configuration
and compatibility remain plan decisions, not an approved installation.

### Memory, index, and traces

Session context and persistent end-user memory remain disabled. The document index
is separately governed by D1. Inspection intentionally exposes approved chunk text;
telemetry must not record secrets or raw document text by default. Trace access and
retention must be defined before collection beyond the immediate demo result.

Retrieval quality, grounded answers, citations, and abstention are later slices.
F1 establishes provenance and index contents only; no answer-quality claim is made.
Model choice, chunk size/overlap, timeouts, retries, input-size limits, and operating
costs are reviewed in planning. No arbitrary latency, throughput, or quality target
is invented for this small learning corpus.

## Acceptance and evaluation

### Observable acceptance criteria

- **AC-001 (FR-001/002/004/005/008):** Every chunk in a successful approved fixture run
  has non-empty text, all required provenance, a matching source location, a valid
  numerical representation, and an inspected count matching the reported count.
- **AC-002 (FR-001/008):** All empty, unsupported, incomplete-metadata, and unapproved
  fixture attempts are rejected; zero chunks are written by those attempts.
- **AC-003 (FR-003/006):** Two identical runs have equal chunk ID sets and counts;
  duplicate count is zero. A shorter replacement leaves exactly its new chunk set
  with zero obsolete chunks and no changes outside the source scope.
- **AC-004 (FR-003/007):** For both isolation corpora, inspection exposes zero foreign
  chunks. Replacing/clearing one scope changes zero records in the other.
- **AC-005 (FR-005/008/009):** Each controlled embedding/index failure or invalid
  representation yields an explicit failed/incomplete outcome within configured
  limits; retry converges to the intended chunk set without duplicate records.
- **AC-006 (FR-010/011/012):** Approval and lifecycle gates precede embedding/indexing;
  selected deletion conditions remove the scoped data; prohibited provider transfers
  and document-driven changes to permissions/policy perform zero such actions.
- **AC-007 (FR-013):** The full existing R1 regression suite passes on the changed
  application, including exact 404 and read-only behavior; no existing contract changes.
- **AC-008 (FR-014):** The demonstration report labels deterministic versus live
  evidence, records configuration and corpus revisions, and explicitly lists any
  unavailable live checks. Scripted vectors are never presented as real embeddings.

### Success criteria

- **SC-001:** Participants can trace 100% of inspected chunks to the exact approved
  source revision and location in the demonstration fixture set (AC-001).
- **SC-002:** Repeated and replacement ingestion leaves zero duplicate or obsolete
  chunks after successful completion across the reviewed scenarios (AC-003).
- **SC-003:** Isolation and rejection scenarios expose zero foreign chunks and write
  zero chunks from invalid or unapproved input (AC-002/004).
- **SC-004:** Every tested failed attempt is visibly distinguishable from success,
  with zero incomplete sources labeled ready evidence (AC-005).
- **SC-005:** The learning report identifies what each mode establishes and any live
  limitation; participants can inspect the real indexing result without running
  retrieval, generation, memory, or tools (AC-008).

### Test and demonstration boundaries

Write API/application tests before production behavior changes; confirm expected
behavioral failures, then implement and rerun. Deterministic fixtures exercise
validation, identity, replacement, isolation, lifecycle, and controlled failures
without a provider or storage service. Real embeddings and actual index inspection
are a separately labeled local integration demonstration, not proof of semantic
retrieval (F2) or grounded answers (F3). Actual deterministic and local live checks are recorded in [validation.md](validation.md).

Use the [existing local verification guidance](../../../docs/release.md). Preserve
the Stage 1 gate and isolated cleanup; no GitHub Actions or Docker Hub automated
builds. F0's prior audit is historical; the fresh full Docker gate is recorded in validation.md. Record fresh evidence before accepting the integrated F1 build.
Do not treat that historical audit, this spec, or the quality checklist as current
application verification. Publication is outside this feature.

## Decisions

| Decision | Owner | Status / approval evidence | Needed before |
| --- | --- | --- | --- |
| D1 — Index lifetime, access, and clearing | Project owner/human reviewer | Resolved 2026-10-02 by user: “use temporary/local”. Temporary demo index, cleared at demo end; local demo operator may ingest/inspect/clear the isolated demo scope. No retained index or end-user memory. | Planning lifecycle and any persistence |
| D2 — Embedding data-flow boundary | Project owner/human reviewer | Resolved 2026-10-02 by user: “use temporary/local”. Local embedding computation; no document text sent to a hosted service. Model selection/download approval remains separate. | Provider/model planning and embedding |
| Corpus, owner, classification, access, redistribution, approval | EDM source custodian/reviewer | Exact T002 synthetic bytes approved by “I approve. Proceed.”; real manifest and hashes recorded in tasks.md | Creating/ingesting corpus data |
| F1 requirements review and implementation intent | User / human reviewer | Approved 2026-10-02: “I've approved the requirements.” Reviewer marked the checklist approval item “by EDM”; preserve that attribution. Renewed `$speckit-implement F1` resumes execution; T002/T003 separately explicitly approved. | Requirements readiness / implementation prerequisites |
| F0 acceptance | Human reviewer | Fresh in-process checks pass in the checklist evidence; fresh full local Docker gate recorded in validation.md. Requirements approval does not retroactively accept F0. | F0 acceptance and integrated F1 acceptance |
| Chunking, embedding compatibility, storage configuration, timeouts, retries, input limits | Feature planner and human reviewer | Concrete choices are documented in plan/contracts; requirements approved, actual compatibility checks in validation.md; no performance guarantee. New teardown details are recorded by the requested readiness remediation. No dependency acquisition approval is inferred. | Implementation and separately authorized live validation |
| Trace retention/access | Human reviewer | No persistent trace policy selected | Persisting traces |
| Legal rights/license and publication | Human release reviewer | Unresolved; external actions not authorized | Any later external release |

Assumptions for review: plain-text-only input; a local operator with approved synthetic
data; sequential ingestion in this learning slice; exact source/use-case identifiers;
and replacement of the current source set rather than maintaining historical indexes.
Concurrent updates and additional formats require separate scope review. Model and
embedding choices are documented design decisions; compatibility, corpus permission,
acquisition authorization and legal grants are not inferred. Index lifetime is demo-end.

Planning artifacts: [plan](plan.md), [research](research.md), [data model](data-model.md),
[CLI contract](contracts/ingestion-cli.md), and [validation guide](quickstart.md).
The [tasks](tasks.md) have been generated and reconciled, and cross-artifact analysis
has occurred. Requirements approval and implementation requests are recorded above;
separate T002/T003 decisions are explicitly approved. Implementation status follows
[tasks.md](tasks.md); acceptance evidence is in [validation.md](validation.md).
