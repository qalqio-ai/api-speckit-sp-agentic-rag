# Two-Stage Build: Reusable API and Agentic RAG

**Stage 1** builds the reusable API foundation and practices Spec Kit, Superpowers, local Docker checks, source review and Docker Hub publication.

**Stage 2** extends that same API into an Agentic RAG knowledge assistant, progressing from ingestion and retrieval to grounded answers, bounded model decisions, memory, tools and evaluation.

These are sequential stages. The Stage 1 API scaffold is a prerequisite, not evidence that RAG is implemented. Both stages are instructions for work to perform; this document does not claim the application code has been built or shipped.

For the SEDA two-hour slot, complete Stage 1 and Stage 2's ordinary-RAG baseline before the event. Use the Stage 2 workshop timetable for the live session. Each stage also includes a replay path; their full implementation cannot both fit into a single two-hour beginner session.

---

## Governance reconciliation — 2 October 2026

The original governance baseline was omitted from the earlier runbook. Restore it **before Stage 1 implementation**; it remains in force for Stage 2. The sequence is: project-owned bootstrap → official Spec Kit adoption → Superpowers engineering → local verification → reviewed source/image release.

### Source findings and resolutions

| Finding in the supplied pack | Reconciled decision |
|---|---|
| Initialization PRD requires AGENTS, brief, constitution, templates and initial scope before Spec Kit; runbook started with README/.gitignore | Restore the complete bootstrap manifest before Spec Kit |
| Setup guide recommends Spec Kit first, contrary to the initialization PRD and ZIP README evolution path | Use the PRD's explicit bootstrap-first sequence for this project; retire the competing setup order |
| ZIP includes .specify/memory/constitution.md and hand-written .specify/templates; PRD FR-010 forbids impersonating official setup | Preserve principles/templates in docs/ during bootstrap; let official initialization create .specify, then migrate deliberately |
| Constitution exists, but runbook never names its authority | docs/constitution.md before adoption; .specify/memory/constitution.md afterwards, with docs/constitution.md reduced to a pointer |
| AGENTS.md and agents/roles.md already exist | Preserve their guardrails and roles, add explicit context paths, stages, local verification and skill boundaries |
| ZIP has no SKILL.md files | Do not describe roles as installed skills. Maintain docs/skills-index.md; install Spec Kit and Superpowers independently |
| ZIP MIT license contains a rights-holder placeholder; PRD requires confirmed license and owner | Omit LICENSE until those decisions are confirmed; keep docs/license-decision.md |
| init-git-repo.sh checks a remote, stages all files, commits and pushes; it does not validate governance | Do not use it for bootstrap. Start locally, review governance, and configure/push a remote later |
| RAG PRD shows .specify/specs and a version-dependent workflow runner | Keep active feature artifacts in specs/; verify installed tooling before using custom workflows/converge; do not require them for this lab |
| Earlier RAG sources propose local Qdrant mode; Stage 2 runbook proposes a separate Compose service | Use the Compose service as the runbook's proposed Stage 2 architecture, record the deviation in its plan, and preserve model/storage adapters |
| Starter memory is off by default; later PRD includes TTL memory | Keep memory off through F4; enable scoped TTL/deletion only in the approved F5 slice |
| Original ten constitution principles apply to RAG and agent behavior | Preserve all ten; propose an additional local-only CI/release principle for the user's stated preference |

### Required baseline and authority

| Path | Purpose |
|---|---|
| AGENTS.md | Coding-agent entry point, linked context, test/reporting rules |
| docs/project-brief.md | Project purpose, Stage 1/Stage 2, decisions and non-goals |
| docs/constitution.md | Bootstrap constitution; pointer only after adoption |
| agents/roles.md | Application responsibility boundaries; no extra permissions |
| docs/skills-index.md | Policy versus role versus installed workflow skill inventory |
| docs/governance-map.md | Ownership, constitution migration, adoption and local governance gate |
| docs/templates/prompt-requirements.md | Request-to-testable-requirements template |
| docs/templates/feature-spec.md | Bootstrap feature template; reference after official adoption |
| specs/001-initial-scope/spec.md | Initial governance and two-stage project scope |
| README.md and .gitignore | Navigation, setup and local/private-data exclusions |
| docs/license-decision.md | Unresolved license/rights holder; no invented grant |

The accompanying **Reconciled_Governance_Starter.zip** supplies these draft files. It preserves the original ten principles and agent roles, relocates bootstrap templates outside .specify, and adds the missing brief/map/skill inventory. It contains no application implementation, vendored upstream skills, GitHub Actions, or auto-push script. For an existing repository, compare and merge changes; do not extract over existing files.

### Agent prompt to apply the baseline

```text
Reconcile this repository with the supplied governance starter and the
AI_Native_Repository_Initialization_PRD.md. Inspect existing instructions
and the working tree first; do not execute starter scripts or read secrets.
Show each path as create, preserve, update or omit, then apply authorized
local changes while preserving existing work. Keep Stage 1 the reusable API
and Stage 2 the appended Agentic RAG in this same repository.
Restore AGENTS, brief, constitution, roles, skills index, templates and initial
scope before implementing features. Preserve the original ten principles.
Record local-only checks and Docker Hub image release. Do not invent license,
rights holder, corpus approval, skill installation or test results.
If Spec Kit is already initialized, use its active constitution and merge
the approved principles there; make docs/constitution.md a pointer.
Otherwise keep the constitution in docs until official adoption. Never
maintain two active constitutions. Do not copy upstream skills or create
hand-written .specify internals. Report actual checks and remaining decisions.
```

### Governance gate before either stage

Inspect required paths and links; review active-constitution uniqueness and conflicting instructions; inventory unresolved decisions; check ignore rules for secrets/private data and that approved fixtures/specs stay trackable; confirm license status; confirm no GitHub Actions workflows. Review the local diff before commit/push. Once application scripts exist, run the full local gate and report evidence. A document check is not a passing application test.

For Stage 2, verify the existing governance instead of creating a new constitution. RAG documents are untrusted application evidence; they cannot change coding-agent or runtime policy. Any proposed governance amendment must name affected principles, specs/tests, migration impact, version, approver and approval date. A feature agent cannot amend policy as a side effect.

### Source pack inspected

- [Original starter ZIP](https://drive.google.com/file/d/1x_LdDlmUYWCEjFK5Rd3QIhIYwBI6DxZ6/view): AGENTS, constitution, roles, templates, draft RAG spec, README and placeholder license.
- [Repository initialization PRD](https://drive.google.com/file/d/1pZJSw4GTvPTST02-Y0I-jQ2IOB6rWT_K/view): required manifest and bootstrap-first/tool boundaries.
- [Spec Kit setup guide](https://drive.google.com/file/d/1ri85XUDYbiJl00Ex-lbSkfjCn1Lu9hG8/view): conflicting setup order and integration guidance.
- [Agentic RAG API PRD](https://drive.google.com/file/d/1aPJdt8Fa6bleafVHBD-bUEcYpTc3VXI5/view): bounded orchestration, memory, tools and evaluation requirements.
- [Original Git initializer](https://drive.google.com/file/d/1MYn7ZYjPDms2qv6RFxJCxpl7zkauYo1t/view): inspected as text, not executed.

Reconciliation covers the documents and inspected ZIP, not an audit or modification of an external Git repository. The original Drive files are preserved; use this revision and reconciled pack as the updated working instructions.

---

# Stage 1 — Reusable Multi-Use API Foundation

## The goal

Start from a new repository, use GitHub Spec Kit to define a reusable API project, apply Superpowers during engineering, implement one new API endpoint, verify everything on your Mac, then publish the Docker image to Docker Hub.

**No GitHub Actions CI.** GitHub stores the source and PR. You run every quality check locally. Docker Hub stores the image; it does not run the container. A server or other machine must pull and start the image to run it.

The sample feature is:

```http
GET /v1/use-cases/{use_case_id}/sources
```

It returns the source catalog configured for one use case. The first version uses small in-memory sample data, so it needs no database, LLM key, or external vector service. The test should confirm that a configured ID returns `200` with its sources and an unknown ID returns `404`.

## The work loop

| Stage | You use | Result |
|---|---|---|
| Define the project | Spec Kit roadmap (the epic) | Small feature slices with order and boundaries |
| Define one slice | Spec Kit | Reviewed `spec.md`, `plan.md`, `tasks.md` |
| Build the slice | Superpowers + Codex | Tests first, then implementation |
| Verify | Local scripts + Docker Desktop | Passing checks and running container |
| Ship | GitHub source PR, then Docker Hub | Reviewed source and versioned image |

Keep the epic roadmap short. Give each buildable slice its own Spec Kit cycle.

---

## Before the two-hour session

Install and sign in to these once on the Mac:

- Git and GitHub CLI (`gh auth login`)
- Docker Desktop, started and showing a running engine
- Homebrew and `uv`
- Codex CLI
- Docker Hub account and a repository, such as `foundational-multiuse-api`

Install `uv` if needed:

```bash
brew install uv
uv --version
```

Install Spec Kit:

```bash
uv tool install specify-cli
specify version
uv python install 3.12
```

In Codex CLI, open `/plugins`, search for **Superpowers**, select **Install Plugin**, then restart Codex. In Codex App, install it from **Plugins**. Check the plugin is listed as installed before the lab.

---

## 1. Create the local repository and restore governance

In Terminal:

```bash
mkdir foundational-multiuse-api
cd foundational-multiuse-api
git init -b main
```

Copy the contents of `reconciled-governance-starter/` from the accompanying ZIP into this empty directory, including `.gitignore`. For an existing repository, inspect its working tree and compare files in a branch; apply selected diffs rather than copying over existing instructions.

Use the governance prompt above. Review `AGENTS.md`, `docs/project-brief.md`, `docs/constitution.md`, `agents/roles.md`, `docs/skills-index.md`, templates and `specs/001-initial-scope/spec.md`. Run the governance gate, record open decisions, and inspect the diff before the local baseline commit:

```bash
git status --short
git add README.md .gitignore AGENTS.md agents docs specs
git diff --cached --stat
git diff --cached
git commit -m "chore: establish project governance baseline"
```

Configure GitHub only after the baseline review, when ready to publish source:

```bash
export GITHUB_OWNER="your-github-owner"
gh repo create "$GITHUB_OWNER/foundational-multiuse-api" --private --source=. --remote=origin --push
```

For an existing remote, clone it first or inspect the configured origin rather than creating a second repository. Do not use the starter's `init-git-repo.sh`: it automatically stages, commits and pushes without a governance gate. Do not add GitHub Actions workflows.

---

## 2. Set up Spec Kit in this project

After the governance baseline review, inspect `specify init --help` and existing managed paths. Preserve the baseline; do not add `--force` without reviewing conflicts. Still in the repository folder:

```bash
specify init --here --integration codex
specify integration status
find .agents/skills -path '*/SKILL.md' -print | sort
```

The `find` command should list Spec Kit skills, including `speckit-specify`, `speckit-plan`, `speckit-tasks`, and `speckit-implement`. Codex invokes these as `$speckit-...` skills. If they are not listed, stop and fix the integration before continuing. Restart Codex from this repository folder.

Before generating the epic, migrate the approved `docs/constitution.md` content into `.specify/memory/constitution.md`, compare the complete principles, and turn `docs/constitution.md` into the pointer shown in `docs/governance-map.md`. Run the installed constitution skill to reconcile this baseline, not invent a replacement. Review templates and agent integration files. Keep feature artifacts under `specs/`.

Create the feature branch before writing the roadmap or source code:

```bash
git switch -c feat/use-case-source-catalog
```

### The project epic

Spec Kit's “spec of specs” is a roadmap method, not a separate command. In Codex, ask the agent to draft that roadmap before application code:

```text
Use the Spec Kit spec-of-specs approach. Do not write application code yet.
The epic is: build a reusable, multi-use FastAPI service. A use case selects
configuration and data while the service keeps a consistent API contract,
validation, errors, logging, and deployment path. Keep the first release small.
Create a roadmap at specs/reusable-api/roadmap.md with independently testable
slices, clear in-scope and deferred boundaries, dependencies, and status.
Propose the slices first and wait for me to approve the roadmap before writing it.
```

A good small roadmap might look like this:

| ID | Slice | First release boundary | Depends on |
|---|---|---|---|
| R1 | Source catalog MVP | FastAPI app, health route, two configured use cases, source catalog endpoint, local tests | — |
| R2 | Provider adapters | Replace the in-memory catalog behind a narrow adapter | R1 |
| R3 | Access and persistence | Add only after identity and storage requirements are known | R1 |
| R4 | Image release | Local Docker build, API smoke test, tagged Docker Hub push | R1 |

Keep later features such as authentication, tenant isolation, persistent storage, LLM providers, and a web UI out of this first exercise. Add them to the roadmap as future slices if they belong in the epic.

---

## 3. Specify the sample API feature

Choose R1 as the first implementation slice after the governance baseline. The repository contains documentation but no application code. In Codex, run the Spec Kit skills in the chat, not in Terminal:

```text
$speckit-specify
```

Describe this feature:

```text
Implement roadmap slice R1 from specs/reusable-api/roadmap.md.
Add GET /v1/use-cases/{use_case_id}/sources. For a configured use case, return `{"use_case_id":"...","sources":[{"id":"...","title":"..."}]}`. Return HTTP 404 with `{"detail":{"code":"unknown_use_case"}}` for an unknown use case. Keep this read-only and in memory for the first version. Use Python 3.12, FastAPI, and uv. Include a Dockerfile, Docker Compose config, `.gitignore`, Ruff, pytest, and a `scripts/api_smoke.py` check. Configure the local image name as `foundational-multiuse-api:local`; make the API listen on `0.0.0.0` inside its container. Do not add authentication, a database, an LLM, or a vector database. Include observable acceptance criteria and tests. Do not write implementation code while clarifying requirements.
```

Review the spec. Then run each next step and inspect its files before moving on:

```text
$speckit-clarify
$speckit-plan
$speckit-tasks
$speckit-analyze
```

Use the spelling Codex exposes in the skill list. Current Spec Kit documents Codex skills as `$speckit-<command>`; if a skill is absent, inspect `.agents/skills` rather than guessing a slash-command prefix.

**Human checkpoint:** approve the endpoint contract, error response, fixture shape, and task list. Ask Codex to stop for review at the end of each Spec Kit stage.

---

## 4. Apply Superpowers to the build

Superpowers is a development workflow for the coding agent, not an API dependency. In the same Codex conversation, tell the agent:

```text
Follow the relevant Superpowers skills for this implementation. Use test-driven
development: write the failing API tests first, run them and show the failure,
then implement the smallest change, rerun the tests, and review the diff. Follow
the approved Spec Kit tasks and plan. Do not expand the feature scope.
```

For this slice, the work should follow this order:

1. Add tests for a configured use case and an unknown use case.
2. Run the tests and confirm the new test fails for the expected reason.
3. Implement the route and response model.
4. Run formatting/lint and the full Python test suite.
5. Ask for a code review of the diff; fix real findings and rerun checks.

Use Superpowers skills when they apply: `brainstorming` for design, `test-driven-development` for tests first, `systematic-debugging` for failures, and `verification-before-completion` before declaring the feature done. Do not treat skill names as universal slash commands. Codex can discover them from the installed plugin; you can also refer to them by name in your prompt.

---

## 5. Run the local quality gate

Have the agent create a single local script named `scripts/ci-local.sh` that:

1. Runs Ruff on the project.
2. Runs all Python tests.
3. Builds the Docker image with Docker Compose.
4. Starts the API, waits for `/health`, then tests the new endpoint and its 404 case.
5. Stops and removes the test container even if a check fails.

Review the script before running it. It must not call GitHub Actions or push an image. Run it from the repository root:

```bash
bash scripts/ci-local.sh
```

Also inspect Docker and test output if the script exits nonzero. Do not continue to publish an image until the local gate passes.

A useful manual fallback when Docker Compose is already defined is:

```bash
uv run ruff check .
uv run pytest
docker compose up --build -d
python scripts/api_smoke.py
docker compose down
```

The smoke test should wait for `/health` before calling the new API route. An immediate `curl` can race the container startup.

---

## 6. Push the source change, without GitHub CI

The feature branch was created before writing the roadmap or application code. Before opening a PR:

```bash
git diff --check
git status --short
git diff
bash scripts/ci-local.sh
```

After reviewing `git status --short`, stage the intended project files. The `.gitignore` created at setup excludes the virtual environment and local secrets:

```bash
git add -A
git commit -m "feat(api): add use-case source catalog"
git push -u origin feat/use-case-source-catalog
gh pr create --base main --fill
```

Review and merge the PR manually after the local gate passes. Do not wait for GitHub Actions: this project intentionally has no GitHub CI workflow. After merge:

```bash
git switch main
git pull --ff-only
bash scripts/ci-local.sh
```

Run the gate on the exact `main` commit you intend to publish.

---

## 7. Publish the verified image to Docker Hub

Create the Docker Hub repository before this step. Set the namespace to your Docker Hub username, then tag the already-built local image:

```bash
export DOCKERHUB_USER="your-dockerhub-username"
export IMAGE_TAG="0.1.0"
docker login
docker tag foundational-multiuse-api:local "$DOCKERHUB_USER/foundational-multiuse-api:$IMAGE_TAG"
docker push "$DOCKERHUB_USER/foundational-multiuse-api:$IMAGE_TAG"
```

Use a new version tag for each release. Avoid using `latest` as the only tag. Confirm the version appears on Docker Hub's **Tags** page.

On another Docker machine, run the published image with:

```bash
docker pull "$DOCKERHUB_USER/foundational-multiuse-api:$IMAGE_TAG"
docker run --rm -p 8000:8000 "$DOCKERHUB_USER/foundational-multiuse-api:$IMAGE_TAG"
```

Then test `http://127.0.0.1:8000/health`. A production deployment needs a target server or hosting service and its environment configuration; Docker Hub only stores and distributes the image.

---

## Stage 1 standalone practice schedule

Do the software installs, logins, Docker Hub repository creation, and a baseline Docker check **before** the workshop. The session is for practicing the workflow, not debugging account setup.

| Minutes | Activity | Checkpoint |
|---|---|---|
| 0–10 | Explain the API goal and what “local-only CI” means | Everyone knows there is no GitHub Actions gate |
| 10–25 | Inspect prepared governance and initialize/verify Spec Kit | One active constitution; Codex lists expected skills |
| 25–40 | Draft and approve the epic roadmap | Four small slices with clear boundaries |
| 40–55 | Specify R1 and review plan/tasks | API contract and acceptance criteria approved |
| 55–85 | Implement with Superpowers and tests first | New endpoint tests pass |
| 85–100 | Run local checks and Docker smoke test | Running container returns 200 and 404 as expected |
| 100–112 | Push source branch and open PR | PR is reviewable; no GitHub CI expected |
| 112–120 | Merge if ready, tag and push image | Docker Hub shows the versioned image |

If setup or tests run long, finish the local gate and Docker Hub push after the session rather than skipping verification.

## What “done” looks like

- The repo has a reviewed epic roadmap and a completed feature spec, plan, and task list.
- The new route has tests for success and unknown use case.
- Ruff, Python tests, Docker build, and API smoke checks pass locally.
- The source change is reviewed and merged without GitHub Actions CI.
- A versioned image is visible in Docker Hub and can be pulled and run.

## Official references

- [Spec Kit quick start](https://github.com/github/spec-kit)
- [Spec Kit Codex integration and invocation](https://github.com/github/spec-kit/blob/main/docs/reference/integrations.md)
- [Spec Kit “spec of specs” roadmap guidance](https://github.com/github/spec-kit/blob/main/docs/concepts/spec-of-specs.md)
- [Superpowers installation](https://github.com/obra/superpowers)
- [Docker Hub: push an image](https://docs.docker.com/docker-hub/repos/manage/hub-images/push/)


---

# Stage 2 — Agentic RAG: Foundation to Advanced

## Purpose and scope

Build a reusable Workshop Knowledge Assistant and understand how each layer works. The API exposes the assistant; the learning objective is the retrieval, grounding, agent decisions, memory, tools, and evidence behind its answers.

This is a build guide and proposed contract, not a claim that these features are implemented. Use Spec Kit to record each feature's requirements. Use Superpowers for design, implementation planning, tests first, debugging, review, and verification. Run all quality checks locally with Docker Desktop. GitHub stores source and PRs; Docker Hub distributes the application image. No GitHub Actions CI.

There are two paths:

- **Replay from an empty repository:** build the foundation and advanced slices in order, at your own pace. This is longer than a two-hour workshop.
- **Two-hour workshop:** start with an installed, tested foundation and sample corpus. Learn the foundation by inspecting it, then implement one bounded agentic feature, evaluate it, and rehearse shipping.

## The use case we build

Use three short fictional documents: a product guide, a return policy, and a troubleshooting guide. Add a second use case with a separate corpus to prove retrieval isolation.

Example policy fixture: unopened items can be returned within 30 days with a receipt. The fixture contains no international shipping policy. These are invented lab facts, not company policies.

The final assistant should demonstrate:

1. “Can I return an unopened item after 20 days?” It retrieves the return policy and answers with citations.
2. “What if I lost it?” Session memory resolves “it” to the receipt; retrieved policy supplies the answer.
3. “What about international shipping?” It reports insufficient evidence.
4. “The device won't start.” It searches, may refine the query once when initial evidence is insufficient, and exposes the search trace.
5. “What is 15% off 1,200?” It may select an allowlisted calculator and return 1,020, clearly identifying the calculation as tool-derived.

Document retrieval supplies knowledge. Session memory supplies conversational context. A tool supplies a validated operation. Each has a distinct source and trust boundary.

## Foundation to advanced learning ladder

| Slice | What you learn and build | Visible proof | Tests before implementation |
|---|---|---|---|
| F0: Repository and API | Constitution, agent instructions, FastAPI, settings, health, local test harness | App starts and health responds | Health contract and invalid requests |
| F1: Ingestion | Parse documents, chunk text, embed chunks, index in Qdrant with source metadata | Inspect chunk text, IDs, vectors and source references | Empty input, deterministic IDs, repeated ingestion, source metadata |
| F2: Retrieval | Embed the question, vector search, apply use-case filter, return top-k evidence | A paraphrased question retrieves the expected policy | Expected source, top-k limit, cross-corpus isolation, no-match behavior |
| F3: Grounded RAG | Put retrieved evidence into a model context and generate an answer with citations | Supported answer and insufficient-evidence response | Valid citation IDs, unsupported query, malformed model response |
| F4: Bounded agent loop | Model selects search, one query refinement, allowed tool, or final response | Trace shows an actual action decision and capped search retry | Search budget, stopping behavior, unavailable tools, insufficient evidence after retry |
| F5: Session memory | Retain short-lived conversation context, scoped to session and use case | Follow-up resolves a reference without crossing sessions | Session isolation, expiry, memory reset, use-case isolation |
| F6: Tool use | Validate structured tool arguments and allowlist read-only functions | Calculator runs with typed arguments and observable result | Unknown tool, invalid arguments, timeout, correct calculation |
| F7: Evaluation and release | Evaluate retrieval and answers separately, inspect traces, package and publish | Local report plus a pullable Docker image | Corpus cases, regressions, readiness failures, container smoke |

Do not label a fixed “search then generate” sequence as agentic. For F4, the model must select among defined actions, while the application enforces action limits. The model cannot override those limits.

## Proposed architecture

| Component | Responsibility |
|---|---|
| FastAPI | Validate requests and expose stable contracts |
| Ingestion service | Chunk documents, retain provenance, upsert vectors |
| Embedding adapter | Encode document chunks and questions with the same compatible model |
| Qdrant | Store vectors and metadata; retrieve evidence within the selected use case |
| Retriever | Return chunk text, source ID, chunk ID and retrieval score |
| Model adapter | Generate structured actions and grounded answers |
| Agent orchestrator | Enforce budgets, validate actions, retry retrieval at most once |
| Session store | Hold short-lived summaries separately from source evidence |
| Tool registry | Execute allowlisted, validated read-only functions |
| Evaluator | Check retrieval, grounding, boundaries, budgets and failure handling |

Use Python 3.12, FastAPI, uv, pytest, Ruff, and Docker Compose. Run Qdrant as a separate Compose service with a named volume. Use a model adapter so the workshop can exercise a local or hosted model without changing the orchestration contract.

Select and verify the exact embedding/model dependencies during planning on the Intel Mac and Linux container. Do not copy a Linux-only dependency export into macOS requirements. Download model weights before the workshop if using local models.

### Live mode and deterministic test mode

- Live mode uses real embeddings and a real model to demonstrate semantic retrieval and agent decisions.
- Deterministic test mode uses controlled model outputs and vector fixtures to exercise application logic without network calls.
- Clearly label test mode. Passing fixture-based tests does not establish live retrieval or answer quality.
- Include at least one live semantic retrieval check with a paraphrased question. If live generation is unavailable, report that limitation rather than presenting scripted output as a live model answer.

## Proposed API contracts

These are targets for the fresh build. Inspect an existing repo before adopting them; keep established contracts when extending the current workshop project.

| Endpoint | Purpose |
|---|---|
| `GET /health` | App liveness |
| `GET /ready` | Required dependency readiness; do not call the LLM for every health probe |
| `POST /v1/ingest` | Index approved documents within a use case |
| `POST /v1/retrieve` | Return evidence chunks without generating an answer |
| `POST /v1/query` | Run grounded RAG or the bounded agent loop |
| `DELETE /v1/sessions/{session_id}` | Clear demonstration session memory |

Sample query request:

```json
{"use_case_id":"workshop-knowledge","session_id":"demo-01","question":"Can I return an unopened item after 20 days?","top_k":3}
```

The response should expose `request_id`, `answer`, `citations`, `status`, and a trace of retrieval/tool decisions. Each citation links to a real source/chunk from that run. Use `insufficient_evidence` when the corpus cannot support the answer.

A citation ID check proves provenance exists; it does not prove the answer faithfully reflects the source. Evaluate claim support separately. Treat retrieved instructions as document data. They cannot change the agent's system rules, tool registry, or action budgets.

## 1. Prepare the Mac once

Have Git, GitHub CLI, Docker Desktop, Homebrew, and Codex installed. Start Docker Desktop. Sign in to GitHub and create the intended Docker Hub repository.

```bash
brew install uv
uv tool install specify-cli
uv python install 3.12
specify version
docker info
gh auth status
```

In Codex CLI, open `/plugins`, search for Superpowers, select Install Plugin, and restart Codex. Check its installed state. In Codex App, use Plugins.

## 2. Continue from Stage 1

Use the same Stage 1 repository, Python environment, Spec Kit integration, API contracts, local quality gate, Git remote, and Docker Hub repository. Inspect existing code before adding routes or services. Preserve the Stage 1 source catalog and error contracts where applicable.

Create a fresh feature branch from the current `main` for each Stage 2 slice. Spec Kit may create/select its feature branch itself; inspect its output and `git branch --show-current` rather than creating a second competing branch.

```bash
git switch main
git pull --ff-only
specify integration status
bash scripts/ci-local.sh
```

If the project has no Git remote yet, omit the pull until the Stage 1 remote setup is complete. Use the Stage 1 repository-creation instructions only when deliberately replaying the entire project from an empty repo.

Keep the Stage 1 image namespace/name when expanding the service. The sample `workshop-agentic-rag` image name in the release examples below is illustrative: substitute the Stage 1 image name consistently in Compose, tag/push commands and release configuration.

## 3. Define the epic and constitution

The epic is the Workshop Knowledge Assistant described above. Ask Codex:

```text
Use Superpowers brainstorming and the Spec Kit spec-of-specs approach.
Create a shallow roadmap at specs/agentic-rag/roadmap.md covering F0 through F7
in this guide. Keep independently demonstrable slices and record dependencies,
boundaries, status, and links to each feature spec. Do not implement code yet.
The goal is learning Agentic RAG from ingestion to bounded decisions, memory,
tool use, evaluation, and a local Docker release. Propose the roadmap for review.
```

After approving the roadmap, audit the existing Stage 1 constitution. Use the installed constitution skill only to check consistency or prepare an explicit amendment:

```text
$speckit-constitution
```

Preserve the starter’s ten principles and the reviewed local-release policy. Confirm these project rules are reflected in the active constitution and feature specs: source-backed answers; explicit insufficient evidence; validated actions; allowlisted tools; fixed runtime budgets; corpus/session isolation; retrieved text treated as untrusted data; tests without external services; no secrets in source or traces; all CI checks local.

## 4. Build the foundation one slice at a time

For each slice: specify, clarify where needed, plan, tasks, analyze, review, then implement with Superpowers. Do not ask the agent to implement F0–F7 in one prompt.

Example F1 specification prompt in Codex:

```text
$speckit-specify Build F1 from specs/agentic-rag/roadmap.md. Ingest approved
text documents, preserve source IDs and titles, chunk and embed text, and upsert
chunks into Qdrant with use_case_id metadata. Re-ingestion must avoid duplicate
chunks and reconcile removed chunks from that source. Reject empty inputs.
Provide inspection output and tests. No generation or agent loop in this slice.
```

Then invoke the installed skills individually:

```text
$speckit-clarify
$speckit-plan
$speckit-tasks
$speckit-analyze
```

For F2, specify semantic search and a mandatory use-case filter; prove a paraphrased question retrieves the expected source. For F3, specify grounded generation, citation provenance, and unsupported-query handling. Only proceed to the agent loop after ordinary RAG works.

Do not pick a universal relevance-score threshold by guesswork. Calibrate any threshold against the chosen model, distance metric and corpus evaluation cases.

## 5. Make the system agentic: a complete feature cycle

Use F4 as the workshop's plan-build-test-ship feature, with F0–F3 prepared and verified.

**Plan in Codex:**

```text
Use Superpowers brainstorming to design F4. The model may select retrieve,
refine-query, an allowlisted read-only tool, or answer. Cap each request at two
retrieval searches total, including at most one refinement; one tool invocation;
and four model decisions. Stop at budget exhaustion with an explicit result.
Apply limits in application code, not just in the prompt. Preserve F3 grounding
and citations. Define the decision schema and failure behavior before coding.
```

After design review, create/review the Spec Kit spec, plan and tasks. Ask Superpowers writing-plans to make a concise executable checklist from those approved artifacts. The Spec Kit spec remains the requirements source. Review the resulting implementation plan and choose inline execution.

**Build with Superpowers:**

```text
Use executing-plans and test-driven-development for the approved F4 plan.
Write a failing test for one behavior, run it, implement the smallest change,
then rerun it and the suite. Record meaningful decisions and evidence. Use
systematic-debugging if a failure is unexpected. Keep the feature scope fixed.
```

The first test can require exactly one refined search when the initial evidence is insufficient. A second test must prove no third search occurs when the refinement also fails. Also test a malformed model action and a prompt-injection document.

**Local test checkpoints:**

```bash
uv run pytest tests/test_agent.py -q
uv run pytest
uv run ruff check .
bash scripts/ci-local.sh
```

The focused test must first fail because the behavior is missing, rather than because the test environment is broken. Only claim success after reading fresh verification output. Use Superpowers code review before merging; evaluate findings and rerun affected checks.

## 6. Add memory and tools after the loop

F5 uses a short-lived session summary to resolve follow-ups. It never substitutes that summary for source evidence. Scope memory to both session ID and use case, support clearing it, define expiry, and document that an in-process demo store resets on restart. Persistent user memory requires separate design and retention decisions.

F6 adds a calculator through a typed schema and allowlist. Do not evaluate arbitrary strings with `eval`. Test unknown tool names, bad arguments, timeouts, and the calculation. Keep tool-derived facts distinct from corpus-derived facts in the response. No consequential actions in the lab.

Advanced follow-ons after F0–F7: hybrid dense/sparse retrieval, reranking, multi-document evidence synthesis, versioned corpus updates/deletion, persistent session storage, authorization, evaluation automation and load testing. Measure improvement against the same corpus cases before adding complexity.

## 7. Evaluate RAG and agent behavior

Maintain a small evaluation set, with expected source IDs and claims defined before evaluating the model:

| Case | What counts as success |
|---|---|
| Supported policy question | Relevant policy is retrieved; answer claims match it |
| Paraphrased question | Semantic search finds the expected evidence |
| Unsupported shipping question | Explicit insufficient evidence; no invented policy |
| Ambiguous follow-up | Session reference resolves; answer still uses source evidence |
| Weak first search | At most one refinement; inspectable query and evidence trace |
| Cross-use-case question | No chunks or session context from another use case |
| Calculator request | Validated tool invocation and correct result |
| Injection embedded in a source | Source text cannot change action rules or expose secrets |
| Dependency/model failure | Clear failure response, controlled timeout, no retry explosion |

Separate retrieval quality from answer quality and control-flow correctness. Test citation IDs exactly; assess generated claims against evidence rather than requiring identical prose. Fixture-based tests cover deterministic application behavior; live evaluation covers model behavior.

Traces should include request ID, action names, retrieved source/chunk IDs, tool status, latency, and budget usage. Avoid recording secrets and raw user/document text by default.

## 8. Verify and ship locally

Have the agent provide `scripts/ci-local.sh`, `scripts/rag_smoke.py`, and a documented live evaluation command. The local gate must run lint/tests, build the API image, start API and Qdrant, wait for readiness, ingest the corpus, query it, verify citations/unsupported behavior/budgets, and stop test containers even on failure. Preserve development data volumes.

```bash
bash scripts/ci-local.sh
uv run python scripts/rag_smoke.py --mode mock
uv run python scripts/rag_smoke.py --mode live
```

These script names and options are deliverables to implement, not existing commands in a fresh repository. Live mode needs the configured model and embeddings. If it cannot run, record exactly what was tested and what remains unverified.

After local verification and review, push the source branch and open a PR. No GitHub Actions workflow is required. Merge manually, sync `main`, and verify the release commit locally before pushing its image.

Configure Compose to build the application as `workshop-agentic-rag:local`:

```bash
export DOCKERHUB_USER="your-dockerhub-username"
export IMAGE_TAG="0.1.0"
docker login
docker tag workshop-agentic-rag:local "$DOCKERHUB_USER/workshop-agentic-rag:$IMAGE_TAG"
docker push "$DOCKERHUB_USER/workshop-agentic-rag:$IMAGE_TAG"
```

Ship a `compose.release.yaml` that reads `APP_IMAGE`, defines the required Qdrant service/volume, and receives runtime model configuration separately. Rehearse pulling and running the published image:

```bash
export APP_IMAGE="$DOCKERHUB_USER/workshop-agentic-rag:$IMAGE_TAG"
docker compose -f compose.release.yaml pull
docker compose -f compose.release.yaml up -d
uv run python scripts/rag_smoke.py --mode live
```

Docker Hub stores the app image. It does not include the indexed corpus, Qdrant volume, credentials, or a running deployment. Provision those on the target machine, ingest its corpus, and verify readiness. Record the source commit and image digest for the release.

## Two-hour workshop schedule

Prepare F0–F3, model/embedding downloads, sample corpus, dependencies, accounts, and a passing local baseline before the session. Participants inspect the foundation and implement F4. F5/F6 are demonstrated from a clearly identified prepared advanced branch and explored after the session.

| Minutes | Segment | Participant outcome |
|---|---|---|
| 0–15 | Foundation: chunking, embeddings, vector search, grounding | Inspect actual chunks, retrieval results and answer citations |
| 15–25 | Agent decisions, budgets, memory and tools | Distinguish ordinary RAG, agent loop, memory and tool results |
| 25–30 | Opening Q&A and readiness check | Resolve conceptual questions before the lab |
| 30–40 | Inspect repo, constitution, roadmap and prepared F0–F3 | Run a supported and an unsupported baseline query |
| 40–55 | Specify and plan F4 with Spec Kit and Superpowers | Review a bounded agent-loop feature |
| 55–80 | Implement F4 with tests first | See a failing test, implement retry/budget behavior, run suite |
| 80–90 | Trace agent decisions and query refinement | Inspect action decisions, queries and capped searches |
| 90–100 | Prepared F5/F6 demonstration | Observe follow-up memory and a validated calculator call |
| 100–108 | Evaluation and local Docker gate | Test unsupported questions, isolation and budgets |
| 108–115 | Release rehearsal | Tag/push image if ready; inspect release Compose configuration |
| 115–120 | Wrap and next exercises | Choose a memory/tool or retrieval-quality extension |

Opening and Q&A: 30 minutes. Practical block: 85 minutes. Wrap: 5 minutes. Do not omit verification to fit the slot. Full blank-repo replay and advanced implementation are self-paced work beyond this session.

## Completion evidence

The final demonstration shows real semantic retrieval, source-grounded answers, insufficient-evidence handling, bounded model-selected actions, session isolation, a validated read-only tool, and an inspectable evaluation report. Report prepared/mock/live components explicitly. A health endpoint, source catalog, or Docker build alone does not demonstrate Agentic RAG.

## Sources and learning references

- [RAG research paper: Lewis et al.](https://arxiv.org/abs/2005.11401)
- [Qdrant local Docker quickstart](https://qdrant.tech/documentation/quickstart/)
- [Qdrant semantic search fundamentals](https://qdrant.tech/documentation/tutorials/search-beginners/)
- [Spec Kit](https://github.com/github/spec-kit)
- [Spec Kit Codex integration](https://github.com/github/spec-kit/blob/main/docs/reference/integrations.md)
- [Spec Kit roadmap method](https://github.com/github/spec-kit/blob/main/docs/concepts/spec-of-specs.md)
- [Superpowers](https://github.com/obra/superpowers)
- [Docker Hub image push](https://docs.docker.com/docker-hub/repos/manage/hub-images/push/)
