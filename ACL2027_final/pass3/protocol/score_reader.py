"""Join actual local generations to frozen contexts and score complete answers."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import collections
from parse_reader import parse_response
from score_predictions import read,run,normalize,paired_bootstrap

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--jobs',type=Path,nargs='+',required=True)
    ap.add_argument('--outputs',type=Path,nargs='+',required=True)
    ap.add_argument('--membership',type=Path)
    ap.add_argument('--predictions',type=Path,required=True)
    ap.add_argument('--labels',type=Path,required=True)
    ap.add_argument('--passages',type=Path,required=True)
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--track',choices=['hash_pilot','completion_sensitive_diagnostic'],required=True)
    args=ap.parse_args()
    freeze=json.loads(Path(__file__).with_name('reader_parser_freeze.json').read_text())
    assert digest(Path(__file__).with_name('parse_reader.py'))==freeze['parser_sha256']
    config=json.loads(args.config.read_text())
    jobs={}
    for path in args.jobs:
        for j in read(path):
            jid=j['job_id']
            if jid in jobs and jobs[jid]!=j:raise ValueError('Conflicting duplicate job.')
            jobs[jid]=j
    outputs={}
    for path in args.outputs:
        for r in read(path):
            if r['id'] in outputs:raise ValueError('Duplicate generation ID.')
            outputs[r['id']]=r
    if not set(jobs)<=set(outputs):raise ValueError(f'Missing {len(set(jobs)-set(outputs))} generations; never score a partial cohort.')
    if args.membership:
        membership=read(args.membership)
    else:
        membership=[{'question_id':j['question_id'],'method':m,'job_id':j['job_id']} for j in jobs.values() for m in j['methods']]
    qids={r['question_id'] for r in membership}
    source_predictions={r['question_id']:r for r in read(args.predictions)}
    predictions={qid:copy.deepcopy(source_predictions[qid]) for qid in qids}
    parsed={}
    for jid,j in jobs.items():
        response=outputs[jid]
        messages=response['request']['messages']
        user_messages=[m['content'] for m in messages if m['role']=='user']
        if user_messages!=[j['prompt']]:raise ValueError('Reader request does not equal frozen prompt.')
        calculated=hashlib.sha256(json.dumps(response['request'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        if calculated!=response['request_sha256']:raise ValueError('Request hash mismatch.')
        parsed[jid]=parse_response(response['generation'],len(j['contexts']),response['finish_reason'])
    pairs=set()
    audit=[]
    for member in membership:
        qid,m,jid=member['question_id'],member['method'],member['job_id']
        if (qid,m) in pairs:raise ValueError('Duplicate question/method membership.')
        pairs.add((qid,m))
        prediction=predictions[qid]['methods'][m]
        job=jobs[jid]
        if prediction['context_signature']!=job['context_signature']:raise ValueError('Context signature differs from frozen reader job.')
        result=parsed[jid]
        prediction['answers']=result['answers']
        prediction['reader_parse_ok']=result['parse_ok']
        prediction['reader_evidence']=result['evidence']
        audit.append(dict(member,parse_ok=result['parse_ok'],parse_failure=result['parse_failure'],
                finish_reason=outputs[jid]['finish_reason'],prediction_answers=result['answers'],evidence=result['evidence']))
    expected={(qid,m) for qid in qids for m in config['methods']}
    if pairs!=expected:raise ValueError('Missing method conditions in frozen cohort.')
    labels=[r for r in read(args.labels) if r['question_id'] in qids]
    passages={r['passage_id']:r for r in read(args.passages)}
    scored,summary=run(labels,list(predictions.values()),passages,config)
    summary['track']=args.track
    summary['selection']='Fixed question-ID hash sample before answer generation.' if args.track=='hash_pilot' else 'All completion-sensitive pilot queries; descriptive mechanism slice, not an independent benchmark.'
    summary['n_logical_conditions']=len(membership)
    summary['n_unique_generations_used']=len({r['job_id'] for r in membership})
    summary['parse_failures_unique']=sum(not parsed[jid]['parse_ok'] for jid in {r['job_id'] for r in membership})
    summary['parse_failures_by_method']={m:sum(not r['parse_ok'] for r in audit if r['method']==m) for m in config['methods']}
    summary['parse_failure_reasons']=dict(collections.Counter(r['parse_failure'] for r in audit if not r['parse_ok']))
    summary['answer_changes']={}
    for left,right in [('earliest_completion','latest_completion'),('possible_support','guaranteed_support'),('possible_support','interval_outer_control'),('possible_support','latest_mentioned_year_top20')]:
        differences=0
        for qid in qids:
            a={normalize(x) for x in predictions[qid]['methods'][left]['answers']}
            b={normalize(x) for x in predictions[qid]['methods'][right]['answers']}
            differences+=a!=b
        summary['answer_changes'][left+'__'+right]={'queries':differences,'denominator':len(qids),'fraction':differences/len(qids)}
    summary['reader_pairwise_article_intervals']={}
    metric='annotated_answer_set_f1'
    methods=sorted(config['methods'])
    for i,m in enumerate(methods):
        for reference in methods[:i]:
            summary['reader_pairwise_article_intervals'][m+'__'+reference]=paired_bootstrap(scored,m,reference,metric,
              config['statistics']['paired_resamples'],config['statistics']['seed'])
    files=args.jobs+args.outputs+[args.predictions,args.labels,args.passages,args.config,Path(__file__),Path(__file__).with_name('parse_reader.py')]
    if args.membership:files.append(args.membership)
    summary['input_sha256']={str(p):digest(p) for p in files}
    args.output.mkdir(parents=True,exist_ok=True)
    save(args.output/'summary.json',summary)
    for name,rows in [('scored_questions',scored),('predictions_with_reader',predictions.values()),('reader_parse_audit',audit)]:
        (args.output/(name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    print(json.dumps({k:summary[k] for k in ['track','n_questions','n_articles','n_logical_conditions','n_unique_generations_used','parse_failures_unique','metrics','answer_changes']},indent=2))
if __name__=='__main__':main()
