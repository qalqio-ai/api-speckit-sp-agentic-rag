# F1 data model

Status: implemented; [requirements](spec.md), [interface](contracts/ingestion-cli.md).
Serialized field names, types, required/null rules, and operation enums are defined
by [the schema](contracts/serialization.schema.json). The CLI contract's
semantic checks supplement those shapes; successful validation is not source approval.

| Entity | Fields / relationships | Validation and lifetime |
| --- | --- | --- |
| ApprovalManifest | approval record/reviewer/date, classification, access/redistribution scope; allowed source tuples and UTF-8 content SHA-256 | Real decision evidence required; tuple/hash match before text processing; local read-only input, not an invented consent flag |
| RunContext | run UUID, owned collection, local model commit/hash, chunk configuration, clock/deadline | Fresh each session; in-memory registry; collection cannot be caller-selected; no restart resume |
| SourceDocument | use_case_id, source_id, title, revision, text | Non-blank metadata; exact untrimmed identities; non-whitespace text, <=64 KiB UTF-8; approval tuple/hash required |
| SourceState | scoped identity, current verified revision/configuration, attempted revision/configuration, status, expected IDs/count, bounded failure code | In-memory per run; complete only after verified replacement; incomplete sources not ready; pre-mutation failure preserves prior readiness |
| Chunk | UUIDv5 chunk_id, source scope/title/revision, start/end character offsets, text, tokenizer/config identity | Text equals original slice; non-empty; token window fits model with special tokens; deterministic canonical identity |
| EmbeddedChunk | Chunk plus embedding model commit/config, 384 float values | All values finite; nonzero norm; dimension matches collection; no scripted live claim |
| IngestionResult | request/run IDs, source scope/attempted revision, current verified revision, attempt status, source_status, ready, intended/current chunk counts, optional error code | complete/rejected/failed/incomplete attempt status; source readiness separate; failed storage read-back uses unknown count, not invented zero |
| InspectionResult | run ID, requested scope, source status, records and exact counts | Mandatory scope filter, exhaust pages; incomplete clearly identified; vectors/text only in explicit inspection |
| ClearResult / CleanupResult | exact cleared scope, verified remaining count, status/error | Report zero only after verified absence; cleanup confined to owned collection/stack |

## Identity and source text

Use Unicode Python character offsets as half-open `[start, end)` into the original
source revision, not byte offsets. Required titles/text preserve Unicode and quoting.
Do not normalize/trim exact scope IDs. Blank identity detection uses whitespace-only
validation without changing a valid identity. UTF-8 content hash binds exact text.
The UUIDv5 input is canonical JSON containing the exact scope, revision, source hash,
chunk/model configuration fingerprints, position, and slice hash; use a fixed project
namespace chosen/documented at implementation, never runtime randomness for chunk IDs.

## State transitions

`unseen -> validated -> preparing -> in_progress -> complete`.
Reject invalid/unapproved input before preparing and before index mutation. Preparing
failure leaves prior complete data unchanged but returns failed attempt. Mutation or
read-back failure moves the source to `incomplete`; explicit retry can converge to
`complete`, while scoped clear moves it to `cleared`. Distinguish failed attempt from
current source readiness. No incomplete state is reported as current ready evidence.
Preparation failures return attempt status `failed`, with the old current verified
revision still separately identified; a new source remains `unseen` and not ready.
Controlled embedding timeout terminates only that attempt's worker and permits
fresh-worker retry. Unexpected worker exit, broken protocol, or failure to terminate
is fatal: whole-run cleanup, nonzero session exit, and recovery by fresh run only.
Mutation/read-back failures return attempt status `incomplete`, not `failed` with
preserved readiness. See the contract's failure-phase table for session behavior.

Compute/validate desired chunks first. During mutation source readiness is false.
Upsert expected IDs, delete obsolete IDs only in scope, verify exhaustive final IDs,
metadata, dimensions, then mark complete. This is recoverable reconciliation, not
atomic rollback. A mismatching config requires replacing that source set, not mixing
incompatible vectors. Two use cases sharing a source ID retain distinct states/IDs.

## Persistence and deletion

Only Qdrant's dedicated tmpfs holds live indexed chunks during the demo. Its
storage mount capacity is 256 MiB (268,435,456 bytes), verified before input; this is
not a total-memory cap. Capacity errors follow the contract's incomplete/not-ready
mutation failure path, with no automatic resize, retry, or disk fallback. Application
registry/context are process memory; no persistent session memory or raw-text traces.
The run configuration also records the contract's worker/teardown budgets. Worker
shutdown has a 5-second bounded TERM/KILL policy; whole-run teardown shares one
45-second deadline (worker 5, collection 10, Docker 30). Unknown residue remains an
error, not a deletion or erasure claim. Scoped clear removes current indexed text,
metadata, and vectors; whole-run close
removes owned collection and stops the dedicated service. Failed verification remains
visible. Model assets are immutable local executable resources, not corpus memory;
their acquisition/review and retention are separate from the temporary document index.
