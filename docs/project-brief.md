# Project brief

Version: 1.0.0 — reconciled 2026-10-02; remaining decisions below.

| Field | Recorded value |
|---|---|
| Repository | `api-speckit-sp-agentic-rag` |
| Existing API/package identity | Foundational Multi-Use API / `foundational-multi-use-api` |
| Description | A reusable API foundation, extended by appended Agentic RAG in the same repository. |
| Purpose | Establish stable, testable API contracts first; add evidence-grounded retrieval and bounded agent behavior next. |
| Intended users | API consumers; participants inspecting an Agentic RAG workflow (proposed audience, subject to review). |
| Authorized workspace | `/Users/edmcbee/Projects/api-speckit-sp-agentic-rag` |
| Existing remote | `git@github.com:qalqio-ai/api-speckit-sp-agentic-rag.git`; observed, not modified. |
| Runtime | Existing Python 3.10+ / FastAPI / Uvicorn. Stage 2 uses this repository; additional components undecided. |
| Project owner / legal rights holder | Decision required; organization in remote URL is not proof of legal ownership. |
| License | Decision required: SPDX identifier and rights holder before generating `LICENSE`. |
| Visibility | Not verified; no visibility change authorized. |
| Harnesses | This session uses Codex. No additional adapter or installation authorized. |
| Data | Existing static synthetic API fixtures only; no Stage 2 corpus approved. |
| Memory | No persistent end-user memory; any future persistence needs explicit requirements and approval. |
| Verification and release | Local-only checks; Docker Hub image release is a separately approved workflow, not a completed publication. |
| Authorized actions | Inspect and reconcile project-owned governance locally; preserve existing work. No feature implementation, installation, commit, push or release. |

## Product stages

**Stage 1 — reusable API:** Preserve the current read-only source catalog, health
endpoint, exact IDs, ordering, JSON/OpenAPI contracts and synthetic data. R1 adds
no database, authentication, LLM, vector database, or outbound calls.

**Stage 2 — appended Agentic RAG:** Add a reviewed, bounded question-to-evidence-to-
cited-answer or abstention slice alongside the API. Select the scenario and approve
its corpus before implementation. No model provider, embedding model, vector store,
UI, cloud or numeric evaluation threshold has been selected by this reconciliation.

## Goals and non-goals

- Restore shared governance, role boundaries, requirements templates and initial scope.
- Keep request → spec → tests → implementation → verification traceable.
- Preserve the original ten principles and a single active constitution.
- Do not reset the repository, execute the starter, import legal grants, copy upstream
  skills, impersonate official tool initialization, or implement Stage 2 now.

## Decisions required before Stage 2 implementation or release

| Decision | Needed before |
|---|---|
| Scenario, intended users and supported question boundary | Stage 2 spec approval |
| Corpus owner, classification, access, redistribution and approval record | Adding source material |
| Retrieval strategy, model/provider, dependencies, costs and evaluation thresholds | Stage 2 implementation |
| Retention/deletion/access for any index, traces or memory | Persistence |
| Official Spec Kit adoption status, harness/version and migration review | Constitution migration |
| SPDX license and rights holder; image contents redistribution clearance | License generation / public image release |
| Docker Hub namespace, image name, tags, platforms, reviewer and authorization | Image publication |

Source inputs: supplied `AI_Native_Repository_Initialization_PRD.md` v1.0,
2026-09-29, and `workshop-agentic-rag-starter`. See
[reconciliation](governance-reconciliation.md) for inspection and dispositions.
