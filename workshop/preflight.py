"""Read-only approved asset checks; never downloads or reports service readiness."""
import hashlib
import json

from workshop.launch import verify_launch
from workshop.seda import ROOT
from workshop.seda_v2 import BUNDLE, verify_bundle


def file_sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def main():
    verify_bundle(BUNDLE)
    launch=json.loads((BUNDLE/"launch-guard-v1.json").read_text())
    verify_launch(ROOT,launch,launch["image_id"])
    generation = ROOT/'local-data/f3-models/a10cc1512eabd3dde888204e902eca88bddb4951'
    embedding = ROOT/'local-data/f1-models/1110a243fdf4706b3f48f1d95db1a4f5529b4d41'
    assets = json.loads((BUNDLE/'inputs/generation-assets.json').read_text())
    config = json.loads((embedding/'f1-model.json').read_text())
    report = {'local_assets_ready': False, 'service_readiness_claimed': False, 'models': []}
    for root, identity, revision, files in [
        (generation, assets['model_id'], assets['revision'], {f['path']: f['sha256'] for f in assets['files']}),
        (embedding, config['model_id'], config['model_commit'], config['model_file_sha256']),
    ]:
        bytes_total = 0
        for name, expected in files.items():
            path = (root/name).resolve()
            if root.resolve() not in path.parents or file_sha(path) != expected:
                raise SystemExit('approved_asset_mismatch')
            bytes_total += path.stat().st_size
        report['models'].append({'model_id': identity, 'revision': revision,
                                 'verified_files': len(files), 'logical_bytes': bytes_total})
    report['local_assets_ready'] = True
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
