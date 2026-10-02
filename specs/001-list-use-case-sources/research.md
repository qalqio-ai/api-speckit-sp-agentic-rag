# R1 Research Decisions

## Framework and runtime

**Decision**: Use FastAPI with Uvicorn and Python 3.10 or later.

**Rationale**: The existing README identifies FastAPI; the approved design uses
it. Local `python3 --version` reports 3.10.10, which supports the proposed type
syntax. Package compatibility will be confirmed when implementation installs
dependencies, rather than guessing exact versions during planning.

**Alternatives considered**: Flask or another framework would contradict the
existing project direction without providing value for this endpoint.

## Configuration and lookup

**Decision**: A static `USE_CASE_SOURCES` mapping associates exact string IDs with
ordered source records. Check ID membership separately from source-list length.

**Rationale**: This preserves the approved difference between unknown and empty
use cases. Ordinary list order preserves configured source order. Construct new
response records rather than changing shared configuration.

**Alternatives considered**: Handler-local samples couple configuration to HTTP
logic. A repository, database, cache, or external configuration service adds
unneeded structure or violates scope. ID normalization changes the contract.

## Response contracts

**Decision**: Declare `SourceResponse` and `UseCaseSourcesResponse` as successful
response models, with an explicit route `response_model`. Return an explicit
HTTPException with `detail={"code":"unknown_use_case"}` for unknown IDs and document the 404 shape in the route's additional
responses. An error model may describe this shape without adding a new module.

**Rationale**: The success schema documents and filters response fields. Explicit
HTTPException preserves the user's amended nested error body. Explicit
`response_model` documents the successful schema independently of error handling.

**Alternatives considered**: The earlier explicit top-level JSONResponse was
superseded by the user's rule amendment. Global exception handling is unnecessary
for one endpoint.

**Sources**: [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/)
and [additional responses](https://fastapi.tiangolo.com/advanced/additional-responses/).

## Verification

**Decision**: Use pytest and FastAPI TestClient with HTTPX, plus a local-server
smoke check after implementation.

**Rationale**: Tests can exercise HTTP status, JSON bodies, ordering, and method
rejection without a running external service. Snapshot comparison of sample
configuration verifies read-only behavior across successful and failed requests.

**Alternatives considered**: Mocking the handler bypasses routing and response
serialization. A deployed environment adds no value for static sample data.

**Source**: [FastAPI testing documentation](https://fastapi.tiangolo.com/tutorial/testing/).

## Research closure

All design choices are resolved from the approved scope, inspected repository,
and official framework documentation. No new user choice, integration research,
performance target, or product dependency installation is needed for planning.
