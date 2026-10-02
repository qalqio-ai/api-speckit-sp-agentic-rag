# R1 HTTP Contract

## Operation

`GET /v1/use-cases/{use_case_id}/sources`

No credentials, query parameters, or request body are required. `use_case_id`
is a string path segment. Match the decoded ID exactly and case-sensitively;
do not trim or normalize it. A URL without an ID segment does not match this
operation and is outside the unknown-use-case contract.

## Configured use case: HTTP 200

Content type: `application/json`.

```json
{
  "use_case_id": "sample-use-case",
  "sources": [
    {"source_id": "sample-source-1", "title": "Sample source"}
  ]
}
```

The top-level object contains exactly `use_case_id` and `sources`. Each source
contains exactly string `source_id` and string `title`. Array order follows
configuration; titles and IDs are not transformed. All configured sources are
returned without pagination.

## Empty configured use case: HTTP 200

Content type: `application/json`.

```json
{"use_case_id": "empty-use-case", "sources": []}
```

An empty source list does not make the use case unknown.

## Unknown use case: HTTP 404

Content type: `application/json`.

```json
{
  "detail": {"code": "unknown_use_case"}
}
```

The object contains exactly `detail`, which contains exactly `code` equal to
`unknown_use_case`, with no message. This follows the user's rule amendment.
Case-different and
whitespace-different IDs are unknown unless separately configured.

## Method rejection and read-only behavior

POST to this path returns HTTP 405. No custom error body is specified for 405.
Successful, empty, unknown, repeated, and rejected POST requests leave all
configuration unchanged. No mutation operation or outbound service call is
part of this contract.

## Documentation

The implementation's generated OpenAPI description should declare the GET
operation, successful response schema, and the explicit 404 error schema.
Framework-generated documentation is not an additional R1 business operation.
