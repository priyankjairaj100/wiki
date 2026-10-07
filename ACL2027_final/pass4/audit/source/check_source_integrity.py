#!/usr/bin/env python3
"""Independent literal-grounding and source-partition checks.

This program reads source records only. It does not load benchmark labels.
Semantic judgments are recorded separately by the model-assisted reviewer.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spans(obj, prefix=''):
    if isinstance(obj, dict):
        if {'start', 'end', 'text'} <= obj.keys() and isinstance(obj['text'], str):
            yield prefix, obj
        for key, value in obj.items():
            yield from spans(value, f'{prefix}.{key}')
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from spans(value, f'{prefix}[{index}]')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', required=True)
    parser.add_argument('--claims', required=True)
    parser.add_argument('--units')
    parser.add_argument('--calibration-sources')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    source_rows = read(args.sources)
    sources = {row['passage_id']: row for row in source_rows}
    assert len(sources) == len(source_rows), 'Duplicate source identifiers'
    claims = read(args.claims)
    ids = [row['claim_id'] for row in claims]
    assert len(set(ids)) == len(ids), 'Duplicate claim identifiers'
    issues = []
    checked_spans = 0
    for row in claims:
        source = sources.get(row['passage_id'])
        if source is None:
            issues.append({'claim_id': row['claim_id'], 'issue': 'missing_passage'})
            continue
        if source['article_path'] != row['article_path']:
            issues.append({'claim_id': row['claim_id'], 'issue': 'article_mismatch'})
        for label, span in spans(row):
            checked_spans += 1
            a, b = span['start'], span['end']
            valid = type(a) is int and type(b) is int and 0 <= a < b <= len(source['text'])
            if not valid or source['text'][a:b] != span['text']:
                issues.append({'claim_id': row['claim_id'], 'issue': 'literal_span_mismatch', 'field': label})
        if row.get('value_span', {}).get('text') != row.get('value'):
            issues.append({'claim_id': row['claim_id'], 'issue': 'value_span_mismatch'})
        for endpoint in ['start', 'end']:
            bound = row.get(endpoint)
            if bound and bound['lower'] > bound['upper']:
                issues.append({'claim_id': row['claim_id'], 'issue': 'reversed_bound', 'field': endpoint})
    unit_report = None
    if args.units:
        units = read(args.units)
        by_passage = collections.defaultdict(list)
        for unit in units:
            by_passage[unit['passage_id']].append(unit)
        unit_issues = []
        for pid, source in sources.items():
            coverage = bytearray(len(source['text']))
            for unit in by_passage[pid]:
                a, b = unit['start_char'], unit['end_char_exclusive']
                if not 0 <= a < b <= len(source['text']) or unit['text'] != source['text'][a:b]:
                    unit_issues.append({'passage_id': pid, 'unit_id': unit['unit_id'], 'issue': 'unit_text_mismatch'})
                    continue
                for index in range(a, b):
                    if coverage[index]:
                        unit_issues.append({'passage_id': pid, 'unit_id': unit['unit_id'], 'issue': 'overlapping_units'})
                        break
                    coverage[index] = 1
            missing = [i for i, char in enumerate(source['text']) if char.isalnum() and not coverage[i]]
            if missing:
                unit_issues.append({'passage_id': pid, 'issue': 'uncovered_source_characters', 'count': len(missing)})
        unit_report = {'units': len(units), 'passages_checked': len(sources), 'issues': unit_issues}
    calibration = set()
    if args.calibration_sources:
        calibration = {row['article_path'] for row in read(args.calibration_sources)}
    confirmation = [row for row in claims if row['article_path'] not in calibration]
    def key(row):
        return hashlib.sha256(('pass4-independent-source-audit-v1\0' + row['claim_id']).encode()).hexdigest()
    sample = sorted(confirmation, key=key)[:60]
    sample_rows = [{'claim': row, 'source_paragraph': sources[row['passage_id']], 'selection_hash': key(row)} for row in sample]
    (out / 'confirmation_sample.jsonl').write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in sample_rows))
    report = {
        'kind': 'Independent deterministic source integrity check',
        'input_hashes': {name: digest(path) for name, path in [('sources', args.sources), ('claims', args.claims)]},
        'source_passages': len(sources), 'claims': len(claims), 'spans_checked': checked_spans,
        'literal_issues': issues, 'partition_check': unit_report,
        'confirmation_population': len(confirmation), 'confirmation_sample_size': len(sample),
        'calibration_articles_excluded': len(calibration), 'answer_label_reads': 0,
        'scope': 'Literal and partition checks do not establish semantic entailment.'
    }
    (out / 'integrity_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 1 if issues or (unit_report and unit_report['issues']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
