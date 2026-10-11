"""Versioned launch guard for the measured candidate; no response changes."""
import argparse
import hashlib
import json
from pathlib import Path


def verify_launch(root, manifest, image):
    root=Path(root).resolve()
    if image != manifest['image_id']:
        raise ValueError('candidate_image_required')
    for name, expected in manifest['host_code'].items():
        path=(root/name).resolve()
        if root not in path.parents or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('host_code_mismatch')
    return True


def main():
    from workshop.seda_v2 import BUNDLE, ROOT, run
    parser=argparse.ArgumentParser(description='Guarded local rehearsal; no acceptance claim')
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    manifest=json.loads((BUNDLE/'launch-guard-v1.json').read_text())
    verify_launch(ROOT,manifest,manifest['image_id'])
    raise SystemExit(run('rehearsal',manifest['image_id'],args.output))


if __name__=='__main__':
    main()
