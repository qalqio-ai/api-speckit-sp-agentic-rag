# Governance reconciliation record

Date: 2026-10-02. Local-only reconciliation, not a repository reset or Stage 2
implementation. Inspected baseline: `main`, commit `683c4bf`, clean working tree.
Remote observed: `git@github.com:qalqio-ai/api-speckit-sp-agentic-rag.git`.
No commit, branch change, push, remote configuration or publication was performed.

## Inputs and authority decision

- Supplied PRD: `/Users/edmcbee/Downloads/AI_Native_Repository_Initialization_PRD.md`,
  v1.0, 2026-09-29, read in full.
- Starter: `/Users/edmcbee/Projects/workshop-agentic-rag-starter`; governance, roles,
  templates, initial demo spec, README, ignore rules and evolution/release guidance
  inspected. Starter scripts were not executed and secrets were not read.
- Supplied archive: `/Users/edmcbee/Downloads/workshop-agentic-rag-starter.zip`;
  inventory inspected and original constitution read for principle comparison.
- Target: existing instructions absent at root/ancestor paths inspected. Existing
  README, ignore rules, R1 plan/tasks, feature metadata, Compose/build and CI
  instructions inspected. No active constitution or official Spec Kit command/
  template structure was found. Existing artifacts alone do not prove installation.

Under the user's explicit reconciliation request, create project-owned governance
and make additive README/ignore updates; preserve all existing implementation work.
The sole active constitution stays in `docs/constitution.md` until separately
authorized official adoption. If an active official constitution is later established,
merge the approved ten principles there and make docs a pointer in the same change.

The starter's tool-adoption stages are not copied as product stages. Product
Stage 1 remains the reusable API; Stage 2 appends Agentic RAG in this repository.

## Path dispositions

Actions were previewed before writes. Existing tracked paths are listed individually.
Directory omissions describe prohibited imports, not deletion of existing content.

| Target path | Action | Rationale |
|---|---|---|
| `AGENTS.md` | create | Shared guidance and authoritative navigation |
| `docs/project-brief.md` | create | Supplied identity, stages and unresolved choices |
| `docs/constitution.md` | create | Sole authority; original ten principles unchanged |
| `agents/roles.md` | create | Responsibility boundaries, not implemented agents |
| `agents/skills-index.md` | create | Project navigation; no installation assertion |
| `docs/templates/prompt-requirements.md` | create | Project-owned requirements intake |
| `docs/templates/feature-spec.md` | create | Project-owned feature template outside `.specify` |
| `docs/templates/implementation-plan.md` | create | Reviewable planning inputs |
| `docs/templates/tasks.md` | create | Test-first tasks and actual result record |
| `specs/001-initial-scope/spec.md` | create | Initial scope without replacing R1 |
| `docs/evolution-path.md` | create | Product/tool-stage distinction and adoption boundary |
| `docs/release.md` | create | Local checks and approval-gated Docker Hub release |
| `docs/governance-reconciliation.md` | create | Manifest, evidence and decisions |
| `README.md` | update | Add governance links and stages; retain existing setup/contracts |
| `.gitignore` | update | Add secret/private-data patterns; retain existing rules |
| `.specify/feature.json` | preserve | Existing feature selection, unchanged |
| `app/__init__.py` | preserve | Existing package marker |
| `app/main.py` | preserve | Existing API and health implementation |
| `app/sample_data.py` | preserve | Existing synthetic configuration |
| `compose.yaml` | preserve | Existing local image build/service |
| `pyproject.toml` | preserve | Existing package/dependency configuration |
| `uv.lock` | preserve | Existing lock file |
| `scripts/ci.sh` | preserve | Existing wrapper, not rewritten or executed |
| `scripts/ci-local.sh` | preserve | Existing local check/build/cleanup workflow |
| `scripts/api_smoke.py` | preserve | Existing standalone health/contract checks |
| `tests/test_sources.py` | preserve | Existing behavioral tests |
| `docs/superpowers/plans/2026-10-02-r1-use-case-sources.md` | preserve | Historical approved planning |
| `docs/superpowers/specs/2026-10-02-r1-use-case-sources-design.md` | preserve | Historical design; later error amendment remains authoritative |
| `specs/001-list-use-case-sources/spec.md` | preserve | Existing R1 spec |
| `specs/001-list-use-case-sources/plan.md` | preserve | Historical plan, including earlier governance state |
| `specs/001-list-use-case-sources/tasks.md` | preserve | Historical implementation/verification record |
| `specs/001-list-use-case-sources/data-model.md` | preserve | Existing data model |
| `specs/001-list-use-case-sources/research.md` | preserve | Existing research |
| `specs/001-list-use-case-sources/quickstart.md` | preserve | Existing setup and validation |
| `specs/001-list-use-case-sources/contracts/sources.md` | preserve | Existing amended API contract |
| `specs/001-list-use-case-sources/checklists/requirements.md` | preserve | Existing requirements review |
| `LICENSE` | omit | No confirmed SPDX license or rights holder; decision recorded in brief |
| `.env.example` | omit | No new configuration requirement; no secret files read/copied |
| `init.sh` | omit | No starter execution or reset |
| `init-git-repo.sh` | omit | Existing Git repository preserved |
| `.specify/memory/constitution.md` | omit | No active official constitution to merge; do not fabricate internals |
| `.specify/templates/spec-template.md` | omit | Starter template adapted outside official tool tree |
| `.specify/templates/plan-template.md` | omit | Project-owned plan template used instead |
| `.specify/templates/tasks-template.md` | omit | Project-owned task template used instead |
| `specs/001-agentic-rag-demo/spec.md` | omit | Adapted into combined initial scope; do not duplicate/replace R1 |
| `docs/public-repo-checklist.md` | omit | Release gates consolidated in `docs/release.md` |
| `.agents/skills/` | omit | No upstream skill copying or new installation |
| `.github/workflows/` | omit | Local-only checks; remote CI not requested |
| `.github/copilot-instructions.md` | omit | Harness not selected |
| `CLAUDE.md` | omit | Harness not selected |
| `GEMINI.md` | omit | Harness not selected |
| `CONTRIBUTING.md` | omit | Outside-contributor process not selected |
| `SECURITY.md` | omit | Supported reporting contact/process not supplied |
| `CODE_OF_CONDUCT.md` | omit | Policy not selected |

## Validation evidence

Using verification-before-completion: results below refer to this reconciliation,
not historical claims or a remote pipeline.

| Check / command | Actual result |
|---|---|
| `git status --short --branch` before writes | Clean `main...origin/main` |
| `.venv/bin/python -m ruff check .` | Passed: all checks passed |
| `.venv/bin/python -m pytest -q` | Passed: 12 tests; one existing Starlette TestClient/HTTPX deprecation warning |
| `docker compose config --quiet` | Parsed successfully; this does not build or run an image |
| `git diff --check` | Passed for tracked edits |
| `git check-ignore` on synthetic secret/private-data paths | All nine probe paths ignored; no actual secret contents inspected |
| Local inline Python structural validation (stdlib, read-only, explicitly scoped to manifest paths and starter constitution) | Passed: 54 unique dispositions; all 23 existing tracked paths accounted for; 15 created/updated files; 37 local Markdown links resolved; headings/fences/newlines valid |
| Principle equality, additive updates and preservation checks in that validation | Passed: ten principle sections byte-identical to supplied ZIP; one active constitution; preserved files byte-identical to HEAD; README/ignore updates additive |
| Bounded proposed-file credential-pattern scan in that validation | No matches for private-key headers, GitHub token, AWS access-key or long `sk-` patterns; not a comprehensive secret audit and no secret files read |
| Trackability checks with `git check-ignore --no-index -q` | Five expected non-ignored paths returned 1: `.env.example`, initial scope, synthetic sample module, API tests, constitution |
| `rg -n` decision/placeholder inventory over brief, release, evolution, templates, skills index and initial scope | Template input cells intentionally unfilled; named maintainer, legal, corpus, architecture/evaluation, tooling and release approvals explicitly unresolved; no license grant or invented approval |
| Full Docker build/live smoke/cleanup via `scripts/ci-local.sh` | Not run during reconciliation; runtime/build configuration unchanged |
| Remote CI, RAG evaluations, vulnerability scan, Docker Hub push/pulled-image checks | Not run; no results or release claimed |
| Formal Markdown lint/render tooling | Not run; structural review only |
| Skill/dependency installation and official Spec Kit initialization | Not performed |

## Remaining decisions

Confirm project owner, legal rights holder and SPDX license; Stage 2 users/scenario;
corpus ownership, classification, access and redistribution approval; retrieval/model
architecture and dependencies; evaluation fixtures/thresholds; persistence/retention
if needed; official Spec Kit adoption and team harness/version; Docker Hub destination,
tags, platforms, release reviewer and specific publication authorization.

No legal text, approved corpus, installed tool version, RAG performance, registry
publication or repository visibility is inferred. Existing local test warnings and
floating image/dependency versions remain visible rather than silently fixed.
