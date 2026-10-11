# F3 systematic debugging — 2026-10-05

Scope: one supported synthetic query (`edm-answer-1`) and the exposed receipt-proof
retrieval regression; no new sources, prompt/model/threshold changes or acceptance
claims. Original frozen configuration, failed acceptance records and production
implementation preserved. Existing sources/model/build/run approvals apply.

## Generation hypothesis: token cap without EOS

Confirmed by [bounded diagnostics](generation-diagnostic-report.json).
Exact failing boundary: app/answer/generation.py:294–295 (new token count/EOS),
not the decoded-byte check at297–298, response framing, or stdout.

| Observation | Value |
| --- | --- |
| Context/prompt byte limits |65,536 each |
| Prompt-token limit / model context |2,048 /8,192 |
| Completion limits |384 new tokens /16,384 decoded UTF8 bytes |
| Actual prompt |541tokens /1,340bytes |
| Actual combined output / new tokens |925 /384 |
| Actual last token / EOS positions |1002 /none |
| Tokenizer EOS / configured EOS / pad |2 /[2] /2 |
| Actual stop reason |max_new_tokens; no configured or tokenizer EOS |
| Generated-text bytes |787 (diagnostic decode only; production rejects before decode) |
| Serialized worker error bytes |45 (JSON payload, excluding four-byte framing lengths) |
| Worker stdout / stderr bytes |0 /803; text discarded |
| Cold model load / actual generate |13.826s /54.015s |

Production slices `output[0][prompt_tokens:]`, so input prompt is excluded from
completion validation/decoding. Decode options skip special tokens. Greedy CPU FP32,
beams1, batch1, four threads, EOS2/pad2 and384token cap unchanged; no stop strings or
custom stop criteria. Worker communicates through a framed private socket;
production stdout/stderr are DEVNULL and cannot contaminate that response.
Diagnostics count/discard Python stdout/stderr without retaining raw output.
The terminal frame remains a fixed error, not a partial answer.

First diagnostic attempt lost its metadata after terminal-send/parent-stop race;
[setup failure](diagnostic-setup-failure.json) is preserved, owned stack absent.
Only temporary instrumentation moved metadata emission before terminal send.
Same question repeated; prompt/model/output limits and production unchanged.

The failure is model non-termination within the approved budget; evidence does
not establish a wrong EOS setting, byte-accounting bug or decoder slicing defect.
Existing missing-EOS safeguard behaves correctly. Rejecting the failure is required;
accepting token-capped output or increasing limits would weaken that boundary.
No production fix is justified by this evidence alone. Next single hypothesis:
a separately versioned schema-explicit prompt may induce one bounded JSON response
and EOS; specific user decision pending because the instruction says not to change
prompt/model yet. No prompt change, repair, retry or fallback was performed.

## Receipt hypothesis: filtering/ranking/threshold

[Initial diagnosis](receipt-diagnostic-initial-report.json) and
[startup timing repeat](receipt-diagnostic-report.json) agree exactly:
returns chunk1565c342-63a0-5216-91fc-115058bfa678 is present, current/approved, rank1,
score0.4537802. Hours is rank2/score-0.068036094. Exact scope, approved source IDs
and verified-current-ID filters pass for both. Expected receipt fact is present in
approved returns source. Threshold0.45614706000000005 rejects both; returns misses
by0.002366860000000026. Top-k3 does not remove the expected chunk.
Cause: the calibration-derived separator does not generalize to this proof wording;
coverage, ranking and filtering are not the cause of this observed miss. Frozen
F2 inclusion (`score >= threshold`) correctly rejects it, so do not alter that code
to manufacture a pass. A richer independently reviewed development/calibration set
and a separately versioned candidate are needed; exposed cases are regressions,
never fresh held-out acceptance. No revised threshold was computed or applied.

## Retrieval latency

Repeated total8.701s: inventory0.627s; query encoding7.425s; search0.649s.
Encoding worker: tokenizer/assets/import initialization6.346s, model load0.735s,
actual embedding0.028s. Worker start handshakes0.294s inventory/0.291s encoding/
0.301s search. Query HTTP operation0.340s includes fresh HTTP client/import/network/
response handling, not an isolated Qdrant server timing. Remaining stage time includes
IPC/validation/owned stop. Major cost is fresh dependency/tokenizer initialization
and cold model loading, not vector similarity computation. Keeping weights/workers
alive would revise the approved fresh-worker/resource lifecycle; no such change made.

## Regression status, verification and preservation

[Quality regression cases v1](quality-regression-cases-v1.json) records unchanged
expected results, original configuration/case SHA256 and known generation/receipt
failures. The real normal service was exercised, not a scripted model answer.
These live regression failures remain unresolved. Do not manufacture a native RED
that labels correct resource rejection or threshold filtering a code defect.
Existing deterministic safeguards: focused EOS tests2pass; focused F2tests53pass,
commands `.venv/bin/python -B -m pytest tests/test_answer_cli.py -q -p no:cacheprovider
-k 'local_decode or missing_legitimate_eos'` and
`.venv/bin/python -B -m pytest tests/test_retrieval.py -q -p no:cacheprovider`, exits0.
Full local gate `./scripts/ci-local.sh`: first run exit0,389tests/Ruff/API200/exact404/
health/temporary container+network cleanup pass. Warnings: existing Starlette/HTTPX,
C.UTF-8 locale, container pip-root/update notices. No native dependency install.
Ordered final gate after focused verification:exit0,389passed/one Starlette warning
in12.85s, Ruff/API200/exact404/health/build/owned cleanup pass. Observed Docker
warnings: missing docker-scan plugin executable, DOCKER_INSECURE_NO_IPTABLES_RAW
set, nondefault seccomp. Settings untouched. All100 protected paths and original
failed evaluation/configuration/case artifact hashes unchanged; diffcheck exit0.

Both diagnostic stacks verified collection/container/network absence. Retained
reports contain bounded safe metadata, no raw questions/passages/model text beyond
already approved regression-case inputs. No model acquisition, changed Docker
settings, commits/pushes/publication. No new acceptance cases executed; independently
prepared untouched cases must be frozen/reviewed after any justified revision.


The exact unused [schema-explicit prompt proposal](generation-prompt-v2-proposal.json)
is prepared for the pending specific decision. It is a single unverified hypothesis,
not an applied fix. No revised threshold/configuration or new acceptance claim exists.
The two known quality regression cases remain failing. No implementation bug has
been demonstrated that warrants changing EOS rejection or threshold inclusion.
