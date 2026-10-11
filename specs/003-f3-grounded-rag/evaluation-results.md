# Frozen provisional evaluation — 2026-10-05

EDM explicitly authorized candidate freeze and held-out/F3 runs in this session.
[Freeze](evaluation-freeze.json) records exact embedding revision, configuration,
metric/direction, inclusion/ties, top-k, scope/source/current-ID filters, source and
expected single-chunk hashes/IDs, calibration cases and threshold rationale.
Threshold0.45614706000000005/calibrationEDM-f2-20261004-v1 stays provisional.
No case expectations, threshold, source text, embedding/generation configuration,
protected code or governance were changed based on observed outcomes.

## Held-out retrieval

[Real report](heldout-retrieval-report.json):4/5pass, acceptance fails.
The receipt-proof case expected matched but returned no_match (false negative).
Return deadline and opening hours matched their expected source at rank1;
unsupported overnight delivery and battery repair correctly returned no_match.
All queries used exactly one actual search, zero generation, no foreign scope
or neighbor evidence. Actual current inventory matched all frozen chunk identities,
provenance/start/end/configuration and slice hashes before any held-out query.
Collection and unique owned stack absence independently verified. Script exit0
means measurement/cleanup succeeded; `all_cases_pass=false` means acceptance failed.
Historical calibration is selection evidence only, never acceptance.

Proposed retrieval correction: investigate embedding coverage of proof/receipt
questions and add independently reviewed calibration examples, then propose a new
candidate against that calibration only and evaluate on a fresh untouched held-out
set. Do not lower this frozen threshold against the failed held-out question or
change its expected match. No correction implemented in this evaluation.

## Generation and wrapper

[Instrumented genuine factory report](f3-generation-report.json) and
[normal wrapper report](f3-wrapper-report.json):supported0/3, negative2/2.
All supported cases actually searched once and generated once, then failed with
`output_too_large`; no partial claims or citations escaped. Grounding/citation
acceptance is unproven, not vacuously successful. Normal wrapper exit1 correctly
reflects failed expectations. Shipping abstained `no_evidence`; used-item query
abstained `unsupported_question`; both searched once, generated zero times and
exposed zero claims/citations. The latter demonstrates the reviewed catalog
boundary, not general semantic reasoning. All retrieved evidence stayed in scope.

The public error groups output-token termination and decoded-byte limit failures;
current safe telemetry does not distinguish the exact triggering condition.
Proposed correction: add safe token-count/EOS/byte-count diagnostics, then evaluate
a more explicit output-schema prompt on independent development cases under the
same model/384-token/single-attempt constraints. Re-freeze the prompt/configuration
and use a fresh untouched acceptance set for any subsequent quality claim.
Do not increase limits, repair/retry output, substitute catalog text, change expected
claims, or switch models as part of this run. No production correction implemented.

## Per-query timings

Retrieval/generation/total below are measured in one instrumented genuine-factory
run. Generation stage includes offline cold weight loading, tokenization, generation,
validation and fresh-worker shutdown. Normal wrapper is a separate unchanged run;
its total is listed separately and no stage times are inferred from that total.


| Case | Outcome | Retrieval s | Generation s | Total s | Normal wrapper total s |
| --- | --- | ---: | ---: | ---: | ---: |
| held-deadline | PASS: matched | 10.225 | 0.000 | 10.225 | — |
| held-proof | FAIL: no_match | 10.280 | 0.000 | 10.280 | — |
| held-hours | PASS: matched | 9.897 | 0.000 | 9.897 | — |
| held-delivery | PASS: no_match | 10.425 | 0.000 | 10.425 | — |
| held-repair | PASS: no_match | 10.022 | 0.000 | 10.022 | — |
| edm-answer-1 | FAIL: failed / output_too_large | 8.305 | 51.217 | 59.533 | 64.074 |
| edm-answer-2 | FAIL: failed / output_too_large | 10.921 | 50.749 | 61.672 | 62.006 |
| edm-answer-3 | FAIL: failed / output_too_large | 9.286 | 50.904 | 60.191 | 58.356 |
| edm-answer-4 | PASS: insufficient_evidence / no_evidence | 9.578 | 0.000 | 9.579 | 8.817 |
| edm-answer-5 | PASS: insufficient_evidence / unsupported_question | 8.426 | 0.000 | 8.427 | 7.920 |

## Memory, cleanup and checks

- Held-out runner peak1,164,079,104bytes (1.084GiB); Qdrant418,820,096bytes
  (0.390GiB). Instrumented generation runner3,250,728,960bytes (3.028GiB);
  Qdrant411,672,576bytes (0.383GiB). Normal wrapper runner3,230,089,216bytes
  (3.008GiB), Qdrant412,065,792bytes (0.384GiB). These are per-container peaks;
  summing them does not establish a simultaneous peak. Ten GiB remains a planning
  estimate, not a minimum. Existing8GiB/1GiB caps, zero swap/four runner CPUs and
 256MiB storage tmpfs verified; no Docker setting changes or OOM claim inferred.
- Genuine factory/held-out collection close verified absence and owned stack
  deletion. Normal wrapper reported collection_absenttrue; independent post-run
  `docker ps --all`/`docker network ls` label checks returned no remaining F3
  containers/networks, exit0. No prune/shared-volume deletion. No cleanup failure.
- All completed answer requests stayed below240s; normal wrapper maximum measured
  transport64.088s. Actual original bound/owned cleanup code ran, but this does not
  claim new live stall/OOM/interrupt fault-injection acceptance.
- Cached pinned F3 image build exit0; real held-out and instrumented model scripts
  exit0 mean measurement/cleanup completion, despite acceptance failures. Wrapper
  exit1 means failed expectations. No repeated tuning or in-request generation retry.
- `.venv/bin/python -B -m pytest -q -p no:cacheprovider --tb=short`:exit0,
 389passed/one existing Starlette warning/14.17s. Ruff and diff checks exit0.
-100 original protected paths retain baseline SHA256, including Stage1/API/F1/F2,
 governance, locks and approved F3 inputs. Existing production code unchanged.
 New/updated files are F3 candidate/case approval/evidence/status records only;
 temporary diagnostic helpers remain under ignored local-data or /tmp.
 No native installs, new downloads, model substitution, settings changes, commits,
 pushes or publication. Implementation completion remains separate from failed
 retrieval/supported-generation live acceptance.
