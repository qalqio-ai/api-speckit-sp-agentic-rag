# F3 validation guide

Native deterministic checks and the factory/wrapper implementation are available.
Live acceptance awaits approved assets, cases, calibration and capacity. [Plan](plan.md),
[CLI contract](contracts/answer-cli.md), [schema](contracts/serialization.schema.json).
No install/download/build/model/corpus operation is authorized by this document.

## Prerequisites and review

The user selected the closed-domain catalog boundary on 2026-10-03: exact reviewed
question aliases and claim renderings only; unknown phrasing abstains without
generation even when evidence might answer it. Do not re-ask this selection or
represent it as approval of arbitrary semantic QA or any execution action. Review
the detailed implementation design before building.
Local implementation and local build/run are already authorized. Verify F2 with real evidence; approve exact
F3 source use/catalog/cases and source owner/classification/access/redistribution;
review proposed model pin, actual file hashes, rights and approved acquisition/reuse;
confirm Docker/cgroup capacity and model/tokenizer/runtime compatibility under stated
ceilings; follow the approved safe-metadata policy when capturing reports.
No draft schema/receipt or historical F1 approval fills these gates.

## Deterministic checks after authorized implementation

Use existing native environment, with injected adapters only; no live model or corpus
processing. Write/run behavioral RED before implementing each behavior, distinguish
collection/environment errors from missing behavior, then rerun GREEN/regressions.
Current checks using the existing native environment:

```bash
.venv/bin/python -B -m pytest tests/test_answer.py tests/test_answer_cli.py -q -p no:cacheprovider
.venv/bin/python -m ruff check app/answer tests/test_answer.py tests/test_answer_cli.py
.venv/bin/python -B -m pytest tests/test_sources.py tests/test_ingestion.py tests/test_ingestion_cli.py -q -p no:cacheprovider
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Cover all schema fields/semantic invariants, full conditions/question coverage and
irrelevant valid IDs, unknown questions, conflict relevance, scope/revision/catalog
mismatch, malicious instructions, malformed/overlarge output, cold-load/stall/OOM,
original deadline and leader/descendant death cleanup. Fakes do not prove semantics.
F2 code/tests exist and remain unchanged. Current tests cover injected grounding/receipt composition,
bounded input/output/framed worker transport, native owned child termination, and
evaluation after successful ingest-only input reaches EOF. They do not prove cgroup
enforcement, escaped-descendant cleanup, real model quality or live F2 compatibility.
The local worker checks the pinned Linux/Python/CPU stack and fails closed on the
native macOS/Python3.10 environment. No model loads are performed by these checks.
See [actual validation](validation.md) and [required decisions](approval-request.md).

## Local session after the live gates

After separate reviewed asset acquisition/build, no runtime pulls/downloads/builds:

```bash
bash scripts/f3-demo.sh --approval-manifest /absolute/approved-manifest.json --retrieval-approval /absolute/f2-receipt.json --answer-approval /absolute/f3-receipt.json --grounding-catalog /absolute/reviewed-catalog.json --embedding-model-dir /absolute/approved-embedding-snapshot --generation-model-dir /absolute/approved-generation-snapshot --generation-assets /absolute/generation-assets.json --tmpfs-proof /absolute/tmpfs-proof.json --min-score REVIEWED_THRESHOLD --calibration-id REVIEWED_CALIBRATION_ID
```

Uppercase values are required actual reviewed settings, not defaults. In this same
ready session ingest only approved sources using unchanged F1 protocol; no collection
reopen. Submit one reviewed exact alias with op=answer and explicit scope. Inspect
actual model attempt count, every factual condition, exact current citations and mode.
Try reviewed unsupported shipping, empty scope, shared-source-ID neighbor, replacement
and clearing; expect explicit insufficiency or controlled failure, no foreign/obsolete
facts. Unknown question aliases must be identified as restricted catalog abstention.

For frozen evaluation add --evaluation-cases /absolute/approved-f3-cases.json; stdin
contains approved ingest requests only, EOF triggers normal answers in the same ready
session then teardown. Review >=3 actual supported generation cases and>=2 negatives.
Record every result/model/config/source/case/catalog identity and actual elapsed time,
not expected text as observed output. Human review assesses full semantic support;
invalid JSON or small-model quality failure stays failed acceptance. No live result
exists until this executes. Retention policy applies before output redirection/capture.

The wrapper mounts an optional case file read-only only when explicitly supplied;
no empty optional Compose bind is created. It creates a unique internal Docker
network and two owned containers from existing image IDs, without runtime pulls
or builds. The factory independently checks kernel caps, source-purpose/file
bindings, tokenizer/model settings and all case fingerprints before READY/input.
`F3_METRICS` on stderr reports observed runner/Qdrant cgroup peaks and maximum
completed transport latency after teardown; it contains no question/source/model
text. These measurements are not semantic acceptance. Ten GiB is a planning
allocation, not measured minimum memory. Asset acquisition is still pending.

## Cleanup and complete acceptance

Verify original240-second request and45-second teardown with deterministic clocks and
real observed cleanup separately. Inspect exact owned process group/descendants,
collection/container/network; uncertainty fails, no shared-volume removal/prune.
Run unchanged local Stage1 gate only with separate Docker approval; follow
[release guidance](../../docs/release.md). Record commands/exits/warnings, RED/GREEN,
model compatibility, live/unrun/failed outcomes and preservation hashes. No publication,
remote CI, commit, push or PR follows these checks automatically.

## Remediation checks before integration

Deterministic tests include an otherwise answerable unseen alias (zero-generation
catalog abstention), original exact rendering acceptance, model-fabricated conflict
reason rejection, F2 receipt count0 before search/count1 on query-send failure,
missing/full-scope receipt versus top_k, original deadline clamp and registry mutation.
Exercise stopped stdout consumers, partial writes, broken pipes and wrapper forwarding
on delegated envelopes: bounded nonzero termination, no accepted partial JSONL result,
no error on failed channel, independently verified cleanup within45 seconds.
F2's actual internal port/regressions must be verified before real composition; injected
F3 tests may precede F2 completion after implementation approval. These are future
checks, not observed results, and do not authorize any model/corpus/Docker run.
