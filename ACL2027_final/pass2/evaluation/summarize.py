#!/usr/bin/env python3
"""Key-cluster confidence intervals and paper-ready tables from frozen predictions."""
import collections,csv,hashlib,json,pathlib
import numpy as np
H=pathlib.Path(__file__).resolve().parent;O=H/'results'
METHODS=['bm25','bm25_recent_tie','date_top5','date_full_pool','age_development_selected','old_earliest','old_latest_witness','graphiti_policy','exact_latest_batch','query_latest_single','query_latest_batch','query_history_distinct','dev_capacity_latest_values']
METRICS=['hit1','value_recall5','valid_value_suppression','stale_value_exposure5']
def dump(path,x):path.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
records=[json.loads(l) for l in (O/'predictions.jsonl').open() if '"split":"test"' in l]
rng=np.random.default_rng(20261006); summaries={}
for name,rr in [('all',records),('historical',[r for r in records if r['kind']=='historical']),('latest',[r for r in records if r['kind']=='latest']),('multi_answer',[r for r in records if r['multi_answer']])]:
 grouped=collections.defaultdict(list)
 for r in rr:grouped[r['key']].append(r)
 keys=sorted(grouped);columns=[(m,metric) for m in METHODS for metric in METRICS]
 sums=np.array([[sum(r['methods'][m][metric] for r in grouped[k]) for m,metric in columns] for k in keys])
 counts=np.array([len(grouped[k]) for k in keys]); estimates=sums.sum(0)/counts.sum(); draws=[]
 # Resample whole source keys; retain every snapshot within each selected key.
 for chunk in range(20):
  weights=rng.multinomial(len(keys),np.full(len(keys),1/len(keys)),size=250)
  draws.append((weights@sums)/(weights@counts)[:,None])
 draws=np.concatenate(draws); low,high=np.quantile(draws,[.025,.975],axis=0)
 summary={'n_rows':len(rr),'n_keys':len(keys),'methods':{},'contrasts':{}}
 for i,(m,metric) in enumerate(columns):summary['methods'].setdefault(m,{})[metric]={'estimate':float(estimates[i]),'ci95':[float(low[i]),float(high[i])]}
 for a,b in [('query_latest_batch','old_earliest'),('query_latest_batch','graphiti_policy'),('query_latest_batch','age_development_selected'),('query_latest_batch','date_full_pool'),('query_latest_batch','query_latest_single'),('graphiti_policy','old_earliest')]:
  summary['contrasts'][a+' - '+b]={}
  for metric in METRICS:
   i=columns.index((a,metric));j=columns.index((b,metric));ci=np.quantile(draws[:,i]-draws[:,j],[.025,.975])
   summary['contrasts'][a+' - '+b][metric]={'difference':float(estimates[i]-estimates[j]),'ci95':ci.tolist()}
 summaries[name]=summary
 print('bootstrap',name,flush=True)
dump(O/'cluster_intervals.json',{'seed':20261006,'repetitions':5000,'sampling_unit':'complete source key','estimand':'row-weighted snapshot mean','notes':['Confidence intervals measure variation across benchmark keys.','They do not represent a population of arbitrary real-world facts.'],'test':summaries})
with (O/'main_table.csv').open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['method']+[s for metric in METRICS for s in (metric,metric+'_ci_low',metric+'_ci_high')])
 for m in METHODS:
  writer.writerow([m]+[v for metric in METRICS for v in (summaries['all']['methods'][m][metric]['estimate'],*summaries['all']['methods'][m][metric]['ci95'])])
# Provenance covers implementation, split and source inputs, plus all results except itself.
manifest={'protocol':'all-positive-source-observations-v1','files':{str(p.relative_to(H)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(H.rglob('*')) if p.is_file() and p.name!='run_manifest.json' and '__pycache__' not in str(p) and not any(part.startswith('.') for part in p.relative_to(H).parts)},'upstream_policy_provenance':'../baselines/vendor/PROVENANCE.json'}
dump(O/'run_manifest.json',manifest)
