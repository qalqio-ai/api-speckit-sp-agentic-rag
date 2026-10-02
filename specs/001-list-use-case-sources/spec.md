# Feature Specification: R1 — List Use-Case Sources

**Feature Branch**: `main` (existing branch; no branch-creation hook configured)

**Created**: 2026-10-02

**Status**: Draft; derived from the approved R1 design

**Input**: User description: "Build GET /v1/use-cases/{use_case_id}/sources using in-memory sample data. A configured use case returns its source IDs and titles. An unknown use case returns HTTP 404 with code unknown_use_case. Keep this read-only. No database, authentication, LLM, or vector database."

**Approved reference**: [R1 design](../../docs/superpowers/specs/2026-10-02-r1-use-case-sources-design.md)

**Rule amendment**: The user subsequently required HTTP 404 with exactly
`{"detail":{"code":"unknown_use_case"}}`. This nested response supersedes
the earlier top-level error and message in the historical approved design.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover Configured Sources (Priority: P1)

As a client consuming a configured use case, I want to retrieve its source IDs
and titles so I can identify the information available for that use case.

**Why this priority**: Discovering configured sources is the primary outcome of R1.

**Independent Test**: Request the sources for a configured use case and compare
the returned IDs, titles, and order with its sample configuration.

**Acceptance Scenarios**:

1. **Given** `sample-use-case` has one source with ID `sample-source-1` and title `Sample source`, **When** the client requests its sources, **Then** it receives HTTP 200 with exactly `{"use_case_id":"sample-use-case","sources":[{"source_id":"sample-source-1","title":"Sample source"}]}`.
2. **Given** a configured use case has multiple sources, **When** the client requests its sources, **Then** every configured source is returned in configuration order with its exact ID and title.
3. **Given** the client has retrieved a configured use case's sources, **When** it repeats the request, **Then** it receives the same source data and the configuration remains unchanged.

---

### User Story 2 - Recognize an Unknown Use Case (Priority: P1)

As a client, I want an explicit unknown-use-case response so I can distinguish
an invalid use-case ID from a configured use case that has no sources.

**Why this priority**: Clients need a reliable distinction between missing configuration and an empty source list.

**Independent Test**: Request `missing-use-case` and verify the status and error fields without relying on a configured use case.

**Acceptance Scenarios**:

1. **Given** `missing-use-case` is not configured, **When** the client requests its sources, **Then** it receives HTTP 404 with exactly `{"detail":{"code":"unknown_use_case"}}`.
2. **Given** `sample-use-case` is configured and `Sample-use-case` is not, **When** the client requests `Sample-use-case`, **Then** it receives HTTP 404 with exactly `{"detail":{"code":"unknown_use_case"}}`.
3. **Given** an unknown ID, **When** the client requests it repeatedly, **Then** it receives the same error and no use case or source is created or changed.

---

### User Story 3 - Recognize an Empty Configuration (Priority: P2)

As a client, I want an empty source list for a configured use case with no
sources so I can recognize valid configuration without treating it as an error.

**Why this priority**: An empty configuration is a valid boundary condition of source discovery.

**Independent Test**: Request `empty-use-case` and verify a successful response containing an empty list.

**Acceptance Scenarios**:

1. **Given** `empty-use-case` is configured with no sources, **When** the client requests its sources, **Then** it receives HTTP 200 with exactly `{"use_case_id":"empty-use-case","sources":[]}`.

### Edge Cases

- A configured empty list is successful, not an unknown-use-case error.
- Source order follows configuration even when source IDs would sort differently.
- Source titles containing Unicode characters or quotation marks are returned unchanged.
- IDs are case-sensitive and are not normalized or trimmed before lookup.
- Successful, empty, and unknown-use-case requests leave configuration unchanged.
- POST to the sources path returns HTTP 405 and changes no configuration.
- Successful and unknown-use-case responses are JSON, with a JSON content type; unknown-use-case errors have a `detail` object containing exactly `code`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose `GET /v1/use-cases/{use_case_id}/sources` for source discovery.
- **FR-002**: The system MUST match the supplied use-case ID exactly and case-sensitively against configured IDs.
- **FR-003**: For a configured ID, the system MUST return HTTP 200 and a JSON object containing exactly `use_case_id` and `sources`; each source MUST contain exactly `source_id` and `title`, both strings.
- **FR-004**: The system MUST preserve configured source order, IDs, and titles.
- **FR-005**: A configured use case with no sources MUST return HTTP 200 with `sources` equal to an empty array.
- **FR-006**: For an unknown ID, the system MUST return HTTP 404 with exactly `{"detail":{"code":"unknown_use_case"}}`, with no additional fields or message.
- **FR-007**: Requests MUST NOT create, update, delete, or reorder configured use cases or sources. POST to the sources path MUST return HTTP 405.
- **FR-008**: R1 MUST use static in-memory sample data, including `sample-use-case` and `empty-use-case` as described in the acceptance scenarios.
- **FR-009**: R1 MUST require no authentication and MUST include no database, LLM, vector database, external calls, or mutation endpoints.
- **FR-010**: Both successful source responses and unknown-use-case responses MUST identify their content as JSON.

### Key Entities *(include if feature involves data)*

- **Use Case**: A configuration identified by an exact string ID and associated with an ordered collection of zero or more sources.
- **Source**: An item associated with a use case, identified by a string source ID and a human-readable string title. Source contents are outside this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A client can discover all configured source IDs and titles in one successful retrieval for each configured sample use case.
- **SC-002**: In all configured acceptance examples, 100% of source IDs, titles, and positions match the sample configuration.
- **SC-003**: In all unknown-ID acceptance examples, clients receive the explicit unknown-use-case result and can distinguish it from an empty configured use case.
- **SC-004**: Across repeated configured, empty, unknown, and rejected POST requests, zero configured use cases or sources change.
- **SC-005**: A client can complete the primary discovery scenario using the supplied sample configuration without credentials or access to another service.

## Assumptions

- The user invoked `speckit-specify` for the R1 scope already described and approved in this conversation.
- The approved R1 design and subsequent user rule amendment are authoritative for response shape, matching rules, and empty-use-case behavior.
- Sample configuration is fixed for this slice; configuration editing, source contents, pagination, search, and filtering are outside scope.
- Performance and concurrency targets are not specified for this small sample-data slice; none are introduced here.
- The user's later task-by-task implementation authorizations supersede the initial instruction not to write product code; scope remains limited to R1.
