#!/usr/bin/env python3
"""Restore compressed historical results and check their original hashes."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil
import tempfile


def checksum(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def main():
    root = Path(__file__).resolve().parent
    records = json.loads((root / 'compressed_runs/manifest.json').read_text())
    for record in records:
        target = root / 'ACL2027_final' / record['path']
        if target.exists():
            if checksum(target) != record['sha256']:
                raise RuntimeError(f'Existing file differs: {target}. Move it before restoring.')
            print(f'Already verified: {record["path"]}', flush=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='restore-', dir=target.parent) as temporary:
            archive = Path(temporary) / 'combined.gz'
            restored = Path(temporary) / 'restored'
            with archive.open('wb') as output:
                for part in record['gzip_parts']:
                    with (root / part).open('rb') as source:
                        shutil.copyfileobj(source, output, 4 * 1024 * 1024)
            with gzip.open(archive, 'rb') as source, restored.open('wb') as output:
                shutil.copyfileobj(source, output, 4 * 1024 * 1024)
            if restored.stat().st_size != record['bytes']:
                raise RuntimeError(f'Size mismatch: {record["path"]}')
            if checksum(restored) != record['sha256']:
                raise RuntimeError(f'Checksum mismatch: {record["path"]}')
            os.replace(restored, target)
        print(f'Restored and verified: {record["path"]}', flush=True)
    print('All historical result files are ready.')


if __name__ == '__main__':
    main()
