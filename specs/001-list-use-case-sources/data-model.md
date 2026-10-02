# R1 Data Model

## Use-case configuration

`USE_CASE_SOURCES` is a static in-memory mapping in `app/sample_data.py`.
Its keys are exact string use-case IDs, and its values are ordered lists of
source records. Membership, not source count, determines whether a use case
exists. No persistence or request-time configuration updates are included.

| Sample use-case ID | Configured sources |
|--------------------|--------------------|
| `sample-use-case` | One source: `sample-source-1`, titled `Sample source` |
| `empty-use-case` | Empty list |

## SourceResponse

| Field | Type | Rule |
|-------|------|------|
| `source_id` | String | Preserve the configured ID exactly |
| `title` | String | Preserve the configured title, including Unicode and quotation marks |

Source contents and metadata are outside R1. No uniqueness or nonempty-string
validation is introduced beyond the approved requirements.

## UseCaseSourcesResponse

| Field | Type | Rule |
|-------|------|------|
| `use_case_id` | String | The exact configured ID requested |
| `sources` | Ordered array of SourceResponse | Include all configured sources; empty is valid |

Response records are constructed without mutating or reordering configuration.
Only these fields appear in successful responses.

## Unknown-use-case error (amended)

The HTTP 404 body contains exactly `detail`, an object with this field:

| Field | Type | Rule |
|-------|------|------|
| `code` | String | Always `unknown_use_case` |

The complete body is exactly `{"detail":{"code":"unknown_use_case"}}`.
There is no message or additional field. This reflects the user's rule amendment.

## Relationships and lifecycle

One configured use case has zero or more ordered source records. Requests read
the mapping and produce a response; there are no state transitions, source
creation, updates, deletion, or cross-use-case association changes.
