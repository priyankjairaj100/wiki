"""Check lazy selection against full masks and previously saved matched runs.

Ranking and compilation are excluded from the reported selection times.
No gold labels are read. Timing reports medians of repeated calls per query.
"""
from __future__ import annotations
import argparse,hashlib,json,statistics,sys,time
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read,parse_query
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles
from pass3.extraction.source_adapter import build_pairs
from pass4.retrieval.ranking import TitleRanker
from pass4.retrieval.lazy_certificate import select_lazy

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def full_masks(rank,units,index,window,k):
    a,b=window
    possible={cid for cid,c in index.certificates.items() if c.possible(a,b)}
    certain={cid for cid,c in index.certificates.items() if c.guaranteed(a,b)}
    def select(mask):
        chosen=[]
        if k:
            for i in rank:
                if units[i]['claim_id'] is None or units[i]['claim_id'] in mask:
                    chosen.append(units[i]['unit_id'])
                    if len(chosen)==k:break
        return chosen
    p,h=select(possible),select(certain)
    return tuple(p),tuple(cid for cid in p if cid not in h),p==h

def timed(fn,repeats):
    values=[]
    for _ in range(repeats):
        start=time.perf_counter_ns();result=fn();values.append(time.perf_counter_ns()-start)
    return result,statistics.median(values)

def main(a):
    units=read(a.units);records=read(a.claims);queries=read(a.queries)
    modeled={u['claim_id'] for u in units if u['claim_id']}
    records=[c for c in records if c['claim_id'] in modeled]
    pairs=json.loads(Path(a.pairs).read_text()) if a.pairs else build_pairs(records)
    if isinstance(pairs,dict):pairs=pairs['pairs']
    index=compile_lifecycles([LifecycleClaim.from_record(c) for c in records],pairs)
    ranker=TitleRanker(units)
    predictions={p['question_id']:p for p in read(a.predictions)} if a.predictions else {}
    rows=[];skipped=0;counter=0
    for q in queries:
        window=parse_query(q['question'])
        if window is None:skipped+=1;continue
        rank=ranker.rank(q['question'])[0]
        # Alternate timing order to avoid assigning every first call to one method.
        if len(rows)%2:
            reference,full_ns=timed(lambda:full_masks(rank,units,index,window,a.k),a.repetitions)
            lazy,lazy_ns=timed(lambda:select_lazy(rank,units,index,window,a.k),a.repetitions)
        else:
            lazy,lazy_ns=timed(lambda:select_lazy(rank,units,index,window,a.k),a.repetitions)
            reference,full_ns=timed(lambda:full_masks(rank,units,index,window,a.k),a.repetitions)
        assert lazy.possible_unit_ids==reference[0],q['question_id']
        assert lazy.unresolved_frontier==reference[1],q['question_id']
        assert lazy.stable==reference[2],q['question_id']
        if q['question_id'] in predictions:
            pred=predictions[q['question_id']]['methods']
            assert list(lazy.possible_unit_ids)==pred['possible_support']['selected_unit_ids'],q['question_id']
            assert lazy.stable==(pred['possible_support']['selected_unit_ids']==pred['guaranteed_support']['selected_unit_ids']),q['question_id']
            counter+=1
        item=asdict(lazy);item['support_checks']=lazy.support_checks
        rows.append({'question_id':q['question_id'],**item,'lazy_median_ns':lazy_ns,'full_masks_median_ns':full_ns,'full_mask_support_checks':2*len(index.claims)})
    # The fallback policy must remain fixed and must not acquire guarantees.
    empty=compile_lifecycles([],[]);fallback_units=[{'unit_id':'f1','claim_id':None},{'unit_id':'f2','claim_id':None}]
    fb=select_lazy([0,1],fallback_units,empty,(0,1),1)
    assert fb.stable and fb.selected_fallback==1 and fb.selected_modeled==0 and fb.support_checks==0
    assert select_lazy([0,1],fallback_units,empty,(0,1),0).possible_unit_ids==()
    avg=lambda key:sum(r[key] for r in rows)/len(rows)
    summary={'status':'passed','queries':len(queries),'parsed_queries_verified':len(rows),'unparsed_queries_skipped':skipped,'saved_runner_comparisons':counter,'modeled_claims':len(index.claims),'source_units':len(units),'k':a.k,'fallback_and_empty_budget_checks':'passed','stable':sum(r['stable'] for r in rows),'mean_examined_candidates':avg('examined_candidates'),'max_examined_candidates':max(r['examined_candidates'] for r in rows),'mean_lazy_support_checks':avg('support_checks'),'full_mask_support_checks_per_query':2*len(index.claims),'support_check_reduction_fraction':1-avg('support_checks')/(2*len(index.claims)) if index.claims else None,'query_selection_timing':{'repetitions_per_query':a.repetitions,'median_query_lazy_microseconds':statistics.median(r['lazy_median_ns'] for r in rows)/1000,'median_query_full_masks_microseconds':statistics.median(r['full_masks_median_ns'] for r in rows)/1000,'aggregate_ratio_of_median_times':sum(r['full_masks_median_ns'] for r in rows)/sum(r['lazy_median_ns'] for r in rows),'excludes':['source extraction','index compilation','relevance ranking','context rendering','reader inference'],'setting':'In-process CPU microbenchmark with cached source inputs; query-only selection, not end-to-end latency.'},'input_sha256':{str(p):sha(p) for p in [a.units,a.claims,a.queries,Path(__file__),Path(__file__).with_name('lazy_certificate.py')]+([a.predictions] if a.predictions else [])+([a.pairs] if a.pairs else [])}}
    summary['slices']={}
    for name,subset in [('selected_modeled_context',[r for r in rows if r['selected_modeled']]),('all_fallback_context',[r for r in rows if not r['selected_modeled']])]:
        summary['slices'][name]={'queries':len(subset),'stable':sum(r['stable'] for r in subset),'mean_support_checks':statistics.mean(r['support_checks'] for r in subset) if subset else None,'mean_examined_candidates':statistics.mean(r['examined_candidates'] for r in subset) if subset else None,'median_lazy_microseconds':statistics.median(r['lazy_median_ns'] for r in subset)/1000 if subset else None,'median_full_masks_microseconds':statistics.median(r['full_masks_median_ns'] for r in subset)/1000 if subset else None}
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'questions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--units',default='pass4/pipeline/smoke_old_adapter/units.jsonl');p.add_argument('--claims',default='pass4/pipeline/smoke_old_adapter/claims.jsonl');p.add_argument('--queries',default='pass4/protocol/dev_pilot_queries.jsonl');p.add_argument('--predictions',default='pass4/pipeline/smoke_old_adapter/predictions.jsonl');p.add_argument('--pairs');p.add_argument('--k',type=int,default=5);p.add_argument('--repetitions',type=int,default=25);p.add_argument('--output',default='pass4/retrieval/lazy_pilot_old_adapter');main(p.parse_args())
