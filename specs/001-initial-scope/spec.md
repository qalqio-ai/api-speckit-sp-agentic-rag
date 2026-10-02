# Initial scope: reusable API, then appended Agentic RAG

Version: 1.0.0 — 2026-10-02. Stage sequencing authorized by the user;
Stage 2 feature design and implementation are not yet approved.
Decision owner role: project owner; person not designated.

## Stage 1 — reusable API

Preserve the existing API, package, tests, Docker and local-check scripts.
[R1](../001-list-use-case-sources/spec.md) remains its feature contract:
configured IDs return ordered source IDs/titles; empty configured IDs return
an empty successful list; unknown IDs return HTTP 404 with exactly
`{"detail":{"code":"unknown_use_case"}}`. Matching is exact and case-sensitive.
`/health` reports readiness. Requests do not change static configuration.
No database, authentication, LLM, vector database, outbound call or user memory
is added to R1 by this governance restoration.

## Stage 2 — appended Agentic RAG

Proposed first slice: an in-scope question retrieves approved evidence, assesses
sufficiency and returns a cited answer, bounded refinement or explicit abstention.
Append this capability in the same repository without replacing Stage 1.
No new endpoint, dependency, provider, vector store, orchestration or UI is
selected or implemented here.

### Proposed requirements for the next reviewed feature spec

- Show passages and source ID, title, location and version/date where available.
- Ground factual claims in reviewed evidence; surface conflicts or stale evidence.
- Abstain or ask a bounded follow-up when evidence is insufficient.
- Treat retrieved instructions as untrusted and preserve authority boundaries.
- Make retrieval/refinement decisions inspectable and tool permissions narrow.
- Evaluate answerable, unanswerable, conflicting/stale and adversarial-document cases.
- Keep end-user persistent memory disabled; distinguish it from any document index.

### Preconditions and acceptance gates

| Gate | Required evidence | Current state |
|---|---|---|
| Restore governance before features | Agent guide, brief, ten-principle constitution, roles, index and templates | This reconciliation; validation recorded separately |
| Preserve Stage 1 | Relevant tests and API compatibility review | Must be checked on each behavior change |
| Approve scenario and corpus | Human decision with owner, classification, access and redistribution scope | Undecided |
| Approve architecture and dependencies | Reviewed feature spec and plan | Not yet supplied |
| Define evaluation | Reviewed fixtures, groundedness/citation/abstention/tool-boundary criteria and thresholds | Undecided; no RAG results claimed |
| Authorize persistence | Retention, access, correction and deletion decisions | Not authorized |
| Authorize Docker Hub release | Namespace/image/tags, legal/data review, tested artifact and release approval | Not authorized |

## Non-goals

Production/customer data, autonomous consequential actions, broad multi-agent
orchestration, cloud deployment, persistent end-user memory and unapproved public
redistribution. Templates are requirements aids, not installations or approvals.

See [brief](../../docs/project-brief.md), [constitution](../../docs/constitution.md)
and [release workflow](../../docs/release.md) for governing boundaries and decisions.
