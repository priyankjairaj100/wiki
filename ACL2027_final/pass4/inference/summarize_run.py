#!/usr/bin/env python3
"""Verify a completed frozen run and summarize decoding without QA labels."""
import argparse
import collections
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pass3.protocol.parse_reader import parse_response
from pass4.inference.run_jsonl import make_request


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--summary', type=Path)
    args = parser.parse_args()
    inputs, outputs = read(args.input), read(args.output)
    expected = {str(row['id']): row for row in inputs}
    actual = {str(row['id']): row for row in outputs}
    assert len(inputs) == len(expected), 'Repeated input ids'
    assert len(outputs) == len(actual), 'Repeated output ids'
    assert set(expected) == set(actual), 'Incomplete or mismatched generation set'
    for identifier, row in expected.items():
        response = actual[identifier]
        assert response['request'] == make_request(row, 96, 1729), identifier
        canonical = json.dumps(response['request'], sort_keys=True, ensure_ascii=False).encode()
        assert hashlib.sha256(canonical).hexdigest() == response['request_sha256'], identifier
    manifest_path = args.output.with_suffix('.manifest.json')
    manifest = json.loads(manifest_path.read_text())
    assert digest(args.input) == manifest['input_sha256']
    assert digest(args.output) == manifest['output_sha256']
    parsing = [parse_response(row['generation'], len(row['metadata']['contexts']),
                              row['finish_reason']) for row in outputs]
    elapsed = [row['wall_seconds'] for row in outputs]
    usage = [row['response']['usage'] for row in outputs]
    summary = {
        'input': str(args.input), 'output': str(args.output),
        'input_sha256': digest(args.input), 'output_sha256': digest(args.output),
        'planned_requests': len(inputs), 'completed_requests': len(outputs),
        'request_integrity_checks': len(inputs),
        'finish_reasons': dict(collections.Counter(row['finish_reason'] for row in outputs)),
        'parse_ok': sum(row['parse_ok'] for row in parsing),
        'parse_failures': dict(collections.Counter(row['parse_failure'] for row in parsing if not row['parse_ok'])),
        'total_wall_seconds': sum(elapsed), 'median_wall_seconds': statistics.median(elapsed),
        'min_wall_seconds': min(elapsed), 'max_wall_seconds': max(elapsed),
        'prompt_tokens': sum(row['prompt_tokens'] for row in usage),
        'completion_tokens': sum(row['completion_tokens'] for row in usage),
        'label_access': False, 'parser': 'pass3/protocol/parse_reader.py',
        'parser_sha256': digest(ROOT / 'pass3/protocol/parse_reader.py'),
        'model_repository': manifest['model_repository'],
        'model_revision': manifest['model_revision'],
        'model_sha256': manifest['model_sha256'],
    }
    target = args.summary or args.output.parent / 'run_summary.json'
    target.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
