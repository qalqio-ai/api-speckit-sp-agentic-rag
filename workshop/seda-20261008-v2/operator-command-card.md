# SEDA operator command card — 8 October 2026

**PARTIAL** — checkpoint `SEDA-20261008-rehearsed-partial-rc2`. This is a known-regression rehearsal of constrained selection of reviewed claims, not fresh F3 acceptance or unrestricted answer generation. Historical fresh F3 acceptance remains 5/6 with a supported-question retrieval miss. No F4.

Execution host: current repository Intel Mac, macOS13.2.1/x86_64, Intel Core i9-9980HK. **Actual presentation-machine identity is UNCONFIRMED**; no user statement identifies this host as that machine. New execution record: [operator-preview receipt](evidence/operator-preview-20261008-01/receipt.md). Source documents: [runbook](organizer-runbook.md), [historical readiness receipt](readiness-receipt.md), [prerequisites](slide-7-prerequisites.md).

Use the existing `.venv`; install/download nothing. Never source an environment file. All blocks run from the repository root. `SEDA_REPORT` below is only a shell variable selecting a local evidence file; it is not a model or service setting.

## 1. Preflight and candidate identity

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
.venv/bin/python -B -m workshop.preflight
docker image inspect sha256:f1dc063ca46a05ccce548121c1f530eb1d7ce2edc87dc27db1f32d3ba2cdf00a --format '{{.Id}}'
shasum -a 256 workshop/seda-20261008-v2/frozen.json workshop/seda-20261008-v2/launch-guard-v1.json
```

Expected: `local_assets_ready:true`, `service_readiness_claimed:false`; image equals the inspected digest above. Bundle hash `664ef00e57d60043758ebadd56e5747f20a4269d73eda73d4eae1fe8049f88fc`; guard hash `c530f5eb97857dae4a906c0ad9f0f220571df38e301ddf009030a912986fa777`. The guard checks host code and the exact image; preflight additionally checks frozen inputs and 17 approved model files. Stop on mismatch.

Candidate image tag `seda-workshop:20261008-rc1`; bundle `SEDA-constrained-selection-rc2`. Threshold `0.42808731`, calibration `EDM-f2-20261007-v2`; retrieval fingerprint `73aa0d04f345d7c4609e6fa4329ff7a8bcd46f1495afd25a04f03819eaf75870`. The original freeze remains unchanged. No fresh acceptance command is included.

## 2. Original local CI gate

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
./scripts/ci-local.sh
```

Exact original script, no arguments or environment overrides. `CI_LOCAL_PYTHON` defaults to this repository’s `.venv/bin/python`; `CI_LOCAL_CONTEXT` is exported internally by the script. Do not substitute the frozen F3 image into this Stage1 gate: its temporary API build is separate. It runs Ruff/tests, Compose build/start, `/health`, exact configured200 and unknown404, then `compose down --timeout 10 --remove-orphans` for its unique `ci-local-…` project. Health deadline60s; each HTTP request2s. There is no script-wide wall-clock timeout. Built image remains cached.

Today's exact invocation was captured in `evidence/operator-preview-20261008-01/original-ci.log`; it passed using cached build/install layers. A future uncached invocation can attempt upstream access because the original script uses `python:3.12-slim` and `pip install .`; offline reproducibility of that script is not claimed. Do not download dependencies or change the frozen candidate to overcome a missing cache.

## 3. Launch, readiness, approved corpus, both queries and cleanup — ONE operation

Exact command executed for today's new record:

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
.venv/bin/python -B -m workshop.launch --output workshop/seda-20261008-v2/evidence/operator-preview-20261008-01/rehearsal.json
```

**That historical destination is exclusive and now exists. Do not repeat it or delete it.** For another live preview, the same operation may use only a fresh evidence filename:

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
SEDA_REPORT="workshop/seda-20261008-v2/evidence/operator-live-$(date +%Y%m%dT%H%M%S).json"
.venv/bin/python -B -m workshop.launch --output "$SEDA_REPORT"
```

The timestamp destination is a prepared repeat instruction; today's execution used the literal path above. No service is left running. The wrapper owns a unique internal `f3-…` network, temporary Qdrant and read-only runner; verifies caps/mounts/tmpfs; factory-starts; ingests frozen `fixtures/ingest.jsonl`; asks **both** questions from steps4/5; verifies results; closes its collection; removes only its owned containers/network; writes one JSON report. No separate provisioning command, interactive question flag, HTTP answer endpoint, port, authentication or persistent-service sequence exists for this rehearsal.

Mounted approvals: `approval.json`, `retrieval-approval.json`, `answer-approval.json`, grounding catalog and fixed source tuples. Provisioning includes approved synthetic returns-v1, opening-hours-v1 and isolated neighbor returns-v1; model snapshots are read-only `/embedding` and `/generation`. Runtime `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`; tokenizer parallelism is disabled. Host exports are unnecessary.

`SEDA_READY` is emitted after actual factory startup and corpus ingestion, but the host wrapper captures container output; it does **not** expose a streaming readiness endpoint. Inspect `cold_factory_startup_ms` and `ready_with_corpus_ms` in the completed report. Expect minutes of quiet waiting, not an interactive terminal prompt.

Preserved limits: request240s, retrieval120s (embedding90s/search10s), generation110s, validation10s, startup120s; generation384newtokens/16,384completionbytes; runner8GiB/4CPUs, Qdrant1GiB, no additional swap; tmpfs runner64MiB/Qdrant256MiB. Host wrapper total Docker deadline1500s. Owned teardown contract≤45s; wrapper recovery uses cleanup-start+10s and removal/absence verification cleanup-start+30s. Do not increase limits. Allow90s corpus preparation and60s answer narration; these are pacing allowances, not acceptance changes. Do not run model sessions concurrently on the ~3.82GiB tested Docker VM.

## 4. Exact supported question — already executed by step3

`use_case_id=f2-synthetic`, `case_id=edm-answer-1`, question **What is the return policy?** Expected reviewed claim: **Unused items may be returned within 7 days with a receipt.** Both answered and abstention choices remain available during genuine generation. There is no separate single-question launcher; do not rerun step3 merely for this section.

To inspect the completed current run (recorded evidence, not a new query):

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
SEDA_REPORT=workshop/seda-20261008-v2/evidence/operator-preview-20261008-01/rehearsal.json
.venv/bin/python - "$SEDA_REPORT" <<'PYCODE'
import json,sys
report=json.load(open(sys.argv[1]))
case=next(c for c in report['cases'] if c['case_id']=='edm-answer-1')
print(json.dumps({k:case[k] for k in ('case_id','question','passed','result','checks','retrieval_ms','generation_ms')},indent=2))
PYCODE
```

For a new preview, use its new `SEDA_REPORT` value instead of resetting to today's record.

## 5. Exact unsupported question — already executed by step3

`use_case_id=f2-synthetic`, `case_id=edm-answer-4`, question **What is the shipping policy?** Expected `insufficient_evidence/no_evidence`, zero claims/citations/generation. This reports missing approved evidence; it makes no factual assertion about a real shop.

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
.venv/bin/python - "$SEDA_REPORT" <<'PYCODE'
import json,sys
report=json.load(open(sys.argv[1]))
case=next(c for c in report['cases'] if c['case_id']=='edm-answer-4')
print(json.dumps({k:case[k] for k in ('case_id','question','passed','result','checks','retrieval_ms','generation_ms')},indent=2))
PYCODE
```

## 6. Evidence and citation inspection — explicitly recorded playback

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
.venv/bin/python -B -m workshop.present "$SEDA_REPORT"
```

It prints **RECORDED LOCAL EVIDENCE**, exact returned claim, supporting chunk IDs, approved passage, scope/source/revision/hash/offsets, query totals and collection/stack absence. It never runs a model. Approved support for the return claim: source `returns`, revision`v1`, passage “Synthetic returns: unused items may be returned within 7 days with a receipt.”, hash`50e85780308baf9945671e2c05be5ef4fa3e02ccd805babd2b6809ee52eb841d`.

Detailed raw generated output, nonce-bound rendered-input/constraint hashes, token/EOS diagnostics and unchanged validation checks are in the report’s supported case. Inspect actual retrieved membership and support; never attach or repair citations afterward.

## 7. Owned cleanup and independent absence

Normal cleanup is already part of step3; step2 likewise cleans its unique CI project. These checks are read-only and independently verify today's exact recorded resources:

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
SEDA_PROJECT="$(.venv/bin/python -c 'import json,re,sys; p=json.load(open(sys.argv[1]))["project"]; assert re.fullmatch(r"f3-[0-9a-f]{32}",p); print(p)' "$SEDA_REPORT")"
docker container ls --all --filter "label=com.docker.compose.project=$SEDA_PROJECT" --format '{{.ID}}'
docker network ls --filter "label=com.docker.compose.project=$SEDA_PROJECT" --format '{{.ID}}'
docker container ls --all --filter label=com.docker.compose.project=ci-local-1791429045-34071 --format '{{.ID}}'
docker network ls --filter label=com.docker.compose.project=ci-local-1791429045-34071 --format '{{.ID}}'
```

Expected: all four outputs empty, all exit0, plus completed report `collection_absent:true`, `ownership_consistent:true`, `stack_absent:true`. The literal CI project is today's actual gate; another gate gets another project printed by the original script. An empty listing with a nonzero command status is **unverified**, not success.

If residue exists, stop the preview and inspect **that exact project** first. The runbook’s manual `docker container rm --force EXACT_OWNED_RUNNER_ID EXACT_OWNED_QDRANT_ID` and `docker network rm EXACT_OWNED_NETWORK_ID` are conditional recovery templates, **not executable filled-in commands or recovery actions exercised today**. Verify names/labels/ownership and use only exact owned IDs; preserve source/model snapshots and history. No prune, broad deletion or shared-volume removal. Record recovery and repeat independent absence. Uncertain cleanup means failure.

## Today's results

Original CI:PASS, exit0, 23.65s;397 tests and one existing deprecation warning. Combined rehearsal:PASS, 98.63s; supported32.46s, unsupported12.02s; corpus readiness49.55s; cleanup0.652s. Runner2.88GiB and Qdrant0.38GiB separate peaks. Independent absence checks for the exact CI and rehearsal containers and networks:PASS. No downloads observed; cached build layers used.

See [new receipt](evidence/operator-preview-20261008-01/receipt.md). Historical readiness and failed acceptance artifacts are preserved. Presentation-machine designation remains unconfirmed. **PARTIAL** remains the workshop status; a successful original CI gate or exposed-question rehearsal cannot establish fresh F3 acceptance.
