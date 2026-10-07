"""Build the predeclared context-sensitive cohort without answer labels."""
from pathlib import Path
import hashlib,json,datetime as dt,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass4.pipeline.run_matched import read,dump,lines,digest,prompt_for,sha

def run():
    folder=ROOT/'pass4/pipeline/human';out=ROOT/'pass4/pipeline/human_diagnostic';out.mkdir(exist_ok=True)
    config=json.loads((ROOT/'pass4/protocol/config.json').read_text())
    audits=read(folder/'mechanism_questions.jsonl')
    eligible={r['question_id'] for r in audits if r['query_time_parsed'] and r['reader_context_certificate'] is False}
    predictions=[p for p in read(folder/'predictions.jsonl') if p['question_id'] in eligible]
    seed=config['selection_seed']+'-diagnostic'
    predictions=sorted(predictions,key=lambda p:digest(seed+'\0'+p['question_id']))[:config['reader']['diagnostic_max_questions']]
    primary={j['job_id']:j for j in read(folder/'reader_jobs.jsonl')}
    jobs={};members=[]
    for p in predictions:
        for method,m in p['methods'].items():
            prompt=prompt_for(p,m['contexts']);jid=digest(prompt)
            j=jobs.setdefault(jid,{'job_id':jid,'question_id':p['question_id'],'question':p['question'],'prompt':prompt,'methods':[],'context_signature':m['context_signature'],'contexts':m['contexts']})
            j['methods'].append(method)
            members.append({'question_id':p['question_id'],'method':method,'job_id':jid,'context_signature':m['context_signature']})
    lines(out/'reader_jobs.jsonl',jobs.values());lines(out/'reader_memberships.jsonl',members)
    lines(out/'reader_additional_jobs.jsonl',[j for jid,j in jobs.items() if jid not in primary])
    lines(out/'queries.jsonl',[{'question_id':p['question_id'],'question':p['question']} for p in predictions])
    dump(out/'freeze.json',{'recorded_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'selection':'Predeclared rendered possible/guaranteed context disagreement, hash order, maximum24. No answer labels or outputs read.','eligible_queries':len(eligible),'selected_queries':len(predictions),'conditions':len(members),'unique_jobs':len(jobs),'additional_jobs':len(set(jobs)-set(primary)),'reused_jobs':len(set(jobs)&set(primary)),'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [folder/'predictions.jsonl',folder/'mechanism_questions.jsonl',folder/'reader_jobs.jsonl',ROOT/'pass4/protocol/config.json',Path(__file__)]},'outputs':{p.name:sha(p) for p in out.glob('*.jsonl')}})
    print((out/'freeze.json').read_text())
if __name__=='__main__':run()
