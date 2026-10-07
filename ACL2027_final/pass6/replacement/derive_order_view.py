#!/usr/bin/env python3
"""Compare replacement and interval support under identical recorded source orders."""
import argparse,collections,datetime,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles
from pass6.modeling.constraint_oracle import Model,SupportOracle
from pass6.replacement.run_challenge import read,write,replay
HERE=pathlib.Path(__file__).resolve().parent

def evaluate_order(records,out):
 out.mkdir(parents=True,exist_ok=True);supports=[];decisions=[];worlds=[]
 for r in records:
  claims=r['claims'];ids=[c['claim_id'] for c in claims];lookup={c['claim_id']:c for c in claims}
  ix=compile_lifecycles([LifecycleClaim.from_record(c) for c in claims],[(e['witness_id'],e['target_id']) for e in r['directed_pairs']])
  events=list(ix.events);pos={c:i for i,c in enumerate(events)};bounds=tuple((int(ix.events[c].lower),int(ix.events[c].upper)) for c in events);visible=tuple(pos[c] for c in ids)
  order=tuple((pos[a],pos[b],-1) for a,b in r['known_precedence'])
  model=Model(bounds,visible,tuple((pos[d],pos[c]) for d,c in ix.event_pairs),order)
  end_pairs=tuple((pos[e],pos[c]) for c,e in ix.explicit_end_ids.items())
  control_model=Model(bounds,visible,end_pairs,order)
  oracle=SupportOracle(model);control=SupportOracle(control_model)
  ranking=sorted(ids,key=lambda c:(lookup[c]['start']['source_span']['start'],ids.index(c)))+['fallback']
  text={c['claim_id']:c['unit_span']['text'] for c in claims};text['fallback']='Fixed unmodeled fallback.'
  dates=sorted({v for e in r['directed_pairs'] for d in [lookup[e['witness_id']]['start']] for v in (d['lower'],(d['lower']+d['upper'])//2,d['upper'])})
  for q in dates:
   answers={c:oracle.query(pos[c],q,q,'overlap') for c in ids};controls={c:control.query(pos[c],q,q,'overlap') for c in ids}
   for c in ids:
    for md,ans in [(model,answers[c]),(control_model,controls[c])]:
     for key,expected in [('support_world',True),('exclusion_world',False)]:
      if ans[key] is not None:assert (pos[c] in replay(md,ans[key],q,q))==expected
    supports.append({'record_id':r['record_id'],'claim_id':c,'query_date':q,'event_order':events,'bounds':bounds,'known_order_constraints':order,'replacement_pairs':model.pairs,'interval_pairs':control_model.pairs,'replacement':answers[c],'interval':controls[c]})
   for k in (1,5):
    def top(results,mode):return tuple(c for c in ranking if c=='fallback' or results[c][mode])[:k]
    p,h=top(answers,'possible'),top(answers,'guaranteed');ip,ih=top(controls,'possible'),top(controls,'guaranteed')
    stable=p==h;cs=ip==ih;pairid=None
    if not stable:
     pivot=next(c for c in p if c!='fallback' and not answers[c]['guaranteed']);ws=[answers[pivot]['support_world'],answers[pivot]['exclusion_world']];ctx=[]
     for w in ws:
      eligible=replay(model,w,q,q);ctx.append(tuple(c for c in ranking if c=='fallback' or pos[c] in eligible)[:k])
     assert ctx[0]!=ctx[1]
     rendered=[[text[c] for c in t] for t in ctx];assert rendered[0]!=rendered[1]
     pairid=f"order:{r['record_id']}:{q}:k{k}"
     worlds.append({'pair_id':pairid,'record_id':r['record_id'],'query_date':q,'k':k,'pivot':pivot,'event_order':events,'bounds':bounds,'known_order_constraints':order,'replacement_pairs':model.pairs,'worlds':ws,'contexts':ctx,'rendered_contexts':rendered,'source_order_obeyed':True,'contexts_differ':True,'rendered_contexts_differ':True})
    decisions.append({'record_id':r['record_id'],'query_date':q,'query_iso':datetime.date.fromordinal(q).isoformat(),'k':k,'possible_context':p,'guaranteed_context':h,'stable':stable,'interval_possible_context':ip,'interval_guaranteed_context':ih,'interval_stable':cs,'possible_differs_from_interval':p!=ip,'rendered_possible_differs_from_interval':[text[c] for c in p]!=[text[c] for c in ip],'stability_differs':stable!=cs,'control_stable_but_replacement_unstable':cs and not stable,'instability_witness_pair':pairid})
 by_k={str(k):{'queries':sum(d['k']==k for d in decisions),**{f:sum(bool(d[f]) for d in decisions if d['k']==k) for f in ['stable','interval_stable','possible_differs_from_interval','rendered_possible_differs_from_interval','stability_differs','control_stable_but_replacement_unstable']}} for k in (1,5)}
 summary={'scope':'Exact source-order view. Both replacement and interval control retain identical calendar bounds and strict source orders. The interval control removes only cross-claim replacement edges. Explicit ends remain.','records':len(records),'point_queries':len(decisions)//2,'context_decisions':len(decisions),'claim_query_pairs':len(supports),'support_judgments_per_model':2*len(supports),'oracle_models':2,'feasible_instability_pairs':len(worlds),'all_source_order_constraints_replayed':True,'all_rendered_witness_pairs_differ':True,'by_k':by_k}
 write(out/'order_decisions.jsonl',decisions);write(out/'order_support.jsonl',supports);write(out/'order_worlds.jsonl',worlds);(out/'order_summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n');return summary
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=HERE/'order_runs');a=ap.parse_args();print(json.dumps(evaluate_order(read(HERE/'accepted_records.jsonl'),a.out),indent=2))
