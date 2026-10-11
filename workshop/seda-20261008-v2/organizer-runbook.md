# SEDA organizer rehearsal — 8 October 2026

Repository: `/Users/edmcbee/Projects/api-speckit-sp-agentic-rag`.
Organizer presentation: 8 October 15:00 Asia/Manila; candidate/recovery rehearsal target noon. This runbook is a local candidate overlay; historical specs/reports retain their original dates/status. Slides have not been revised.

**Current decision: PARTIAL demo candidate. Fresh F2 retrieval passed 5/5; fresh F3 passed 5/6. `fresh2-return-2` retrieved no evidence for a supported question. Full F3 acceptance failed. F4 is omitted; F5/F6 remain roadmap items. Rehearsal is a regression demonstration, never acceptance.**

## Launch and readiness

```bash
cd /Users/edmcbee/Projects/api-speckit-sp-agentic-rag
.venv/bin/python -B -m workshop.preflight
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest -q
```

Expected preflight: `local_assets_ready: true`, exact approved model IDs/revisions/files verified. That check does not claim service readiness. Read the candidate receipt before using a recording or running a model.

The versioned wrapper starts a new internal Docker network, temporary Qdrant tmpfs and a read-only offline runner, verifies configured caps/mounts, ingests approved source texts and emits `SEDA_READY` only after corpus readiness. Initial preparation took about 50 seconds in the first fresh rehearsal candidate; allow 60–90 seconds before questions. Measured rehearsal: factory18.66s, ready49.88s; supported30.60s, unsupported11.28s. Retained in `evidence/rehearsal.json`; allow90s startup because fresh-v2 readiness took80.04s.

```bash
.venv/bin/python -B -m workshop.launch --output workshop/seda-20261008-v2/evidence/organizer-live-1.json
```

This runs the already-exposed supported and unsupported regression examples as a live rehearsal, not fresh acceptance. Each output filename is exclusive: existing evidence is never overwritten. For another rehearsal use the versioned wrapper with a new output file and the candidate image digest from the receipt:

```bash
.venv/bin/python -B -m workshop.launch --output workshop/seda-20261008-v2/evidence/rehearsal-repeat-1.json
.venv/bin/python -B -m workshop.present workshop/seda-20261008-v2/evidence/rehearsal.json
```

`workshop.present` explicitly says RECORDED LOCAL EVIDENCE. It presents retained results from a completed run; it never queries or invokes a model. Use that label even for a recording created moments earlier. During live waiting, narrate how actual returned chunks constrain IDs, reviewed rules constrain wording, and the unchanged validator checks claim support. Do not call this unrestricted answer generation. The original isolated query took 46s; allow up to 60s per answer and use measured rehearsal timing rather than promising instant responses.

## Ten-minute organizer demonstration

1. **0:00–1:30 — governance:** Stage1 remains the reusable API; Stage2 appends F0–F7. Show AGENTS.md, the sole constitution and actual owner/source/model approval records. Roles and roadmap entries do not grant consent. All CI is local. F5 memory and F6 tools remain outside the demonstration if absent.
2. **1:30–2:30 — identity/readiness:** Show `candidate-freeze.json`, the original freeze, versioned threshold review, new frozen acceptance cases and image digest. Distinguish calibration, exposed regressions and fresh results. Show approved local snapshots and source hashes; no credentials or environment files.
3. **2:30–4:30 — supported query:** `What is the return policy?` Expected reviewed rendering: unused items may be returned within 7 days with a receipt. Show the actual generated chunk ID, original returned passage, use case/source/revision/hash/offsets. Both answered and abstention paths were available; genuine model selection and unchanged grounding validation are required.
4. **4:30–5:30 — unsupported query:** `What is the shipping policy?` Expected `insufficient_evidence/no_evidence`, zero claims/citations and zero generation. This is evidence insufficiency, not a claim that no real-world policy exists.
5. **5:30–7:00 — acceptance boundary:** Show the failed supported question and frozen expected answer. Explain why safe abstention is still an acceptance failure here. Show the F4 plan as an unimplemented next step; no live F4 claim or budget trace.
6. **7:00–8:30 — tests/build/release:** Show local tests, offline fresh application rebuild, exact API smoke and image ID. Dependency layers were reused by retained digest; no clean dependency reinstall or published image is claimed. No GitHub Actions or Docker Hub automated build.
7. **8:30–10:00 — recovery/cleanup:** Show collection absence and independently checked container/network absence. Stop on any unverified cleanup state. Use the named fallback below if runtime or acceptance is unavailable.

## Two-hour workshop allocation

- 15 min repository/governance walkthrough.
- 85 min guided practical: 10 min preflight/API; 20 min approved ingestion/provenance/replacement; 20 min retrieval/threshold separation; 20 min constrained F3 evidence/claim validation; 15 min frozen evaluation/debugging exercise. Explain the unbuilt F4 gate; no F4 behavior is implemented or demonstrated.
- Remaining 20 min: setup buffer, evaluation/release recap, Q&A and owned cleanup. F5/F6 remain roadmap items; do not build them under the deadline.

## Named fallback and recovery

**SEDA-F0-F3-constrained-v1-fallback** retains the originally successful reviewed helper/model/prompt/threshold/corpus identities in `../seda-20261008/candidate-freeze.json` and the original regression report `specs/003-f3-grounded-rag/constraint-v1-live-report.json`. Show its verified API, ingestion/retrieval contracts and recorded constrained-selection success; disclose original F2 receipt and later acceptance gates. It is not full F3 acceptance.

```bash
.venv/bin/python -B -m workshop.present specs/003-f3-grounded-rag/constraint-v1-live-report.json
```

All wrappers remove only their owned IDs/network. To independently check a recorded project, use its exact `project` value:

```bash
docker container ls --all --filter label=com.docker.compose.project=EXACT_PROJECT --format '{{.ID}}'
docker network ls --filter label=com.docker.compose.project=EXACT_PROJECT --format '{{.ID}}'
```

Expected: both empty, command exit0. If residue exists, inspect exact names/labels and remove only those recorded owned IDs:

```bash
docker container rm --force EXACT_OWNED_RUNNER_ID EXACT_OWNED_QDRANT_ID
docker network rm EXACT_OWNED_NETWORK_ID
```

Do not use prune, shared-volume deletion or broad name patterns. Record the removal and repeat both absence checks. Model snapshots, source approvals, code and historical evidence are preserved; the temporary index/run stack is deleted.

## Guarded launch

Use `workshop.launch`, not the historical measured wrappers directly. `launch-guard-v1.json` pins the exact rebuilt image and host-code hashes. The guard does not change retrieval, generation, validator, source, or model behavior. `workshop.preflight` checks this guard too. Original v1/v2 wrappers and failed artifacts remain unchanged for audit.

Final guarded rehearsal:factory23.39s, ready73.75s, supported38.55s, unsupported13.74s, cleanup0.760s. See readiness-receipt.md for current failed fresh gate and exact candidate identities. The rehearsed partial checkpoint is SEDA-20261008-rehearsed-partial-rc2.
