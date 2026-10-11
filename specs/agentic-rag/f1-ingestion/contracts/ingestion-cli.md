# F1 local ingestion session contract

Status: implemented contract; actual verification in [validation.md](../validation.md). [Spec](../spec.md).

## Entry point and permission boundary

Entry point: `python -m app.ingestion session --approval-manifest PATH
--model-dir PATH --qdrant-url URL --tmpfs-proof PATH`. Use the reviewed wrapper
to generate the read-only receipt from the actual owned tmpfs mount. The only accepted URL is the literal
`http://qdrant:6333`; omission uses that same fixed URL. Validate it before constructing
the storage client, connecting, or processing source text. Reject every other value,
including remote hosts, IP literals, localhost aliases, credentials, alternate ports,
paths, query strings and fragments. No credential arguments or hosted provider.
Storage requests must not follow redirects, use environment proxies, or fall back to
another endpoint; a redirect is a controlled `index_failed` outcome without sending
the request to its target. Runner and Qdrant join only the recorded project's dedicated
Compose network with `internal: true`, without host networking, additional networks,
or published ports. The wrapper verifies the Qdrant service's project membership;
runtime has no external-network acquisition path. The operator supplies real approved
source evidence and reviewed model assets. Startup validates offline assets/index
compatibility, creates an owned collection, and reads newline-delimited JSON operations
sequentially. stdout contains one result per input line; stderr contains IDs/status
and errors, not source text. EOF closes/cleans the run. No HTTP route is added.

## Operations

| op | Required input | Outcome |
| --- | --- | --- |
| ingest | use_case_id, source_id, title, revision, text | complete/rejected/failed/incomplete attempt status; source readiness separately; intended/current counts and bounded error code |
| inspect | use_case_id; optional source_id | exact scoped inventory/status, text/provenance/vectors, exhaustive count |
| clear | use_case_id; optional source_id | removes only exact scope; verified remaining count; failure stays visible |
| close | no additional fields | whole-run cleanup then session exit; no arbitrary collection/database delete |

All scopes are exact and case-sensitive and must be permitted by the startup approval
manifest for ingestion, inspection, and clearing. Reject unknown operations, malformed JSON,
unknown fields, missing/non-string metadata, unapproved content hashes, oversize text,
and unsupported format before adapter calls. Blank text is invalid. Inspection of a
scope with no records returns an empty inventory; it cannot leak another scope.
Stage 1's existing HTTP errors remain independent and unchanged.

Every result includes request_id, run_id, op, status, and selected scope where applicable.
Errors use a fixed machine-readable code and safe message. Codes:
`invalid_input`, `endpoint_not_allowed`, `source_not_approved`, `model_unavailable`, `embedding_failed`,
`index_failed`, `deadline_exceeded`, `incomplete_source`, and `cleanup_failed`.
Ingest results also include `source_status` and `ready`, separate from attempt
`status`. A failed attempt never claims successful ingestion of the attempted revision.
`ready` describes only the previously verified current source, if preserved; its
revision remains separately identifiable. A new source has `source_status: unseen`
and `ready: false` after preparation failure. Counts unavailable after storage failure
are null, not guessed. No complete outcome
is emitted before confirmed writes plus exact read-back. Inspect can expose incomplete
records for diagnosis but always labels them not ready.

## Lifecycle and exit behavior

The dedicated `/qdrant/storage` tmpfs is capped at **256 MiB (268,435,456 bytes)**
using `size=268435456`. Preflight must verify tmpfs type and actual capacity before
input is accepted; an absent/unverifiable cap is fatal startup failure. This bounds
storage capacity, not all container/model memory. Capacity exhaustion during mutation
or read-back uses `index_failed` with attempt status `incomplete`, `ready: false`,
and unknown counts null, within existing deadlines. Never auto-resize, auto-retry,
or switch to disk. Explicit recovery is permitted scoped clearing or close/teardown
and a fresh approved run; clearing must still be verified, not presumed to work on
a full filesystem. Deterministic tests inject capacity errors rather than fill host
storage; the authorized live demo checks the actual mount limit, not an invented
capacity benchmark.

Per-ingest total deadline 120 seconds; request timeout <=10 seconds and <=remaining
budget. At most one underlying attempt per storage call; user retry is separate.
Embedding deadline terminates the worker. Source size <=64 KiB UTF-8; <=2,048 chunks.
Normal close/EOF returns success only on verified cleanup. Failure behavior is fixed
by the phase in which it occurs, not by a blanket dependency-failure rule:

| Failure phase/class | Attempt outcome and source readiness | Session / recovery |
| --- | --- | --- |
| Invalid/unapproved input | rejected; prior source state unchanged | Continue; submit corrected approved input |
| Preparation: embedding error, invalid vector, or controlled embedding deadline | failed; no index mutation; prior readiness unchanged, or unseen/not ready for a new source | Continue; explicit retry uses a fresh embedding worker |
| Mutation or final read-back: storage error, redirect, or deadline | incomplete; source not ready; unavailable counts null | Continue; explicit retry reconciles the intended set |
| Fatal startup, unexpected worker exit, broken worker protocol, or inability to terminate worker | failed; no success claim; ending run invalidates readiness | Stop input; whole-run cleanup; nonzero exit; retry only in a fresh approved run |
| Final cleanup failure or interrupt | cleanup failure remains visible; no successful clearing claim | Nonzero exit; outer wrapper teardown; scoped operator recovery if residue remains |

Expected worker termination on the enforced embedding deadline is recoverable, not
a fatal worker failure. The outer wrapper attempts bounded teardown of its dedicated
stack on trappable exits; failed/unverifiable removal remains an error. No automatic
retry is introduced.

### Bounded shutdown and teardown policy

Use monotonic deadlines. Controlled embedding cancellation has a **5-second shutdown
budget**, reserved within the 120-second ingestion deadline: request termination
(TERM), wait at most 2 seconds, then force termination (KILL) and wait at most the
remaining 3 seconds. Never use an unbounded worker join. Cancellation begins before
the reserved window expires; no worker starts without sufficient remaining budget.
Expected deadline termination is recoverable only after the worker is confirmed gone.
Unexpected exit/broken protocol or failure to confirm termination is fatal and must
not lead to another ingestion worker being started.

Normal close, EOF, interrupt or fatal session failure starts one **45-second overall
teardown deadline** at its first trigger. Further signals/errors do not reset it.
Every phase/call is capped by its allocation and the remaining overall deadline:

| Phase | Maximum allocation | Required outcome / escalation |
| --- | --- | --- |
| Owned worker shutdown | 5 seconds | TERM <=2 seconds, then KILL and bounded wait <=3 seconds; no unbounded join; uncertain termination stays fatal |
| Owned collection deletion and absence verification | 10 seconds total | Each storage call <=10 seconds and <=remaining phase time; no automatic retries; failed verification remains cleanup_failed with unknown count |
| Owned Docker stack teardown | 30 seconds total | Compose down gets <=15 seconds wall time with a 10-second container stop grace; if unsuccessful, exact-owned-container kill gets <=5 seconds, exact-owned-container/network removal <=5 seconds, and absence verification <=5 seconds |

The outer wrapper owns this final deadline and supervises the runner/cleanup commands;
a hung runner, storage request or Docker CLI must not block it indefinitely. Subprocess
guards must reserve TERM/KILL handling inside their assigned phase time, stop waiting
at expiry, and record unverified residue rather than assume server-side removal. A
phase that exhausts its allocation yields cleanup_failed/nonzero; continue other
owned-scope cleanup only within the original remaining budget. All cleanup commands,
ownership lookups and verification are covered by the deadline.

Record exact project/container/network identities before the run and verify ownership
before each destructive cleanup step. Never global-prune, remove unrelated resources,
remove model/input mounts, or delete persistent development volumes. Successful final
cleanup requires verified worker exit, collection absence (or verified removal of its
own tmpfs service if collection verification failed), and owned container/network
absence. Earlier ingestion/fatal/cleanup errors preserve nonzero exit even if later
stack removal succeeds. At 45 seconds stop cleanup attempts, exit nonzero and report
remaining identities/unknown verification; operator recovery must use the same bounded
owned-scope policy before a new run. SIGKILL/host/OS failure can defeat supervision;
this is a bounded reporting/recovery policy, not guaranteed erasure or guaranteed
termination of an unresponsive Docker daemon.

SIGKILL/host failures bypass process traps. Operator recovery stops/removes the exact
recorded dedicated project before starting another demo; no global prune. tmpfs is
not secure erasure and may use swap. Preserve unrelated development containers/volumes.

## Approval and configuration records

Approval manifest records the actual reviewer/decision reference and exact approved
source/revision/content hashes plus scope/classification/access/redistribution. It does
not accept a self-asserted `approved: true` as authorization. The implementation review
must verify this local artifact reflects an actual decision; no remote identity service
or automatic approval is introduced. The planning command provides no sample approval.

Run configuration identifies model snapshot commit/file hashes, token-window/overlap,
vector dimension/distance, and scoped collection/run IDs. Changing embedding config
invalidates prior source sets; incompatible dimensions cannot share a collection.
Runtime models load offline with remote-code trust disabled. Corpus text may flow
only to the local worker and local Qdrant, never a hosted endpoint.

## Serialized schemas and semantic validation

[serialization.schema.json](serialization.schema.json) is the JSON Schema
2020-12 contract, not runtime code. Its `$defs/ApprovalManifest`,
`$defs/OperationRequest`, and `$defs/OperationResult` are the respective validation
entry points. All object fields are required unless excluded from that object's
`required` list. Unknown fields are rejected, including `approved: true`. The only
map with dynamic keys is `model_file_sha256`, whose keys are model-relative file
paths and whose values are lowercase 64-character SHA-256 hashes. It has no approvals,
secrets, corpus text, or absolute paths. Manifest and result `schema_version` is
integer 1; input operations omit that field and caller-supplied request/run IDs.

The manifest requires actual owner/reviewer, decision reference, RFC 3339 approval
timestamp, classification, redistribution scope, local-operator access, demo-end
retention/deletion scope and a nonempty list of exact allowed source tuples/hashes.
No sample approval is supplied. Validate the calendar timestamp with format checking;
reject duplicate `(use_case_id, source_id, revision)` tuples even if hashes differ.
Inspection/clear permission is derived from approved tuples: whole-use-case requests
include only approved source IDs, never every record merely sharing a use-case label.
The human review must establish authenticity of the decision; a schema cannot do so.

An absent request `source_id` selects the exact permitted use-case inventory/clear
scope; explicit null is invalid. Serialized result `scope.source_id: null` represents
that whole-use-case selection. Ingest results require a non-null source ID. Invalid
or unavailable scope is result `scope: null`; never copy arbitrary rejected text into
results. Generate UUID request/run IDs locally. Unknown operation/malformed input uses
`ErrorResult` (`op: null`, safe error code/message); parsed known operations use their
operation result shape. Startup errors are safe stderr diagnostics before input is
read. Explicit `close` has one stdout result; EOF/interrupt cleanup has no fabricated
input line/result and reports its cleanup outcome to stderr and process exit status.

Operation statuses are closed enums: ingest and inspect use
`complete/rejected/failed/incomplete`; clear uses `complete/rejected/incomplete`;
close uses `complete/failed`. `complete` requires error null and populated operation
data/configuration; other statuses require a safe error object. Rejected/failed
results may have data/configuration null when unavailable. Inspect succeeds with
empty sources and count zero for approved absent records, uses `incomplete` with
`incomplete_source` for diagnostic incomplete inventories, and uses `failed` with
sources/count null if exhaustive reading fails. No partial page is reported as complete.
Clear success requires verified remaining count zero. Close success requires
`collection_removed: true` and remaining count zero; outer wrapper stack teardown is
reported separately, never claimed by the CLI's collection result.

Additional semantic checks are mandatory: strict JSON (no duplicate keys, NaN or
Infinity); integers must not accept booleans; strings preserve exact IDs and text;
UTF-8 text <=65,536 bytes; chunk count <=2,048; offsets satisfy `0 <= start < end`
and text equals the original slice; vectors have 384 finite values and nonzero norm.
Every chunk retains scope, title, revision, content hash, offsets/text, deterministic
UUID, tokenizer/configuration fingerprints and model identity. Verify model-relative
hash paths cannot escape the read-only snapshot and all approved file hashes match.
The schema defines run configuration keys and approved numeric defaults; unavailable
configuration is null, never populated with invented model hashes.

Result invariants supplement the schema: complete ingest has ready true, complete
source status, attempted/current verified revisions equal and equal verified counts;
preparation failure preserves the prior source state/revision/count (or unseen/not
ready/zero current count for an untouched new source); mutation failure has incomplete
source status and ready false. Unavailable counts are null. In incomplete inspection,
each record carries its actual revision/configuration, including mixed sets, and each
source is labeled not ready. Whole-run fatal failure invalidates readiness. The schema
checks shape; deterministic application tests must establish these relationships.
Complete source inventories require non-null current verified revision and counts,
ready true, matching record/count totals and exact approved scope; incomplete sources
require ready false. An inspect-complete result has non-null sources/count with an
exhaustive sum matching the returned records, never guessed or partial-page counts.
