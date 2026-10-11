# F1 validation quickstart

Status: implemented local validation guide. See [actual checks](validation.md);
deterministic results and live integration evidence are recorded separately.
[Spec](spec.md), [contract](contracts/ingestion-cli.md), [data model](data-model.md).

## Prerequisites

Requirements approval is recorded on 2026-10-02 (“I've approved the requirements.”),
and prior implementation requests are acknowledged. The subsequent “I approve. Proceed.” authorizes the exact T002 synthetic fixtures,
T003 acquisitions/builds and in-place execution recorded in [tasks.md](tasks.md).
The approved manifest is `tests/fixtures/f1/approval.json`; real source hashes, model
commit/file hashes and image digests are recorded in that execution ledger.
Other sources/acquisitions need their own authorization. Docker Desktop must be running. Preserve Stage 1's native venv.
An approved build records exact Linux dependency lock and image digests. Do not execute
unreviewed starter scripts or read credentials/environment files.

No installation/download command is run by this guide. Obtain model assets in a
separately authorized step; do not bake them or the corpus into the application image.
Runtime loading is offline. If prerequisites are absent, label the live check not run.

## Deterministic local checks

From repository root:

```bash
.venv/bin/python -m pytest tests/test_ingestion.py tests/test_ingestion_cli.py -q
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
bash scripts/ci-local.sh
```

Expected: new tests and existing R1 regressions pass, lint passes, and the Stage 1
Docker gate passes with its exact 404. New tests must first show a behavioral failure
before implementation; record commands/status/output, not presumed results.
These tests inject deterministic tokenizer/vector/index fixtures and make no provider
or service call. They do not establish live embedding or actual storage behavior.

## Local live demonstration

With the approved assets already acquired and the images locally available:

```bash
# Separate local build, after acquisition approval; dependencies are hash locked.
docker build -f Dockerfile.f1 -t f1-ingestion:local .
bash scripts/f1-demo.sh --approval-manifest /absolute/approved-manifest.json --model-dir /absolute/reviewed-model-snapshot
```

Supply newline-delimited operations on stdin and finish with `{"op":"close"}`
or EOF. Example ingestion uses the exact bytes of an approved fixture, including
its title/revision from the manifest; see [the contract](contracts/ingestion-cli.md).
The acquired snapshot directory in this workspace is
`local-data/f1-models/1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.

The wrapper uses `compose.f1.yaml`, an isolated recorded project name, a read-only
model/input mount, and tmpfs Qdrant storage. It preflights offline imports/model
shape, actual storage readiness, and a verified 256 MiB (268,435,456-byte) tmpfs
mount limit before ingestion. The wrapper verifies the actual mount type and limit; this is a filesystem limit,
not a total-RAM cap or a measured corpus-capacity guarantee. Compose must use an explicit
empty env-file unless a separately approved non-secret configuration is provided;
do not auto-read `.env`. The wrapper creates a read-only `--tmpfs-proof` receipt from Docker mount evidence.
The CLI requires that receipt for live startup. The wrapper's supported input follows the CLI contract.
Its trap stops/removes only this stack; no named corpus volume or global deletion.

Within the session, demonstrate:

1. Ingest one approved text; inspect exact chunk slices, offsets, IDs, metadata,
   384-dimensional vectors, model/config identity, and reported count.
2. Repeat identical input: same ID set/count, zero duplicates.
3. Submit approved shorter revision: exactly the new set, zero obsolete IDs.
4. Use a second approved corpus with the same source ID: zero cross-scope records.
5. Reject empty/unapproved/malformed input before embedding/indexing.
6. Simulate failures in deterministic mode: preparation/embedding failure or
   controlled worker timeout returns a failed attempt while preserving prior source
   readiness; explicit retry uses a fresh worker. A mutation/read-back failure returns
   incomplete/not ready and explicit retry reconciles. Unexpected worker exit, broken
   protocol, or failure to terminate ends the session with cleanup/nonzero exit;
   recovery uses a fresh approved run. Label simulation, not a live outage result.
   Also inject a storage-capacity failure: incomplete/not ready, index_failed,
   unknown counts null, no resize/retry/disk fallback; recover by verified scoped
   clearing or a fresh approved run. Do not fill host storage for this check.
7. Clear one scope; confirm zero records and unchanged neighbors. Close the demo;
   confirm owned collection/service cleanup. Never report cleanup on uncertain status.

Inspect all scroll pages; test an input longer than one model window so final content
cannot disappear through token truncation. A vector from a fake is not a live embedding.
No semantic search, answer, memory, agent, or tool call belongs in this F1 demonstration.
Validate manifest and protocol shape against [the serialization contract](contracts/serialization.schema.json)
and its [semantic rules](contracts/ingestion-cli.md). Unknown fields, invalid types,
nulls/enums, duplicate keys and conflicting approval tuples are deterministic failure
cases. A schema-valid artifact is not proof of actual approval.

## Evidence and recovery

Record source revision, code revision, commands/exits/warnings, model snapshot/file
hashes, package lock/image identities, inspection counts, and cleanup status. Explicitly
separate deterministic tests, actual local live demonstration, and unrun checks.
A local vector/index result says nothing about F2 retrieval or F3 answer quality.

If cleanup fails or a process is killed, stop/remove the recorded dedicated project
using the reviewed F1 Compose file and explicit env-file before the next demo. Do not
run global prune or remove unrelated volumes. Apply the [bounded teardown policy](contracts/ingestion-cli.md#bounded-shutdown-and-teardown-policy):
one 45-second deadline, worker <=5 seconds (TERM 2/KILL wait 3), collection <=10
seconds, Docker <=30 (down 15/kill 5/remove 5/verify 5). Remaining time caps all calls;
repeated signals do not reset it. Preserve failure status and report any residue until recovery is
verified. Docker tmpfs does not promise secure erasure. No GitHub Actions, Docker Hub
automated build, commit, push, PR, authentication, or publication is part of this guide.
