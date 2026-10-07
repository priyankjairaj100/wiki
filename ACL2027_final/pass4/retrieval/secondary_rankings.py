"""Secondary certificate portability over all six prespecified rank variants.

No labels are loaded. The main selected ranking remains frozen.
"""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,statistics,sys,time
from dataclasses import asdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read,parse_query,YEAR
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles
from pass3.extraction.source_adapter import build_pairs
from pass4.retrieval.ranking import TitleRanker,VARIANTS
from pass4.retrieval.lazy_certificate import select_lazy

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def orders_for(ranker,question):
    """Share two lexical score computations; preserve frozen rank semantics."""
    base,_,metadata=ranker.rank_with_metadata(question,'bm25')
    residual=ranker.rank(question,'title_residual')[0]
    linked=set(metadata['article_paths'])
    title=sorted(base,key=lambda i:ranker.units[i]['article_path'] not in linked) if linked else base
    orders={'bm25':base,'title_bm25':title,'title_residual':residual}
    window=parse_query(question)
    if window:
        year=dt.date.fromordinal(window[1]).year
        def last(i):return max((int(y) for y in YEAR.findall(ranker.units[i]['text']) if int(y)<=year),default=0)
        for name,order in list(orders.items()):orders[name+'_latestyear']=sorted(order[:20],key=lambda i:-last(i))+order[20:]
    else:
        orders.update({name+'_latestyear':order for name,order in list(orders.items())})
    return orders,metadata

def audit(args):
    units=read(args.units);queries=read(args.queries);ranker=TitleRanker(units);comparisons=0
    for q in queries:
        orders,_=orders_for(ranker,q['question'])
        for variant in VARIANTS:
            assert orders[variant]==ranker.rank(q['question'],variant)[0],(q['question_id'],variant)
            assert len(orders[variant])==len(units) and len(set(orders[variant]))==len(units)
            comparisons+=1
    result={'status':'passed','queries':len(queries),'full_ranking_equivalence_checks':comparisons,'input_sha256':{str(p):sha(p) for p in [args.units,args.queries,Path(__file__),Path(__file__).with_name('ranking.py')]}}
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

def analyze(args):
    protocol=Path(__file__).with_name('SECONDARY_RANKING_PROTOCOL.json');assert protocol.is_file()
    audit_path=Path(__file__).with_name('secondary_rank_equivalence.json');ar=json.loads(audit_path.read_text());assert ar['status']=='passed' and ar['full_ranking_equivalence_checks']==1056
    assert ar['input_sha256'][str(Path(__file__))]==sha(Path(__file__))
    paths=[args.units,args.claims,args.queries,Path(__file__),Path(__file__).with_name('ranking.py'),Path(__file__).with_name('lazy_certificate.py'),protocol,audit_path]
    inputs={str(p):sha(p) for p in paths};out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    (out/'input_manifest.json').write_text(json.dumps({'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'input_sha256':inputs},indent=2)+'\n')
    units=read(args.units);records=read(args.claims);queries=read(args.queries);modeled={u['claim_id'] for u in units if u['claim_id']};records=[c for c in records if c['claim_id'] in modeled]
    index=compile_lifecycles([LifecycleClaim.from_record(c) for c in records],build_pairs(records));ranker=TitleRanker(units);rows=[];skipped=0;start=time.time()
    for q in queries:
        window=parse_query(q['question'])
        if window is None:skipped+=1;continue
        orders,metadata=orders_for(ranker,q['question']);variants={}
        for variant in VARIANTS:
            result=select_lazy(orders[variant],units,index,window,5);item=asdict(result);item['support_checks']=result.support_checks;item['ranking_sha256']=hashlib.sha256(np.asarray(orders[variant],dtype='<u4').tobytes()).hexdigest();variants[variant]=item
        rows.append({'question_id':q['question_id'],'query_window':window,'title_link_count':len(metadata['article_paths']),'variants':variants})
        if len(rows)%250==0:print('processed',len(rows),flush=True)
    fixed_main=[r for r in rows if r['variants']['title_residual']['selected_modeled']]
    fixed_union=[r for r in rows if any(v['selected_modeled'] for v in r['variants'].values())]
    def metrics(subset,variant):
        rr=[r['variants'][variant] for r in subset]
        return {'queries':len(rr),'stable':sum(x['stable'] for x in rr),'modeled_contexts':sum(x['selected_modeled']>0 for x in rr),'mean_examined_candidates':statistics.mean(x['examined_candidates'] for x in rr) if rr else None,'mean_support_checks':statistics.mean(x['support_checks'] for x in rr) if rr else None,'max_examined_candidates':max((x['examined_candidates'] for x in rr),default=None)}
    summary={'analysis':'Declared post-confirmation ranking portability; no answer labels read.','queries':len(queries),'parsed_queries':len(rows),'unparsed_queries':skipped,'full_mask_checks_per_query':2*len(index.claims),'source_units':len(units),'modeled_claims':len(index.claims),'fixed_main_modeled_cohort':len(fixed_main),'fixed_union_modeled_cohort':len(fixed_union),'variants':{v:{'all_parsed':metrics(rows,v),'own_modeled_contexts':metrics([r for r in rows if r['variants'][v]['selected_modeled']],v),'fixed_main_modeled_cohort':metrics(fixed_main,v),'fixed_union_modeled_cohort':metrics(fixed_union,v)} for v in VARIANTS},'elapsed_seconds':time.time()-start,'input_sha256':inputs}
    assert all(sha(p)==h for p,h in inputs.items())
    (out/'questions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audit',action='store_true');p.add_argument('--units',required=True);p.add_argument('--queries',required=True);p.add_argument('--claims');p.add_argument('--output',required=True);args=p.parse_args();audit(args) if args.audit else analyze(args)
