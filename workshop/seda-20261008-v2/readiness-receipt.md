# SEDA readiness receipt — PARTIAL

Checkpoint: **SEDA-20261008-rehearsed-partial-rc2**. Organizer:8October2026,15:00Asia/Manila; recovery/rehearsal target noon. EDM retains owner/reviewer identity; local implementation/calibration decisions were delegated. No further local approval decision is pending.

| Component | Status | Actual evidence |
|---|---|---|
| Stage1/API | PASS | Fresh offline application rebuild exit0; health/known/empty/exactunknown404 smoke4/4, readiness1.57s, container removed. |
| F1 ingestion | PASS for tested synthetic fixtures | Live approved ingestion, replacement, verified current inventory and clear; native contract tests passed. |
| F2 retrieval | PARTIAL overall | Fresh retrieval5/5; known receipt rank1 score0.4537802 now passes independently calibrated v2 threshold. One additional supported F3 phrasing missed retrieval. |
| F3 implementation/wrapper | PASS for constrained regression mode | Genuine answered/abstention alternatives; actual retrieved supporting IDs; unchanged schema/support/citation validation. Rehearsal2/2passed. This mode selects reviewed claims, not unrestricted generation. |
| F3 fresh acceptance | FAILED / PARTIAL |5/6. `fresh2-return-2` expected answered, returned no_evidence. No generation/claims/citations; expectation unchanged. Lifecycle/isolation/replacement/current-version/clear gates passed. |
| F4 | BLOCKED by precondition; omitted | Plan only. No new implementation or live decision/budget claim. |
| F5/F6 | OMITTED | Roadmap preserved; no deadline feature builds. |
| Local image/checks | PASS for executed gates |397repository tests;16Linuxnegative tests; Ruff/diff/Composeconfiguration pass; fresh application rebuild/API smoke pass. |
| Target release | PARTIAL | Local versioned image/handoff prepared. No publication, registry pull, archive transfer, target host test, clean dependency reinstall or scan executed. |

## Exact candidate identities

- Image tag:`seda-workshop:20261008-rc1`; ID:`sha256:f1dc063ca46a05ccce548121c1f530eb1d7ce2edc87dc27db1f32d3ba2cdf00a`.
- Bundle:`SEDA-constrained-selection-rc2`; frozen manifest SHA256:`664ef00e57d60043758ebadd56e5747f20a4269d73eda73d4eae1fe8049f88fc`.
- Launch guard SHA256:`c530f5eb97857dae4a906c0ad9f0f220571df38e301ddf009030a912986fa777`; enforces exact image and host-code hashes. All197protected historical files match baseline.
- Embedding:MiniLM-L6-v2 revision`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; generation:SmolLM2-360M-Instruct revision`a10cc1512eabd3dde888204e902eca88bddb4951`.
- Retrieval fingerprint:`73aa0d04f345d7c4609e6fa4329ff7a8bcd46f1495afd25a04f03819eaf75870`; generation fingerprint:`d2a0101d823ac6ad736a7a6c5d0ddeee4471e7145f2ba2bae5f1e04c3edffd1f`.
- Threshold:`0.42808731` / `EDM-f2-20261007-v2`, selected solely from separate development calibration. Original0.45614706000000005/EDM-f2-20261004-v1freeze immutable.
- Worker/trie/prompt/model hashes and exact corpus/catalog/source receipts are in frozen.json, launch-guard-v1.json and fresh-acceptance-freeze.json. Original constraint-v1 failures/success preserved.

## Executed commands and results

- `.venv/bin/python -m pytest -q`:397passed,1existingStarlette/HTTPXdeprecation,16.04s; evidence/full-local-tests.log.
- `.venv/bin/python -m ruff check .`, `git diff --check`, `docker compose config --quiet`:exit0.
- `.venv/bin/python -B -m workshop.build`:fresh application rebuild exit0; ../seda-20261008/evidence/build.json and build.log. Retained pinned dependency image reused, buildnetwork disabled; not a clean dependency reinstall.
- `.venv/bin/python -B -m workshop.api_smoke`:exit0; ../seda-20261008/evidence/api-smoke.json,4exactchecks.
- `.venv/bin/python -B local-data/f3-run/test-constraint-v1.py`:16tests,oneTorchtest skipped natively. Actual pinned-image run of `/input/test-constraint-v1.py`:16/16,none skipped,5.523s; evidence/linux-negative-tests.log.
- `.venv/bin/python -B -m workshop.finalize --step fresh-v2`:live runner exit0, wrapper exit1 for failed acceptance; evidence/fresh-v2-live.json + fresh-v2-summary.md. Earlier default-sandbox launch failure separately retained in fresh-v2.json; no model run there.
- `.venv/bin/python -B -m workshop.finalize --step rehearse-v2`:exit0; evidence/rehearsal.json.
- `.venv/bin/python -B -m workshop.launch --output workshop/seda-20261008-v2/evidence/guarded-rehearsal.json`:exit0; evidence/guarded-rehearsal.json. Launch guard fixes verified RED→GREEN; evidence/launch-guard-regression.md.
- `.venv/bin/python -B -m workshop.preflight`:exact17model files and bundle/hostcode ready; does not claim service readiness.
- `.venv/bin/python -B -m workshop.inspect_local`:exit0, independent absence for6recorded projects and API smoke; evidence/independent-inspection.json. Collection absence verified by each completed live run; hostcontainer/networkabsence checked independently.
- `.venv/bin/python -m workshop.present …/evidence/rehearsal.json`:recorded playback exercised, visible approved claim/actualpassage/chunkID and unsupported abstention. Always labelled **RECORDED LOCAL EVIDENCE**.

Original `scripts/ci-local.sh` was read but not executed: it uses a floating base/package installation, unlike this pinned offline candidate. Required test/build/smoke functions ran individually. No original-script, clean-install, registry, target-platform or published-image claim.

## Rehearsal timings and resources

Guarded rehearsal factory:23.39s; corpus ready:73.75s. Supported retrieval13.40s +generation25.14s =total38.55s; unsupported retrieval/total13.74s, no generation. Supported80newtokens includingEOS; schema/claimsupport/citation correctness passed. Unguarded earlier rehearsal30.60s/11.28s; fresh-v2 readiness80.04s. Allow90sstartup and60sanswer narration; do not promise instant answers.

Guarded runner peak:3024035840bytes (~2.82GiB); Qdrant:385564672bytes (~0.36GiB), cleanup:0.760s. Per-container maxima are not simultaneous total peak. VM allocation~3.82GiB; serialized tiny runs worked, little headroom.10GiB remains planning headroom, not measuredminimum.8+1GiBcaps/token/time limits unchanged; noDocker settings changed. IntelMac/Linuxamd64 only; AppleSilicon untested.

## Recommended organizer scope and remaining gates

Use the runbook: governance/API, approved F1/F2, supported constrained F3 query with visible evidence/citations, unsupported abstention, frozen failure explanation, local release/cleanup walkthrough. Omit F4/F5/F6 demonstrations. Keep the original **SEDA-F0-F3-constrained-v1-fallback** and the newer rehearsed partial checkpoint. Playback is clearly recorded.

Remaining gate is technical, not an approval request: diagnose the fresh supported retrieval miss using separately frozen development cases and complete raw score/filter diagnostics; review any correction against F2 requirements; freeze a revised candidate and entirely new acceptance cases. Do not tune on these now-exposed cases. Source/model acquisition changes are unnecessary for this rehearsal. Publication destination/legalrelease review and target verification remain outside executed work; nothing is published.

Changes are confined to new workshop overlay files, two workshop test files and the new implementation plan. Protected implementation/governance/history preserved. No downloads, commits, publication or slides changes. Prepared prerequisites:slide-7-prerequisites.md. Organizer/recovery:organizer-runbook.md. Handoff:release-handoff.md.

Measured allocated local disk at final documentation:workshop v1 package396KiB; v2 package528KiB; embedding89,468KiB; generation708,788KiB. Evidence grows slightly when checks are added. These are allocated `du -sk` values, not archive-transfer sizes.
