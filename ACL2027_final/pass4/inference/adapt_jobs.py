#!/usr/bin/env python3
"""Copy frozen reader prompts into the inference runner's input interface."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--max-tokens', type=int, default=96)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    rows = [json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    adapted = []
    for row in rows:
        identifier = row.get('id', row.get('job_id'))
        if identifier is None or not isinstance(row.get('prompt'), str):
            raise ValueError('Every job must supply an id/job_id and an exact prompt string')
        adapted.append({'id': identifier, 'prompt': row['prompt'],
                        'max_tokens': args.max_tokens,
                        'metadata': {k: v for k, v in row.items() if k != 'prompt'}})
    if len({str(row['id']) for row in adapted}) != len(adapted):
        raise ValueError('Duplicate job identifiers')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w') as stream:
        for row in adapted:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    manifest = {'original_path': str(args.input), 'original_sha256': digest(args.input),
                'adapted_path': str(args.output), 'adapted_sha256': digest(args.output),
                'rows': len(adapted), 'prompt_changes': 0, 'max_tokens': args.max_tokens,
                'metadata_enters_request': False}
    args.output.with_suffix('.adaptation.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
