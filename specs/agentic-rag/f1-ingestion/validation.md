# F1 implementation validation

Date: 2026-10-02. Status: complete for the approved F1 scope. All checks below are
local. [Spec](spec.md), [plan](plan.md), [tasks and acquisition ledger](tasks.md),
[run guide](quickstart.md), [CLI contract](contracts/ingestion-cli.md).

## Authorization and revision

Requirements were explicitly approved by the user. “I approve. Proceed.” subsequently
approved the exact T002 synthetic corpus, T003 model/dependency/image acquisitions,
local builds/runs and in-place execution. The approval receipt is recorded in
[approval.json](../../../tests/fixtures/f1/approval.json); it does not authorize other
sources, redistribution, a license grant or publication. Demo index lifetime is demo-end.

Base checkout HEAD: `4ed4368fbaabd5e9aaa333b071164119f46a37bd`; F1 is uncommitted working-tree
work, not a released revision. Existing work was preserved. Model commit:
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; full model-file hashes, exact source hashes,
resolved versions and image digests are in tasks.md. Final runner image:
`sha256:57969416c3863fc0b7c5e7ede8439cfc114cddcfeb3be1e4ec104dae577de3b5`.
Stage 1's native environment has neither sentence_transformers nor qdrant_client;
no installation was made there. F1 dependencies are confined to the Linux CPU image.

## Actual deterministic and configuration checks

| Command/procedure | Actual result |
| --- | --- |
| `.venv/bin/python -B -m pytest -q -p no:cacheprovider` | Exit 0: 113 passed, one existing Starlette TestClient/HTTPX deprecation warning |
| `.venv/bin/python -B -m ruff check . --no-cache` | Exit 0: all checks passed |
| `bash -n scripts/f1-demo.sh` | Exit 0; host C.UTF-8 locale warning |
| `F1_MODEL_DIR=/tmp/f1-reviewed-model F1_MANIFEST=/tmp/f1-approved-manifest.json F1_TMPFS_PROOF=/tmp/f1-tmpfs-proof.json docker compose --env-file /dev/null -f compose.f1.yaml config --quiet` | Exit 0; parsing only, separate from live mount proof |
| Protected-file SHA-256 comparison | 11 unchanged: AGENTS, constitution, R1 app/data/tests, Stage 1 Compose and verification scripts, roadmap, both F1 checklists |
| Post-implement hooks | `.specify/extensions.yml` absent; no registered hook dispatched |

The tests use deterministic clocks, tokenizer/vector/index fakes and injected
transports. They prove approval/input/schema handling, Unicode offsets and boundary
shrinking, stable IDs, replacement, exact allowlists and pagination, partial writes,
readiness/retry, malformed storage replies, offline hash verification, worker/command
budgets, ownership checks, EOF/interrupt/fatal cleanup and safe error envelopes.
They are not live outage, capacity, retrieval or answer-quality evaluations.
Behavioral RED/GREEN results and corrected harness/lint failures are recorded in tasks.md.

One independent read-only review found four Important issues; all were reproduced and
fixed. The final hard storage deadline uses a supervised process, shared bounded
response memory and a reserved termination budget, rather than relying on HTTPX's
inactivity timeout. An unconfirmed worker stop invalidates readiness and ends the
session. No acceptance criteria or checklist criteria were weakened.

## Fresh Stage 1 Docker gate

`COMPOSE_DISABLE_ENV_FILE=1 COMPOSE_ENV_FILES=/dev/null bash scripts/ci-local.sh`
exited 0 on the final code. Ruff, all 113 tests, local build/start, healthy `/health`,
configured-source HTTP 200, exact unknown-use-case nested HTTP 404 and owned cleanup
passed. Project: `ci-local-1790930359-26278`. Log: `/tmp/f1-stage1-gate.log`.
Independent project-filtered Docker container/network queries returned no IDs.
The reusable API contracts and implementations remain unchanged.

## Actual local live embedding/index demonstration

`docker build -f Dockerfile.f1 -t f1-ingestion:local .` exited 0. Dependencies were
installed with exact versions/hashes; build warnings concern root pip in the disposable
container. The separate offline one-vector probe ran with Docker `--network none`,
read-only model assets and offline flags: real vector dimension 384, max sequence 256.
The final live run rechecked the acquired hashes before each fresh embedding worker.

Actual final command (repository root):

```bash
bash scripts/f1-demo.sh --approval-manifest /Users/edmcbee/Projects/api-speckit-sp-agentic-rag/tests/fixtures/f1/approval.json --model-dir /Users/edmcbee/Projects/api-speckit-sp-agentic-rag/local-data/f1-models/1110a243fdf4706b3f48f1d95db1a4f5529b4d41 < /tmp/f1-live-input.jsonl > /tmp/f1-live-output.jsonl 2> /tmp/f1-live-stderr.log
```

Exit 0, 17 input lines and 17 schema-valid results. Actual records, not scripted
vectors, passed independent local assertions:

| Scenario | Actual evidence |
| --- | --- |
| Original ingest/inspect | 3 chunks; 100% non-whitespace character coverage, exact original slices/half-open offsets, matching source SHA and model/config identity; all vectors finite, nonzero, dimension 384 |
| Identical repeat | Same three IDs/count, no duplicates |
| Approved shorter revision | Exactly one replacement chunk, zero original IDs left |
| Same source ID in second use case | One isolated neighbor; zero foreign records; unchanged through replacement and clearing of first scope |
| Empty/unapproved text | Both rejected; later inventory unchanged |
| Scoped clear | First scope count zero; neighbor unchanged; second clear/inspect also zero |
| Close | Collection removal verified; owned containers/network removed; independent Docker queries returned no IDs |

The full original is 485 tokenizer wordpieces. Transformers warns about its length
while obtaining offsets without truncation; the model receives only re-tokenized
chunks within 256 tokens. Offset coverage and the maximum-end chunk verified the
final “End of original guide.” span; Qdrant scroll order is not source order.
Multi-page behavior and controlled storage-capacity failure are deterministic tests;
the live original inventory fits one scroll page. Storage was not filled as a stress probe.

Before ingestion, the wrapper verified tmpfs type and capacity 268435456 bytes,
Qdrant project ownership and an internal-only network; the runner's only attached
network was also verified before forwarding input. No ports, host networking, named
corpus volume, environment proxy, redirect or runtime download path is enabled.
Project: `f1-5646a9c517b0`. Qdrant container: `7f1b704ddb7cbcbf64035bff65d11e6fee4eacb9adea3ac7745f9791edad9e9f`.
Runner container: `88af8e470f212685c81ec3201aed93c16177cf7694af9c94ae2f12e2d141b628`. Network: `e3c6c2c444c2bf68410c17253637c66ed51023638fda5711bee6355275d4800f`.
Final teardown took **3.343 seconds** under the single 45-second
policy; absence verified, no unknown residue. `/tmp/f1-live-verified.json` contains the
local assertion summary. Temporary logs are local session evidence, not publication.

## Remaining boundaries and checks not run

No blocker remains for this approved F1 scope. Later F2–F7 retrieval, grounded answers,
model-selected decisions, memory, tools, evaluation and release remain separate slices.
No live forced slow-response/worker-crash/capacity-exhaustion or host-failure test was
run; controlled failure/deadline cases are explicitly deterministic. SIGKILL/host
failure can bypass traps; use the recorded owned project for scoped recovery and
report residue until verified. Tmpfs is not secure erasure or a total-RAM cap.

Dependency hashes and upstream card metadata do not establish vulnerability clearance
or legal redistribution rights. License/rights holder and any external release still
require their own decisions. Authorized external acquisition retrieved public model,
package and image bytes; source text stayed local. No corpus upload, native F1 install,
GitHub Actions, Docker Hub automated build, commit, push, PR or publication occurred.

Final application/source snapshot SHA-256 (working-tree bytes):

| Path | SHA-256 |
| --- | --- |
| `app/ingestion/__init__.py` | `81f7e53987ce84ce20d093770bcc8670372e6847dc91ed7e72b2a3824811a832` |
| `app/ingestion/__main__.py` | `c8df838a59cf3a1c1cf12ecf0804a71490da29104af21cd45fe9d3d68fa9dfbc` |
| `app/ingestion/chunking.py` | `3a711262efd2b3fc5bbe73d0be26f686e810cb5e6a3e1bb2bfd17f04bf2d56cc` |
| `app/ingestion/demo.py` | `b6e8175c1c3a7be43d25c457207827f5f9c0c14fa919f1a9adc2e3fe6afbee32` |
| `app/ingestion/embedding.py` | `563bb49f63fd582b975b60dc8a1d51d6abfbbe127a6bbf06eba4144915b29eb5` |
| `app/ingestion/index.py` | `35900793ea5f3b2ec7a9a7d54dcb3dd83b85a6481d6d6343eab9fb2d0c67637e` |
| `app/ingestion/lifecycle.py` | `baaa063ec755896db8af74577a440661a83d19f32af04d20844d340b1bf5ec07` |
| `app/ingestion/service.py` | `96fad3ab5216ffad5a8d26ce9c950b3825b65ff110d09f87d4c65a29b71e4092` |
| `app/ingestion/types.py` | `82a5baca2541bdc7ae6e59070fdce41994bb4678c8a2e62cec39213f8d883149` |
| `app/ingestion/validation.py` | `a6e6e926e425cdcf29f2bab67f4d0eb8dee1b0708371a74ff37d11e76c9060e2` |
| `tests/test_ingestion.py` | `15f2a7d74e5990faa171bc42a458e39af0cb2dca1e94f3cc08800ef2643ee120` |
| `tests/test_ingestion_cli.py` | `387bf567a36a820424bb92ead54458022a77787c5ddf7e0bd76244dc12e63ad8` |
| `Dockerfile.f1` | `c736ee87f96cdcdcf0edab5725c1ecf321eafb23ca73b76a11d103b5a7bf7515` |
| `compose.f1.yaml` | `0a648967b91003192cf9908ce1e6400bede9073099ffe4763ddbea63846bc8cf` |
| `requirements.f1.lock` | `f690cea86a714676b147030443627caf8d5ba90840fda58e483c642932193335` |
| `scripts/f1-demo.sh` | `67cf38ff2ca3942ad44e5acb225d20b1ead3ea238e60dd5131ea78263ae6fa66` |
