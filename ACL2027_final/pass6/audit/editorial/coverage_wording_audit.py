#!/usr/bin/env python3
"""Audit frozen corpus coverage and visible question wording without answer labels."""
from __future__ import annotations
import hashlib
import json
import re
import argparse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=OUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((OUT / 'WORDING_PROTOCOL.json').read_text())
    rules = {key: re.compile(pattern, re.I) for key, pattern in protocol['rules'].items()}
    inputs = [OUT / 'WORDING_PROTOCOL.json', Path(__file__)]
    all_rows = []
    tracks = {}
    for name, file in [('template', 'dev_validation_queries.jsonl'),
                       ('human', 'human_test_confirmation_queries.jsonl')]:
        folder = 'validation' if name == 'template' else 'human'
        qpath = ROOT / 'pass5/protocol' / file
        mpath = ROOT / 'pass5/pipeline' / folder / 'mechanism_questions.jsonl'
        ppath = ROOT / 'pass5/pipeline' / folder / 'predictions.jsonl'
        inputs.extend([qpath, mpath, ppath])
        questions = rows(qpath)
        mechanisms = {r['question_id']: r for r in rows(mpath)}
        predictions = {r['question_id']: r for r in rows(ppath)}
        assert len(questions) == len(mechanisms) == len(predictions)
        partition = Counter()
        selected = Counter()
        for q in questions:
            mid = q['question_id']
            m = mechanisms[mid]
            p = predictions[mid]
            parsed = bool(m['query_time_parsed'])
            modeled = int(m.get('possible_context_modeled', p['methods']['possible_support']['modeled_units']))
            stable = m['claim_context_certificate']
            group = ('unparsed' if not parsed else
                     'parsed_all_fallback' if not modeled else
                     'modeled_stable' if stable else 'modeled_unstable')
            partition[group] += 1
            contexts = p['methods']['possible_support']['contexts']
            selected['selected_units'] += len(contexts)
            selected['fallback_units'] += sum(c['kind'] == 'fallback' for c in contexts)
            selected['modeled_units'] += sum(c['kind'] == 'modeled' for c in contexts)
            selected['contexts_with_any_fallback'] += any(c['kind'] == 'fallback' for c in contexts)
            selected['contexts_with_only_modeled'] += bool(contexts) and all(c['kind'] == 'modeled' for c in contexts)
            hits = {key: [x.group(0) for x in rule.finditer(q['question'])]
                    for key, rule in rules.items()}
            active = [key for key, values in hits.items() if values]
            wording = active[0] if len(active) == 1 else ('mixed_cues' if active else 'unspecified_or_ambiguous')
            all_rows.append({'track': name, 'question_id': mid, 'question': q['question'],
                             'wording_class': wording, 'matched_cues': hits, 'coverage_group': group,
                             'selected_modeled_units': modeled,
                             'heuristic_not_semantic_gold': True})
        assert sum(partition.values()) == len(questions)
        track_rows = [r for r in all_rows if r['track'] == name]
        cross = {kind: dict(Counter(r['coverage_group'] for r in track_rows if r['wording_class'] == kind))
                 for kind in protocol['categories']}
        tracks[name] = {'questions': len(questions), 'coverage_partition': dict(partition),
                        'coverage_percentage_all_questions': {k: 100 * v / len(questions) for k, v in partition.items()},
                        'selected_units': dict(selected),
                        'fallback_unit_percentage': 100 * selected['fallback_units'] / selected['selected_units'],
                        'wording_classes': dict(Counter(r['wording_class'] for r in track_rows)),
                        'wording_by_coverage': cross}
    aggregate = Counter(r['coverage_group'] for r in all_rows)
    wording = Counter(r['wording_class'] for r in all_rows)
    examples = {}
    for category in protocol['categories']:
        available = [r for r in all_rows if r['wording_class'] == category]
        examples[category] = sorted(available, key=lambda r: hashlib.sha256(r['question_id'].encode()).hexdigest())[:8]
    report = {'status': 'passed', 'scope': protocol['scope'], 'tracks': tracks,
              'aggregate': {'questions': len(all_rows), 'coverage_partition': dict(aggregate),
                            'coverage_percentage_all_questions': {k: 100*v/len(all_rows) for k,v in aggregate.items()},
                            'modeled_contexts': aggregate['modeled_stable'] + aggregate['modeled_unstable'],
                            'modeled_context_percentage_all_questions': 100*(aggregate['modeled_stable'] + aggregate['modeled_unstable'])/len(all_rows),
                            'wording_classes': dict(wording)},
              'hash_selected_examples': examples,
              'input_sha256': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
              'limitations': protocol['limitations']}
    (args.output_dir / 'coverage_wording.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    (args.output_dir / 'question_wording.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in all_rows))
    print(json.dumps({'status': 'passed', 'aggregate': report['aggregate'], 'tracks': tracks}, indent=2))


if __name__ == '__main__':
    main()
