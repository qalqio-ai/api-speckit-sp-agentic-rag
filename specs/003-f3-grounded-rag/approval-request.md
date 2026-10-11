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

# Current approval status — 2026-10-04

Received user decision: “Yes i'm EDM or emcbee@alphaqidz.com and is the owner/reviewer.
I approved all.” EDM ownership/review and the displayed source/model proposals are
now approved; contact emcbee@alphaqidz.com. The prior requests below are historical,
not outstanding source/model ownership or acquisition questions.

Recorded [session approval](session-approval.json), created only the four exact
approved synthetic texts and purpose receipts under tests/fixtures/f3, acquired
only the six pinned allowlisted model files and verified their sizes plus upstream
Git-blob SHA1/LFS SHA256 and independently computed local SHA256. See
[acquisition receipt](acquisition-receipt.json). Model card Apache declaration is
retained locally outside the strict snapshot. No repository license grant inferred.

Actual offline tokenizer and FP32 model-weight loading succeeded under unchanged
8GiB/four-CPU/no-swap caps. Model load15.93seconds, peak2.72GiB; no generation attempt
or semantic acceptance in those probes. Approved live calibration processed the
fixed corpus/cases, complete candidate sets and actual single query per case.
See [live calibration](live-calibration-report.json): positive minimum0.7199879,
negative maximum0.19230622, proposed midpoint0.45614706000000005. Collection and
owned stack absence verified; runner peak1.08GiB/Qdrant0.39GiB,8.13–8.27s per query.
Ten GiB is planning headroom; Desktop settings unchanged.

The remaining numerical review is specific: min_score0.45614706000000005,
calibration_id EDM-f2-20261004-v1, frozen before held-out and F3 answer acceptance.
[The existing F2 plan](../002-f2-retrieval/plan.md#verification-and-calibration)
requires proposing the measured separator “then obtain review.” This number did
not exist when the earlier source/model proposals were approved; no historical
approval is fabricated for it. [Concrete threshold/case fingerprints](threshold-proposal.json)
are ready for review. No renewed source, owner, model or local implementation/build/
run approval is requested. Held-out/generation acceptance waits for that decision.

Preserve Stage1/API/F1/F2/governance/specifications/contracts/checklists/locks.
No Docker settings or caps changed, hosted transfer, persistent end-user memory,
commit, push, PR or publication. The resource probes/calibration are genuine live
measurements, not full F2/F3 acceptance or a claim that generation quality passed.

---

# Historical approval requests (superseded above)

# Decisions required for complete F3 acceptance

Implementation is authorized by the user’s speckit-implement F3 complete request.
This document makes the remaining actions reviewable; it is not an approval receipt.

## Decision received and concrete values still needed

The user replied “Proceed with your recommendations”. F2 implementation and the
proposed local capacity/build/run checks are authorized; safe repository metadata
and claim checks are the selected capture default. The F2 native core and internal
receipt bridge now exist and pass class-composition tests. Live predecessor
acceptance, factory/wrapper/worker supervision remain pending.

Last recorded capacity: host64GiB, Docker4101435392bytes (about3.8GiB)/16CPUs. F3's
unchanged8GiB runner plus1GiB Qdrant ceilings and approximately1GiB VM headroom
motivate a recommended10GiB allocation; this is not a measured physical minimum.
No Desktop settings or budgets changed. Model location/acquisition and source
owner/reviewer name are still concrete missing values, not a repeated approval
request for implementation. No source/model/receipt fixture created.

The 2026-10-04 continuation is limited to deterministic fixtures. See
[concrete source/model/memory/code decisions](continuation-decisions.md) for exact
documents, pinned model byte sizes/destination and current implementation versus
live-verification gaps. Existing build/run authorization does not fill those gates;
the latest instruction prohibits model downloads and Docker setting changes.

F2 needs competing sources beyond the single-source F3 proposal. Exact additional
texts/hashes and separate calibration/held-out cases are prepared in
[F2 T002 proposal](../002-f2-retrieval/tasks.md); explicit source-use approval and
owner/reviewer name are requested before creating or processing that corpus.

The original review request below is retained as history; current status above
supersedes its statement that no F2 code exists.

1. F2 prerequisite: implement the existing specs/002-f2-retrieval plan/tasks and
   its internal retrieve_with_receipt bridge, preserving its public envelopes and
   Stage1/F1 contracts. F3 task T041 assigns F2 to its own workflow. No F2 code exists.
2. Synthetic sources: exact proposal and SHA256 are in F3 tasks.md T002 ledger.
   Proposed owner/reviewer must be supplied, classification synthetic/nonpersonal,
   local demo operator access only, no upload or redistribution. Approve F3 purpose
   and exact aliases/claim wording/cases, including replacement and neighboring
   scope variants, before corpus/fixture creation or ingestion.
3. Generation assets: SmolLM2-360M-Instruct revision
   a10cc1512eabd3dde888204e902eca88bddb4951, CPU FP32 and existing locked stack.
   Supply an approved absolute existing asset directory, or specifically approve
   acquisition and rights review. No fallback/dependency installation is proposed.
4. Capacity/run: permit local capacity probes and dedicated F3 Docker build/run
   under 8GiB runner/4CPU and1GiB Qdrant hard ceilings, read-only model/source mounts,
   offline/internal network and owned temporary index. Source/index lifetime ends
   at demo cleanup; no global prune or shared-volume deletion.
5. Evidence: retain code/test reports in this repository; actual raw evaluation
   output needs a chosen local location, reviewer access and expiry/deletion policy.
   Proposed default: safe metadata/claim checks only in validation.md; no raw prompts,
   source/model diagnostics or persistent end-user memory.

These decisions are required by AGENTS.md: do not invent sources/consent/ownership
or approvals; do not ingest a corpus before owner/classification/redistribution/access
are approved; installations and external actions need specific authorization.
Local implementation and injected OS/process tests continue independently.
