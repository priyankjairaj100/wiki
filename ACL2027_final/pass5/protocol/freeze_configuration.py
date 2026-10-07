"""Record a write-once algorithm freeze before confirmation execution.

This utility hashes paths supplied by the caller. It does not load benchmark
labels or model responses. The timestamp documents recording, not preregistration.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CODE = [
    'pass5/protocol/config.json',
    'pass5/pipeline/run_matched.py',
    'pass4/retrieval/ranking.py',
    'pass3/pipeline/run_matched.py',
    'pass5/extraction/source_adapter.py',
    'pass3/theory/lifecycle.py',
    'pass3/theory/refinement.py',
    'pass2/theory/uncertain_time.py',
    'pass3/protocol/parse_reader.py',
    'pass3/protocol/score_predictions.py',
]
FORBIDDEN_NAMES = ('labels', 'annotations', 'histories', 'scored_questions',
                   'reader_output', 'predictions', 'answers')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-input', type=Path, action='append', required=True,
                   help='Source corpus or frozen extracted claims. Repeat as needed.')
    p.add_argument('--query-input', type=Path, action='append', required=True)
    p.add_argument('--extra-code', type=Path, action='append', default=[])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--note', default='Algorithm selected from calibration before this confirmation run.')
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError('Keep the original freeze. Use a new output for an amendment.')
    inputs = args.source_input + args.query_input
    for path in inputs:
        if any(name in path.name.lower() for name in FORBIDDEN_NAMES):
            raise ValueError('A scoring or outcome file cannot be an inference input: ' + str(path))
    for path in args.query_input:
        for line in path.read_text().splitlines():
            if line:
                row = json.loads(line)
                if set(row) != {'question_id', 'question'}:
                    raise ValueError('Sanitized query fields required: ' + str(path))
    paths = [ROOT / value for value in DEFAULT_CODE] + args.extra_code + inputs
    hashes = {}
    for path in paths:
        path = path.resolve()
        hashes[str(path.relative_to(ROOT))] = {'sha256': digest(path), 'bytes': path.stat().st_size}
    record = {
        'run_id': args.run_id,
        'recorded_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'status': 'Local pre-execution freeze; not an external preregistration.',
        'note': args.note,
        'inputs_and_code': hashes,
        'reader_sample_sha256': digest(ROOT / 'pass5/protocol/reader_primary_queries.jsonl'),
        'input_policy': 'Visible question only. Join identifiers are uninterpreted. Full declared source pool.',
        'confirmation_status': 'Earlier pass outcomes were inspected. No untouched-test claim.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'freeze': str(args.output), 'files': len(hashes), 'sha256': digest(args.output)}, indent=2))


if __name__ == '__main__':
    main()
