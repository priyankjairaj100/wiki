#!/usr/bin/env python3
"""Render complete, frozen reader scores without rerunning or changing scoring.

Each input directory must contain summary.json, scored_questions.jsonl, and
reader_parse_audit.jsonl from pass4/protocol/score_reader.py. This program never
reads raw generations, labels, prompts, or source passages. It refuses partial
cohorts and writes nothing until both complete cohorts pass consistency checks.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SCORER_SHA256 = '5542da2fdd32d72c2b0f27f48a0a533c204cdaed5e903fbb02516c9d19ccc6e7'
PARSER_SHA256 = 'fe0d8ffedafcd1fa62bb2e6f3cd4ee86624c529e5eea68e7d8958e0b0fa23eff'
ANSWER_SCORER_SHA256 = 'd947af316ffcf0f716fca86051e4b0ba9867dc591cabf79c323e96b4bd09575f'
COHORTS = {
    'primary': {'track': 'human_confirmation', 'questions': 60,
                'query_sha256': 'ac16d6a63bed55d2cbf10c65d747e943b3c1b364fcd89ce5158e0216f79f8ded'},
    'diagnostic': {'track': 'context_sensitive_diagnostic', 'questions': 11,
                   'query_sha256': 'b1d2f20e919ef90e8aa6a46dbbd7aa75e49f0c5145992898ed8956727aadd0a0'},
}
METHODS = [
    ('original_bm25', 'Original BM25'),
    ('original_bm25_latestyear', 'Original BM25 + year'),
    ('no_temporal_filter', 'Title-aware ranking'),
    ('earliest_completion', r'\quad + earliest completion'),
    ('midpoint_completion', r'\quad + midpoint completion'),
    ('latest_completion', r'\quad + latest completion'),
    ('interval_outer_control', r'\quad + interval control'),
    ('possible_support', r'\quad + possible support'),
    ('guaranteed_support', r'\quad + guaranteed support'),
    ('latest_mentioned_year_top20', 'Title-aware + year'),
]
EM = 'exact_annotated_answer_set'
F1 = 'annotated_answer_set_f1'
INPUT_NAMES = ('summary.json', 'scored_questions.jsonl', 'reader_parse_audit.jsonl')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def number(value, lower, upper, description):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and lower <= value <= upper,
            description + ' is outside its valid range.')
    return value


def count(value, lower, upper, description):
    require(isinstance(value, int) and not isinstance(value, bool)
            and lower <= value <= upper, description + ' is not a valid count.')
    return value


def check_provenance(summary, role):
    inputs = summary.get('input_sha256', {})
    require(isinstance(inputs, dict) and inputs, role + ': missing scorer provenance.')
    for suffix, expected in [
        ('pass4/protocol/score_reader.py', SCORER_SHA256),
        ('pass3/protocol/parse_reader.py', PARSER_SHA256),
        ('pass3/protocol/score_predictions.py', ANSWER_SCORER_SHA256),
    ]:
        matches = {value for name, value in inputs.items()
                   if name.replace('\\', '/').endswith(suffix)}
        require(matches == {expected}, role + ': frozen scorer provenance differs for ' + suffix)
    require(COHORTS[role]['query_sha256'] in inputs.values(),
            role + ': the frozen query cohort hash is absent.')


def load_complete(directory, role):
    directory = Path(directory)
    for name in INPUT_NAMES:
        require((directory / name).is_file(),
                role + ': complete saved scoring is required; missing ' + name)
    hashes = {name: digest(directory / name) for name in INPUT_NAMES}
    summary = json.loads((directory / 'summary.json').read_text())
    expected = COHORTS[role]
    require(summary.get('track') == expected['track'], role + ': wrong scoring track.')
    require(summary.get('n_questions') == expected['questions'], role + ': incomplete question cohort.')
    check_provenance(summary, role)
    method_ids = {method for method, _ in METHODS}
    require(set(summary['metrics']) == method_ids, role + ': the ten-method summary is incomplete.')
    n = expected['questions']
    conditions = n * len(METHODS)
    require(summary.get('n_logical_conditions') == conditions, role + ': incomplete logical conditions.')
    scored = read_rows(directory / 'scored_questions.jsonl')
    audit = read_rows(directory / 'reader_parse_audit.jsonl')
    qids = {row['question_id'] for row in scored}
    require(len(scored) == len(qids) == n, role + ': scored questions are incomplete or duplicated.')
    require(len({row['article_path'] for row in scored}) == summary['n_articles'],
            role + ': article count differs from saved question rows.')
    for row in scored:
        require(set(row['methods']) == method_ids, role + ': a scored question lacks a method.')
        for method in method_ids:
            for metric in (EM, F1):
                number(row['methods'][method][metric], 0, 1, role + ': saved per-question score')
    for method in method_ids:
        for metric in (EM, F1):
            value = number(summary['metrics'][method][metric], 0, 1, role + ': aggregate score')
            average = sum(row['methods'][method][metric] for row in scored) / n
            require(abs(value - average) <= 1e-12, role + ': aggregate score differs from saved rows.')
    keys = [(row['question_id'], row['method']) for row in audit]
    require(len(keys) == len(set(keys)) == conditions and set(keys) == set(itertools.product(qids, method_ids)),
            role + ': parse audit does not cover each question and method exactly once.')
    jobs = {}
    failures_by_method = dict.fromkeys(method_ids, 0)
    reasons = collections.Counter()
    for row in audit:
        require(isinstance(row['parse_ok'], bool), role + ': parse status must be Boolean.')
        state = (row['parse_ok'], row['parse_failure'])
        jid = row['job_id']
        require(jid not in jobs or jobs[jid] == state, role + ': a reused generation has conflicting parse outcomes.')
        jobs[jid] = state
        if not row['parse_ok']:
            failures_by_method[row['method']] += 1
            reasons[row['parse_failure']] += 1
    require(len(jobs) == summary['n_unique_generations_used'], role + ': generation count differs from the audit.')
    require(sum(not state[0] for state in jobs.values()) == summary['parse_failures_unique'],
            role + ': unique parse-failure count differs from the audit.')
    require(failures_by_method == summary['parse_failures_by_method'], role + ': per-method parse failures differ.')
    require(dict(reasons) == summary['parse_failure_reasons'], role + ': parse-failure reasons differ.')
    changes = summary.get('answer_changes', {})
    for name, result in changes.items():
        left, right = name.split('__')
        require({left, right} <= method_ids, role + ': unknown answer-change comparison.')
        count(result['queries'], 0, n, role + ': answer-change numerator')
        require(result['denominator'] == n, role + ': answer-change denominator differs.')
        require(abs(result['fraction'] - result['queries'] / n) <= 1e-12,
                role + ': answer-change fraction differs from its count.')
    pairwise = summary.get('reader_pairwise_article_intervals', {})
    expected_pairs = {method + '__' + reference for reference, method in itertools.combinations(sorted(method_ids), 2)}
    require(set(pairwise) == expected_pairs, role + ': paired reader intervals are incomplete.')
    for family in (pairwise, summary.get('prespecified_frontend_intervals', {})):
        for name, metrics in family.items():
            method, reference = name.split('__')
            require({method, reference} <= method_ids and set(metrics) == {EM, F1},
                    role + ': paired interval schema differs.')
            for metric, result in metrics.items():
                number(result['delta'], -1, 1, role + ': paired delta')
                require(len(result['ci95']) == 2, role + ': paired interval needs two bounds.')
                low, high = result['ci95']
                number(low, -1, 1, role + ': paired lower bound')
                number(high, -1, 1, role + ': paired upper bound')
                require(low <= high and result['article_clusters'] == summary['n_articles'],
                        role + ': paired interval bounds or clusters differ.')
                difference = summary['metrics'][method][metric] - summary['metrics'][reference][metric]
                require(abs(result['delta'] - difference) <= 1e-12, role + ': paired delta differs from aggregate scores.')
    require(all(digest(directory / name) == value for name, value in hashes.items()),
            role + ': a scoring file changed while it was read.')
    return summary, qids, jobs, hashes


def percent_intervals(family):
    return {comparison: {metric: {
        'delta_percentage_points': result['delta'] * 100,
        'ci95_percentage_points': [value * 100 for value in result['ci95']],
        'article_clusters': result['article_clusters'],
        'repetitions': result['repetitions'], 'seed': result['seed'],
    } for metric, result in metrics.items()} for comparison, metrics in family.items()}


def atomic_write(path, text):
    path = Path(path)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def build(primary_dir, diagnostic_dir, output_dir):
    loaded = {role: load_complete(directory, role)
              for role, directory in [('primary', primary_dir), ('diagnostic', diagnostic_dir)]}
    cohorts = {}
    table_rows = []
    for role, (summary, _, _, _) in loaded.items():
        cohorts[role] = {key: summary[key] for key in [
            'track', 'selection', 'n_questions', 'n_articles', 'n_logical_conditions',
            'n_unique_generations_used', 'parse_failures_unique', 'parse_failures_by_method',
            'parse_failure_reasons', 'answer_changes', 'reader_pairwise_article_intervals',
            'prespecified_frontend_intervals']}
        cohorts[role]['metrics'] = {
            method: {'exact_match_fraction': summary['metrics'][method][EM],
                     'strict_set_f1_fraction': summary['metrics'][method][F1],
                     'exact_match_percent': summary['metrics'][method][EM] * 100,
                     'strict_set_f1_percent': summary['metrics'][method][F1] * 100}
            for method, _ in METHODS}
        cohorts[role]['paired_intervals_percentage_points'] = percent_intervals(summary['reader_pairwise_article_intervals'])
        cohorts[role]['frontend_intervals_percentage_points'] = percent_intervals(summary['prespecified_frontend_intervals'])
        cohorts[role]['answer_change_percentages'] = {name: result['fraction'] * 100
                                                    for name, result in summary['answer_changes'].items()}
    for method, label in METHODS:
        values = [cohorts[role]['metrics'][method][metric]
                  for role in ('primary', 'diagnostic')
                  for metric in ('exact_match_percent', 'strict_set_f1_percent')]
        table_rows.append(label + ' & ' + ' & '.join(f'{value:.2f}' for value in values) + r'\\')
    primary, diagnostic = cohorts['primary'], cohorts['diagnostic']
    caption = (
        r'Reader exact match (EM) and strict answer-set F1 (\%). '
        'Primary: 60 questions and 600 conditions. Diagnostic: 11 questions and 110 conditions. '
        f"Unique generation parse failures: {primary['parse_failures_unique']}/{primary['n_unique_generations_used']} "
        f"and {diagnostic['parse_failures_unique']}/{diagnostic['n_unique_generations_used']}, respectively. "
        'Failures remain in both denominators.')
    latex = '\n'.join([
        '% Generated only from complete frozen-scoring outputs.',
        r'\begin{table}[t]', r'\centering\footnotesize', r'\setlength{\tabcolsep}{3pt}',
        r'\begin{tabular}{@{}lrrrr@{}}', r'\toprule',
        r' & \multicolumn{2}{c}{Primary} & \multicolumn{2}{c}{Diagnostic}\\',
        r'Method & EM & F1 & EM & F1\\', r'\midrule', *table_rows,
        r'\bottomrule', r'\end{tabular}', r'\caption{' + caption + '}',
        r'\label{tab:reader}', r'\end{table}', '',
    ])
    main_rows = [label + ' & ' + ' & '.join(
        f"{cohorts[role]['metrics'][method]['strict_set_f1_percent']:.2f}"
        for role in ('primary', 'diagnostic')) + r'\\'
        for method, label in METHODS]
    main_caption = (
        r'Strict answer-set F1 (\%). The primary sample has 60 questions. '
        'The diagnostic selects eleven questions with differing possible and guaranteed contexts.')
    main_latex = '\n'.join([
        '% Generated only from complete frozen-scoring outputs.',
        r'\begin{table}[t]', r'\centering\small',
        r'\begin{tabular}{@{}lrr@{}}', r'\toprule',
        r'Method & Primary & Diagnostic\\', r'\midrule', *main_rows,
        r'\bottomrule', r'\end{tabular}', r'\caption{' + main_caption + '}',
        r'\label{tab:reader_main}', r'\end{table}', '',
    ])
    all_jobs = {}
    for role, (_, _, jobs, _) in loaded.items():
        for jid, state in jobs.items():
            require(jid not in all_jobs or all_jobs[jid] == state,
                    'A generation shared by cohorts has conflicting parse outcomes.')
            all_jobs[jid] = state
    question_sets = [loaded[role][1] for role in ('primary', 'diagnostic')]
    payload = {
        'schema_version': 1,
        'source': 'Completed saved outputs of the unchanged frozen pass4 reader scorer.',
        'score_definitions': {'exact_match': 'Exact normalized annotated answer-set match.',
                              'strict_set_f1': 'F1 over normalized annotated answer strings; articles are preserved.',
                              'failure_policy': 'Parse failures use empty predicted answers and remain in every question denominator.'},
        'method_order': [method for method, _ in METHODS],
        'cohorts': cohorts,
        'combined_counts_only': {
            'unique_questions': len(set.union(*question_sets)),
            'overlapping_question_ids': sorted(set.intersection(*question_sets)),
            'logical_conditions': primary['n_logical_conditions'] + diagnostic['n_logical_conditions'],
            'unique_generations_used': len(all_jobs),
            'shared_generations': len(loaded['primary'][2].keys() & loaded['diagnostic'][2].keys()),
            'parse_failures_unique': sum(not state[0] for state in all_jobs.values()),
            'interpretation': 'Primary and diagnostic scores remain separate; metrics are not pooled.'},
        'provenance': {'frozen_reader_scorer_sha256': SCORER_SHA256,
                       'frozen_parser_sha256': PARSER_SHA256,
                       'frozen_answer_scorer_sha256': ANSWER_SCORER_SHA256,
                       'saved_score_files_sha256': {role: data[3] for role, data in loaded.items()}},
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {'reader.tex': latex,
                 'reader_main.tex': main_latex,
                 'paper_reader_results.json': json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + '\n'}
    manifest = {'generator_sha256': digest(__file__),
                'input_sha256': {role: data[3] for role, data in loaded.items()},
                'output_sha256': {name: hashlib.sha256(text.encode()).hexdigest() for name, text in artifacts.items()},
                'full_cohorts_verified': {'primary_questions': 60, 'diagnostic_questions': 11,
                                          'primary_conditions': 600, 'diagnostic_conditions': 110,
                                          'methods_per_question': 10},
                'runtime_dependencies': 'Python standard library only.',
                'determinism': 'No runtime paths, timestamps, or random resampling enter generated files.'}
    for name, text in artifacts.items():
        atomic_write(output_dir / name, text)
    atomic_write(output_dir / 'reader_build_manifest.json', json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--primary-score-dir', type=Path, required=True)
    parser.add_argument('--diagnostic-score-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'pass4/pipeline')
    args = parser.parse_args()
    try:
        manifest = build(args.primary_score_dir, args.diagnostic_score_dir, args.output_dir)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
