#!/usr/bin/env python3
"""Compare temporal policies with exactly the same text-derived candidate pairs."""
import hashlib,json,math,pathlib,sys
H=pathlib.Path(__file__).resolve().parent;R=H.parents[1];O=H/'results'
sys.path.insert(0,str(R/'pass2/baselines'))
from policies import graphiti_endpoints,direct_first_endpoints,latest_batch_endpoints
rows=[json.loads(l) for l in (O/'observations.jsonl').open()]
obs=[{k:r[k] for k in ('cid','text','timestamp')} for r in rows]
parsed=[r['parsed'] for r in rows]
for p in parsed:
 if p['slot'] is not None:p['slot']=tuple(p['slot'])
a,diag=graphiti_endpoints(obs,parsed);b=direct_first_endpoints(obs,parsed);c=latest_batch_endpoints(obs,parsed)
out={'n_observations':len(obs),'graphiti_equals_exact_direct_first':a==b,'n_different_endpoints':sum(x!=y for x,y in zip(a,b)),'graphiti_equals_latest_batch':a==c,'n_latest_batch_differences':sum(x!=y for x,y in zip(a,c)),'endpoints_sha256':hashlib.sha256(json.dumps(a).encode()).hexdigest(),'input_observations_sha256':hashlib.sha256((O/'observations.jsonl').read_bytes()).hexdigest(),'interpretation':['This comparison supplies both policies with identical parsed slots and values.','The old lexical predicate has a different matcher and is a separate condition.','Equality concerns the temporal policy, not the complete Graphiti system.'],'upstream_diagnostics':diag}
(O/'matched_policy_validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='upstream_diagnostics'},indent=2))
assert a==b
