# Current frozen evaluation result — 2026-10-05

EDM authorized the measured threshold/configuration/case freeze as a provisional
candidate and actual held-out/F3 evaluation; no numerical approval remains pending.
[Freeze](evaluation-freeze.json), [actual results and corrections](evaluation-results.md).
Retrieval4/5 (receipt-proof false negative); supported generation0/3
(output_too_large); both unsupported cases pass with zero generation.
Normal wrapper exit1; collection and owned stack absence verified. Candidate,
expected results and protected code preserved. Full live acceptance failed;
implementation completion is separate. Earlier pending-review statements below
are historical and superseded. No commits/publication/settings changes.

---

# Latest acquired-asset and live evidence — 2026-10-04

Implementation is complete for the remaining integration/factory/wrapper/cleanup/
evaluation wiring. Full live acceptance remains pending. EDM source/model approvals
are recorded in [session-approval.json](session-approval.json); current decisions
and precise remaining review are in [continuation-decisions.md](continuation-decisions.md).

Actual checks in this continuation:

- `.venv/bin/python -B -m pytest -q -p no:cacheprovider --tb=short`: exit0,
  389passed in17.31s, one existing Starlette/HTTPX warning.
- `.venv/bin/python -B -m ruff check .` and `git diff --check`: exit0.
- Six acquired generation files: exact allowlist/length/localSHA256 checks passed;
  upstream LFS SHA256/Git blob identities checked separately. Four source SHA256
  checks passed. Catalog/receipt/configuration/case bindings validated.
- Pinned image build: exit0, image
  `sha256:139a1f015734889f0bef40f66a4db65a1addc1a3dc5dc41f6bc82fe9d936757f`.
  Real offline CPU tokenizer/FP32 load: exit0; [safe runtime measurements](live-runtime-probes.json).
- Genuine unchanged F1/F2 full-candidate calibration: exit0, four fixed calibration
  queries; search1 each; [report](live-calibration-report.json). No held-out use/tuning.
- Genuine approved same-source-ID neighbor isolation, shorter replacement, obsolete
  IDs absent, selected scope clear and neighbor preserved: exit0;
  [report](live-isolation-report.json), elapsed50.33s, runner peak1,164,652,544bytes,
  Qdrant413,601,792bytes, search0/generation0. Collection and owned stack absence
  independently verified. This is state/cleanup evidence, not answer acceptance.
- Baseline SHA256 audit:100 protected existing paths unchanged, including Stage1/
  API/F1/F2, governance, locks and approved F3 inputs. F3 implementation/tests and
  its designated status/evidence documents are excluded from that protection set.

Measurement setup failures were not production behavioral REDs: an absent local
image tag required the authorized cached rebuild; temporary calibration script import
path and process-group setup were corrected; isolation script initially treated F2's
rows mapping as a list. Failed owned stacks were removed/absence checked before
reruns. Existing TLS verification remained enabled using the installed certifi CA;
initial DNS sandbox/native CA failures preceded successful approved acquisition.
No production source was changed in this continuation. Actual model generation,
held-out quality, supported answer/citation acceptance and full-stack generation
memory/latency/resource timeout acceptance have not run. The freshly measured
separator requires the specific numeric review already requested; earlier approvals
remain effective. No commits/publication/settings changes.

Historical implementation evidence follows; its earlier unacquired/pending statements
are superseded by the dated records above.

---

# Latest F3 runtime implementation evidence — 2026-10-04

Implementation status: remaining F3 integration/factory/wrapper/cleanup/evaluation
wiring is implemented. Live acceptance is pending and is not inferred from fixtures,
builds or dependency imports. Preserve the approved exact-alias/claim boundary.
Latest user authorizes local implementation and prior build/run, while requiring
specific source/model decisions. No renewed generic implementation permission.

## Changed paths and purpose

- app/answer/runtime.py: F3-owned fresh embedding/storage adapters bridge unchanged
  F1/F2; actual Linux/cgroup checks, owned identity/absence registry, source-purpose
  and frozen configuration/file binding preflight, genuine fresh factory.
- app/answer/generation.py, service.py: allowlisted fresh module workers, duplex
  pipe transport, actual search/generation controls and typed live adapters; fatal
  transport/ownership failures stop input before public output.
- app/answer/__main__.py, lifecycle.py: fresh exec, one acknowledged public record,
  hard delegated-operation ceilings, original teardown, independent recorded-worker
  checks, case-phase deadline transitions after ingest EOF without stdin replay.
- app/answer/demo.py, scripts/f3-demo.sh: executable unique owned stack with exact
  images/caps/mounts/actual tmpfs/DNS alias checks, remaining-time forwarding,
  scoped lost-create recovery and exact-ID cleanup/absence; optional evaluation
  mounts, safe peak/latency metrics. Script mode0755, no runtime build/pull.
- tests/test_answer_runtime.py, test_answer_stack.py, test_answer_lifecycle.py:
  deterministic kernel/approval/counter/registry/protocol/create-loss/stall/cleanup
  regressions and native private five-case same-session probe. These are not live
  generation, actual cgroup or Docker enforcement acceptance.
- tasks.md, quickstart.md, continuation-decisions.md, this record: reconcile
  implementation versus live gates and trace resource controls to FR/SC criteria.
- generation-download-proposal.json: exact six-file pin/URL/size/license/upstream
  checksums/destination for approval. Computed local SHA256 stays null; no model
  snapshot or source approval receipt has been fabricated.

## Actual checks

- .venv/bin/python -B -m pytest -q -p no:cacheprovider --tb=short:
  final exit0,389 passed,13.99s; one existing Starlette HTTPX deprecation warning.
  Before final recovery/EOF fixes:388 passed; those are historical checkpoints.
- .venv/bin/python -B -m ruff check .: exit0 after final changes.
- bash -n scripts/f3-demo.sh: exit0; shell warns unavailable C.UTF-8 locale.
- git diff --check: exit0. Explicit byte-hash preservation audit:118 baseline paths,
  108 protected paths unchanged, zero unauthorized differences. Protected README,
  governance, Stage1/API/F1/F2, specifications/plans/contracts/checklists, locks,
  existing packaging preserved. Four exact source proposal hashes recomputed and
  match. Extension hook absent; .env absent (existence only, contents never read).
- docker compose --env-file /dev/null config --quiet: exit0.
- docker compose --env-file /dev/null -f compose.f3.yaml config --no-interpolate
  --format json: exit0; rendering only, required live locations not populated.
- docker info --format {{json .MemTotal}}:4,101,431,296 bytes (~3.82GiB).
  Initial sandbox Docker access denied; approved outside-sandbox read-only retry
  succeeded; missing initial F3 image was an expected image-inspect exit1.
- docker build --platform linux/amd64 --progress=plain -f Dockerfile.f3
  -t f3-grounded-rag:local .: exit0. Official Torch/Transformers target metadata
  checked before locked hashed installation; subsequent cached rebuilds include
  final code. Final local image:
  sha256:139a1f015734889f0bef40f66a4db65a1addc1a3dc5dc41f6bc82fe9d936757f.
  Container pip root-user warnings; no native environment installation or lock edits.
- Source-free Docker runtime check: --rm, --pull=never, Linuxamd64, --network none,
  --read-only, two GiB/no extra swap, four CPUs,64MiB /tmp; no source/model mounts.
  Exit0: Python3.12.15/Linuxx86_64/glibc2.41/Torch2.14.1+cpu/Transformers5.18.0,
  threads4/interop1; AutoTokenizer/LlamaForCausalLM imports work, no weights loaded
  or sources processed. Tested image2bf0d663...; final image reuses its unchanged
  verified dependency layer. Probe container absence observed by exact name.
- ./scripts/ci-local.sh (reviewed unchanged script): exit0; Ruff,388 then-current
  tests, temporary Stage1 API image/build/run, health and exact knownHTTP200/unknown
  HTTP404 bodies passed. Temporary project ci-local-1791077862-53942 container/network
  removed; read-only label queries found no resources. Final F3-only cleanup/EOF
  changes then passed389 tests; protected API byte hashes remain identical.
- Final source-free container entry without session arguments emitted only
  session_unavailable/no READY. Combined run/absence/image-inspection command exit0;
  individual expected nonzero entry exit was not captured separately. Exact named
  probe container absent. This is fail-closed transport evidence, not live readiness.
- Independent read-only review reproduced five integration/cleanup defects, then
  confirmed fixes. Final focused runtime/stack/lifecycle check:exit0,41 passed.
  Delayed evaluation first-case fixture observed RED under an expired EOF input
  deadline, then GREEN with separate bounded case transition at both layers.
  Lost-create fixture RED missing recovery, then GREEN exact owned label/name IDs.
  Additional details/fixture environment failures are in tasks.md; no fixture
  collection error or historical test result is counted as live acceptance.

## Approval gates, unrun checks and risks

Await actual user confirmation of EDM owner/reviewer and the four exact synthetic
texts/hashes/purpose/access/local-only redistribution/deletion rules, MiniLM F2
purpose reuse, exact source/catalog aliases/full claims/spans and frozen calibration
and held-out cases. Generation acquisition awaits the six-file immutable manifest,
Apache upstream declaration/notice review and exact destination approval; verified
post-download SHA256/actual tokenizer/config/EOS fingerprints cannot exist before
acquisition. Review the measured F2 threshold after calibration. Specific host or
Docker setting changes need their own decision; current settings stay unchanged.

Ten GiB is eight GiB runner ceiling plus one GiB Qdrant ceiling and approximately
one GiB VM headroom, not observed minimum usage. Current3.82GiB Desktop is below
combined ceilings; actual selected workload fit is unknown. Sequential fresh
embedding/generation workers reduce overlap in code, not measured peak yet. After
approved acquisition and reviewed cases measure cgroup runner/Qdrant peak and
transport/model latency under selected caps; a smaller decoder or another host
must pass the same frozen acceptance criteria, no automatic fallback/cap change.

Not run: generation weight load/inference/template/EOS/strict JSON or semantic
quality; approved-source F2/F3 ingestion/query/live calibration, frozen held-out
answers/abstentions or replacement/clear/isolation; actual eight/one GiB stack,
OOM/cgroup/escaped-descendant/tmpfs/residue stress acceptance. Cold Qdrant startup
readiness timing remains a live concern; unavailable storage fails closed. Source-
free import probe deliberately uses smaller memory and cannot prove reviewed
stack enforcement or model memory/latency. T003/T004/T041–T045 remain pending.
Task checkboxes retaining exhaustive/live criteria are not unbuilt runtime code.

External actions: official public metadata checks; authorized local F3 image builds,
hashed container dependency downloads/installations; source-free Docker import/
entry probes and unchanged local Stage1 CI build/run/cleanup. Local built images
retained. No model acquisition, unapproved source processing/upload, native install,
Docker settings/limit changes, license grant, commit/push/PR/publication or remote CI.

---

# Historical continuation records (superseded where noted)

# Latest continuation after approval of recommendations

User authorized F2 implementation and proposed local capacity/build/run checks,
with safe repository metadata capture. Implemented native F2 inventory/search/
receipt composition now passes actual F1/F2/F3 class-composition probes.
**Final native pytest:324 passed/one existing Starlette warning; scoped F2/F3 Ruff
exit0.** F3 live acceptance is still incomplete: F2 owned worker/factory/wrapper
and live calibration/acceptance, F3 owned runtime, source owner/reviewer, model
location/acquisition and actual Docker capacity gates remain.

Host64GiB; Docker about3.8GiB/16CPUs. Preserve8GiB runner plus1GiB Qdrant caps;
Docker needs at least10GiB allocation. No Desktop settings changed or Docker
build/run performed. Additional exact F2 source/case proposal prepared and
presented; no corpus or approval fixture/receipt created. The outstanding values
and specific source decision are in [approval request](approval-request.md).

F3 demo module now exits1/session_unavailable rather than silently exiting0;
three native unready-entry regressions preceded the fix. No READY emitted or live
activation. See [current F2 evidence](../002-f2-retrieval/validation.md) and current
tasks.md for scope, command/results and unchanged18-file Stage1/F1/lock/governance
audit. Read-only official model-card metadata review declares apache-2.0; separate
LICENSE retrieval failed, so no acquisition or grant is inferred.

The following earlier257-test/67-file snapshot is retained as historical evidence.
Its file hashes are not current identities after the separately authorized F2
prerequisite and F3 demo correction. No whole-F3 completion or live result claimed.

---

# F3 observed validation — 2026-10-03 continuation

Status: **partial implementation; 23/50 tasks completed**. The explicit local
implementation request is authorization for code work. It is not source/model/run
approval. Requirements checklist is read-only:16 checked,0 unchecked. The sole
constitution remains docs/constitution.md. No extension hook file exists.

## Implemented and checked

- app/answer/validation.py: closed F3 shapes with local F1/F2 schema references,
  strict JSON, semantic catalog/receipt/result/case checks, bounded file reads and
  manifest/catalog/receipt/model/config/case fingerprint bindings. Snapshot files
  must exactly match the reviewed hash allowlist; no extra loader inputs, symlinks
  or FIFO JSON reads. Exhaustive nested schema mutation task remains incomplete.
- grounding.py/service.py: exact aliases/renderings, full Unicode OR-of-AND support,
  full-question coverage before relevant conflicts, current represented sources,
  strict citations, one injected retrieval/adapter call, actual receipt counts,
  original deadline propagation, outer serialization lock and invocation-owned busy
  guard through delivery. Native adapter is cooperative and deterministic-only;
  it cannot terminate arbitrary synchronous adapters. Live mode remains rejected.
- generation.py: framed JSON IPC, fresh fork for injected probes and fresh exec for
  proposed Linux model workers, owned PID/group handshake, bounded termination,
  fixed diagnostics and actual generation-attempt control. Proposed local worker
  verifies pinned assets/runtime, offline local-only standard safetensors loading,
  CPU FP32/greedy/thread/context/template/token/EOS/completion limits. No real model
  loaded or quality/capacity demonstrated. Fresh-exec invalid/platform probe exits
  model_unavailable with zero model attempts and verified owned group stop.
- __main__.py/evaluation.py: injected dispatch/delegation, bounded LF JSONL input and
  oversized-line drain, incomplete EOF discard, close/output-failure termination,
  nonblocking partial writes with original deadlines, frozen case checking and
  ingest-only EOF evaluation after at least one successful complete ingest. No
  retries, expected outcomes in model context, corpus creation or persistence.
- Dockerfile.f3/compose.f3.yaml: separate prepared runner using exact F1 base/Qdrant
  identities and existing locked dependencies; hard memory/no enlarged swap/four
  CPUs/read-only mounts/internal network/tmpfs in rendered config. .dockerignore
  changes narrowly permit schema files; model/corpus/receipts/secrets remain excluded.
  Read-only rendering is configuration evidence, not runtime enforcement/build.
- README.md navigation, quickstart.md actual native commands and intended live
  interfaces, tasks.md checked work/continuation evidence and approval-request.md
  concrete missing decisions. Original spec/plan/research/contracts/checklist intact.

## Actual commands and outcomes

| Check | Exit / result | Limits |
| --- | --- | --- |
| bash .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks |0; F3 docs resolved |C.UTF-8 locale warning |
| .venv/bin/python -B -m pytest tests/test_answer.py tests/test_answer_cli.py -q -p no:cacheprovider --tb=short |0;142 passed before last two evaluation regressions |Injected/native process checks; no model/corpus/index |
| .venv/bin/python -B -m pytest -q -p no:cacheprovider --tb=short |0;257 passed,1 warning at final snapshot |Includes144 F3 and113 Stage1/F1 tests |
| .venv/bin/python -m ruff check app/answer tests/test_answer.py tests/test_answer_cli.py |0;all checks passed |Scoped lint |
| docker compose --env-file /dev/null -f compose.f3.yaml config --no-interpolate --format json |0 |No env-file/secrets read; placeholders not approved mount paths; no daemon action |
| git diff --check plus direct untracked-file whitespace audit |0 |All current F3 source/config files checked directly |
| Protected-file SHA256 comparison |67 unchanged |Stage1/F1/F2/governance/lock files and F3 immutable design/checklist; approved changes excluded |
| Pre/post hooks |Absent |No hook executed |

Warning: existing Starlette TestClient HTTPX integration deprecation, not F3 failure.
No dependency installation was performed to silence it. Earlier full snapshots
passed204 then255 tests; those are historical checkpoints, not final evidence.

## Behavioral failures, fixes and independent review

Prior stub RED/GREEN and five receipt/guard/deadline/grounding review fixes remain
recorded in tasks.md. This continuation added genuine failures for bounded input
and session consumers (4), optional/unlisted model snapshot inputs (3), FIFO and
parent-symlink JSON inputs (2), successful F1 ingest status handling (1), and empty
or incomplete input improperly triggering evaluation (2). Each was corrected and
rerun. Fixture mistakes (`ok` status, undefined binding) and lint findings were
corrected separately and do not count as behavior evidence. Native worker group
signals initially failed with macOS zombie-only EPERM; an escalated rerun reproduced
it. Stop now requires verified absence after reap; leader exit alone is not success.
The timeout fixture allows actual KILL/reap scheduling; this does not prove Linux
cgroup or escaped-descendant cleanup.

Independent read-only review reproduced the unlisted tokenizer-file integrity gap
and empty-EOF evaluation gap. New failing regression tests preceded both fixes.
Review found no additional LF framing, oversized-line recovery or output-failure
regression. Native synthetic OS processes only; no external review publication.

## Unbuilt, unrun and pending decisions

- F2 predecessor code/tests/acceptance/receipt bridge absent (T041). F2 belongs to
  its own implementation workflow. Injected port compatibility is not acceptance.
- Actual approved corpus/catalog/cases/F3 purpose/owner/access/redistribution/
  retention receipt and real asset path/hashes/rights remain missing (T003/T004).
  See [reviewable decisions](approval-request.md); no approval inferred or forged.
- Live owned factory and wrapper are unbuilt; app.answer entry point exits
  unavailable and demo.py remains explicit stub. No F3_READY emitted, script/live
  activation, cgroup/descendant registry or independently verified Qdrant/container/
  network cleanup. Injected cleanup callbacks prove invocation only. Do not label
  cooperative consumers as hard request/session supervision or verified cleanup.
- Actual model/tokenizer/locked runtime, host capacity, Docker image/build/run,
  read-only mount/internal network/cgroup/tmpfs enforcement, held-out supported/
  unsupported cases, semantic claim review, same-session real replacement/clearing
  and owned descendant/resource residue have not run (T042–T045). No broad semantic
  QA inferred from exact-alias abstention. Unknown aliases, missing support and
  actual injected model insufficiency are distinct tested outcomes.
- scripts/ci-local.sh/Docker Stage1 gate not run in this continuation; build/run
  authorization is pending. Local pytest/lint are not remote CI or image release.

No new corpus/approval fixture or model manifest, download, model load, dependency
install, Docker daemon action, branch change, commit, push, PR, publication or other
external write. Preexisting working-tree work preserved; no retained raw model/source
traces. Full F3 completion remains pending; unchecked tasks remain the continuation
queue and require their recorded criteria, including complete live supervision.

## Final code/configuration identities

| Path | SHA256 |
| --- | --- |
| .dockerignore | `8d250888ef20c911724723f78b65bdcaf4dc534286503bd8fc85175b6736937a` |
| Dockerfile.f3 | `179dbeef9735010b30e4791a242e8adea44eb5ad8dd16f4e2f3ebd67bcb2cb16` |
| app/answer/__init__.py | `a6d606a6ed3c9b1585f973e9dcc5d9530719269f07c79559f88e0691257ae527` |
| app/answer/__main__.py | `579c2ad41c1a86e6bcf496caca384b0ed0fa2166154a2181a79de7e693951e21` |
| app/answer/demo.py | `9a6139ef53354647e2d60ea2a87d3fca9b7cea8b247b47894e9c9c657945cb39` |
| app/answer/evaluation.py | `af9809fd7fb36f901c9512afbfe055e0566f7bcab0a779e4e49ab3b36ed4c514` |
| app/answer/generation.py | `5c9aebe66d522d67911d321f52417df621966be7d1b239eac9661178e15eebd7` |
| app/answer/grounding.py | `2b8358a9f90d8ac2be155e2dbb0194df31f5f59b3ee87748a13c2ea04b4b901b` |
| app/answer/service.py | `785d1a3360273dd3af27f28119f9860eb24d3196e3de019393d02d127a709e27` |
| app/answer/validation.py | `0cbfec62f15a6f1ed97d47b0f1bba71926f19ad83132a5e2f18f666f5e652899` |
| compose.f3.yaml | `d33c77598482b5b5fd0409a45520170ea7a7520ed01263c5a20e8153c4e7cc58` |
| tests/test_answer.py | `8a1cf0930240c01894c478f11b1b760bf27257f14cffa311f8f6c10ab133e274` |
| tests/test_answer_cli.py | `5c41df3a49e2e3ed8877004eacc2a2ba03925e2a6eb319131a76d99b9d4da183` |

## Protected snapshot hashes

| Path | SHA256 |
| --- | --- |
| app/__init__.py | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
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
| docs/Foundational_Multiuse_API_SpecKit_Superpowers_Runbook.md | `447f979bcbf93ea713cc5361fdc013ea118937570340b6e9537dad2f51b786a5` |
| docs/constitution.md | `d029360ae8f3fe38b120ac395325c346902d985674a446f6b6236e99826728cc` |
| docs/evolution-path.md | `b977e61316c7882e3d5ac7f80fbf1b92dae8c67f41f7d8249eec61bfa6b5004b` |
| docs/governance-reconciliation.md | `7a32ce217ba7559b74e174cd5f8dd487ad87445c58408a8e20da045ff5948517` |
| docs/project-brief.md | `2e00e805fd33e5743667c449df7fc996ebe2f49b7f7fc88d6b47784e381d9cae` |
| docs/release.md | `394e79c60059b003fe613a080ef9c7393bf645dc5ed5d5b1273a371284dc1f41` |
| docs/superpowers/plans/2026-10-02-r1-use-case-sources.md | `b517b59259e7c97016202e35480a3941e3a9b2ad771450b3d118710007949061` |
| docs/superpowers/specs/2026-10-02-r1-use-case-sources-design.md | `97d63441bc6c78037f647cb009f32c52fc9cb02d8d154457ccef545219317782` |
| docs/templates/feature-spec.md | `da5c2bb2a25e22800e556bd4e8c644730ebc8aed4ac339af51be660c561d855d` |
| docs/templates/implementation-plan.md | `44a8e615b5adb27218e69c41db26bc8f59a9e256c825845cd1cc3078fd982a96` |
| docs/templates/prompt-requirements.md | `2f628c0778213d50f80cd2eba48bc7e32a86be51f6c237da603e69ef9ddf89fe` |
| docs/templates/tasks.md | `52fdebdb32d700b8e012f1dcceac161289bed2215a5e21de1ded313bdf6e766f` |
| pyproject.toml | `edbd043b7f656d8097b53c24d52aae849c91fd6597b84518ce8095b42548e9fc` |
| specs/001-initial-scope/spec.md | `97b20ad0cbdcca57bd9cd7fdd7b70560426868702ae4ab22dff23926d750efa6` |
| specs/001-list-use-case-sources/checklists/requirements.md | `3fc7104bd7f8a960b12b61edf18e72f9727185b47902f560b78199d755f9bb5f` |
| specs/001-list-use-case-sources/contracts/sources.md | `61a555afd448375394d3dd5fc88179b1e809af165231c60df4058ffda27a18de` |
| specs/001-list-use-case-sources/data-model.md | `c893d80fa76a200c0bf40ca9a711f25aeff286433ca4d055c2e034fe5a166f48` |
| specs/001-list-use-case-sources/plan.md | `bae42c6dafe11cc9efa443e822ef9b5acec51145020b6df63bde801fd75359dc` |
| specs/001-list-use-case-sources/quickstart.md | `24d05caa35bd42c41ff77c9728716f33c406c9ba667832a3e208f2622b712d9f` |
| specs/001-list-use-case-sources/research.md | `74a4c86d6972ad67ff862d2d0f9ad36666061ec7023be3d1b864b4a3eee760a0` |
| specs/001-list-use-case-sources/spec.md | `ef73f724a7e2f3ba98d419707978b11fb9a3bca8faed3733e934a8fde6369b74` |
| specs/001-list-use-case-sources/tasks.md | `51d514f97a9f46e3faf4f5228d4bc5a76956f3e62e4ea58ee1edd37ae591b2e3` |
| specs/002-f2-retrieval/checklists/requirements.md | `a5f8de7a5dfec99633e00844881d6353e4af0aebcdeebf5c3e3691cd84fd54f6` |
| specs/002-f2-retrieval/contracts/retrieval-cli.md | `651a31d9c37d82be4343e5b129690edcb9fbd7db0ab0caf86a59a0bd4035d019` |
| specs/002-f2-retrieval/contracts/serialization.schema.json | `d84c505d6a9312024441c9f3c8e7c7ae95abebdfe8680720e92016e043dab5c2` |
| specs/002-f2-retrieval/data-model.md | `fb3556df8a0acb0fe279655387545a65ead45abca7fa68845fd9bd3a06b7c66d` |
| specs/002-f2-retrieval/plan.md | `dfa45993efa072d8bdcb43acb92b63d7d5921f4293f61f1cbf510a28cfbdfcfb` |
| specs/002-f2-retrieval/quickstart.md | `22fa64a8e8132aaf1c14b72ddb8733769c5e75a0cdef52bb3942204245bec401` |
| specs/002-f2-retrieval/research.md | `90f1bf836ffd452521923024840f2260f66fe78166f58ea1408690dd7cfd8270` |
| specs/002-f2-retrieval/spec.md | `f9e71953fa04adbc7b68d46f07642b3046a2a7793a6df208f82b0dcc13c825f5` |
| specs/002-f2-retrieval/tasks.md | `b432ea5fcc07a871d79e32d937ad40ee1656cba4c3251e1393c7ec4e91fc10e6` |
| specs/003-f3-grounded-rag/checklists/requirements.md | `0eb5c732774f571349999612e4abf15f6b376505b88a15cea5281685fd7c941a` |
| specs/003-f3-grounded-rag/contracts/answer-cli.md | `8c8fd2944ba61e5f48951ac1daf538ee8ce9597097c31d48edb3f11d0f0d733f` |
| specs/003-f3-grounded-rag/contracts/serialization.schema.json | `09b60d0e2aea7ef88866ac72356d49b18b147fad7027e871c6e5abcff56f84b2` |
| specs/003-f3-grounded-rag/data-model.md | `8796f171df0d79493b14cf29b52d051cb47005f7d1b42c297adbe07d3f00dd8a` |
| specs/003-f3-grounded-rag/plan.md | `522a375cf5e0767619c1cc424a40ec0c9a2e15a82dfba4a95ab28be24347ef2a` |
| specs/003-f3-grounded-rag/research.md | `56f0641e82314c9eb5b961aa2d84d8cf80dc03a34bcb6b83f021111839f727f5` |
| specs/003-f3-grounded-rag/spec.md | `2b94367e938047f4a9d8bc7027def4d2777f26e1962ff0876259c86aca0fbfb5` |
| specs/agentic-rag/f1-ingestion/checklists/readiness.md | `a13728c07bca23aa2e215c01f8a0f616e03cd7a1c32ca93631dbd33b509dd581` |
| specs/agentic-rag/f1-ingestion/checklists/requirements.md | `e2af1c44e3583d02fab2310ef4fafea8a0d9b84a54f1dbbe708e6a3f0d57d31c` |
| specs/agentic-rag/f1-ingestion/contracts/ingestion-cli.md | `861de7a84b129f79fcabf43c6d6a71213f269a2b14c1f0cd0242bb2ae7fb1cbb` |
| specs/agentic-rag/f1-ingestion/contracts/serialization.schema.json | `427c2c72cec8e090ee159e775b5e1cf45dcdf7571101ca5b6541f2b5419e86b7` |
| specs/agentic-rag/f1-ingestion/data-model.md | `cd7c8a97650cee5673d6ed934a1c77ac61fae5006fe0eab9516584325b55da54` |
| specs/agentic-rag/f1-ingestion/plan.md | `79821b416d3fd5786b811716dc34585ce93f81510b4015dfb83c039f91f012fb` |
| specs/agentic-rag/f1-ingestion/quickstart.md | `445a9851bff16d1af748d8e8c1df092d46dcd0ac6ff72e6dc59c9689bf351628` |
| specs/agentic-rag/f1-ingestion/research.md | `fab4e53c0f882e016c2d1c2f4ec354e0a0c9936b4f30ee6a6e066414250369f2` |
| specs/agentic-rag/f1-ingestion/spec.md | `a94849416274d2e04d13b97ede62b1b6ad07da73f02df75beceb12b2bccd86dd` |
| specs/agentic-rag/f1-ingestion/tasks.md | `a6c19bd5b38ce9d7e7a178440f01058d7c1edd3c77e19219b04b598c719a4ccc` |
| specs/agentic-rag/f1-ingestion/validation.md | `285f5b22fee5fae797f611a8179da0a116351b7992e260028153d060f32338ae` |
| specs/agentic-rag/roadmap.md | `27425d2c46e6d3baca599971a52eeec0caefd90c4f1db6e66f00118fe526c3dc` |
| tests/test_ingestion.py | `15f2a7d74e5990faa171bc42a458e39af0cb2dca1e94f3cc08800ef2643ee120` |
| tests/test_ingestion_cli.py | `387bf567a36a820424bb92ead54458022a77787c5ddf7e0bd76244dc12e63ad8` |
| tests/test_sources.py | `43eb5ba66dbedbc30683e2429d62d175c0772a278dd99e9232783b2eb697b4aa` |
| uv.lock | `8d5b3aa91d944febb4f97d3b3c2f24a14184551383ac1082b042ad2a75c78775` |
# Latest continuation — 2026-10-04

This section supersedes earlier test totals for the current snapshot; historical
records below are not rerun evidence. Work is deterministic/native fixture-only.
See [decision report](continuation-decisions.md) for exact sources, model identities,
public metadata byte sizes, Docker allocation derivation and remaining approvals.

Changed paths and rationale:
- `app/answer/lifecycle.py`: new owned native fixture factory supervision; hard
  startup/request/delivery deadlines and independently verified group stop.
- `app/answer/__main__.py`: retain failure status, cleanup uncertainty, actual
  request start, fatal input stop and frozen evaluation mismatch exit semantics.
- `app/answer/generation.py`, `service.py`, `validation.py`: distinguish fatal
  adapter transport loss, stop the session and begin cleanup before public output.
- `app/answer/demo.py`: review-only explicit-path plans, captured Docker inspect
  field validation and exact-ID cleanup command plans; no Docker executor.
- `tests/test_answer_lifecycle.py`, `test_answer_wrapper.py`, `test_answer_cli.py`:
  behavioral RED/GREEN regressions and synthetic native-process/captured-state probes.
- F3 `tasks.md`, `approval-request.md`, `continuation-decisions.md`, this report:
  observed evidence, corrected memory claim and concrete remaining decisions.

Actual checks:
- `.venv/bin/python -B -m pytest -q -p no:cacheprovider --tb=short`: exit0,
  **367 passed**, one existing Starlette HTTPX integration deprecation warning.
- `.venv/bin/python -m ruff check app/retrieval app/answer tests/test_retrieval.py tests/test_retrieval_cli.py tests/test_answer.py tests/test_answer_cli.py tests/test_answer_lifecycle.py tests/test_answer_wrapper.py`:
  exit0, all checks passed.
- `.venv/bin/python -B -m pytest tests/test_answer_lifecycle.py tests/test_answer_wrapper.py -q -p no:cacheprovider --tb=short`:
  exit0,42 passed; independently confirmed by read-only reviewer.
- `git diff --check`: exit0. Direct untracked-file whitespace audit also required
  because these feature paths have not been committed.
- Protected hash comparison against `/tmp/f3-deterministic-continuation-before.json`:
  exit0,104 paths unchanged outside explicitly allowed F3 code/test/report edits;
  includes Stage1/F1/F2 files, authoritative governance, specs/plans/schemas and locks.
  `.specify/extensions.yml` absent; no hooks dispatched.
- `uname -m`: exit0,x86_64. Local approved MiniLM file-size inventory: exit0,
  91,578,415 bytes; no model loading.
- Public pinned model tree metadata: sandbox curl exit6 DNS restriction; approved
  metadata-only retry exit0. Small config metadata GET exit0 returned a redirect,
  not a inspected configuration; not counted as compatibility proof. Model card
  read via web tool; tree page/tool errors recovered using metadata-only HTTP.

Failures before fixes:15 supervisor/consumer behavioral failures,22 wrapper stub
failures, shortened-start/evaluation/fatal-generation/SIGTERM/network-detail
regressions recorded in tasks.md. Scoped lint initially reported import order,
unused import and intentionally safe exception boundaries; corrected. A combined
documentation patch was rejected on missing context before applying; reissued
with correct context. A full-suite run during the final fatal-output RED state
had1 failure/365 passes; after applying the fix, the final current run passed.
No fixture/environment error is presented as behavioral acceptance.

Not run: genuine generation load/template/EOS/semantic tests; F2 live query worker,
factory/wrapper/calibration/held-out acceptance; F3 live factory/wrapper and frozen
file integration; actual Docker builds/runs/cgroup/tmpfs/OOM/descendant/owned residue
checks; `scripts/ci-local.sh`. No remote CI or image release evidence.

Limitations: native fixture factory uses fork and cannot activate a live model path;
captured inspect checks do not prove kernel resource enforcement. Genuine factory,
query integration, executable stack/cleanup/evaluation wiring remain implementation
work, distinct from approval-gated live verification. No all-task completion claim.
The10GiB allocation is a ceiling/headroom recommendation, not measured minimum RSS.

External actions: public model-card/file metadata reads only, explicitly no weight
or tokenizer acquisition; no corpus ingestion/upload, dependency installation,
Docker setting/runtime modification, license grant, commit, push, PR or publication.
