"""Independently replay every saved context and counterworld without gold labels.

The support oracle scans incoming events directly. It never calls the compiler,
its certificates, completion helpers, or counterworld construction functions.
The frozen relevance ranker is shared, while mask application and rendering checks
are independently implemented here.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import itertools
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pass4.retrieval.ranking import TitleRanker


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def unique(rows, key):
    result = {row[key]: row for row in rows}
    assert len(result) == len(rows)
    return result


def events_from_records(claims):
    bounds = {cid: (c['start']['lower'], c['start']['upper']) for cid, c in claims.items()}
    incoming = {cid: [] for cid in claims}
    for cid, claim in claims.items():
        if claim.get('end'):
            eid = '@explicit-end:' + cid
            end = claim['end']
            bounds[eid] = (end['lower'], end['upper'])
            incoming[cid].append(eid)
            assert bounds[cid][1] < bounds[eid][0]
        assertion = claim.get('exclusion_assertion')
        if assertion and assertion.get('kind') == 'explicit_succession':
            for target in assertion['excluded_claim_ids']:
                assert target in claims
                if target != cid:
                    incoming[target].append(cid)
    return bounds, incoming


def support_in_world(cid, dates, incoming, a, b):
    start = dates[cid]
    if start > b:
        return False
    witness_time = max(a, start)
    return all(not (start < dates[other] <= witness_time) for other in incoming[cid])


def masks_from_bounds(claims, bounds, incoming, window):
    if window is None:
        return {name: set(claims) for name in ['no_temporal_filter', 'earliest_completion',
                'midpoint_completion', 'latest_completion', 'interval_outer_control',
                'possible_support', 'guaranteed_support', 'latest_mentioned_year_top20',
                'original_bm25', 'original_bm25_latestyear']}
    a, b = window
    possible, guaranteed, outer = set(), set(), set()
    for cid, claim in claims.items():
        lower, upper = bounds[cid]
        if lower <= b and all(not (bounds[d][0] > upper and bounds[d][1] <= a) for d in incoming[cid]):
            possible.add(cid)
        if upper <= b and (a <= lower or all(not (bounds[d][1] > lower and bounds[d][0] <= a)
                                              for d in incoming[cid])):
            guaranteed.add(cid)
        if lower <= b and (not claim.get('end') or a < claim['end']['upper']):
            outer.add(cid)
    masks = {'possible_support': possible, 'guaranteed_support': guaranteed,
             'interval_outer_control': outer}
    for mode, position in [('earliest_completion', 0), ('latest_completion', 1), ('midpoint_completion', None)]:
        dates = {cid: ((bound[0] + bound[1]) / 2 if position is None else bound[position])
                 for cid, bound in bounds.items()}
        masks[mode] = {cid for cid in claims if support_in_world(cid, dates, incoming, a, b)}
    for mode in ['no_temporal_filter', 'latest_mentioned_year_top20', 'original_bm25', 'original_bm25_latestyear']:
        masks[mode] = set(claims)
    return masks


def choose(order, units, keep, budget):
    return list(itertools.islice((units[i]['unit_id'] for i in order
            if units[i]['claim_id'] is None or units[i]['claim_id'] in keep), budget))


def render(selected, units_by_id, budget):
    result = []
    remaining = budget
    for cid in selected:
        unit = units_by_id[cid]
        words = list(re.finditer(r'\S+', unit['text']))
        if not words or remaining == 0:
            break
        end = len(unit['text']) if len(words) <= remaining else words[remaining - 1].end()
        text = unit['text'][:end]
        result.append((unit['unit_id'], unit['passage_id'], unit['start_char'], unit['start_char'] + end, text))
        remaining -= len(text.split())
    return result


def context_key(contexts):
    return [(c['unit_id'], c['passage_id'], c['start_char'], c['end_char_exclusive'], c['text']) for c in contexts]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--folder', type=Path, required=True)
    p.add_argument('--passages', type=Path, required=True)
    p.add_argument('--queries', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    folder = args.folder
    manifest = json.loads((folder / 'manifest.json').read_text())
    config = json.loads((folder / 'config.json').read_text())
    assert sha(folder / 'config.json') == sha(ROOT / 'pass5/protocol/config.json')
    for name, value in manifest['inputs'].items():
        assert sha(ROOT / name) == value, name
    units = read(folder / 'units.jsonl'); by_unit = unique(units, 'unit_id')
    claims = unique(read(folder / 'claims.jsonl'), 'claim_id')
    modeled_ids = {u['claim_id'] for u in units if u['claim_id'] is not None}
    assert modeled_ids == set(claims), 'This audit requires all frozen claims to be modeled.'
    passages = unique(read(args.passages), 'passage_id')
    by_passage = collections.defaultdict(list)
    for unit in units:
        source = passages[unit['passage_id']]['text']
        assert source[unit['start_char']:unit['end_char_exclusive']] == unit['text']
        by_passage[unit['passage_id']].append(unit)
        if unit['claim_id']:
            claim = claims[unit['claim_id']]
            assert unit['source_subject'] == claim['subject']['canonical']
            assert unit['source_relation'] == claim['slot']
    for pid, passage in passages.items():
        excerpt_units = sorted(by_passage[pid], key=lambda row: row['start_char'])
        assert all(left['end_char_exclusive'] <= right['start_char'] for left, right in zip(excerpt_units, excerpt_units[1:]))
        assert re.findall(r'\w+', passage['text']) == [word for unit in excerpt_units for word in re.findall(r'\w+', unit['text'])]
    queries = unique(read(args.queries), 'question_id')
    predictions = unique(read(folder / 'predictions.jsonl'), 'question_id')
    mechanism = unique(read(folder / 'mechanism_questions.jsonl'), 'question_id')
    assert set(queries) == set(predictions) == set(mechanism)
    worlds = unique(read(folder / 'counterworlds.jsonl'), 'question_id')
    bounds, incoming = events_from_records(claims)
    index = TitleRanker(units, config['ranking']['k1'], config['ranking']['b'])
    k = config['contexts']['unit_limit']; word_limit = config['contexts']['word_limit']
    counts = collections.Counter(); stable_budgets = collections.Counter(); exclusions = collections.Counter()
    claim_unstable = set(); rendered_world_differences = 0
    for count, (qid, query) in enumerate(queries.items(), 1):
        prediction, audit = predictions[qid], mechanism[qid]
        assert prediction['question'] == query['question']
        window = prediction['query_window']
        assert window == audit['query_window']
        masks = masks_from_bounds(claims, bounds, incoming, window)
        order = index.rank(query['question'])[0]
        assert len(order) == len(units) and len(set(order)) == len(units)
        orders = {'original_bm25': index.rank_with_metadata(query['question'], 'bm25')[0],
                  'original_bm25_latestyear': index.rank_with_metadata(query['question'], 'bm25_latestyear')[0],
                  'latest_mentioned_year_top20': index.rank_with_metadata(query['question'], 'title_residual_latestyear')[0]}
        for method, result in prediction['methods'].items():
            selected = choose(orders.get(method, order), units, masks[method], k)
            assert selected == result['selected_unit_ids'], (qid, method, 'selected')
            assert render(selected, by_unit, word_limit) == context_key(result['contexts']), (qid, method, 'rendered')
            assert len(result['contexts']) <= k
            assert sum(len(c['text'].split()) for c in result['contexts']) <= word_limit
            for c in result['contexts']:
                cid = c['claim_id']
                expected = ('unknown' if cid is None or window is None else
                            'guaranteed' if cid in masks['guaranteed_support'] else
                            'unresolved' if cid in masks['possible_support'] else 'unsupported')
                assert c['temporal_status'] == expected, (qid, method, cid, c['temporal_status'], expected)
            counts['method_contexts_checked'] += 1
        counts['queries'] += 1
        if window is None:
            counts['unparsed'] += 1
            continue
        counts['parsed'] += 1
        possible = prediction['methods']['possible_support']
        stable = possible['selected_unit_ids'] == prediction['methods']['guaranteed_support']['selected_unit_ids']
        assert stable == audit['claim_context_certificate']
        modeled = any(c['claim_id'] is not None for c in possible['contexts'])
        category = 'modeled' if modeled else 'all_fallback'
        counts['parsed_' + category] += 1
        counts['parsed_' + category + ('_stable' if stable else '_unstable')] += 1
        for budget in [1, 3, 5, 10, 20]:
            direct = choose(order, units, masks['possible_support'], budget) == choose(order, units, masks['guaranteed_support'], budget)
            assert direct == audit['stable_at_budgets'][str(budget)]
            counts['budget_equalities_checked'] += 1
            if modeled and direct:
                stable_budgets[str(budget)] += 1
        if not stable:
            claim_unstable.add(qid)
            record = worlds[qid]
            assert record['query_window'] == window
            assert record['pivot_id'] in record['frontier']
            exclusions[record['exclusion_reason']] += 1
            replayed = []
            for world in record['worlds'].values():
                dates = world['event_dates']
                assert set(dates) == set(bounds)
                assert all(lower <= dates[cid] <= upper for cid, (lower, upper) in bounds.items())
                active = {cid for cid in claims if support_in_world(cid, dates, incoming, *window)}
                selected = choose(order, units, active, k)
                assert selected == world['selected_unit_ids']
                rendered = render(selected, by_unit, word_limit)
                assert rendered == context_key(world['contexts'])
                replayed.append((selected, rendered))
                counts['worlds_checked'] += 1
                counts['event_assignments_checked'] += len(dates)
            assert replayed[0][0] != replayed[1][0]
            rendered_world_differences += replayed[0][1] != replayed[1][1]
        if count % 250 == 0:
            print('audited', count, '/', len(queries), flush=True)
    assert set(worlds) == claim_unstable
    memberships = read(folder / 'reader_memberships.jsonl')
    selected_queries = read(folder / 'reader_selected_queries.jsonl')
    pairs = [(m['question_id'], m['method']) for m in memberships]
    expected = set(itertools.product((q['question_id'] for q in selected_queries), config['methods']))
    assert len(pairs) == len(set(pairs)) and set(pairs) == expected
    jobs = unique(read(folder / 'reader_jobs.jsonl'), 'job_id')
    for membership in memberships:
        assert membership['job_id'] in jobs
        result = predictions[membership['question_id']]['methods'][membership['method']]
        assert membership['context_signature'] == result['context_signature']
        assert hashlib.sha256(jobs[membership['job_id']]['prompt'].encode()).hexdigest() == membership['job_id']
    summary = {
        'audit_kind': 'Independent source-free-label replay; direct event scans replace compiler calls.',
        'all_checks_passed': True, 'counts': dict(counts),
        'stable_at_budgets_fixed_modeled_cohort': {budget: {'stable': stable_budgets[budget], 'denominator': counts['parsed_modeled']}
                                                for budget in ['1', '3', '5', '10', '20']},
        'counterworld_pairs': len(worlds), 'pairs_with_different_rendered_sources': rendered_world_differences,
        'counterworld_exclusion_reasons': dict(exclusions),
        'reader_questions': len(selected_queries), 'reader_logical_conditions': len(memberships),
        'reader_unique_jobs': len(jobs), 'config_unchanged': True,
        'source_partition_words_preserved': True, 'source_partition_nonoverlapping': True,
        'files': {str(path): sha(path) for path in [Path(__file__), args.passages, args.queries,
                  folder / 'manifest.json', folder / 'predictions.jsonl', folder / 'counterworlds.jsonl']}}
    dump(args.output, summary)
    print(json.dumps({key: value for key, value in summary.items() if key != 'files'}, indent=2))


if __name__ == '__main__':
    main()
