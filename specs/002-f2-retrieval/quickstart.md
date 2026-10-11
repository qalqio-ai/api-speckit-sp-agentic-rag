# F2 planned validation quickstart

Status: native deterministic core implemented; live factory/wrapper/image and
source fixtures remain pending. Native tests are runnable now. Live examples
below remain proposed interfaces and have no acceptance evidence.
[Spec](spec.md), [plan](plan.md), [CLI](contracts/retrieval-cli.md),
[data model](data-model.md), [research](research.md).

Current native checks:

```bash
.venv/bin/python -B -m pytest tests/test_retrieval.py tests/test_retrieval_cli.py -q -p no:cacheprovider
.venv/bin/python -B -m pytest -q -p no:cacheprovider
.venv/bin/python -m ruff check app/retrieval tests/test_retrieval.py tests/test_retrieval_cli.py
```

These verify synthetic memory ports and actual F1/F2/F3 class composition, not
live embeddings or calibration. Unfinished module entry points exit nonzero with
`session_unavailable` and emit no READY. See [observed validation](validation.md).

## Prerequisites

Human review of written requirements/plan/limits; implementation tasks; exact F2
corpus/reuse and source-use receipt; reviewed calibration and held-out cases; specific
local image build/run and asset reuse authorization. Record approvals separately.
Keep Stage 1 venv intact. Existing fixtures alone lack competing within-scope sources.
No data creation, package install, model download or retained question/report capture
is authorized by this guide. Docker must be running for later integration checks.

## Deterministic checks after implementation

From repository root, establish unchanged regression baseline, then write/run F2
behavioral tests before implementing each behavior. Import/asset failures are not RED.

```bash
.venv/bin/python -B -m pytest tests/test_sources.py tests/test_ingestion.py tests/test_ingestion_cli.py -q -p no:cacheprovider
.venv/bin/python -B -m pytest tests/test_retrieval.py tests/test_retrieval_cli.py -q -p no:cacheprovider
.venv/bin/python -B -m pytest -q -p no:cacheprovider
.venv/bin/python -B -m ruff check . --no-cache
```

Cover bytes/tokens/types, exact scope, incomplete state, exhaustive pages, cap refusal,
configuration/hash changes, one exact full-N query, tied group crossing k, inclusive
threshold, missing/foreign/duplicate/payload-mismatch rows, safe failed-vs-no_match,
worker budgets, no question logs, EOF/close/interrupt and owned cleanup. Label all fake
vectors/scores. No unapproved real corpus is used to satisfy deterministic tests.

## Approved local live run after implementation

With specifically authorized prepared assets, an operator separately builds:

```bash
docker build -f Dockerfile.f2 -t f2-retrieval:local .
```

Then run without runtime build/pull/download or output capture:

```bash
bash scripts/f2-demo.sh --approval-manifest /absolute/f2-approved-manifest.json --retrieval-approval /absolute/f2-source-use-receipt.json --model-dir /absolute/reviewed-model-snapshot --min-score REVIEWED_NUMERIC_THRESHOLD --calibration-id REVIEWED_CALIBRATION_ID
```

The uppercase arguments describe required reviewed values; there is no default
threshold or claimed calibration. Normal retrieval and held-out require the explicit
reviewed threshold; the separate calibration evaluator examines full candidates
without a threshold, as specified below.
Keep reports on operator output unless a separate evidence retention policy approves capture.

In the same F2 session:

1. Ingest at least two approved distinct sources in the searched use case and an
   approved neighbor in another use case; inspect complete readiness/provenance.
2. Calibrate with separate reviewed positive/negative cases. Freeze threshold,
   corpus/source/configuration fingerprints and calibration case set. Nonseparation
   is a failure; do not tune on held-out questions or invent successful measurements.
3. Run at least three held-out supported paraphrases with top_k3: expected source in
   first3 each time. Inspect exact text/offsets/revision/model IDs and score ordering.
4. Run at least two held-out unsupported questions: no_match, zero passages under
   the frozen setting. Failure remains failed acceptance, not generation/abstention proof.
5. Search each scope sharing a source identifier: zero foreign passages. Replace a
   source: zero obsolete identities. Clear one scope: no_match, neighbor unchanged.
6. Close/EOF: collection removed and owned containers/network absent under the
   45-second policy. Independently inspect exact recorded project ownership/residue.

No live forced crash/capacity/host outage is required here; controlled failures and
cutoff ties are deterministic. A real query against pinned Qdrant1.19.1 must verify
the proposed API/response; documentation is not compatibility evidence.

## Full regression gate and evidence

After final code changes and approved Docker access:

```bash
COMPOSE_DISABLE_ENV_FILE=1 COMPOSE_ENV_FILES=/dev/null bash scripts/ci-local.sh
```

Record commands/exits/warnings, code snapshot, image/model/source identities, actual
supported/unsupported outcomes, score settings, elapsed time and owned cleanup. Separate
planning/static, deterministic, actual live, failed and unrun checks. Persist these
artifacts only under a reviewed access/retention/deletion decision.
F1 and R1 contracts including exact nested unknown-use-case 404 remain unchanged.
No remote CI, authentication, publication, commit or release follows this guide.

## Proposed evaluation runner (not yet executable)

After actual source/runtime/retention approval, prepare schema-valid reviewed
EvaluationCaseSet JSON and approved ingest-only JSONL. The latter must contain every
approved source/revision needed by the case set in the same session. Do not create
or process these files merely from this design. Proposed calibration invocation:

```bash
bash scripts/f2-demo.sh --approval-manifest /absolute/f2-approved-manifest.json --retrieval-approval /absolute/f2-source-use-receipt.json --model-dir /absolute/reviewed-model-snapshot --evaluation-cases /absolute/evaluation-cases.json --evaluation-split calibration < /absolute/approved-ingest.jsonl
```

EOF triggers `evaluate_cases` in the existing ready session, then owned cleanup.
Calibration has no --min-score/--calibration-id. Use its complete candidate summaries,
not ordinary top_k/threshold-filtered evidence, for the separator and expected-source
rank<=3 check. Failed ingest, missing expected candidate, empty negative scope,
nonseparation or any failed case prevents a claimed calibration success.

After review/freeze, repeat with `--evaluation-split held_out`, adding required
`--min-score REVIEWED_NUMERIC_THRESHOLD --calibration-id REVIEWED_CALIBRATION_ID`.
Verify case-file SHA-256 and manifest/config fingerprints before execution. Held-out
uses normal top_k3 output; no tuning or calibration on that split. Retain reports
only at the specifically approved location, with access/expiry/deletion recorded.
Isolation/replacement/clear scenarios remain the separate normal-session steps above.
