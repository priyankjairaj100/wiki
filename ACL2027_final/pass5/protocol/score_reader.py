"""Score complete revised reader cohorts with the unchanged pass-3 parser.

Membership, source contexts, full prompts, and request hashes are checked before
scoring. Missing questions or methods cause failure, never silent exclusion.
"""
from __future__ import annotations
import argparse
import collections
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pass3.protocol.parse_reader import parse_response
from pass3.protocol.score_predictions import read, run, normalize, paired_bootstrap
from pass5.pipeline.run_matched import prompt_for

PARSER = ROOT / 'pass3/protocol/parse_reader.py'
PARSER_FREEZE = ROOT / 'pass3/protocol/reader_parser_freeze.json'
PRIMARY_QUERIES = ROOT / 'pass5/protocol/reader_primary_queries.jsonl'
PRIMARY_MANIFEST = ROOT / 'pass5/protocol/reader_sample_manifest.json'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def unique_by(rows, key, description):
    mapped = {}
    for row in rows:
        identifier = row[key]
        if identifier in mapped:
            raise ValueError('Duplicate ' + description + ': ' + str(identifier))
        mapped[identifier] = row
    return mapped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=Path, nargs='+', required=True)
    ap.add_argument('--outputs', type=Path, nargs='+', required=True)
    ap.add_argument('--membership', type=Path, required=True)
    ap.add_argument('--cohort-queries', type=Path)
    ap.add_argument('--predictions', type=Path, required=True)
    ap.add_argument('--labels', type=Path, required=True)
    ap.add_argument('--passages', type=Path, required=True)
    ap.add_argument('--config', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--track', choices=['human_confirmation', 'context_sensitive_diagnostic'], required=True)
    args = ap.parse_args()
    freeze = json.loads(PARSER_FREEZE.read_text())
    if digest(PARSER) != freeze['parser_sha256']:
        raise ValueError('The frozen pass-3 reader parser changed.')
    if args.track == 'human_confirmation':
        cohort_path = args.cohort_queries or PRIMARY_QUERIES
        primary = json.loads(PRIMARY_MANIFEST.read_text())
        if digest(cohort_path) != primary['sample_sha256']:
            raise ValueError('Primary reader membership differs from the frozen 60-question sample.')
    else:
        if args.cohort_queries is None:
            raise ValueError('Diagnostic scoring requires its frozen cohort query file.')
        cohort_path = args.cohort_queries
    cohort = unique_by(read(cohort_path), 'question_id', 'cohort query')
    if not cohort:
        raise ValueError('Cannot score an empty cohort.')
    config = json.loads(args.config.read_text())
    methods = set(config['methods'])
    jobs = {}
    for path in args.jobs:
        for job in read(path):
            jid = job['job_id']
            if jid in jobs and jobs[jid] != job:
                raise ValueError('Conflicting duplicate job.')
            if hashlib.sha256(job['prompt'].encode()).hexdigest() != jid:
                raise ValueError('Job identifier does not hash its frozen prompt.')
            jobs[jid] = job
    outputs = unique_by([row for path in args.outputs for row in read(path)], 'id', 'generation ID')
    membership = read(args.membership)
    pairs = [(row['question_id'], row['method']) for row in membership]
    expected = set(itertools.product(cohort, methods))
    if len(set(pairs)) != len(pairs):
        raise ValueError('Duplicate question/method membership.')
    if set(pairs) != expected:
        raise ValueError('Membership does not supply every frozen question and method exactly once.')
    used_jobs = {row['job_id'] for row in membership}
    if not used_jobs <= set(jobs):
        raise ValueError('A membership lacks its frozen reader job.')
    if not used_jobs <= set(outputs):
        raise ValueError('Missing generations; never score a partial cohort.')
    source_predictions = unique_by(read(args.predictions), 'question_id', 'prediction')
    if not set(cohort) <= set(source_predictions):
        raise ValueError('A frozen question lacks source predictions.')
    predictions = {qid: copy.deepcopy(source_predictions[qid]) for qid in cohort}
    parsed = {}
    for jid in sorted(used_jobs):
        job, response = jobs[jid], outputs[jid]
        user_messages = [m['content'] for m in response['request']['messages'] if m['role'] == 'user']
        if user_messages != [job['prompt']]:
            raise ValueError('Reader request does not equal its frozen prompt.')
        calculated = hashlib.sha256(json.dumps(response['request'], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if calculated != response['request_sha256']:
            raise ValueError('Request hash mismatch.')
        parsed[jid] = parse_response(response['generation'], len(job['contexts']), response['finish_reason'])
    audit = []
    for member in membership:
        qid, method, jid = member['question_id'], member['method'], member['job_id']
        prediction = predictions[qid]['methods'][method]
        job = jobs[jid]
        if member.get('context_signature', prediction['context_signature']) != prediction['context_signature']:
            raise ValueError('Membership context signature mismatch.')
        # Identical rendered prompts can arise from different source IDs.
        # The membership binds the actual source offsets for each condition.
        # This check also prevents wrong-query reuse when contexts happen to match.
        if prompt_for(cohort[qid], prediction['contexts']) != job['prompt']:
            raise ValueError('Reader job does not render this question and these exact contexts.')
        result = parsed[jid]
        prediction['answers'] = result['answers']
        prediction['reader_parse_ok'] = result['parse_ok']
        prediction['reader_evidence'] = result['evidence']
        audit.append(dict(member, parse_ok=result['parse_ok'], parse_failure=result['parse_failure'],
                          finish_reason=outputs[jid]['finish_reason'], prediction_answers=result['answers'],
                          evidence=result['evidence'],
                          deduplicated_context_signature_differs=(prediction['context_signature'] != job['context_signature'])))
    labels = [row for row in read(args.labels) if row['question_id'] in cohort]
    passages = unique_by(read(args.passages), 'passage_id', 'source passage')
    scored, summary = run(labels, list(predictions.values()), passages, config)
    summary['track'] = args.track
    summary['selection'] = (
        'Fixed 60-question pass-4 sample reused after source audit; same previously inspected human track.'
        if args.track == 'human_confirmation' else
        'Fixed 11-question pass-4 diagnostic reused after source audit; membership is unchanged.')
    summary['n_logical_conditions'] = len(membership)
    summary['n_unique_generations_used'] = len(used_jobs)
    summary['parse_failures_unique'] = sum(not parsed[jid]['parse_ok'] for jid in used_jobs)
    summary['parse_failures_by_method'] = {method: sum(not row['parse_ok'] for row in audit if row['method'] == method)
                                         for method in sorted(methods)}
    summary['parse_failure_reasons'] = dict(collections.Counter(row['parse_failure'] for row in audit if not row['parse_ok']))
    contrasts = [
        ('earliest_completion', 'latest_completion'),
        ('possible_support', 'guaranteed_support'),
        ('possible_support', 'interval_outer_control'),
        ('possible_support', 'latest_mentioned_year_top20'),
        ('no_temporal_filter', 'original_bm25_latestyear'),
        ('no_temporal_filter', 'original_bm25'),
        ('possible_support', 'original_bm25_latestyear'),
        ('latest_mentioned_year_top20', 'original_bm25_latestyear'),
    ]
    summary['answer_changes'] = {}
    for left, right in contrasts:
        if not {left, right} <= methods:
            continue
        differences = sum(
            {normalize(x) for x in predictions[qid]['methods'][left]['answers']} !=
            {normalize(x) for x in predictions[qid]['methods'][right]['answers']}
            for qid in cohort)
        summary['answer_changes'][left + '__' + right] = {
            'queries': differences, 'denominator': len(cohort), 'fraction': differences / len(cohort)}
    summary['reader_pairwise_article_intervals'] = {}
    for reference, method in itertools.combinations(sorted(methods), 2):
        summary['reader_pairwise_article_intervals'][method + '__' + reference] = {
            metric: paired_bootstrap(scored, method, reference, metric,
                                     config['statistics']['paired_resamples'], config['statistics']['seed'])
            for metric in ['exact_annotated_answer_set', 'annotated_answer_set_f1']}
    summary['prespecified_frontend_intervals'] = {}
    for method, reference in config['statistics'].get('prespecified_frontend_contrasts', []):
        if not {method, reference} <= methods:
            continue
        summary['prespecified_frontend_intervals'][method + '__' + reference] = {
            metric: paired_bootstrap(scored, method, reference, metric,
                                     config['statistics']['paired_resamples'], config['statistics']['seed'])
            for metric in ['exact_annotated_answer_set', 'annotated_answer_set_f1']}
    files = (args.jobs + args.outputs + [args.membership, cohort_path, args.predictions, args.labels,
             args.passages, args.config, Path(__file__), PARSER, PARSER_FREEZE,
             ROOT / 'pass3/protocol/score_predictions.py', ROOT / 'pass5/pipeline/run_matched.py'])
    summary['input_sha256'] = {str(path): digest(path) for path in files}
    args.output.mkdir(parents=True, exist_ok=True)
    save(args.output / 'summary.json', summary)
    for name, rows in [('scored_questions', scored), ('predictions_with_reader', predictions.values()),
                       ('reader_parse_audit', audit)]:
        (args.output / (name + '.jsonl')).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    print(json.dumps({key: summary[key] for key in ['track', 'n_questions', 'n_articles',
                     'n_logical_conditions', 'n_unique_generations_used', 'parse_failures_unique',
                     'metrics', 'answer_changes']}, indent=2))


if __name__ == '__main__':
    main()
