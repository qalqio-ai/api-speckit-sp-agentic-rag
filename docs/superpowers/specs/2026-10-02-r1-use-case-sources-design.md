# R1: List configured use-case sources

## Intent and approval

Let an API client discover the sources configured for a use case through
`GET /v1/use-cases/{use_case_id}/sources`.

The user approved the in-chat design on 2026-10-02. Implementation remains
deferred: this document records the design for review, not permission to write
product code. The repository currently contains a README identifying FastAPI
as the framework, but no application implementation or roadmap file.

## Scope

Build one read-only endpoint backed by static in-memory sample data. No database,
authentication, LLM, vector database, external calls, or mutation endpoints are
included. Do not add unrelated refactoring or infrastructure.

## API contract

Use-case IDs are matched exactly and case-sensitively. A configured use case
returns HTTP 200 with its ID and an array of source IDs and titles:

```json
{
  "use_case_id": "sample-use-case",
  "sources": [
    {"source_id": "sample-source-1", "title": "Sample source"}
  ]
}
```

Preserve the configured source order. A configured use case with no sources
returns HTTP 200 with its ID and `"sources": []`.

An unknown use-case ID returns HTTP 404 with this top-level JSON error shape:

```json
{
  "code": "unknown_use_case",
  "message": "Unknown use case: missing-use-case"
}
```

The message includes the requested ID. The error is not wrapped in FastAPI's
default `detail` field.

## Components and data flow

- `app/main.py`: the FastAPI application, route, response contract, and unknown
  use-case response.
- `app/sample_data.py`: a static mapping from use-case IDs to ordered source
  records. Include the sample use case shown above and an empty configured use
  case so both configured outcomes can be verified.
- `tests/test_sources.py`: endpoint tests for the approved behavior.

The route looks up the requested ID in the mapping. Membership determines
whether the use case exists; an empty list must not be treated as an unknown
use case. For a configured ID, return its records in configuration order. For
an absent ID, return the specified error. Request handling never changes the
sample mapping. No service or repository abstraction is needed for this slice.

## Verification

Endpoint tests should verify:

1. A configured use case returns HTTP 200 and the exact approved response fields,
   including source IDs, titles, and configured order.
2. A configured use case with no sources returns HTTP 200 and an empty array.
3. An unknown use case returns HTTP 404 and the top-level `unknown_use_case` code
   and message containing the requested ID.
4. Case-different IDs are unknown unless independently configured.
5. Repeated requests return the same data and leave sample configuration intact.

## Next approval gate

Review and approve this written spec before preparing an implementation plan.
Product code remains deferred until the user authorizes implementation.
