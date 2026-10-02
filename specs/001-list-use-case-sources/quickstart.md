# R1 Quickstart Validation Guide

This guide validates the implemented R1 slice. The user's rule amendment is
authoritative: unknown use cases return exactly
`{"detail":{"code":"unknown_use_case"}}` with HTTP 404.

## Prerequisites

- Python 3.10 or later, with venv and pip available.
- The R1 implementation present in the repository.
- Network access for initial package installation only; source discovery needs
  no credentials or external service.

## Setup

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
```

The package metadata includes FastAPI and Uvicorn as runtime
dependencies, and pytest and HTTPX in the `test` extra. Use a compatible
dependency set and record resolved versions during implementation.

## Automated validation

```bash
.venv/bin/python -m pytest -v
git diff --check
```

Expected: all endpoint tests pass and no whitespace errors are reported. Cover
the scenarios in [spec.md](spec.md), including exact body shapes, configured
order, empty configuration, unknown IDs, case and whitespace differences,
Unicode and quoted titles, JSON content types, and configuration preservation.
Use isolated temporary fixtures for source-order and title edge cases.

For test-first implementation, confirm the initial endpoint tests fail because
the application or required behavior is missing after dependencies are
installed; then add the minimum behavior and rerun them.

## Local HTTP validation

Start the server:

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

In another terminal:

```bash
curl -i http://127.0.0.1:8000/v1/use-cases/sample-use-case/sources
curl -i http://127.0.0.1:8000/v1/use-cases/empty-use-case/sources
curl -i http://127.0.0.1:8000/v1/use-cases/missing-use-case/sources
curl -i http://127.0.0.1:8000/v1/use-cases/Sample-use-case/sources
curl -i -X POST http://127.0.0.1:8000/v1/use-cases/sample-use-case/sources
```

Expected statuses, respectively: 200, 200, 404, 404, and 405. Compare JSON bodies
with [contracts/sources.md](contracts/sources.md). Repeat the configured request
after the failed and rejected requests; its response must remain unchanged.
Automated snapshot tests additionally verify the full configuration is intact.

Inspect `http://127.0.0.1:8000/docs` to confirm the operation and its 200/404
response shapes are documented. Stop the local server after validation.

## Validation results

The full suite passed all 11 tests, with one existing Starlette/HTTPX deprecation
warning. Live HTTPX requests against Uvicorn on localhost:8000 verified the five
scenarios above with statuses 200/200/404/404/405 and exact expected JSON bodies.
The configured response remained unchanged after rejected requests. `/docs` and
the generated 200/404 OpenAPI schemas were checked, and the server was stopped.
