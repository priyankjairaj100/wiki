#!/usr/bin/env python3
"""Delete observed matcher links. No synthetic claims or fake benchmark cases.

Each intervention changes one accepted directed pair to rejected. The original
latest-edge graph is then rebuilt, including replacement latest edges. Direct
certificates are rebuilt from the same modified pair set. We compare endpoints
and eligibility over every distinct source-time cutoff.
"""
import argparse, collections, json, math, pathlib, sys
from run_evidence import DEFAULT_SOURCE, HERE, compile_masks, gold_ends, norm, UF, write_json

def closure_ends(cs,fs,newest):
    uf=UF(len(cs))
    for i,j in enumerate(newest):
        if j is not None: uf.union(i,j)
    groups=collections.defaultdict(list)
    for i in range(len(cs)): groups[uf.find(i)].append(i)
    def value(i): return ('n',fs[i].numbers) if fs[i].numbers else ('t',fs[i].value_tokens)
    end=[math.inf]*len(cs)
    for ids in groups.values():
        for i in ids:
            candidates=[cs[j].timestamp for j in ids if cs[j].timestamp>cs[i].timestamp and value(i)!=value(j)]
            if candidates: end[i]=min(candidates)
    return end

def run(name,source,out,imports):
    Claim,load_claims,extract_features,same_subject_relation,changed_value=imports
    gold=load_claims(str(source/'data'/name/'claims.jsonl'))
    cs=[Claim(cid=c.cid,text=c.text,timestamp=c.timestamp) for c in gold]
    compiled=compile_masks(cs,extract_features,same_subject_relation,changed_value)
    byolder=collections.defaultdict(list)
    for i,j in compiled['pairs']: byolder[i].append(j)
    first=compiled['first']; component=compiled['component']; dates=sorted({c.timestamp for c in cs})
    rows=[]
    for i,j in compiled['pairs']:
        rest=[k for k in byolder[i] if k!=j]
        first_new=min((cs[k].timestamp for k in rest),default=math.inf)
        d_affected=[i] if first_new!=first[i] else []
        d_flips=sum((t<first_new)!=(t<first[i]) for t in dates if t>=cs[i].timestamp)
        if compiled['newest'][i]==j:
            new_latest=list(compiled['newest'])
            new_latest[i]=max(rest,key=lambda k:cs[k].timestamp) if rest else None
            component_new=closure_ends(cs,compiled['features'],new_latest)
            c_affected=[k for k in range(len(cs)) if component_new[k]!=component[k]]
            c_flips=sum((t<component_new[k])!=(t<component[k]) for k in c_affected for t in dates if t>=cs[k].timestamp)
        else: c_affected=[]; c_flips=0
        false_pair=(gold[i].gold_key!=gold[j].gold_key or norm(gold[i].value)==norm(gold[j].value))
        rows.append(dict(dataset=name,older=cs[i].cid,newer=cs[j].cid,false_pair=false_pair,cross_key=gold[i].gold_key!=gold[j].gold_key,
                         direct_affected_claims=len(d_affected),component_affected_claims=len(c_affected),direct_membership_flips=d_flips,component_membership_flips=c_flips,
                         component_affected_ids=[cs[k].cid for k in c_affected]))
    summary={}
    for tag,items in [('all_pairs',rows),('false_pairs',[r for r in rows if r['false_pair']]),('cross_key_pairs',[r for r in rows if r['cross_key']])]:
        summary[tag]=dict(n=len(items),direct_max_affected=max((r['direct_affected_claims'] for r in items),default=0),
            component_max_affected=max((r['component_affected_claims'] for r in items),default=0),
            component_more_than_one=sum(r['component_affected_claims']>1 for r in items),
            direct_total_flips=sum(r['direct_membership_flips'] for r in items),component_total_flips=sum(r['component_membership_flips'] for r in items))
    write_json(out/(name+'_sensitivity.json'),dict(dataset=name,n_cutoffs=len(dates),summary=summary,interventions=rows))
    print(name,json.dumps(summary),flush=True)
    return dict(dataset=name,n_cutoffs=len(dates),summary=summary)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=pathlib.Path,default=DEFAULT_SOURCE); ap.add_argument('--output',type=pathlib.Path,default=HERE/'results'); ap.add_argument('--datasets',nargs='+',default=['wikidata','templama','wikidata_prose','realprose','realwiki','realworld']); args=ap.parse_args()
    sys.path.insert(0,str(args.source))
    from wikigraphrag.core.claim import Claim
    from wikigraphrag.data.io import load_claims
    from wikigraphrag.detect import extract_features,same_subject_relation,changed_value
    imports=(Claim,load_claims,extract_features,same_subject_relation,changed_value)
    args.output.mkdir(exist_ok=True,parents=True)
    cards=[run(name,args.source,args.output,imports) for name in args.datasets]
    write_json(args.output/'sensitivity_summary.json',dict(protocol='observed-pair-deletion-v1',cards=cards))
if __name__=='__main__': main()
