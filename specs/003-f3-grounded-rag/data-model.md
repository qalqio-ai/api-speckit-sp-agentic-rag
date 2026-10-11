# F3 data model

Proposed design under [spec](spec.md) and [plan](plan.md). Closed serialized shapes
are in [schema](contracts/serialization.schema.json); semantic validation in
[CLI contract](contracts/answer-cli.md) is equally mandatory.

| Entity | Fields / relationships | Constraint / lifetime |
| --- | --- | --- |
| AnswerRequest | op=answer, exact use_case_id, question | Closed; F2 question256-token/4,096-byte limit; no normalization/history/evidence override |
| RequestEvidence | F2 RetrievalResult and verified snapshot/generation | Current exact scope; top_k3; internal request memory only |
| GroundingCatalog | version/id, manifest hash, approval attribution, source_rules, claims, questions | Reviewed validation rules, not alternative factual evidence or consent; frozen exact file hash |
| SourceRule | scope/source/revision/content hash; reviewed whole-source relevance/conflict assessment | Covers every approved source tuple in selected scope; stale/missing/unreviewed tuples fail |
| CatalogClaim | scope/claim_id/text, support alternatives of span lists, conflict claim IDs | Complete reviewed proposition including conditions; each alternative requires all spans; <=5 requested claims |
| SupportSpan | source identity/revision/hash, original start/end, exact quote | Entire span inside a current returned passage; quote/source-boundaries validated; no fragment semantic inference |
| QuestionCoverage | scope/exact question; expected_claim_ids; insufficient_reason nullable | Exact aliases only; answered expectations require nonempty claims and null reason; unsupported/conflict expectations require empty claims and explicit reason |
| ModelResponse | status; claim IDs/text/current chunk IDs; reason nullable | Strict JSON; exact approved rendering; all requested claims; no unrelated extras or free prose |
| AnswerResult | version3, request/run IDs, outcome, claims, citations, reason/error, configuration, counts/elapsed | Answered1–5 claims only; other outcomes zero claims/citations; safe metadata/no question/vector |
| Citation | unchanged F2 EvidencePassage provenance | Deduplicated chunk IDs from actual request; every citation used and every claim supported |
| F3ApprovalReceipt | purpose, manifest/catalog SHA256, owner/reviewer/decision/date, access/retention/deletion | Real separately reviewed F3 use decision; does not add sources or broaden rights |
| EvaluationCaseSet | IDs/fingerprints/attribution; >=3 positives and>=2 negatives | Separate approved frozen expectations; no quality assertion from shape |

## State transitions

received → validated → retrieval → coverage/support checked → one generation
→ strict response/claim/citation checks → answered or model-declared
insufficient(unsupported_question only). Model-declared conflict/no_evidence is
invalid_model_response; reviewed/verified conflicts stop before generation.
Successful empty retrieval → insufficient(no_evidence), zero generation.
Unknown question/incomplete reviewed support → insufficient(unsupported_question),
zero generation. Relevant reviewed contradiction → insufficient(conflicting_evidence).
Input invalid → rejected; dependency/catalog/config/output/grounding failure → failed.
No partial result. Missing reviewed support is insufficiency; mismatching revision,
unknown source rules or stale catalog is configuration failure, never silently accepted.

Keep shared mutation guard and snapshot generation until final result. A registry
change fails with zero claims; no repair/source-state mutation on nonfatal failure.
Fatal worker/protocol/uncertain stop invalidates the session and begins one owned
cleanup. Reopen loses readiness and is forbidden as recovery within the session.

## Trust, memory and review

Reviewers assess full source text when approving rules, including relevant conflicting
facts and complete conditions; a hash validates identity, not correctness of that
review. Scope-wide rules must cover all current represented sources. Multiple support
alternatives allow approved chunk splits without guessing missing context.
No review fact replaces actual returned evidence. Questions/model output live in
request memory; catalog/cases are approved read-only assets with explicit lifecycle,
not persistent user memory. Retained reports require separate authorization.

## Internal receipt and output lifecycle

RetrievalReceipt / ScopeSnapshot shapes in the schema define the internal F2 port:
one unchanged result, complete current represented source bindings, immutable registry
fingerprint, actual query dispatch count and the original clamped monotonic deadline.
This receipt is not serialized to the public operator protocol and supplies no new
passage facts. F3 does not infer full scope or attempt counts from top_k/status.

A validated answer is pending delivery until its whole JSONL line transfers within
remaining request/validation deadlines. Failure after partial transfer is undelivered,
fatal/nonzero with independent cleanup; never emits a second error on that channel.
The exact-alias/exact-claim requirements boundary was selected by the user on
2026-10-03; detailed design approval remains pending. Unknown exact aliases
may abstain despite answerable passages; accepted claim renderings are exact.
