#!/usr/bin/env python3
"""Key-cluster intervals for pre-existing source label audit rates."""
import collections,json,pathlib
import numpy as np
H=pathlib.Path(__file__).resolve().parent;O=H/'results'
keys=json.loads((H/'split_manifest.json').read_text())['keys'];test=sorted(k for k,s in keys.items() if s=='test');index={k:i for i,k in enumerate(test)}
source=H.parents[1]/'work/external/TempLAMA_official_test.json'
counts=np.zeros((len(test),6))
for r in map(json.loads,source.open()):
 k=r['id'].rsplit('_',1)[0]
 if k not in index:continue
 i=index[k]; counts[i,0]+=len({a['wikidata_id'] for a in r['answer']})>1; counts[i,1]+=1
for e in map(json.loads,(O/'source_transitions.jsonl').open()):
 if e['split']!='test':continue
 i=index[e['key']];counts[i,2]+=e['first_changed'] and e['previous_first_retained'];counts[i,3]+=e['first_changed']
 changed=bool(e['added'] or e['absent_from_next_label']);counts[i,4]+=changed and bool(e['retained']);counts[i,5]+=changed
rng=np.random.default_rng(20261006);draws=[]
for _ in range(20):
 w=rng.multinomial(len(test),np.ones(len(test))/len(test),size=250);z=w@counts;draws.append(z[:,::2]/z[:,1::2])
d=np.concatenate(draws);s=counts.sum(0);rates=s[::2]/s[1::2];low,high=np.quantile(d,[.025,.975],axis=0)
out={'split':'test','n_keys':len(test),'repetitions':5000,'seed':20261006,'resampling':'complete source keys','rates':{name:{'numerator':int(s[2*i]),'denominator':int(s[2*i+1]),'estimate':float(rates[i]),'ci95':[float(low[i]),float(high[i])]} for i,name in enumerate(['multiple_annual_answers','changed_first_answer_retains_previous_first','changed_answer_set_retains_value'])}}
(O/'source_audit_intervals.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
