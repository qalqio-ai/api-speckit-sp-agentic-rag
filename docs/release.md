# Local checks and Docker Hub image release

## Local-only verification

From an already prepared environment, run:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest -q
docker compose config --quiet
./scripts/ci-local.sh
```

The CI script builds a temporary Compose service, waits up to 60 seconds for
health, checks exact configured/unknown responses, and removes its container
and network on exit. It retains built images. These are local checks, not a
remote CI workflow or a Docker Hub release. Dependency installation and Docker
access may require separate permissions. Do not execute unreviewed starter scripts.

For an already-running API:

```bash
python scripts/api_smoke.py
```

For persistent local development, the existing `compose.yaml` supports
`docker compose up --build -d` and `docker compose down`. That is not publication.
Record the command, exit status, date, revision, warnings and environment for
every release candidate. Historical checks are not proof for a changed artifact.

## Docker Hub release gates — not yet performed

Docker Hub image publication is the release workflow to prepare, not a claim
that an image exists there. Namespace, image name, tags, target platforms,
rights holder, license and authorization remain undecided.

Before publishing, the human release reviewer must approve:

- Legal rights and redistribution of application, dependencies and image contents;
  no license is inferred from the GitHub organization or starter license.
- Corpus/source redistribution and classification, if any source material is included.
- Image contents excluding secrets, local environments and private data; review
  the build context and layers without exposing secret values.
- An immutable version tag tied to a reviewed commit and test record, platform list,
  vulnerability review and acceptance of findings. No scan is claimed here.
- Exact Docker Hub destination and explicit authority to authenticate and push.
  Authenticate separately using approved tooling; never put credentials in docs.

After those approvals, an operator may use the following command outline with
explicitly supplied environment variables (no destination defaults):

```bash
: "${DOCKERHUB_NAMESPACE:?Set the approved namespace}"
: "${DOCKERHUB_IMAGE:?Set the approved image name}"
: "${RELEASE_TAG:?Set the approved immutable version tag}"
: "${LOCAL_IMAGE_ID:?Set the verified image ID from the approved build}"
docker tag "$LOCAL_IMAGE_ID" "$DOCKERHUB_NAMESPACE/$DOCKERHUB_IMAGE:$RELEASE_TAG"
docker push "$DOCKERHUB_NAMESPACE/$DOCKERHUB_IMAGE:$RELEASE_TAG"
```

These commands have **not** been executed. Avoid a `latest` tag unless separately
approved. Record published digest, commit, tag, platform, reviewer, actual checks,
scan findings and smoke results for the pulled image. Rollback uses an earlier
approved digest; do not silently overwrite release tags or claim reproducibility
from currently floating dependency/base-image constraints.

## Release record

Status: **not released by this reconciliation; external registry state not checked**.
No Docker Hub authentication, push, remote CI, release scan or pulled-image test
was performed. See [reconciliation](governance-reconciliation.md) for actual local
checks. GitHub visibility/security settings have not been inspected or changed.
