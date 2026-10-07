"""Build a declared diagnostic reader cohort from context disagreements only."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read,lines,dump,digest,prompt_for,sha

def build(folder):
    folder=Path(folder);audit=read(folder/'mechanism_questions.jsonl')
    qids={r['question_id'] for r in audit if r['completion_sensitive']}
    existing=read(folder/'reader_jobs.jsonl');existingids={r['job_id'] for r in existing}
    queries={q['question_id']:q for q in read(ROOT/'pass3/protocol/dev_pilot_queries.jsonl')}
    jobs={};membership=[]
    for p in read(folder/'predictions.jsonl'):
        if p['question_id'] not in qids:continue
        q=queries[p['question_id']]
        for method,item in p['methods'].items():
            prompt=prompt_for(q,item['contexts']);jobid=digest(prompt)
            membership.append({'question_id':q['question_id'],'method':method,'job_id':jobid,'already_in_primary_pilot':jobid in existingids})
            if jobid in existingids:continue
            job=jobs.setdefault(jobid,{'job_id':jobid,'question_id':q['question_id'],'question':q['question'],'prompt':prompt,'methods':[],'context_signature':item['context_signature'],'contexts':item['contexts'],'provenance':{'cohort':'completion-sensitive pilot diagnostic','selection':'All pilot queries where earliest, midpoint, and latest returned different contexts','gold_used_for_selection':False,'not_primary_qa_benchmark':True,'prediction_sha256':sha(folder/'predictions.jsonl')}})
            job['methods'].append(method)
    lines(folder/'reader_mechanism_jobs.jsonl',jobs.values());lines(folder/'reader_mechanism_membership.jsonl',membership)
    manifest={'cohort':'All completion-sensitive pilot queries','queries':len(qids),'question_ids':sorted(qids),'new_jobs':len(jobs),'reused_jobs':len({r['job_id'] for r in membership if r['already_in_primary_pilot']}),'method_conditions':len(membership),'selection_uses_gold':False,'primary_qa_benchmark':False,'files':{n:sha(folder/n) for n in ['reader_mechanism_jobs.jsonl','reader_mechanism_membership.jsonl','reader_jobs.jsonl','mechanism_questions.jsonl','predictions.jsonl']}}
    dump(folder/'reader_mechanism_manifest.json',manifest);print(json.dumps(manifest,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',default='pass3/pipeline/pilot_final');a=p.parse_args();build(a.folder)
