"""Freeze pass-4 query tracks and reader membership without loading labels.

Question identifiers remain uninterpreted join keys. They are not features.
The reader sample uses identifier hashes only and never loads retrieval output.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
INPUT = ROOT / 'pass3/protocol'
SEED = 'acl2027-pass4-reader-confirmation-20261006-v1'
N_READER = 60
TRACKS = ('dev_pilot', 'dev_additional_calibration', 'dev_validation',
          'human_test_confirmation')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def lines(path, rows):
    Path(path).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def rank(question_id):
    return hashlib.sha256((SEED + '\0' + question_id).encode()).hexdigest()


def main():
    all_tracks = {}
    inputs = {}
    for track in TRACKS:
        path = INPUT / (track + '_queries.jsonl')
        rows = read(path)
        assert len({row['question_id'] for row in rows}) == len(rows)
        # No annotation metadata enters an inference query row.
        clean = [{key: row[key] for key in ('question_id', 'question')} for row in rows]
        lines(OUT / (track + '_queries.jsonl'), clean)
        lines(OUT / (track + '_evaluation_groups.jsonl'),
              [{'question_id': row['question_id'], 'article_path': row['article_path']}
               for row in rows])
        all_tracks[track] = rows
        inputs[str(path.relative_to(ROOT))] = sha(path)
    human = all_tracks['human_test_confirmation']
    selected = sorted(human, key=lambda row: (rank(row['question_id']), row['question_id']))[:N_READER]
    reader = [{key: row[key] for key in ('question_id', 'question')} for row in selected]
    lines(OUT / 'reader_primary_queries.jsonl', reader)
    dump(OUT / 'reader_sample_manifest.json', {
        'protocol_id': 'acl2027-pass4-evidence-confirmation-v1',
        'selection_frozen_date': '2026-10-06',
        'seed': SEED,
        'selection': 'Smallest SHA256(seed NUL original question ID) among all 830 published human questions.',
        'sample_size': len(reader),
        'article_count': len({row['article_path'] for row in selected}),
        'source_track_size': len(human),
        'uses_gold': False,
        'uses_context_outcomes': False,
        'prior_status': 'Earlier baseline results were inspected. This is confirmation, not untouched test evidence.',
        'no_postselection_exclusions': True,
        'unparsed_time_empty_context_and_reader_failure_remain_in_denominator': True,
        'question_ids': [row['question_id'] for row in selected],
        'sample_sha256': sha(OUT / 'reader_primary_queries.jsonl'),
        'inputs': inputs,
        'selection_script_sha256': sha(__file__),
    })
    dump(OUT / 'query_manifest.json', {
        'inputs': inputs,
        'tracks': {name: {'questions': len(rows),
                          'articles': len({row['article_path'] for row in rows}),
                          'queries_sha256': sha(OUT / (name + '_queries.jsonl'))}
                   for name, rows in all_tracks.items()},
        'inference_query_fields': ['question_id', 'question'],
        'identifier_policy': 'Treat question_id as opaque. Never parse article or relation components.',
        'evaluation_groups_are_not_inference_inputs': True,
        'reader_sample': 'reader_sample_manifest.json',
    })
    print(json.dumps({'reader_questions': len(reader),
                      'reader_articles': len({row['article_path'] for row in selected}),
                      'sample_sha256': sha(OUT / 'reader_primary_queries.jsonl')}, indent=2))


if __name__ == '__main__':
    main()
