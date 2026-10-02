# R1 Use-Case Sources Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution or superpowers:subagent-driven-development if the user selects delegation. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose configured source IDs and titles through `GET /v1/use-cases/{use_case_id}/sources`, returning HTTP 404 with `unknown_use_case` for an unknown ID.

**Architecture:** A small FastAPI app looks up an exact use-case ID in a static in-memory mapping in a separate module. It returns ordered source records or a top-level JSON error, without a service or repository layer.

**Tech Stack:** Python, FastAPI, Uvicorn, pytest, and HTTPX for FastAPI TestClient.

**Spec:** [Approved design](../specs/2026-10-02-r1-use-case-sources-design.md)

## Global Constraints

- Build one read-only endpoint backed by static in-memory sample data.
- No database, authentication, LLM, vector database, external calls, or mutation endpoints are included.
- Do not add unrelated refactoring or infrastructure.
- Use-case IDs are matched exactly and case-sensitively.
- Preserve the configured source order.
- A configured use case with no sources returns HTTP 200 with its ID and `"sources": []`.
- An unknown use-case ID returns HTTP 404 with top-level `code` and `message`; the error is not wrapped in `detail`.
- Request handling never changes the sample mapping.
- This plan is documentation only. Wait for plan review and explicit implementation authorization before writing product code.

## Review Focus

These additional checks exercise conditions implicit in the approved contract:

- Multiple sources must retain configuration order, including when IDs sort differently.
- Titles containing Unicode or quotation marks must survive JSON serialization unchanged.
- Failed lookups must leave the configuration intact, just like successful requests.
- POST to the sources path must return HTTP 405 and leave configuration intact.
- Both successful and unknown-use-case responses must have JSON content type.

---

## File Structure

- Create `pyproject.toml`: package metadata, runtime dependencies (`fastapi`, `uvicorn`), a test extra (`pytest`, `httpx`), and package discovery for `app`.
- Create `app/__init__.py`: package marker.
- Create `app/sample_data.py`: static configured source mapping.
- Create `app/main.py`: application, response models, route, and explicit JSON 404 response.
- Create `tests/test_sources.py`: endpoint contract and read-only checks.
- Modify `README.md`: local setup, test, run, and request examples.

### Task 1: Deliver the R1 endpoint and its verification

**Files:** All files listed above. Do not modify the approved design.

**Interfaces:**
- Consumes: the approved API contract; there is no existing application code.
- Produces: `app.main.app`, a FastAPI application importable by TestClient and `uvicorn app.main:app`.
- Produces: `app.sample_data.USE_CASE_SOURCES`, a mapping of string use-case IDs to ordered lists of records containing string `source_id` and `title` fields.
- Route function: `get_sources(use_case_id: str) -> UseCaseSourcesResponse | JSONResponse` in `app/main.py`.
- Models in `app/main.py`: `SourceResponse(source_id: str, title: str)` and `UseCaseSourcesResponse(use_case_id: str, sources: list[SourceResponse])`. Configure the route's successful response model explicitly.

- [ ] **Step 1: Prepare the local test environment.** Create package metadata and the package marker; use a project-local `.venv`. Install with `.venv/bin/python -m pip install -e '.[test]'`. Installation must succeed before the endpoint test cycle; dependency errors are not the intended red test.

- [ ] **Step 2: Write the primary contract tests in `tests/test_sources.py`.** Use TestClient with `app.main.app`. Assert exact response bodies and status codes:
  - `test_configured_use_case`: `/v1/use-cases/sample-use-case/sources` returns 200, `use_case_id` of `sample-use-case`, and one source with `source_id` of `sample-source-1` and `title` of `Sample source`.
  - `test_empty_use_case`: `/v1/use-cases/empty-use-case/sources` returns 200 and exactly `use_case_id` of `empty-use-case` and an empty `sources` array.
  - `test_unknown_use_case`: `/v1/use-cases/missing-use-case/sources` returns 404 and exactly `code` of `unknown_use_case` and `message` of `Unknown use case: missing-use-case`.
  - `test_case_sensitive_use_case`: `Sample-use-case` returns 404 with `unknown_use_case` and message `Unknown use case: Sample-use-case`.

- [ ] **Step 3: Verify the tests are red.** Run `.venv/bin/python -m pytest tests/test_sources.py -v`. Expect failure because `app.main` does not exist. Confirm the failure is the missing application, not a missing installed dependency.

- [ ] **Step 4: Implement the minimum endpoint.** Define the mapping with the exact sample record and `empty-use-case` mapped to an empty list. Define the models, app, and route in `app/main.py`. Use membership rather than list truthiness to distinguish unknown from empty. For an absent ID, return JSONResponse with status 404 and the exact top-level error fields. Copy records into the response models without modifying configuration. Register only GET for this path.

- [ ] **Step 5: Verify the primary contract.** Run `.venv/bin/python -m pytest tests/test_sources.py -v`. Expect all four contract tests to pass.

- [ ] **Step 6: Add the read-only and Review Focus checks.** Keep synthetic fixtures isolated with pytest monkeypatch:
  - `test_order_and_title_round_trip`: temporarily configure two records with IDs `source-z` then `source-a`; include title `Café "Guide"`. Assert exact titles and order in the JSON response.
  - `test_requests_preserve_configuration`: deep-copy the mapping, make repeated configured, empty, and unknown GET requests, assert repeated responses are identical and mapping equals its snapshot.
  - `test_post_is_not_allowed`: POST to the configured path, assert 405 and unchanged mapping.
  - `test_json_content_type`: parameterize configured and unknown GET requests and assert the content type starts with `application/json`.

- [ ] **Step 7: Verify all endpoint tests.** Run `.venv/bin/python -m pytest -v`. Expect all tests to pass. If an added check fails, reproduce it, make the smallest correction, and rerun the suite.

- [ ] **Step 8: Document local use in `README.md`.** Include virtual environment creation, installation with the test extra, `.venv/bin/python -m uvicorn app.main:app --reload`, the test command, and example requests for configured, empty, and unknown IDs. State that the source data is static sample configuration.

- [ ] **Step 9: Complete verification and review.** Run `.venv/bin/python -m pytest -v` and `git diff --check`; require passing tests and no whitespace errors. Check the implementation against the approved spec, including the absence of external calls and configuration writes. Review the resulting diff before committing.

- [ ] **Step 10: Commit the completed slice.** Stage only the implementation, tests, package metadata, and README files listed in this plan. Commit with message `feat: add read-only use-case sources endpoint`. Report the test results and local run command.

## Plan Self-Review

The single task covers every approved contract, static sample data, module boundary,
and verification requirement. Its additional tests cover all five Review Focus
conditions. No endpoint implementation or test code has been written as part of
planning. No execution method has been selected yet.
