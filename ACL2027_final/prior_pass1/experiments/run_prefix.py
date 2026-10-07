#!/usr/bin/env python3
"""Observed-source prefix consistency, using all event times and historical probes."""
import argparse, collections, json, math, pathlib, sys
from run_evidence import DEFAULT_SOURCE,HERE,compile_masks,gold_ends,make_probes,BM25,write_json
from run_sensitivity import closure_ends

def run(name,source,out,imports):
    Claim,load_claims,extract_features,same_subject_relation,changed_value=imports
    gold=load_claims(str(source/'data'/name/'claims.jsonl'))
    cs=[Claim(cid=c.cid,text=c.text,timestamp=c.timestamp) for c in gold]
    compiled=compile_masks(cs,extract_features,same_subject_relation,changed_value)
    groups,gend=gold_ends(gold); probes=make_probes(gold,groups)
    dates=sorted({c.timestamp for c in cs})
    cutoffs=sorted(set(dates)|{t for key,q,t,kind in probes if kind=='historical'})
    rows=[]; masks={}
    for t in cutoffs:
        newest=[None]*len(cs); direct_end=[math.inf]*len(cs)
        for i,j in compiled['pairs']:
            if cs[j].timestamp>t: continue
            direct_end[i]=min(direct_end[i],cs[j].timestamp)
            if newest[i] is None or cs[j].timestamp>cs[newest[i]].timestamp: newest[i]=j
        prefix_end=closure_ends(cs,compiled['features'],newest)
        eligible={i for i,c in enumerate(cs) if c.timestamp<=t}
        df={i for i in eligible if t<compiled['first'][i]}; dp={i for i in eligible if t<direct_end[i]}
        cf={i for i in eligible if t<compiled['component'][i]}; cp={i for i in eligible if t<prefix_end[i]}
        assert df==dp
        masks[t]=(cp,cf)
        rows.append(dict(cutoff=t,is_event=t in dates,n_observed=len(eligible),direct_differences=len(df^dp),component_differences=len(cf^cp),
                         only_full=[cs[i].cid for i in sorted(cf-cp)],only_prefix=[cs[i].cid for i in sorted(cp-cf)]))
    idx=BM25(cs); qrows=[]
    for key,q,t,kind in probes:
        if kind!='historical': continue
        rank,scores=idx.rank(q); cp,cf=masks[t]
        p=next((i for i in rank if i in cp),None); f=next((i for i in rank if i in cf),None)
        live={i for i in groups[key] if cs[i].timestamp<=t<gend[i]}
        qrows.append(dict(key=key,cutoff=t,full_hit=int(f in live),prefix_hit=int(p in live),
                          full_cid=cs[f].cid if f is not None else None,prefix_cid=cs[p].cid if p is not None else None))
    def summarize(items):
        return dict(n_cutoffs=len(items),direct_mismatch_cutoffs=sum(r['direct_differences']>0 for r in items),
                    component_mismatch_cutoffs=sum(r['component_differences']>0 for r in items),
                    component_membership_differences=sum(r['component_differences'] for r in items),
                    component_max_differences=max((r['component_differences'] for r in items),default=0))
    card=dict(dataset=name,event_cutoffs=summarize([r for r in rows if r['is_event']]),all_cutoffs=summarize(rows),historical_queries=dict(n=len(qrows),
              full_hits=sum(r['full_hit'] for r in qrows),prefix_hits=sum(r['prefix_hit'] for r in qrows),changed_top1=sum(r['full_cid']!=r['prefix_cid'] for r in qrows)),cutoffs=rows,queries=qrows)
    write_json(out/(name+'_prefix.json'),card)
    print(name,json.dumps({k:card[k] for k in ['event_cutoffs','historical_queries']}),flush=True)
    return {k:v for k,v in card.items() if k not in ('cutoffs','queries')}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=pathlib.Path,default=DEFAULT_SOURCE); ap.add_argument('--output',type=pathlib.Path,default=HERE/'results'); ap.add_argument('--datasets',nargs='+',default=['wikidata','templama','wikidata_prose','realprose','realwiki','realworld']); args=ap.parse_args()
    sys.path.insert(0,str(args.source))
    from wikigraphrag.core.claim import Claim
    from wikigraphrag.data.io import load_claims
    from wikigraphrag.detect import extract_features,same_subject_relation,changed_value
    args.output.mkdir(exist_ok=True,parents=True)
    cards=[run(name,args.source,args.output,(Claim,load_claims,extract_features,same_subject_relation,changed_value)) for name in args.datasets]
    write_json(args.output/'prefix_summary.json',dict(protocol='observed-prefix-v1',cards=cards))
if __name__=='__main__':main()
