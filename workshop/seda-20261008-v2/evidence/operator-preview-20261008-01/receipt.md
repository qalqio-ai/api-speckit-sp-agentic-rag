# Organizer operator preview — 8 October 2026

**Status: PARTIAL.** Existing frozen rehearsed candidate unchanged. Original fresh F3 acceptance remains 5/6 with `fresh2-return-2` no_evidence; no fresh acceptance was run here. This is an exposed supported/unsupported regression rehearsal.

Machine: current repository Intel Mac, macOS13.2.1 (22D68), x86_64, Intel Core i9-9980HK. **Actual presentation-machine designation: UNCONFIRMED.** The user has not identified this host as the presentation machine. `machine.json` retains the original sandbox-denied CPU probe; `cpu-check.json` records the successful authorized CPU check.

| Operation | Command | Result | Wall time |
|---|---|---|---:|
| Preflight | `.venv/bin/python -B -m workshop.preflight` | PASS;17 model files +frozen inputs/host hashes; not service readiness | 2.14s |
| Original CI | `./scripts/ci-local.sh` | PASS, exit0;397 tests / 1 warning, tests12.80s; cached build, exactAPI200/404; scopedcleanup | 23.65s |
| Combined rehearsal | `.venv/bin/python -B -m workshop.launch --output workshop/seda-20261008-v2/evidence/operator-preview-20261008-01/rehearsal.json` | PASS, exit0;2/2cases; approved corpus provision +queries +ownedcleanup | 98.63s |
| Independent absence | Four exact Docker container/network listings in independent-absence.json | PASS;all empty, each exit0 | recorded separately |

Working directory for all commands:`/Users/edmcbee/Projects/api-speckit-sp-agentic-rag`. No CLI environment overrides. CI_LOCAL_PYTHON used its existing default `.venv/bin/python`; CI_LOCAL_CONTEXT was set internally by the original script. The script was executed unchanged, unlike yesterday's individual equivalent gates.

CI:2026-10-08T11:10:31.121707+08:00 →2026-10-08T11:10:54.771680+08:00. Rehearsal:2026-10-08T11:14:16.169750+08:00 →2026-10-08T11:15:54.799256+08:00 (Asia/Manila).

| Rehearsed query | Outcome | Retrieval | Generation | Total |
|---|---|---:|---:|---:|
| What is the return policy? | answered;PASS | 8.59s | 23.87s | 32.46s |
| What is the shipping policy? | insufficient_evidence/no_evidence;PASS | 12.02s | 0.00s | 12.02s |

Factory startup:21.07s; approved corpus ready:49.55s. Supported output:80 new tokens including EOS, `configured_eos`. Genuine model choice among answered/abstention paths; schema/support, citation and isolation checks true. Exact approved rendering:Unused items may be returned within 7 days with a receipt. Citation:returns/v1, `1565c342-63a0-5216-91fc-115058bfa678`, hash`50e85780308baf9945671e2c05be5ef4fa3e02ccd805babd2b6809ee52eb841d`, original span0–77. Unsupported query:zero generation, claims and citations.

Runner peak:3090317312bytes (2.88GiB); Qdrant peak:410132480bytes (0.38GiB). These are separate cgroup peaks, not a simultaneous aggregate. Hard caps unchanged at8GiB/1GiB;10GiB remains planning headroom, not a measured minimum. Cleanup:0.652s. Collection absent/ownership consistent/stack absent:true. Independently checked exact projects:`f3-f46b2576ec8d4eb7a523047ea8eefa05` and `ci-local-1791429045-34071`; no containers or networks remain for either.

Image:`sha256:f1dc063ca46a05ccce548121c1f530eb1d7ce2edc87dc27db1f32d3ba2cdf00a`; bundle SHA256:`664ef00e57d60043758ebadd56e5747f20a4269d73eda73d4eae1fe8049f88fc`. Threshold0.42808731/EDM-f2-20261007-v2; model/code/prompt/evidence/constraint/validator unchanged. Candidate image and both manifest hashes matched the historical receipt. All232pre-existing inspected workshop/app/spec/doc/script files preserved; audit:preservation-after.json.

Warnings:one existing Starlette/HTTPX TestClient deprecation in the397 tests; shell/shasum locale warnings on this host. They did not fail the commands. Docker build reported cached app/dependency-install layers; no image/package/model downloads observed. CI retained its separate built API image; it did not rebuild or replace the frozen F3 image.

Card validation:eight Bash blocks syntax-checked; supported/unsupported read-only inspection snippets executed exit0; workshop.present exercised with explicit RECORDED LOCAL EVIDENCE label. Timestamp-named repeat command is prepared instruction, not a second live run. Manual recovery removals were not needed or executed; only scoped automatic cleanup and independent absence checks ran.

Created operator-command-card.md and new evidence under operator-preview-20261008-01. Existing runbook, readiness/prerequisite docs, historical reports and frozen candidate preserved. No F4 work or new API endpoints, source changes, downloads, commits, publication or slide edits. No local approval decision pending. Actual presentation-machine identity remains unconfirmed; no claim for another host.

Evidence:original-ci.log/command.json, preflight.log/command.json, rehearsal.json/command.json, independent-absence.json, machine.json/cpu-check.json, card-verification.json, preservation-after.json. Unrestricted generation and full fresh F3 acceptance remain unproven.
