#!/usr/bin/env python3
"""Score source-single-valued query keys without changing the full retrieval pool."""
import json
from run_evidence import HERE,bootstrap_delta,write_json
out=HERE/'results'
keys=set(json.loads((out/'templama_single_value_keys.json').read_text()))
rows=[json.loads(l) for l in (out/'templama_predictions.jsonl').read_text().splitlines()]
rows=[r for r in rows if '_'.join(k.upper() for k in r['key']) in keys]
summary={}
for kind in ('current','historical'):
 a=[r for r in rows if r['kind']==kind]
 summary[kind]={'n':len(a),'n_keys':len({tuple(r['key']) for r in a}),
 'methods':{m:{metric:sum(r['methods'][m][metric] for r in a)/len(a) for metric in ('hit1','hit5','value_hit1','stale_exposure5','relevant_precision5','wrong_key1')} for m in a[0]['methods']},
 'comparisons':{m:bootstrap_delta(a,'direct_first',m) for m in ('bm25','component','exact_group_latest','direct_last')}}
write_json(out/'templama_single_value_results.json',{'filter':'all source years have exactly one answer QID','n_pool_claims':747,'selection_uses_source_metadata_only':True,'results':summary})
