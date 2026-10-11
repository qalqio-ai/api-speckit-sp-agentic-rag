# F2 data model

Status: proposed design. [Spec](spec.md), [CLI](contracts/retrieval-cli.md),
[shape contract](contracts/serialization.schema.json). Reuse F1 records unchanged.

| Entity | Fields and relationships | Validation/lifetime |
| --- | --- | --- |
| RetrievalRequest | op=retrieve; exact use_case_id; question; optional top_k | Strict closed object; question nonblank <=4,096 UTF-8 bytes; top_k integer 1–10, default3; no booleans |
| F2ApprovalReceipt | purpose=f2_local_retrieval; manifest_sha256; owner, reviewer, decision_reference, approved_at; local_demo_operator access; until_demo_end retention; owned_run_collection_and_stack deletion | Real decision evidence binds exact read-only F1 manifest; timestamp calendar-valid; does not add sources or grant redistribution |
| RetrievalConfiguration | mode; top_k; min_score; calibration_id nullable; query_encoding; scoring; model_configuration; retrieval/inventory/encoding/search budgets and max_scope_chunks | Mode deterministic/local_live explicit; generic F1-compatible encode, cosine exact; model_configuration is unchanged F1 RunConfiguration; threshold finite [-1,1] |
| ReadyScopeSnapshot | exact use case; approved source IDs; complete state map; expected IDs/counts/payload hashes; verified records; registry generation | Internal memory only; at most2,048 total passages; unknown stored rows or incomplete states fail; no source-state writes on nonfatal retrieval failure |
| EvidencePassage | all F1 ChunkRecord payload fields except vector, plus rank and score | Rank1-based contiguous; score finite; exact scope/config/revision/offsets/text; known IDs; verify payload hash against snapshot |
| RetrievalResult | schema_version2; run/request UUIDs; op; status; use_case_id nullable; configuration nullable; elapsed_ms; evidence_count; evidence; error nullable | matched nonempty; no_match empty; rejected/failed empty with fixed error; no raw question or vector |
| EvaluationCase | case_id; split=calibration/held_out; question; use_case_id; expected matched/source_ids or no_match; belongs to EvaluationCaseSet | Future approved synthetic case set; held-out expectations frozen before threshold evaluation |

## Request lifecycle

`received -> validated -> scope_verified -> query_encoded -> searched -> validated_result
-> matched/no_match`. Empty verified scope still validates question token length,
then returns no_match without semantic encoding/search.
Invalid input goes to rejected. Readiness/configuration/asset/search/deadline errors
are failed with no evidence; no transition repairs or marks a source complete.
Fatal worker/protocol/unconfirmed-stop errors end the whole session using existing F1
fatal invalidation and owned cleanup. Nonfatal read-only failures preserve F1 source states.

The session serializes all operations. A shared busy guard protects ingestion,
replacement, clear and retrieval; no concurrency or restart resume is supported.
If the observed registry generation changes despite the guard, fail instead of
returning stale evidence. Preserve original F1 operation envelopes and semantics.

## Identity and provenance

Retain canonical UUIDv5 chunk IDs and F1 source/configuration fingerprints. Original
Unicode character `[start,end)` offsets, source SHA-256 and exact payload text must
match the verified current record. Rank/scores are per search, never durable passage
identity. Strict fields, scalar identity types and known approved tuple/hash checks
prevent array payload equality from bypassing application scope validation.

## Search snapshot and completeness

Exhaustively read the approved scoped inventory with payload/vectors. Verify finite
nonzero 384-vectors and F1 record shape, exact expected set/count and payload hashes.
Verify actual configuration against the immutable run configuration. Candidate query
includes exact scope plus source/ID allowlists and returns every N snapshot ID once.
Reject any differing payload, foreign/unknown/duplicate/omitted ID or nonfinite score
before exposing any evidence. Threshold applies only after complete validation.

## Memory, retention and output

Questions, vectors and snapshots live only in request/process memory. The existing
index remains dedicated tmpfs until demo-end; registry disappears on close/restart.
No new user memory, retained trace or raw-text logging. Explicit operator results
contain evidence but not the question or vectors. Redirecting/capturing results,
calibration cases or reports to storage needs a separate approved retention/access/
deletion decision. Model assets/locks are executable resources, not corpus memory.

## Evaluation records

EvaluationCaseSet owns case_set_id, exact manifest/configuration fingerprints, actual
review attribution and closed EvaluationCase records defined in the schema. Case IDs
are unique across splits. Expected source IDs are approved within the exact scope;
matched expectations have nonempty unique IDs, no_match has no source_ids. Require
both calibration classes and >=3 positive/>=2 negative held-out cases. Shape tests
are visibly synthetic, never evidence of approval. Cases and their file SHA-256 are
frozen before held-out threshold evaluation.

The evaluator consumes a ready session, not a reopened index. Calibration summaries
use complete validated pre-threshold/pre-top-k candidates, share one search per case
with retrieval, and contain only identifiers/counts/finite score summaries and full
rank. Missing expected candidates/rank>3 or empty negative candidate sets fail.
Held-out uses normal top_k3 retrieval under frozen settings, passing any expected
source in first3 or exact no_match for negatives. See CLI contract for consumer,
startup modes, deadlines and output/retention boundaries.
