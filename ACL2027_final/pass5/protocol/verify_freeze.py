"""Verify that all frozen inference inputs and code still match their hashes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--freeze', type=Path, default=ROOT / 'pass5/protocol/ALGORITHM_FREEZE.json')
    p.add_argument('--output', type=Path)
    p.add_argument('--resource-amendment', type=Path, default=ROOT / 'pass5/protocol/RESOURCE_AMENDMENT.json')
    args = p.parse_args()
    record = json.loads(args.freeze.read_text())
    failures = []
    for name, expected in record['inputs_and_code'].items():
        path = ROOT / name
        if not path.exists():
            failures.append({'path': name, 'reason': 'missing'})
        elif digest(path) != expected['sha256']:
            failures.append({'path': name, 'reason': 'sha256 differs'})
    resource_checks = 0
    if args.resource_amendment.exists():
        amendment = json.loads(args.resource_amendment.read_text())
        assert amendment['retrieval_config_unchanged'] is True
        assert amendment['supersedes_reader_resource_fields_only'] is True
        for name, expected in amendment['hashes'].items():
            path = ROOT / name
            resource_checks += 1
            if not path.exists() or digest(path) != expected:
                failures.append({'path': name, 'reason': 'resource amendment hash differs'})
    result = {'run_id': record['run_id'], 'freeze_sha256': digest(args.freeze),
              'resource_amendment_files_checked': resource_checks,
              'original_hash_exceptions_allowed': 0,
              'checked_files': len(record['inputs_and_code']), 'failures': failures,
              'all_files_match': not failures}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
