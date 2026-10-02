# Tasks: R1 — List Use-Case Sources

**Input**: Design documents from `specs/001-list-use-case-sources/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/sources.md](contracts/sources.md), and [quickstart.md](quickstart.md).

**Tests**: Included because the approved design explicitly requires endpoint tests and the technical plan specifies test-first validation. Write and run each story's tests before its implementation. An installation error is not a valid red test.

**Organization**: Tasks are grouped by user story. Every source path is relative to the repository root. The user authorized T001–T018; all tasks are complete.

**Rule amendment**: API tests precede production endpoint code. The unknown-use-case response is now HTTP 404 with exactly `{"detail":{"code":"unknown_use_case"}}`, superseding the earlier top-level error and message requirements in the historical design. The current Spec Kit specification, plan, data model, research, and contract reflect the amendment. All 11 tests pass after T015–T018.

## Format: `[ID] [P?] [Story] Description`

- `[P]` identifies work in different files that can run concurrently once its prerequisites are complete; it does not authorize agent delegation.
- `[US1]`, `[US2]`, and `[US3]` map directly to the specification's stories.
- Do not add a database, authentication, LLM, vector database, outbound call, mutation endpoint, service layer, or repository abstraction.

## Phase 1: Setup

**Purpose**: Prepare the minimal package and a working test environment.

- [X] T001 Create `pyproject.toml` for Python 3.10 or later, with explicit setuptools package discovery for `app`, FastAPI and Uvicorn runtime dependencies, and a `test` extra containing pytest and HTTPX; select a compatible dependency set.
- [X] T002 Create the package marker `app/__init__.py`, create a project-local `.venv`, install with `.venv/bin/python -m pip install -e '.[test]'`, and confirm FastAPI, pytest, and HTTPX imports work before beginning the endpoint test cycle.

## Phase 2: Foundational

**Purpose**: Establish the shared app and configuration interfaces. T001–T002 must be complete first.

- [X] T003 [P] Create `app/main.py` with the FastAPI application exported as `app`, plus `SourceResponse(source_id: str, title: str)` and `UseCaseSourcesResponse(use_case_id: str, sources: list[SourceResponse])`; source IDs and titles must be strings, and responses must preserve their configured values. Do not register the business endpoint yet.
- [X] T004 [P] Create `app/sample_data.py` with `USE_CASE_SOURCES` as an initially empty mapping from exact string use-case IDs to ordered lists of records containing string `source_id` and `title`; do not add persistence or request-time writes.

**Checkpoint**: Application imports and configuration exists. Story tests can now fail on missing behavior rather than missing dependencies.

## Phase 3: User Story 1 — Discover Configured Sources (Priority: P1)

**Goal**: Retrieve source IDs and titles for a configured use case in configuration order.

**Independent Test**: GET the configured sample and assert HTTP 200 with the exact configured ID, source ID, and title; use isolated synthetic configuration to exercise multiple sources and title serialization.

- [X] T005 [US1] Write configured-source tests in `tests/test_sources.py` using TestClient with `app.main.app`: assert exact JSON `{"use_case_id":"sample-use-case","sources":[{"source_id":"sample-source-1","title":"Sample source"}]}` and HTTP 200; add isolated monkeypatch fixtures with `source-z` before `source-a` and title `Café "Guide"`, assert exact order and title round-trip, JSON content type, and repeated GET responses without mapping changes. Run `.venv/bin/python -m pytest tests/test_sources.py -v` and confirm failure on missing route behavior.
- [X] T006 [US1] Add `sample-use-case` with one record, `source_id` equal to `sample-source-1` and `title` equal to `Sample source`, to `USE_CASE_SOURCES` in `app/sample_data.py`; keep extra test fixtures out of this production mapping.
- [X] T007 [US1] Register `GET /v1/use-cases/{use_case_id}/sources` in `app/main.py` with an explicit `UseCaseSourcesResponse` response model and a `get_sources` handler; return new response records for configured IDs without sorting, trimming, normalizing, or changing configuration. Successful bodies contain exactly `use_case_id` and `sources`, with exactly `source_id` and `title` per source. Unknown-ID handling is completed in US2.
- [X] T008 [US1] Run `.venv/bin/python -m pytest tests/test_sources.py -v` against the US1 tests in `tests/test_sources.py` and resolve failures until configured, ordered, quoted/Unicode-title, JSON-content-type, and repeated read-only requests pass.

**Checkpoint**: US1 is independently demonstrable. This is an internal discovery checkpoint, not the complete R1 deliverable; US2 and US3 are required before handoff.

## Phase 4: User Story 2 — Recognize an Unknown Use Case (Priority: P1)

**Goal**: Return an explicit unknown-use-case result for IDs absent from configuration.

**Independent Test**: GET `missing-use-case` and compare HTTP 404 and exactly `{"detail":{"code":"unknown_use_case"}}`; no configured use case is required for this scenario.

- [X] T009 [US2] Add unknown-ID tests in `tests/test_sources.py`: assert HTTP 404 and exactly `{"detail":{"code":"unknown_use_case"}}`; parameterize `missing-use-case`, `Sample-use-case`, and URL-encoded leading/trailing whitespace variants; assert JSON content type, repeatable errors, and unchanged mapping. Confirm the new error-contract tests fail before changing the handler.
- [X] T010 [US2] Update `get_sources` in `app/main.py` to test mapping membership and raise HTTPException with HTTP 404 and `detail={"code":"unknown_use_case"}` for absent IDs. Add nested error response models in this same module and declare the amended 404 response in OpenAPI metadata. Keep the explicit success response model; do not introduce a global exception handler.
- [X] T011 [US2] Run `.venv/bin/python -m pytest tests/test_sources.py -v` and the full suite for all current tests in `tests/test_sources.py`; require US1 and US2 to pass, including exact case/whitespace-sensitive lookup and configuration preservation after failed requests.

**Checkpoint**: Configured and unknown requests satisfy their contracts without requiring credentials or an external service.

## Phase 5: User Story 3 — Recognize an Empty Configuration (Priority: P2)

**Goal**: Distinguish a configured use case with zero sources from an unknown ID.

**Independent Test**: GET `empty-use-case` and assert HTTP 200 with exactly `{"use_case_id":"empty-use-case","sources":[]}`.

- [X] T012 [US3] Add empty-use-case tests in `tests/test_sources.py` that assert the exact successful empty JSON body, JSON content type, stable repeated responses, and unchanged mapping. Run `.venv/bin/python -m pytest tests/test_sources.py -v` and confirm failure because `empty-use-case` is not configured yet.
- [X] T013 [US3] Add `empty-use-case` mapped to an empty list in `app/sample_data.py`; confirm `app/main.py` uses membership rather than source-list truthiness and preserves the empty array. Do not add a special error for zero sources.
- [X] T014 [US3] Run `.venv/bin/python -m pytest tests/test_sources.py -v` for all three stories in `tests/test_sources.py`; require configured, unknown, and empty outcomes to pass together.

**Checkpoint**: All R1 user stories are functional and independently verifiable.

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Verify the full read-only contract and document local use after all story phases.

- [X] T015 Add cross-story tests in `tests/test_sources.py`: snapshot the complete sample mapping, send successful, empty, unknown, repeated, and POST requests, assert HTTP 405 for POST, exact stable bodies for GET, and snapshot equality afterward. Assert generated OpenAPI contains this GET operation's successful response shape and amended nested 404 error shape. Run `.venv/bin/python -m pytest -v` and correct any failure in `app/main.py` without adding integrations or changing the contract.
- [X] T016 Review `app/main.py`, `app/sample_data.py`, and `pyproject.toml` against FR-001 through FR-010 in `specs/001-list-use-case-sources/spec.md`, including the user's rule amendment; confirm there are no configuration writes, outbound calls, mutation operations, authentication dependencies, or database/LLM/vector integrations. Require complete tests in `tests/test_sources.py` to pass after any correction.
- [X] T017 [P] Update `README.md` with the setup, install, test, and run commands from `specs/001-list-use-case-sources/quickstart.md`, the configured/empty/unknown request examples, and the static-sample-data limitation; record the Python and installed dependency versions verified during implementation.
- [X] T018 Execute `specs/001-list-use-case-sources/quickstart.md`: require `.venv/bin/python -m pytest -v` to pass, run the local server and confirm HTTP 200/200/404/404/405 for its five requests, inspect generated 200/404 documentation, and stop the server. Run `git diff --check`, review the final changes to `app/`, `tests/test_sources.py`, `pyproject.toml`, and `README.md`, then report actual validation results without claiming unrun checks.

## Dependencies and Execution Order

```text
T001 → T002 → (T003 + T004) → US1 → US2 → US3
                                         ├→ T015 → T016 ─┐
                                         └→ T017 ───────┴→ T018
```

The story sequence is US1 → US2 → US3. US2 extends US1's handler; US3 verifies its
empty case after unknown handling exists. Each story has an independent
acceptance test, but shares `app/main.py`, `app/sample_data.py`, and
`tests/test_sources.py` with the others, so implementation must be serialized.

T003 and T004 may run concurrently after setup because they create different
files and have no dependency on each other. T017 may run concurrently with
T015–T016 once all story checkpoints pass. T018 waits for both review and README
completion. No other task has a parallel marker.

## Parallel Examples by User Story

- **US1**: Run T005, T006, T007, then T008 in order. No independent parallel edits exist within this story.
- **US2**: Run T009, T010, then T011 in order. Do not overlap handler/test changes with another story.
- **US3**: Run T012, T013, then T014 in order. The red test must precede adding the empty sample.
- **Shared work**: T003 and T004 are a valid parallel pair; T017 is independent of T015–T016 after all stories pass.

## Requirement Coverage

| Requirement | Owning tasks |
|-------------|--------------|
| FR-001: GET operation | T005, T007, T015 |
| FR-002: Exact case-sensitive IDs | T007, T009–T011 |
| FR-003: Exact success fields and types | T003, T005, T007–T008 |
| FR-004: Source values and order | T005–T008 |
| FR-005: Empty configuration succeeds | T012–T014 |
| FR-006: Exact unknown-use-case error | T009–T011 |
| FR-007: Read-only and POST rejection | T005, T009, T012, T015–T016 |
| FR-008: Static sample configuration | T004, T006, T013 |
| FR-009: Excluded integrations and authentication | T001, T016, T018 |
| FR-010: JSON content types | T005, T009, T012 |

## Implementation Strategy

Use US1 as the first runnable checkpoint, then add the other P1 story and the
empty-configuration story before treating R1 as complete. Keep the implementation
limited to the approved modules and dependencies. Commit cohesive verified
changes if implementation is later authorized; no deployment is part of R1.

The task list contains 18 completed tasks: setup 2, foundation 2, US1 4, US2 3,
US3 3, and final validation/documentation 4. There are no unresolved clarifications.
No project constitution or task-generation extension hooks exist. The local
setup script could not resolve its shared template; the CLI resolver selected
the bundled core `tasks-template.md`, whose phase and checklist structure is
used here. No product files or dependencies were created during task generation.

## Final Verification

- Full pytest suite: 11 passed, with one existing Starlette/HTTPX deprecation warning.
- Mixed request snapshots verify the complete configuration remains unchanged.
- Live local HTTP checks: configured 200, empty 200, unknown 404, case-different ID 404, and POST 405; exact bodies matched the amended contract.
- A repeated configured request after rejected requests returned unchanged data.
- `/docs` served successfully; generated OpenAPI declared 200 and the amended nested 404 schema.
- The temporary local validation server shut down successfully.
- Source and dependency review confirmed the excluded integrations are absent.
