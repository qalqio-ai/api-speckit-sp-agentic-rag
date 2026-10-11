# F2 prerequisite validation — authorized native implementation

User authorization: “Proceed with your recommendations” following F3's concrete
approval-request.md, authorizes F2 implementation and internal F3 receipt bridge,
local capacity/build/run within proposed limits, and safe repository metadata.
Source owner/reviewer and model directory/acquisition values remain pending. No
corpus processing, invented consent, package installation or legal grant.

## Implemented

app/retrieval/validation.py supplies independent strict F2/F1 closed shape resolution,
question byte/limit/type checks, error/result semantics and frozen case binding,
split minima, contradictory expectation and held-out leakage checks. index.py
verifies complete F1 readiness/current payloads/configuration/expected IDs and finite
vectors under bounded exhaustive paging, then makes one exact full-scope query,
validates every returned payload, ranks ties globally and filters inclusively.
service.py composes actual F1 classes, shares busy ownership, preserves delegated
version1 envelopes, returns version2 evidence and a separate internal receipt with
complete represented sources/registry fingerprint, original deadline and actual
query-dispatch count. F3 class-composition probe uses this implemented receipt.
embedding.py is an injected deterministic no-truncation/token/vector query seam;
evaluation.py only computes full-candidate score summaries and a reviewable separator,
never observed calibration. __main__/demo entry points fail closed, no READY.

## Actual checks

| Command / check | Result | Limit |
| --- | --- | --- |
| .venv/bin/python -B -m pytest tests/test_sources.py tests/test_ingestion.py tests/test_ingestion_cli.py -q -p no:cacheprovider |exit0;113 passed/1 existing warning |Fresh unchanged baseline |
| .venv/bin/python -B -m pytest tests/test_retrieval.py tests/test_retrieval_cli.py -q -p no:cacheprovider --tb=short |Intermediate exit0:48 then52 then64 |Final additions exercised by full suite below |
| .venv/bin/python -B -m pytest -q -p no:cacheprovider --tb=short |exit0;324 passed,1 warning |67 F2,144 F3,113 Stage1/F1; native/injected only |
| .venv/bin/python -m ruff check app/retrieval app/answer tests/test_retrieval.py tests/test_retrieval_cli.py tests/test_answer.py tests/test_answer_cli.py |exit0 |Scoped lint |
| Protected SHA256 comparison against /tmp/f2-approved-start.json |all unchanged |Stage1/F1/constitution/lock files below |
| sysctl -n hw.memsize |exit0;68719476736 |64GiB host; initial sandbox denial then escalated read-only rerun |
| docker info --format '{{.MemTotal}} {{.NCPU}}' |exit0;4101435392/16 |About3.8GiB Docker; initial sandbox socket denial then approved read-only rerun |

Warning is the existing Starlette HTTPX TestClient integration deprecation. It was
not silenced by changing dependencies. Full RED/GREEN/fixture distinctions are in
tasks.md. Independent review reproduced malformed search scalar acceptance, early
query counter and contradictory-case expectations; all fixed with failing regressions.
No claim of remote CI, real semantic quality or local image release.

## Pending

F2 live model/query worker, owned factory/session/group/cgroup registry, wrapper,
packaging, live evaluator consumer and exact model/Qdrant integration are not built
or verified. F2 remains incomplete; native receipt tests are not T041 F3 predecessor
acceptance. No F2/F3 source-use/retention approval receipt, live corpus/case set,
calibrated reviewed threshold/held-out acceptance or actual owned-resource cleanup.
F3 requires8GiB runner plus1GiB Qdrant; Docker currently about3.8GiB. Keep budgets
unchanged; increase Docker allocation to at least10GiB before those runtime gates.
No Docker Desktop setting changed. A model asset path or explicit pinned acquisition
and source owner/reviewer are still needed; the question is pending, not inferred.

Not run: Docker build/run/ci-local, real embedding/model/query/semantic calibration,
held-out grounding, Qdrant/process/container/network/cgroup/tmpfs enforcement or
cleanup/residue. Source fixtures/models/approval files were not written. No secrets
read, dependencies installed, branch/commit/push/PR/publication or corpus upload.
Read-only model rights metadata review: publisher's pinned [model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct/blob/a10cc1512eabd3dde888204e902eca88bddb4951/README.md)
declares apache-2.0. Separate LICENSE-page retrieval failed; no acquisition or grant
is inferred from metadata. No model files downloaded or loaded.

## Current core file hashes

| Path | SHA256 |
| --- | --- |
| app/retrieval/__init__.py | `80659577f63521426df1a64c6f5a0f88b4c131877526ce580b11e972e1925b5b` |
| app/retrieval/__main__.py | `a480e38ea16fe160e1dad6216bc120848133d6e1d2c7ec2deb7c7e3121bb4d7c` |
| app/retrieval/demo.py | `a480e38ea16fe160e1dad6216bc120848133d6e1d2c7ec2deb7c7e3121bb4d7c` |
| app/retrieval/embedding.py | `6da741382a53478b0a4218c2fe1b2e7126fb7fc675b62f667cc1d4fc73b6feac` |
| app/retrieval/evaluation.py | `0560438feb72a4945357824f0507c3828319e727df9d7bb62e1546f1b220d206` |
| app/retrieval/index.py | `c93303917fbdd57e764148001490b0a19aecd9572dcc1dc97be33b9542232a4f` |
| app/retrieval/service.py | `fa46c134f917f7836bffd4ffad013fe1f85c3c4eca6800b91938394f6e782d57` |
| app/retrieval/validation.py | `c84aa372783a3d27a676dbe743539378739d18d9a14f26835cf542b40635a973` |
| tests/test_retrieval.py | `cedfe971e226a80db3fc23acf368f983cfd787cc1f0e6b92d1a70128479b0e18` |
| tests/test_retrieval_cli.py | `2a588967d821c1b2f0243af4367783cf5dac2a17173fa9ee69d0d98ded640a14` |

## Preserved file hashes

| Path | SHA256 |
| --- | --- |
| app/ingestion/__init__.py | `81f7e53987ce84ce20d093770bcc8670372e6847dc91ed7e72b2a3824811a832` |
| app/ingestion/__main__.py | `c8df838a59cf3a1c1cf12ecf0804a71490da29104af21cd45fe9d3d68fa9dfbc` |
| app/ingestion/chunking.py | `3a711262efd2b3fc5bbe73d0be26f686e810cb5e6a3e1bb2bfd17f04bf2d56cc` |
| app/ingestion/demo.py | `b6e8175c1c3a7be43d25c457207827f5f9c0c14fa919f1a9adc2e3fe6afbee32` |
| app/ingestion/embedding.py | `563bb49f63fd582b975b60dc8a1d51d6abfbbe127a6bbf06eba4144915b29eb5` |
| app/ingestion/index.py | `35900793ea5f3b2ec7a9a7d54dcb3dd83b85a6481d6d6343eab9fb2d0c67637e` |
| app/ingestion/lifecycle.py | `baaa063ec755896db8af74577a440661a83d19f32af04d20844d340b1bf5ec07` |
| app/ingestion/service.py | `96fad3ab5216ffad5a8d26ce9c950b3825b65ff110d09f87d4c65a29b71e4092` |
| app/ingestion/types.py | `82a5baca2541bdc7ae6e59070fdce41994bb4678c8a2e62cec39213f8d883149` |
| app/ingestion/validation.py | `a6e6e926e425cdcf29f2bab67f4d0eb8dee1b0708371a74ff37d11e76c9060e2` |
| app/main.py | `9e4d63962398db1e9b797426c57c83eef316a9d0cd68716a33394292366f72ef` |
| app/sample_data.py | `f9ea8b946b619d4b07a9af5bc7b00c06a51eac56a57da2cc766b483011acb317` |
| docs/constitution.md | `d029360ae8f3fe38b120ac395325c346902d985674a446f6b6236e99826728cc` |
| pyproject.toml | `edbd043b7f656d8097b53c24d52aae849c91fd6597b84518ce8095b42548e9fc` |
| tests/test_ingestion.py | `15f2a7d74e5990faa171bc42a458e39af0cb2dca1e94f3cc08800ef2643ee120` |
| tests/test_ingestion_cli.py | `387bf567a36a820424bb92ead54458022a77787c5ddf7e0bd76244dc12e63ad8` |
| tests/test_sources.py | `43eb5ba66dbedbc30683e2429d62d175c0772a278dd99e9232783b2eb697b4aa` |
| uv.lock | `8d5b3aa91d944febb4f97d3b3c2f24a14184551383ac1082b042ad2a75c78775` |
