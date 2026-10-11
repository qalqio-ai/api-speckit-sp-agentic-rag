# F1 planning research

Date: 2026-10-02. Status: design decisions documented; subsequent acquisitions and runtime checks
are recorded in [tasks.md](tasks.md) and [validation.md](validation.md).
Research used primary documentation; no package/model download or service startup.
User answer **“use temporary/local”** resolves D1/D2. No source approval is inferred.

## Temporary local storage

Decision: a dedicated Compose Qdrant service with tmpfs storage and runner-owned
collections, stopped at demo end. Proposed server/client pair: 1.19.1, with exact
image digest and dependency resolution recorded at the authorized build.
Rationale: demonstrates real vector indexing without retaining a document index or
altering Stage 1's service. Qdrant uses REST port 6333 and `/qdrant/storage`; keep it
inside the dedicated network. The client's declared Python floor is 3.10, but no
installation/server-client compatibility was tested.
Alternatives: persistent named volume conflicts with D1; embedded Qdrant weakens the
runbook's separate-service exercise. The tmpfs choice is an explicit runbook deviation.

Sources: [Qdrant installation](https://qdrant.tech/documentation/installation/),
[server release](https://github.com/qdrant/qdrant/releases/tag/v1.19.1),
[client metadata](https://pypi.org/project/qdrant-client/1.19.1/),
[Docker tmpfs behavior](https://docs.docker.com/engine/storage/tmpfs/).
Tmpfs can reach swap and is not a secure-erasure guarantee. Docker Desktop mount
permissions and real operation must be checked; no silent disk-persistence fallback.

## Identity, scoping, and failure recovery

Decision: UUIDv5 over canonical use-case/source/revision/content/configuration/offset
identity. Every inspection/mutation uses exact scope filters; replace by upsert,
scoped obsolete-ID deletion, then exhaustive read-back. Track source readiness in the
single runner's memory, with fresh collections on restart.
Rationale: Qdrant accepts UUID IDs and upsert overwrites an existing ID. Its filters
support mandatory conditions, and scroll pagination needs explicit exhaustion.
Our UUID construction/readiness protocol is a design inference, not a database feature.
Alternatives: random IDs break stable repeats; delete-first replacement destroys good
records before computation; asserting atomic multi-step replacement is unsupported.

Use `upsert(..., wait=True)`, `delete(..., wait=True)`, and
`scroll(..., with_payload=True, with_vectors=True)` with scope filters. A timeout
makes completion uncertain: mark incomplete and explicitly reconcile; no blind retry
or successful receipt. Application state is not resumed after restart.
Sources: [point IDs/upsert](https://qdrant.tech/documentation/concepts/points/),
[filtering](https://qdrant.tech/documentation/search/filtering/),
[scroll](https://api.qdrant.tech/api-reference/points/scroll-points),
[write completion](https://qdrant.tech/documentation/manage-data/points/).

## Local CPU embedding and chunking

Decision: a local Linux Python 3.12 CPU runner with proposed
`sentence-transformers==6.1.0` and a reviewed local
`sentence-transformers/all-MiniLM-L6-v2` snapshot. Preserve Stage 1's native venv.
The model produces 384-dimensional embeddings and truncates beyond 256 wordpieces.
Use proposed windows of 200 content wordpieces/20 overlap, original character offsets,
and re-tokenization with special tokens and truncation disabled before encode. Reject
or subdivide oversize slices; do not silently truncate. These window values are our
learning-demo design, not universal retrieval-quality recommendations.
Rationale: small local English baseline, inspectable outputs, no hosted text transfer.
Alternatives: hosted embeddings violate D2; native Intel macOS requires a separately
validated dependency stack and is not required for this container demonstration.
Older published Intel PyTorch wheels do not establish security or runtime compatibility.

Use `device="cpu"`, `local_files_only=True`, `trust_remote_code=False`, and offline
hub mode before imports. Mount model assets read-only; missing assets fail. Exact
snapshot commit/hash, transitive dependency locks, and image digest must be recorded
when separately authorized acquisition/build occurs; none is invented here.
Sources: [model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2),
[package metadata](https://pypi.org/project/sentence-transformers/6.1.0/),
[model constructor](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html),
[offline mode](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables#hfhuboffline).
No weights, benchmarks, transitive imports, or legal clearance were obtained.

## Interface and budgets

Decision: a local sequential JSON-lines session, scoped approval manifest, injected
adapters/clock, no new HTTP endpoints. Source deadline 120 seconds, storage request
cap 10 seconds, no automatic retries, 64 KiB source text and 2,048 chunks maximum.
Rationale: bounded workshop ingestion with deterministic failure tests; the limits
are proposed engineering defaults for review, not measured performance promises.
Alternatives: unrestricted parallel ingestion and a remote API increase scope.
An interruptible worker process enforces embedding timeout; thread timeout alone
would not stop computation. No implementation was performed to verify this design.

All Phase 0 design choices have a proposed resolution. Requirements approval and
prior implementation requests are recorded in plan.md. The subsequent explicit T002/T003 approval and actual local checks are recorded
in tasks.md and validation.md. Initial research is not runtime evidence.
