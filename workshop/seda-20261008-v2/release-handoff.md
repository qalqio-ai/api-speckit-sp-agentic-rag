# Local image handoff and reproducibility

All CI/evaluation runs locally. No GitHub Actions or Docker Hub automated build was added. No commit, push or publication was executed. No registry destination/remote tag is inferred from the repository organization.

Executed application rebuild: `python -B -m workshop.build`. The script copied only current application code, three serialization contracts and reviewed workshop code into an isolated temporary context, then ran a fresh `docker build --no-cache --pull=false --network=none --platform linux/amd64`. Dependency layers came from retained image `sha256:139a1f015734889f0bef40f66a4db65a1addc1a3dc5dc41f6bc82fe9d936757f`. This is a fresh application rebuild, not a clean dependency reinstall. The actual Dockerfile, context hashes, command, exit status and output image are in `../seda-20261008/evidence/build.json`/build.log.

Initial locally versioned tag: `seda-workshop:20261008-rc1`, image `sha256:f1dc063ca46a05ccce548121c1f530eb1d7ce2edc87dc27db1f32d3ba2cdf00a`. Runtime helper/fixture/model bind mounts are independently frozen; an image ID alone does not identify the full candidate. A later rehearsal image/version must be recorded separately without retagging the original checkpoint.

## Rebuild instructions

Use the complete approved local dependency image and repository state/hash manifest, not an unreviewed floating package install. `workshop/build.py` refuses to overwrite its original evidence. For a later rebuild, version the script/tag/evidence destination first. No source/model corpus is placed in the image. Model snapshots and approvals remain external read-only inputs.

A clean rebuild of dependency layers is described by the original pinned `Dockerfile.f3` and `requirements.f1.lock`, but was not executed in this finalization. It requires approved network/package acquisition or a verified offline wheel cache. Do not claim that reproducibility includes a freshly installed dependency stack merely because application code was rebuilt.

## Target-machine launch

The target machine must have the approved repository/bundle, compatible tested Linux amd64 Docker runtime, both exact model snapshots and source/access/retention approvals. Apple Silicon and a different target host remain untested. Copy/use only within approved local-demo access/redistribution; do not publish the synthetic corpus or infer an application/model license grant.

There is presently **no published image to pull** from this work. An offline handoff can be prepared with `docker image save` and loaded with `docker image load`, but no archive transfer/load was executed here and compressed/archive size is unmeasured. Verify the loaded image ID against the receipt before running it.

After a separately authorized registry publication with a recorded immutable digest, these conditional commands would apply:

```bash
: "${SEDA_APPROVED_IMAGE:?Explicit approved registry image@sha256 digest required}"
docker pull --platform linux/amd64 "$SEDA_APPROVED_IMAGE"
docker image inspect "$SEDA_APPROVED_IMAGE" --format '{{.Id}}'
.venv/bin/python -B -m workshop.preflight
.venv/bin/python -B -m workshop.launch --output workshop/seda-20261008-v2/evidence/target-rehearsal-1.json
```

Before guarded launch, require the pulled local image ID to equal `launch-guard-v1.json.image_id`; the guard requires the tested image, not an arbitrary registry tag. The commands are prepared instructions, **not executed target/pull verification**. No credentials belong in command arguments, environment dumps, logs or presentation material. Use actual local smoke/readiness, evidence/citation, unsupported-query and cleanup results before claiming target readiness.

## Recovery

Keep the old image digest, source/model snapshots and `SEDA-F0-F3-constrained-v1-fallback` manifest. Do not prune shared Docker layers/volumes during recovery. Use unique owned run labels and exact resource identities for teardown, then verify independent absence. Retained recordings must be explicitly labeled and must disclose failed/unverified acceptance gates.

The versioned **bundle** is rc2; its runtime **image** remains rc1 because the changed threshold/catalog/session/launch guard are read-only host inputs, not a new application image. `/workshop/session.py` inside rc1 is unused: runtime explicitly executes the frozen `/input/session.py`. Use image + bundle + launch-guard identities together.

## Exact context replay (prepared, not executed)

The original temporary context was deleted by the build helper. Its exact files remain in the tested image, including the unused older session helper. Reconstruct the reviewed bytes from that local image, then verify every original context hash before a new build. These commands do not install packages or obtain models. The fixed container name must be absent first; do not remove a pre-existing container with that name.

```bash
docker image tag sha256:139a1f015734889f0bef40f66a4db65a1addc1a3dc5dc41f6bc82fe9d936757f seda-f3-dependencies:20261007
docker create --pull=never --name seda-rc1-context-read --network none --read-only --entrypoint python sha256:f1dc063ca46a05ccce548121c1f530eb1d7ce2edc87dc27db1f32d3ba2cdf00a -c pass
mkdir -p /tmp/seda-rc1-stage-20261008
mkdir -p /tmp/seda-rc1-context-20261008
docker cp seda-rc1-context-read:/app/app /tmp/seda-rc1-stage-20261008/app
docker cp seda-rc1-context-read:/app/specs /tmp/seda-rc1-stage-20261008/specs
docker cp seda-rc1-context-read:/workshop /tmp/seda-rc1-stage-20261008/workshop
docker container rm seda-rc1-context-read
.venv/bin/python - <<'CHECK'
import hashlib,json
from pathlib import Path
record=json.loads(Path('workshop/seda-20261008/evidence/build.json').read_text())
stage=Path('/tmp/seda-rc1-stage-20261008')
context=Path('/tmp/seda-rc1-context-20261008')
assert not any(context.iterdir()), 'Use a new empty context; never overwrite'
for name,expected in record['context_files'].items():
    value=record['dockerfile'].encode() if name=='Dockerfile' else (stage/name).read_bytes()
    assert hashlib.sha256(value).hexdigest()==expected, name
    destination=context/name
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('xb') as output:output.write(value)
print('Original context hashes verified; no extra files copied')
CHECK
docker build --pull=false --network=none --platform linux/amd64 --no-cache --progress=plain -t seda-workshop:20261008-rc1-replay /tmp/seda-rc1-context-20261008
docker image inspect seda-workshop:20261008-rc1-replay --format '{{.Id}}'
docker container ls --all --filter name=seda-rc1-context-read --format '{{.ID}}'
```

Expected final container listing:empty. Reconstruction/new build was not executed here. Original source/context bytes can be reproduced; a byte-identical new image ID is not promised (image metadata/build implementation can differ). A new image requires its own build/smoke/rehearsal evidence and versioned launch manifest; the current guard intentionally refuses an untested image.
