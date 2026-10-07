#!/usr/bin/env python3
"""Rescore frozen retrieved CIDs against complete original TempLAMA answer sets.

The fixed 747-claim pool and all rankings remain unchanged. At each cutoff, use
that key's most recent observed yearly answer set. This evaluates the released
snapshot history; it does not assert truth beyond the source observation dates.
"""
import bisect,collections,json,pathlib,sys
from run_evidence import DEFAULT_SOURCE,HERE,bootstrap_delta,write_json
out=HERE/'results'
source_rows=json.loads((out/'templama_source_rows.json').read_text())
source=collections.defaultdict(list)
for row in source_rows: source[row['key'].lower()].append(row)
for key in source:source[key].sort(key=lambda row:int(row['date']))
dates={key:[int(row['date']) for row in rows] for key,rows in source.items()}
def state(key,t):
 pos=bisect.bisect_right(dates[key],t)-1
 if pos<0:return set(),None
 row=source[key][pos]
 return set(row['answer_qids']),row['date']
claims={c['cid']:c for c in [json.loads(l) for l in (DEFAULT_SOURCE/'data/templama/claims.jsonl').read_text().splitlines()]}
old=[json.loads(l) for l in (out/'templama_predictions.jsonl').read_text().splitlines()]
rows=[]
for row in old:
 key='_'.join(row['key']); allowed,date=state(key,row['cutoff'])
 result=dict(dataset='templama',key=row['key'],question=row['question'],cutoff=row['cutoff'],kind=row['kind'],source_date=date,source_answer_qids=sorted(allowed),methods={})
 for method,pred in row['methods'].items():
  top=pred['cids']; hits=[]; stale=[]
  for cid in top:
   c=claims[cid]; ck=c['meta']['key'].lower(); qid=c['meta']['answer_qid']; cstate,cdate=state(ck,row['cutoff'])
   hits.append(ck==key and qid in allowed); stale.append(qid not in cstate)
  result['methods'][method]=dict(cids=top,hit1=int(bool(hits) and hits[0]),hit5=int(any(hits)),stale_exposure5=int(any(stale)),relevant_precision5=sum(hits)/len(hits) if hits else 0)
 rows.append(result)
summary={}
for kind in ('historical','current'):
 subset=[r for r in rows if r['kind']==kind]
 summary[kind]=dict(n=len(subset),n_keys=len({tuple(r['key']) for r in subset}),methods={m:{metric:sum(r['methods'][m][metric] for r in subset)/len(subset) for metric in ('hit1','hit5','stale_exposure5','relevant_precision5')} for m in subset[0]['methods']},comparisons={m:bootstrap_delta(subset,'direct_first',m) for m in ('bm25','component','exact_group_latest','direct_last')})
with (out/'templama_source_set_predictions.jsonl').open('w') as f:
 for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
write_json(out/'templama_source_set_results.json',dict(protocol='complete-source-answer-sets-v1',pool_claims=747,pool_keys=300,n_original_source_rows=len(source_rows),
 notes=['No ranking or matcher changes from full-pool-lexical-evidence-v1.','All answer QIDs from the original yearly source are accepted.','At a cutoff, each key uses its most recent observed yearly source state.','States persist between observations and after the final observation within this snapshot evaluation.','The oracle condition remains the old first-answer oracle and is not a source-set oracle.','These are evidence selection metrics, not reader or generation metrics.','This source audit is a post-hoc development evaluation with no parameter tuning.'],results=summary))
print(json.dumps({kind:{m:round(v['hit1'],4) for m,v in block['methods'].items()} for kind,block in summary.items()},indent=2))
