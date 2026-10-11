# SEDA PR checkpoint — 11 October 2026

This checkpoint packages the existing F1 ingestion, F2 retrieval, F3 grounded
answer implementation and frozen workshop overlays for review. It preserves R1
and the sole active constitution in `docs/constitution.md`.

The candidate remains **PARTIAL**: historical fresh F3 acceptance was 5/6,
with one supported query returning no evidence before generation. Historical
receipts and failures are retained unchanged. A successful exposed-query
rehearsal is regression evidence, not fresh acceptance.

## Scope and dispositions

- Include the application modules, contract tests, synthetic fixture manifests,
  reviewed specs, Docker configuration, dependency locks and workshop records.
- Update README summaries to reflect implemented live supervision and partial
  acceptance rather than describing the CLI as disabled.
- Preserve frozen manifests, host guards, historical receipts and existing work.
- Exclude local `.agents/` skills and all `.specify/` changes from this PR.
  Tool adoption and duplicate constitution reconciliation remain separate work.
- Exclude model snapshots, private runtime inputs, caches and environment files.
- Defer the October 11 generation-adapter/warm-inference intake, F4, image
  publication, target-host acceptance and legal/license decisions.

## Fresh checks on this workspace

- `.venv/bin/python -m pytest -q`: exit 0; 397 passed in 13.05 seconds,
  one existing Starlette TestClient/HTTPX deprecation warning.
- `.venv/bin/python -m ruff check .`: exit 0.
- `git diff --check`: exit 0.
- `docker compose config --quiet`: exit 0.
- F1/F3 Compose configuration validation: exit 0 when supplied explicit
  approved local model, manifest, catalog and receipt paths. Initial invocations
  without those required variables failed as expected; no environment files read.
- `.venv/bin/python -B -m workshop.preflight`: exit 0; bundle/host guard and
  17 approved model files verified. This does not establish service readiness.
- Independent review reported no blocking runtime/security regressions and
  identified the stale README status, corrected in this checkpoint.

Docker daemon access failed both inside and outside the sandbox. No new container
build, `scripts/ci-local.sh`, API container smoke, live model rehearsal, Linux
worker test, fresh acceptance, vulnerability scan or target-host check ran.
Historical results are labeled historical and do not replace these unrun gates.

## Publication boundary

The destination GitHub repository is public. Historical fixture approvals permit
local repository/demo use only. After the public redistribution question was
presented in this session, the user explicitly directed: “I approved all.
(2026-10-04) proceed with a push and PR”. This current instruction authorizes
public inclusion of the existing synthetic fixtures and reports in this PR,
as well as the branch push and PR creation. The historical approval receipts
are preserved unchanged; this records the current authorization without
backdating it or expanding the original receipt.

Model uploads and Docker Hub publication are excluded. A PR is a review
checkpoint, not a release or promotion. No software/model license is granted.
