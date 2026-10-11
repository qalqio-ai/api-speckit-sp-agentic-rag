# Agentic RAG learning roadmap

Status: **Reconciled proposal for review; not approved for implementation**.
Created: 2026-10-02. Reconciled: 2026-10-02.

Learn the Workshop Knowledge Assistant through independently demonstrable slices:
reuse the API, ingest documents, retrieve evidence, generate grounded answers, add
bounded model decisions, then session memory, validated tools, and evaluation with
a local Docker release. This shallow spec-of-specs records each slice's outcome,
dependencies, boundaries, acceptance criteria, status, and feature-spec destination.
Each slice needs its own reviewed specification, plan, tasks, and verification.

## Source, authority, and reconciliation

Source: the complete **Governance reconciliation** and **Stage 2** sections of the
[runbook](../../docs/Foundational_Multiuse_API_SpecKit_Superpowers_Runbook.md).
The F0–F7 mapping below now follows its learning ladder. Repository context remains
[project brief](../../docs/project-brief.md),
[initial scope](../001-initial-scope/spec.md),
[authoritative constitution](../../docs/constitution.md), and
[adoption boundary](../../docs/evolution-path.md).

Only this roadmap is reconciled. Stage 1 and the existing ten-principle constitution
remain authoritative and unchanged. The runbook's governance bootstrap, migration,
new policy principle, installation, branch, commit, and publication instructions are
not authorization to execute those actions. No second constitution is activated.

Stage 1 retains exact, case-sensitive IDs, ordered source IDs/titles, successful
empty lists, read-only configuration, JSON/OpenAPI contracts, and `/health` readiness.
Unknown use cases remain HTTP 404 with exactly
`{"detail":{"code":"unknown_use_case"}}`. No RAG dependency or outbound call is
added to the R1 request path. New Stage 2 contracts require separate review.

Discrepancies resolved:

- F2 previously combined retrieval and generation. It is now retrieval only;
  grounded generation has its own F3 slice.
- The agent loop was previously F3, memory F4, tools F5, and evaluation F6.
  These are corrected to F4, F5, F6, and F7 respectively, with explicit criteria.
- F0 verifies and reuses the existing Stage 1 API and local harness; it does not
  rebuild the repository, upgrade its runtime, or substitute fresh-build contracts.
- The runbook's F4 example permits a tool action before its F6 implementation.
  Under the user's clarification, tools are unavailable through F5. F4 rejects
  attempted tool actions; F6 introduces the one-call tool budget and calculator.
- The runbook's F7 includes image publication. The current scope ends at local
  evaluation, packaging, and release rehearsal; publication is separately authorized.
- The runbook proposes Python 3.12/uv, Qdrant in Compose, and new routes. Preserve
  Stage 1's existing environment and contracts; review Stage 2 architecture and
  dependency compatibility in feature plans, rather than silently adopting them.

## Learning scenario and boundaries

The runbook proposes three fictional documents (product guide, return policy,
troubleshooting guide) and a separate second use-case corpus for isolation checks.
The return fixture permits unopened-item returns within 30 days with a receipt;
there is no international-shipping policy. These are proposed synthetic lab facts,
not real company policy or an approved ingested corpus.

Demonstrations progress from a paraphrased return question to a grounded answer,
unsupported shipping abstention, one weak-search refinement, a receipt follow-up,
and a typed calculator result. Source evidence, session context, and tool results
must remain distinguishable. Select/approve the supported scenario and inputs in
F1's spec before ingestion; preserve owner, classification, access, redistribution,
and provenance decisions. No source data is added by this roadmap.

## F0–F7 slices

All acceptance criteria below are proposed requirements, not passing results.
**D** denotes deterministic local tests with controlled model outputs/vector fixtures;
**L** denotes live local evaluation with real embeddings and, where relevant, a real
model. Feature-spec destinations were initially reserved; F1 and F2 now have
feature documents whose own status and validation records govern their readiness.
Other feature-spec links remain reserved destinations. F0 reuses the existing R1
spec; no duplicate F0 implementation spec is needed.

| Slice | Independent demonstration | Dependencies | Boundary | Acceptance criteria | Status | Feature spec |
| --- | --- | --- | --- | --- | --- | --- |
| F0 — Repository and API reuse | Start the existing API; inspect health/OpenAPI and ordered, empty, and unknown source catalogs. | Existing Stage 1 implementation, governance, synthetic fixtures, and local harness. | Reuse Stage 1 unchanged; no new routes, runtime migration, corpus, or RAG implementation. | D: readiness and existing invalid-request handling; exact configured/empty/unknown responses; case-sensitive IDs and preserved order; rejected mutations leave configuration unchanged. Run the existing local gate before accepting F0. | Existing implementation/spec; current verification pending. | [Existing R1 spec](../001-list-use-case-sources/spec.md). |
| F1 — Ingestion | Inspect approved document chunks, deterministic IDs, vectors, and source references in the proposed Qdrant index. | F0 accepted; approved inputs and index lifecycle; compatible embedding adapter and proposed Compose Qdrant service reviewed in the plan. | Parse/chunk/embed/upsert only; retain use_case_id, source ID/title, chunk ID, and location/version where available. No answer generation, agent loop, memory, or tools. | D: reject empty input; stable IDs; repeated ingestion adds no duplicates and reconciles removed chunks from that source; preserve metadata and isolate use cases. L: real embeddings produce inspectable indexed vectors. | Proposed; not implemented or verified. | [Planned F1 spec](f1-ingestion/spec.md). |
| F2 — Retrieval | A paraphrased question retrieves the expected source and exposes top-k evidence, provenance, and scores. | F1; compatible question/document embeddings and reviewed retrieval cases. | Mandatory use-case filter; evidence-only response. No generated answer, agent loop, memory, or tools; relevance thresholds need calibration. | D: expected fixture source, top-k bound, no-match behavior, and no cross-use-case chunks. L: real semantic retrieval returns the expected source for a paraphrase on the approved corpus. | Draft requirements created; not implemented or verified. | [F2 draft spec](../002-f2-retrieval/spec.md). |
| F3 — Grounded RAG | Show a supported cited return answer and explicit insufficient evidence for international shipping. | F2; reviewed model adapter, answer contract, and expected claims. | Ordinary retrieve-then-generate baseline; citations refer to evidence from this run. No adaptive loop, memory, or tools; retrieved instructions cannot override policy. | D: exact valid source/chunk citation IDs, unsupported-query behavior, malformed model responses, and controlled dependency failure. L: claims match retrieved evidence and unsupported questions do not invent policy; citation validity alone is insufficient. | Proposed; not implemented or verified. | [Planned F3 spec](f3-grounded-rag/spec.md). |
| F4 — Bounded agent loop | A real model selects retrieve, refine-query, or final response; inspect its actions and at most one refined search after weak evidence. | Verified F0–F3; approved typed decision schema and stop/failure contract. | Application-enforced maximum two retrieval searches total, at most one refinement, and four model decisions per request. Tools unavailable (zero calls); memory off. Preserve F3 grounding and citations. | D: one permitted refinement, no third search or fifth decision, explicit exhaustion/insufficient-evidence termination, malformed-action rejection, unavailable-tool denial, injection resistance, and bounded timeout/retry behavior. L: genuine model-selected actions and capped refinement appear in the trace; a fixed search/generate pipeline is not proof. | Proposed; not implemented or verified. | [Planned F4 spec](f4-bounded-agent-loop/spec.md). |
| F5 — Session memory | Resolve “What if I lost it?” to the receipt, then clear/expire the summary and demonstrate isolation. | F4; reviewed summary lifecycle, TTL, access, and deletion rules. | Short-lived context scoped to both session ID and use case; context never replaces source evidence. In-process store resets on restart. Tools remain unavailable; persistent end-user memory excluded. | D: session/use-case isolation, TTL expiry, explicit clearing, restart reset, and unchanged F4 budgets. L: follow-up reference resolves while the answer remains grounded in retrieved policy. | Proposed; not implemented or verified. | [Planned F5 spec](f5-session-memory/spec.md). |
| F6 — Tool use | Model selects an allowlisted calculator with typed arguments; show 15% off 1,200 = 1,020 as a tool-derived result. | F4 action/budget enforcement; reviewed tool schema/allowlist. F5 for the full conversational demo. | One read-only calculator, at most one tool invocation per request; retain two searches/one refinement/four model decisions. No arbitrary eval, write tool, external action, or consequential decision. | D: correct calculation, unknown-name denial, invalid-argument rejection, timeout control, no second invocation, and tool/corpus provenance separation. L: actual model-selected valid tool action and result appear in the trace. | Proposed; not implemented or verified. | [Planned F6 spec](f6-tool-use/spec.md). |
| F7 — Evaluation and local release | Produce separate retrieval/answer/control-flow reports; build/run the local API image with Qdrant and demonstrate readiness, ingestion, query, and cleanup. | Accepted F0–F6 for the integrated candidate; reviewed evaluation cases/thresholds, image contents, runtime configuration, and local Docker access. | Local gate, mock/live smoke modes, and release rehearsal only. Preserve Stage 1 image identity and development volumes; no GitHub Actions or Docker Hub automated builds; no publication in this scope. | D: Stage 1 regressions, isolation/budgets, readiness failure and container smoke; clean up test containers on failure. L: supported/paraphrased/unsupported queries, follow-ups, weak retrieval, calculator, injection, and dependency failure are assessed with actual evidence. Record tested revision/image ID and each mode's results or limitations. | Proposed; not implemented, evaluated, or released. | [Planned F7 spec](f7-evaluation-local-release/spec.md). |

## Dependencies and feature review cycle

Integrated ladder: **F0 → F1 → F2 → F3 → F4 → F5 → F6 → F7**.
F6's core tool behavior depends on F4, not memory; the integrated learning path
includes F5. F0–F3 form the ordinary-RAG baseline. F4 adds agentic behavior; F5
adds short-lived memory; F6 first enables tools. Reviewed fixtures can isolate tests,
but cannot establish that predecessors or the live integrated demo are complete.

For the two-hour workshop, prepare and verify F0–F3 before the session and implement
F4 during it. F5/F6 demonstrations must identify their prepared advanced revision;
they are not evidence of participant implementation. Full replay is self-paced.

After roadmap review, verify F0 and specify F1 alone with `$speckit-specify` and an
explicit feature directory matching its planned link. Follow the current adoption
boundary and [project-owned feature template](../../docs/templates/feature-spec.md).
Clarify material ambiguity, review each spec, then review its plan/tasks and analysis
before implementation. Keep Superpowers design, test-first engineering, review, and
verification aligned with the feature's requirements. No feature commands run here.

Track proposed → spec drafted → spec approved → plan/tasks approved → implementing
→ verified, with actual approval and verification evidence linked from each spec.
Before production behavior changes, write/run API tests, confirm the expected failure
is behavioral, implement, and rerun relevant checks. Roadmap approval alone is not
implementation approval. Existing or prepared artifacts do not prove current success.

## Deterministic tests, live evaluation, and local release

Deterministic tests use controlled model actions/answers and vector fixtures without
network services. They prove application contracts, validation, isolation, budgets,
and failure behavior. Passing them does not prove semantic retrieval, grounded model
claims, adaptive decisions, or model-selected tools.

Live evaluation runs locally against real embeddings/models and approved corpus
cases. Define expected source IDs and claims before evaluating. Separate retrieval
quality, claim support, citation provenance, and control-flow correctness; do not
require identical generated prose. Calibrate relevance thresholds against the actual
embedding model, distance metric, and corpus. Record model/embedding versions, corpus
version, configuration, observed results, latency/cost, and unverified cases. If live
mode is unavailable, report it explicitly; never present scripted output as live.

Evaluation accompanies every slice; F7 consolidates it. Trace request IDs, actions,
queries where approved, source/chunk IDs, tool status, latency, and budget usage.
Do not log secrets or raw user/document text by default; define access and retention.

F7 should extend the existing local gate to build the API image, start API/Qdrant,
wait for readiness, ingest approved fixtures, check queries/citations/unsupported
behavior/budgets, and clean up isolated test containers on any exit while preserving
development volumes. Preserve the existing `/health` readiness contract; review any
new dependency-readiness route separately. Do not call the LLM for each health probe.

The runbook's `scripts/rag_smoke.py --mode mock`, `--mode live`, live-evaluation command,
and release Compose configuration are future deliverables, not commands verified
here. Follow [local verification/release guidance](../../docs/release.md). All quality
checks run locally; **no GitHub Actions and no Docker Hub automated builds**.

Retain the Stage 1 image namespace/name where established; example workshop image
names are illustrative. Keep corpus/index volumes and credentials outside the app
image; supply runtime configuration separately. A locally built image is not a
published or remotely pullable release. Docker Hub authentication, source pushes,
PRs, tagged image publication, digest capture, and pull/run verification require a
separate authorized release step. No implementation or publication occurs here.

## Remaining decisions

- Approve this reconciled roadmap and each feature's scenario, scope, and acceptance
  criteria before implementation; no feature spec or plan is created by this change.
- Approve synthetic corpus ownership/classification/access/redistribution and index
  lifecycle before F1 ingestion. Persistent user memory stays disabled; F5 needs
  explicit TTL, access, correction, expiry, and clearing decisions.
- Review the runbook's proposed Compose Qdrant architecture, model/embedding adapters,
  platform compatibility (Intel Mac/Linux), dependency versions, provider/cost limits,
  and any Python/uv migration in plans. No installation or environment upgrade here.
- Define model/dependency timeouts, retry ceilings, session TTL, evaluation thresholds,
  and any additional time/cost caps during feature review. Fixed F4/F6 action budgets
  above come from the runbook plus the user's tool-availability clarification.
- Legal rights, license, image redistribution, registry destination, and publication
  authorization remain unresolved. The runbook is a guide, not approval evidence.
