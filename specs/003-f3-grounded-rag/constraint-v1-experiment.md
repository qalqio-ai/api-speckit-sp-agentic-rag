# Single constrained-selection regression experiment — 2026-10-07

**Result: regression-experiment pass only. Full F3 acceptance is not claimed.**

User approved one isolated bounded-token-trie experiment on known exposed case `edm-answer-1`. No other generation regression or fresh acceptance case was run. Prior failed prompt artifacts and frozen evaluations remain unchanged. The initial tag-based startup failure is retained in `constraint-v1-single-report.json`; it occurred before retrieval or generation. The actual run used the confirmed existing image digest and its independent result is `constraint-v1-live-report.json`.

## Implementation and selection boundary

The four new ignored helpers under `local-data/f3-run/` implement the reviewed isolated experiment: `constraint-v1-trie.py`, `constraint-v1-worker.py`, `constraint-v1-single.py`, and `test-constraint-v1.py`. A separate frozen run configuration records their hashes and the proposal hash. Production application files, validators, schema, catalog, dependencies, protected documents, retrieval threshold and all prior evaluation files were preserved.

The compiler receives runtime retrieved evidence, the reviewed catalog and the runtime scope snapshot, then reuses unchanged eligible/claim validation. It verifies exact rule wording and current complete support before compiling one answered path plus one abstention path. The compiler does not load the expected evaluation result; the evaluation helper uses expectations only to judge actual output. This is **constrained selection of reviewed claims**, not unrestricted answer generation. All structural tokens and claim wording are constrained. At the branch, the model chooses among the permitted alternatives using its genuine greedy logits.

One actual model.generate call occurred. At new-token position 3, both token IDs 927 and 37488 were allowed; the model selected 37488, yielding answered. Abstention was an available valid terminal response. No retry, post-generation repair, citation-ID attachment, fabricated IDs or validator relaxation occurred. Existing service resolution of a generated citation ID to its full returned passage remains unchanged.

## Raw generated output

```json
{"status":"answered","claims":[{"claim_id":"returns","text":"Unused items may be returned within 7 days with a receipt.","chunk_ids":["1565c342-63a0-5216-91fc-115058bfa678"]}],"reason":null}
```

The chunk ID was selected from actual runtime evidence, not copied from the expected test answer. Strict JSON, closed schema, exact reviewed rendering, returned-ID membership, claim support and citation correctness all passed. Raw completion was 190 UTF-8 bytes; serialized worker result was 229 bytes. Worker stdout count was zero; stderr diagnostics counted 1,340 bytes and did not enter the response.

## Measurements

| Measurement | Actual |
|---|---:|
| Retrieval searches / generation calls | 1 / 1 |
| Prompt tokens / bytes | 684 / 1,894 |
| New tokens, including EOS | 80 |
| Stopping reason | configured EOS, token ID 2 at position 79 |
| Constraint compilation | 3.63 ms |
| Retrieval | 12.207 s |
| Cold generation component load | 13.698 s |
| Actual model.generate | 19.664 s |
| Whole generation stage | 33.792 s |
| Whole request | 46.002 s |
| Runner cgroup peak | 3,087,802,368 bytes (2.88 GiB) |
| Qdrant cgroup peak | 408,350,720 bytes (0.38 GiB) |
| Trie edges / accounted storage | 100 / 29,450 bytes |
| Owned stack teardown | 0.780 s |

Existing token, byte, time, CPU, memory and swap limits were unchanged and this single request stayed within them. Collection absence and owned container/network absence were verified. Successful private worker response also required the existing supervisor's owned child-stop/reap checks; native lifecycle tests passed in the full suite. These observations do not establish resource behavior for other workloads.

## Retained input and constraint binding

The live report retains full bounded rendered synthetic input, input token IDs, both constraint paths and their token IDs, raw output, runtime evidence receipt, schema/grounding results and pre-generation diagnostics. Independent audit recomputed these hashes and checked pre/post-generation nonce agreement and all frozen helper hashes:

| Bound artifact | SHA-256 |
|---|---|
| Rendered input | `a04aa07f55f270f9ea0f9689c816b407e6552a4bb1c5f5aafc6bd5551e9d4107` |
| Input token-ID array | `ab629c34596ff250ed006a7ee7aff79646db503a4eef06c0930de1bca42e3de8` |
| Two constraint token paths | `caf41a006c507ac0ac35d17561ca531ea1ea94cc5ecec368189c91c2e6c16a21` |
| Raw completion | `7632418497c33d8764cc6b6a01e59892338c7e70ca843f7a94642d38f7e85bb6` |

User-context hash exactly matches the retained v3 experiment, confirming unchanged runtime evidence/rules/question. Model and base generation fingerprint match prior v3; retrieval fingerprint remains `e91a67aac7fe729f79512bc5ce2cdcc5aa8f38d172a042af9cfa2894448af04e`, with threshold `0.45614706000000005`, calibration `EDM-f2-20261004-v1`. New experiment fingerprint is `34bca4bf33f64c49864a33cfd9fd9e7545a8a601accbc4625faf11bc77061ca8`.

## Actual verification and limitations

- Native focused tests: exit 0, 16 tests, one Torch-dependent test skipped natively. Offline Linux image: exit 0, all 16 tests passed without skips, including real Transformers masks against invalid IDs and premature EOS.
- Negative tests cover fabricated IDs, unsupported claims, valid-but-unrelated evidence, stale revision, foreign scope, ambiguous support, unreviewed rules, binding mismatch, missing fields, trailing text, wrong rendering and overlong paths. The red phase is retained, showing behavioral failures before the constraint implementation; some dependent tests also errored on absent paths. The initial Linux test fixture-path error was corrected before any model run.
- `.venv/bin/python -m ruff check .`: exit 0. `.venv/bin/python -m pytest -q`: exit 0, 389 passed in 19.70 s, one existing Starlette TestClient/HTTPX deprecation warning.
- `docker compose config --quiet` and `git diff --check`: exit 0. Independent hash audit: all 149 prior app/tests/docs/spec paths unchanged.
- Full `scripts/ci-local.sh` rebuild/API smoke was not run: its build could download dependencies. No build or installation was necessary for this isolated experiment. No full local build-gate pass is claimed.

No production rollout, full F3 acceptance, general reasoning capability or general abstention capability is established. Other exposed regressions and independently prepared fresh acceptance remain unrun. This task leaves no new acquisition decision: existing assets were used without downloads. No commits, pushes, publication or external transfers occurred.
