# Implementation Plan: R1 — List Use-Case Sources

**Branch**: `main` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-list-use-case-sources/spec.md`

## Summary

Expose `GET /v1/use-cases/{use_case_id}/sources` through the FastAPI service
described in the README. Look up exact IDs in static in-memory sample data and
return configured sources in order. A known empty configuration returns HTTP
200 with an empty list; an unknown ID returns HTTP 404 with exactly
`{"detail":{"code":"unknown_use_case"}}`, following the user's rule amendment.

The planning command originally produced design documents only. Subsequent
user authorizations completed T001–T018; [tasks.md](tasks.md) records implementation
and verification results.

## Technical Context

**Language/Version**: Python 3.10 or later; local `python3` reports 3.10.10.

**Primary Dependencies**: FastAPI and Uvicorn at runtime; Pydantic response models through FastAPI. Select compatible dependency versions during implementation and record the installed versions; no dependency installation has occurred during planning.

**Storage**: Static in-memory mapping; no persistence, database, or external data service.

**Testing**: pytest and FastAPI TestClient with HTTPX; endpoint contract tests and configuration-preservation checks.

**Target Platform**: Local development on macOS and a Python ASGI runtime; deployment is outside R1.

**Project Type**: Small web service, without a frontend.

**Performance Goals**: No throughput or latency target was requested. One lookup returns the entire configured source list; no benchmark work is included.

**Constraints**: Read-only; no authentication, database, LLM, vector database, outbound calls, or mutation endpoints. Exact case-sensitive matching, JSON responses, and configured ordering are required.

**Scale/Scope**: One endpoint, two fixed sample use cases, focused response models, and endpoint tests. No pagination, filtering, configuration editing, or source-content retrieval.

## Constitution Check

*GATE: Check before Phase 0 and again after Phase 1 design.*

No project constitution exists at `.specify/memory/constitution.md` or
`memory/constitution.md`. This is an absent governance document, not a claim
that constitutional requirements were evaluated. No new constitution is
introduced by this command.

The applicable gates are the user's scope and approved design:

| Gate | Before research | After design |
|------|-----------------|--------------|
| One read-only source-discovery endpoint | Pass | Pass |
| Static sample data; no external integrations | Pass | Pass |
| No authentication, database, LLM, or vector database | Pass | Pass |
| Preserve exact response contract and ordering | Pass | Pass |
| No product code during planning | Pass | Pass |

No unresolved clarification or scope violation remains. No planning extension
hooks are registered because `.specify/extensions.yml` does not exist.

## Project Structure

### Documentation (this feature)

```text
specs/001-list-use-case-sources/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── sources.md
└── checklists/
    └── requirements.md
```

`tasks.md` is a future `speckit-tasks` output and is not created by this command.
The earlier Superpowers design and implementation plan are retained as
references; this feature directory contains the Spec Kit planning artifacts.

### Source Code (planned repository-root layout)

```text
app/
├── __init__.py
├── main.py
└── sample_data.py
tests/
└── test_sources.py
pyproject.toml
README.md
```

**Structure Decision**: Use the approved two-module application layout. Keep the
application, route, and response models in `app/main.py`, and the sample mapping
in `app/sample_data.py`. No service, repository, or routing abstraction is
necessary for this slice. These source files are planned, not created.

## Phase 0: Research Decisions

See [research.md](research.md) for rationale, alternatives, and official FastAPI
documentation. Resolve missing-versus-empty by mapping membership, use an
HTTPException with the amended nested detail for unknown IDs, and declare a successful response model
so the route's mixed return type does not become the inferred schema.

## Phase 1: Design and Contracts

- [data-model.md](data-model.md) defines configuration and response entities.
- [contracts/sources.md](contracts/sources.md) defines the public HTTP contract.
- [quickstart.md](quickstart.md) defines implementation-time setup and validation.

Request flow: capture the path ID without normalization, check membership in
`USE_CASE_SOURCES`, return the exact 404 error if absent, or construct a new
response from the configured records. Never mutate the mapping or its lists.
Only GET is registered for the sources path; POST is rejected by routing.

The future test suite will cover configured, empty, unknown, case-different,
and whitespace-different IDs; multiple-source ordering; Unicode and quoted
titles; JSON content types; repeated requests; and rejected POST requests.
Synthetic configurations are isolated test fixtures and do not change the
production sample configuration.

## Complexity Tracking

No violations require justification. No extra application layers or integration
dependencies are proposed.
