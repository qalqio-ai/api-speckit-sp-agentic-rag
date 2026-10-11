# SEDA workshop finalization implementation plan

> **For agentic workers:** Execute inline with superpowers:executing-plans. User explicitly requests autonomous execution; no commits or publication.

**Goal:** Rehearse a truthful, recoverable organizer candidate before 8 October noon Asia/Manila, for the 15:00 presentation.

**Architecture:** Preserve the production API/F1/F2/F3 and historical evidence. Package the reviewed bounded-trie helper without changing its model/prompt/validator behavior. Separate fresh question/catalog bindings, calibration proposal, regression results and rehearsal evidence.

**Tech Stack:** Existing Python environments, pinned Linux x86_64 Torch/Transformers CPU image, Qdrant and Docker; no model substitutions or new dependencies.

**Spec:** User finalization request; specs/003-f3-grounded-rag/spec.md; generation-constraint-review.md; specs/002-f2-retrieval/plan.md.

## Global constraints

- Preserve all pre-existing paths/hashes, Stage 1 exact 404, approvals and original freeze.
- Keep threshold 0.45614706000000005 / EDM-f2-20261004-v1 until measured-threshold review.
- No slides, secrets, source additions, commits, publication, F5/F6 development.
- Fresh acceptance cases frozen before measurement, never tuned against.
- Keep 384 new tokens/16,384 completion bytes, generation 110s, request 240s, cleanup 45s, runner 8GiB/Qdrant1GiB.

## Review focus

Missing/tagless cached image: use digest, report startup failure. New question bindings: preserve approved claim/source rules and identify agent-prepared review, never invent prior human case approval. Valid IDs with unsupported spans: unchanged validator must reject. Replaced sources: no v1 claim may survive v2. Cleanup uncertainty: nonzero outcome and named fallback, never broad prune.

## Tasks

- [x] Freeze hashes/uncommitted inventory and copy approved helper snapshot to workshop/seda-20261008.
- [x] Add a reusable isolated wrapper and meaningful wrapper/choice/cleanup tests; retain RED/GREEN; no production adapter edits.
- [x] Freeze new question expectations/catalog-alias bindings and lifecycle criteria in a separately versioned acceptance file. Validate schemas/source/claim hashes before run.
- [x] Run local tests/Ruff/whitespace, Docker rebuild and Stage1 smoke, constrained wrapper and live fresh acceptance; retain exact commands/outcomes.
- [x] Recheck receipt regression and measure separate development calibration; review and adopt a separately versioned measured threshold under EDM’s explicit delegated authority. Original freeze remains unchanged.
- [x] If full F3 gate passes, prepare reviewed bounded F4 plan/tests; otherwise omit implementation and retain roadmap exercise.
- [x] Rehearse supported/unsupported demo and fallback; write organizer runbook, slide7 prerequisite table, local release/pull instructions and readiness receipt.
- [x] Independently verify preservation and owned resource absence; perform final review.

## Execution rulings

User-directed autonomous execution overrides skill handoff/commit prompts. New source texts are not required. The current acceptance preparation may add exact aliases in a separate catalog version but may not change reviewed claim renderings, source rules or historical catalog receipts. Full acceptance remains blocked if known F2 gate persists, regardless of a narrow F3 answer-case pass. Use existing approved build/run authority; never silently change threshold.

## Execution outcomes and rulings

- Ruling: EDM delegated local goal decisions, so agent reviewed the measured calibration proposal and adopted v2 threshold0.42808731. This is not an assertion of individual human value review. Cost if wrong: broadened false-positive risk; separately frozen fresh retrieval negatives passed.
- Fresh-v1 answer cases5/5 but lifecycle failed; preserved. Fresh-v2 retrieval5/5, F3 answers5/6, lifecycle/cleanup passed; full F3 acceptance remains failed.
- Ruling: omit F4 because F3 gate failed; retain plan/roadmap only. Cost: narrower guided workshop.
- Final review: important launch image/host-hash enforcement gaps fixed in a separate guard; three regression tests observed RED then GREEN, exact identity positive test passed. Historical wrappers preserved.
- Minor deferred: frozen Ruff cache entries retained to avoid altering the measured bundle; portability may require the complete frozen package.
- Ruling: no original ci-local.sh execution because its floating base/package build is different from the retained pinned-stack candidate. Execute/report local tests, fresh offline application rebuild and exact Stage1 smoke separately. Cost: original-script and clean dependency reinstall remain unverified.
- No commits/publication; preserve workspace evidence rather than skill cleanup that would discard the only record.
