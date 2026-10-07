"""Separate parsed answer changes from changes involving output-format failure.

This post-run descriptive audit uses no labels. It does not change any frozen
accuracy metric, parser, prediction, cohort, or denominator.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pass3.protocol.score_predictions import normalize


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--predictions', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    rows = read(args.predictions)
    qids = {row['question_id'] for row in rows}
    assert rows and len(qids) == len(rows)
    methods = sorted(rows[0]['methods'])
    assert all(sorted(row['methods']) == methods for row in rows)
    contrasts = {}
    for left, right in itertools.combinations(methods, 2):
        total_changed = both_valid = changed_both_valid = changed_with_failure = 0
        pairs_with_failure = []
        changed_valid_ids = []
        for row in rows:
            a, b = row['methods'][left], row['methods'][right]
            valid = bool(a['reader_parse_ok'] and b['reader_parse_ok'])
            changed = {normalize(x) for x in a['answers']} != {normalize(x) for x in b['answers']}
            both_valid += valid
            total_changed += changed
            changed_both_valid += changed and valid
            changed_with_failure += changed and not valid
            if changed and valid:
                changed_valid_ids.append(row['question_id'])
            if changed and not valid:
                pairs_with_failure.append(row['question_id'])
        contrasts[left + '__' + right] = {
            'full_cohort_questions': len(rows),
            'all_answer_set_changes': total_changed,
            'both_outputs_parsed_questions': both_valid,
            'answer_changes_with_both_outputs_parsed': changed_both_valid,
            'answer_changes_involving_parse_failure': changed_with_failure,
            'changed_both_parsed_question_ids': changed_valid_ids,
            'changed_with_parse_failure_question_ids': pairs_with_failure,
        }
        assert total_changed == changed_both_valid + changed_with_failure
    result = {'scope': 'Post-run descriptive interpretation audit. No labels read. Frozen scoring and denominators unchanged.',
              'questions': len(rows), 'methods': len(methods), 'contrasts': contrasts,
              'hashes': {str(path): sha(path) for path in [args.predictions, Path(__file__), ROOT / 'pass3/protocol/score_predictions.py']}}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    selected = ['earliest_completion__latest_completion', 'guaranteed_support__possible_support',
                'no_temporal_filter__original_bm25_latestyear']
    print(json.dumps({name: contrasts[name] for name in selected if name in contrasts}, indent=2))


if __name__ == '__main__':
    main()
