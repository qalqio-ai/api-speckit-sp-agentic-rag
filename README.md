# Foundational Multi-Use API

A small FastAPI service that exposes stable API contracts across configured use cases.

## Project stages and governance

Stage 1 is this reusable API. Stage 2 appends Agentic RAG in the same repository,
preserving the API contracts. F1 ingestion is approved and implemented as a separate
local CLI; see its [run guide](specs/agentic-rag/f1-ingestion/quickstart.md).
See the [project brief](docs/project-brief.md), [initial scope](specs/001-initial-scope/spec.md),
[agent guidance](AGENTS.md), [roles](agents/roles.md), and [skills index](agents/skills-index.md).

The sole active [constitution](docs/constitution.md) preserves the starter's ten
principles. Existing R1 Spec Kit-style artifacts are preserved; official adoption
is not established. Follow the [adoption boundary](docs/evolution-path.md) to avoid
duplicate constitutions or hand-written tool internals. Project-owned
[requirements](docs/templates/prompt-requirements.md), [feature](docs/templates/feature-spec.md),
[plan](docs/templates/implementation-plan.md), and [task](docs/templates/tasks.md)
templates support the next reviewed slice without copying upstream skills.

Checks are local-only. [Docker Hub image release](docs/release.md) requires separate
approval; no publication is claimed. License, rights holder and Stage 2 corpus
permission for other corpora remain undecided. F1 uses the explicitly approved
synthetic fixtures only. [Reconciliation](docs/governance-reconciliation.md)
records dispositions and actual checks. No license grant is generated.

## Local setup

Requires Python 3.10 or later. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
```

## Run and test

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

The service runs at `http://127.0.0.1:8000`. Interactive API documentation is at
`http://127.0.0.1:8000/docs`; the schema is at `/openapi.json`.

Run the full test suite:

```bash
.venv/bin/python -m pytest -v
```

## R1: Discover sources

Run the complete local CI check with Docker running and the test extra installed:

```bash
./scripts/ci-local.sh
```

The script runs Ruff and all tests, builds and starts a temporary Docker Compose
API service, waits up to 60 seconds for `/health`, checks the configured and
unknown-use-case responses, and removes its container and network on exit.
The Docker setup is embedded in the script. Each run uses its own Compose
project and a random localhost port. Built images remain available in Docker's
cache. `CI_LOCAL_PYTHON` can select a different Python executable.

`GET /v1/use-cases/{use_case_id}/sources` reads static in-memory sample data in
`app/sample_data.py`. IDs are exact and case-sensitive; source order and titles
are preserved. Requests require no credentials and make no outbound calls.
R1 does not load an embedding model or vector database and has no
configuration-editing endpoint.

Configured use case — HTTP 200:

```bash
curl -i http://127.0.0.1:8000/v1/use-cases/sample-use-case/sources
```

```json
{"use_case_id":"sample-use-case","sources":[{"source_id":"sample-source-1","title":"Sample source"}]}
```

Configured use case with no sources — HTTP 200:

```bash
curl -i http://127.0.0.1:8000/v1/use-cases/empty-use-case/sources
```

```json
{"use_case_id":"empty-use-case","sources":[]}
```

Unknown use case — HTTP 404:

```bash
curl -i http://127.0.0.1:8000/v1/use-cases/missing-use-case/sources
```

```json
{"detail":{"code":"unknown_use_case"}}
```

All these responses are JSON. POST to the sources path returns HTTP 405.
Requests never create, update, delete, or reorder the sample configuration.

## Verified environment

Python 3.10.10; FastAPI 0.142.2; Uvicorn 0.54.0; Pydantic 2.13.5;
Starlette 1.7.0; pytest 9.1.1; HTTPX 0.28.1.

The tested Starlette version emits a deprecation warning about TestClient's
HTTPX integration. The tests pass; migrating the test client is outside R1.


## F1: Local ingestion learning slice

F1 accepts approved plain text, produces original-character chunks and local CPU
embeddings, and maintains an inspectable temporary Qdrant index. It demonstrates
stable IDs, shorter-revision replacement, exact scope isolation and verified clearing.
F1 provides ingestion; retrieval and grounded answers are separate later features.

The dedicated Linux runner uses hash-locked dependencies, a separately mounted
immutable MiniLM snapshot, an internal Docker network and a verified 256 MiB tmpfs.
Models and corpus are excluded from images; runtime downloads are disabled. Build
and acquire assets only under specific operator authorization. The native Stage 1
venv remains separate. Run instructions and actual evidence are in the
[F1 quickstart](specs/agentic-rag/f1-ingestion/quickstart.md) and
[validation record](specs/agentic-rag/f1-ingestion/validation.md).

## F2: Scoped retrieval in progress

The F2 core verifies the complete current ready scope, performs one exact
search, validates every candidate and returns ranked evidence. The local workshop
candidate has live scoped retrieval and calibration evidence, including 5/5 fresh
F2 cases. Overall status remains PARTIAL because an additional supported F3
phrasing failed retrieval before generation. See the
[F2 guide](specs/002-f2-retrieval/quickstart.md) and
[observed validation](specs/002-f2-retrieval/validation.md).

## F3: Grounded answers in progress

F3 implements a closed catalog of reviewed question aliases and complete claim
renderings, with current-evidence support and citation checks. Supervised local
execution and the guarded workshop launcher are implemented. The workshop model
selects among reviewed supported claims and abstention; fresh F3 acceptance was
5/6, so the candidate remains PARTIAL. Exposed-question rehearsals are regression
demonstrations. Model assets and approval-bound runtime inputs are prepared
separately and are required for live execution.
See the [F3 guide](specs/003-f3-grounded-rag/quickstart.md),
[validation record](specs/003-f3-grounded-rag/validation.md), and
[remaining decisions](specs/003-f3-grounded-rag/approval-request.md).

The current workshop checkpoint is `SEDA-20261008-rehearsed-partial-rc2`.
Use its [operator command card](workshop/seda-20261008-v2/operator-command-card.md)
and [readiness receipt](workshop/seda-20261008-v2/readiness-receipt.md).
Generation-backend adapters and warm-inference optimization are follow-up work;
no latency improvement or full F3 acceptance is claimed. F4 remains outside this
checkpoint.
