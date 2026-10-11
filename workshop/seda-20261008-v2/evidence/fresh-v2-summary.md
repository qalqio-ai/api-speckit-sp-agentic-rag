# Fresh v2 acceptance — FAILED

Frozen before running; cases now exposed and must be treated as regressions. No threshold or expected-result changes after this run.

F2:5/5. F3:5/6. Lifecycle/isolation/replacement/current evidence/catalog mismatch/clear:PASS. Original failed evaluation and freeze remain unchanged.

| F3 case | Expected / actual | Retrieval s | Generation s | Total s | Outcome |
|---|---|---:|---:|---:|---|
| fresh2-return-1 | answered/— | 10.420 | 27.904 | 38.329 | PASS |
| fresh2-return-2 | insufficient_evidence/no_evidence | 13.644 | 0.000 | 13.646 | FAIL: expected answered |
| fresh2-return-3 | answered/— | 12.804 | 22.558 | 35.364 | PASS |
| fresh2-shipping | insufficient_evidence/no_evidence | 9.844 | 0.000 | 9.845 | PASS |
| fresh2-used | insufficient_evidence/unsupported_question | 9.512 | 0.000 | 9.514 | PASS |
| fresh2-neighbor | insufficient_evidence/unsupported_question | 10.401 | 0.000 | 10.403 | PASS |

| Fresh F2 case | Actual | Total retrieval s | Outcome |
|---|---|---:|---|
| held2-deadline | matched | 8.061 | PASS |
| held2-receipt | matched | 8.140 | PASS |
| held2-hours | matched | 8.187 | PASS |
| held2-hotel | no_match | 8.866 | PASS |
| held2-overseas | no_match | 10.972 | PASS |

Two actual generation calls: both80newtokens includingEOS, schema/claim support/citation membership passed. Four abstentions made zero generation calls. Both answer and abstention choices were present for generation. Exact raw outputs, rendered-input/constraint hashes, nonces and worker diagnostics are retained in fresh-v2-live.json.

Failure boundary: `fresh2-return-2` (“Under the return policy, what do customers need to bring?”) returned no_evidence before generation. Zero claims/citations/generation. Expected answered was not weakened. The approved returns chunk existed (other fresh queries retrieved it); this run does not record rejected raw candidate scores, so it does not prove whether its individual rejection was ranking versus score threshold. No raw score is invented.

Proposed next correction: independently freeze new development paraphrases for document/receipt requirements, measure complete ranked candidate scores and filters, then apply the F2 measured-threshold review procedure or evaluate an embedding-design change. Exclude this exposed question and every fresh-v2 case from threshold selection. A revised candidate requires new untouched acceptance. Do not change the threshold to fit this failed case.

Cold factory:38.296s; corpus readiness:80.042s; runner peak:3158437888bytes; Qdrant peak:389472256bytes; cleanup:0.805s. Per-container peaks are not a simultaneously measured total.

Receipt regression: rank1 score0.4537802 passes independently calibrated threshold0.42808731, EDM-f2-20261007-v2. Original threshold0.45614706000000005 remains in original frozen evidence. Separate development calibration—not acceptance scores—selected the new value.

Workshop selection: verified F0–F2 plus explicitly limited constrained-F3 regression demonstration; full F3 acceptance failed. F4 implementation omitted. F5/F6 remain roadmap items.
