# Prompt / request requirements template

Version: 1.0.0. Owner role: repository maintainer. Project-owned; not an upstream tool template.
Blank fields are intentional template inputs, not approved decisions.

## Request record

- ID / date / decision owner:
- Original request (separate from interpretation):
- Intended users and desired outcome:
- Stage: reusable API / appended Agentic RAG
- In scope / out of scope:
- Existing contracts to preserve:
- Assumptions and unresolved questions:

## Data, evidence and boundaries

- Inputs, source owner, classification and explicit approval record:
- Freshness and provenance (source ID, title, location, version/date):
- Answer without retrieval allowed when:
- Insufficient, conflicting, stale or adversarial evidence behavior:
- Tools, scopes and human approval points:
- Memory: none / session-only / persistent (justify any persistence):
- Retention, access, correction and deletion:
- Privacy, latency and cost limits:

## Observable acceptance and evaluation

| Case | Given / when | Expected status, output or decision | Evidence / pass condition |
|---|---|---|---|
| Input required | Input required | Input required | Input required |

Record answerable, unsupported, conflicting and prompt-injection cases when RAG
is in scope. For API changes, write tests first and record an expected behavioral
failure before production code. Do not treat missing dependencies as that failure.

## Approval and risks

- Consequential decisions and risks:
- Required approvals, named approver and actual decision/date:
- Verification commands and actual results (or not run):
