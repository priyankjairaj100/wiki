#!/usr/bin/env python3
"""Reproduce the fixed source challenge from frozen, independently audited records."""
import argparse,collections,datetime,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles,select_context,stable_lifecycle_context
from pass4.retrieval.lazy_certificate import select_lazy
from pass6.modeling.constraint_oracle import Model,SupportOracle
HERE=pathlib.Path(__file__).resolve().parent

def read(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def write(p,rows):p.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replay(model,world,a,b):
 assert all(lo<=x<=hi for x,(lo,hi) in zip(world,model.bounds))
 assert all((0 if i==-1 else world[i])-(0 if j==-1 else world[j])<=v for i,j,v in model.constraints)
 active=[]
 for c in model.visible:
  stop=min([world[d] for d,t in model.pairs if t==c and world[d]>world[c]] or [float('inf')])
  if world[c]<=b and a<stop:active.append(c)
 return active

def evaluate(records,out):
 out.mkdir(parents=True,exist_ok=True);decisions=[];supports=[];witnesses=[];tot=collections.Counter();by_record=[]
 for record in records:
  claims=record['claims'];ids=[c['claim_id'] for c in claims];loc={c:i for i,c in enumerate(ids)}
  pairs=[(p['witness_id'],p['target_id']) for p in record['directed_pairs']]
  index=compile_lifecycles([LifecycleClaim.from_record(c) for c in claims],pairs)
  interval_index=compile_lifecycles([LifecycleClaim.from_record(c) for c in claims],[])
  events=list(index.events);epos={c:i for i,c in enumerate(events)}
  model=Model(tuple((int(index.events[c].lower),int(index.events[c].upper)) for c in events),tuple(epos[c] for c in ids),tuple((epos[d],epos[c]) for d,c in index.event_pairs))
  oracle=SupportOracle(model)
  order_constraints=tuple((epos[a],epos[b],-1) for a,b in record.get('known_precedence',[]))
  constrained_model=Model(model.bounds,model.visible,model.pairs,order_constraints)
  constrained_oracle=SupportOracle(constrained_model)
  dates=sorted({v for p in record['directed_pairs'] for v in (claims[loc[p['witness_id']]]['start']['lower'],(claims[loc[p['witness_id']]]['start']['lower']+claims[loc[p['witness_id']]]['start']['upper'])//2,claims[loc[p['witness_id']]]['start']['upper'])})
  ranking=sorted(ids,key=lambda c:(claims[loc[c]]['start']['source_span']['start'],loc[c]))+['fallback'];units=[{'unit_id':c['claim_id'],'claim_id':c['claim_id']} for c in claims]+[{'unit_id':'fallback','claim_id':None}]
  text={c['claim_id']:c['unit_span']['text'] for c in claims};text['fallback']='Fixed unmodeled fallback.'
  rs=collections.Counter()
  for q in dates:
   qs={};possible=[];guaranteed=[];constrained_possible=[];constrained_guaranteed=[]
   for c in ids:
    result=oracle.query(epos[c],q,q,'overlap');cert=index.certificates[c]
    assert result['possible']==cert.possible(q,q),(record['record_id'],c,q,'possible')
    assert result['guaranteed']==cert.guaranteed(q,q),(record['record_id'],c,q,'guaranteed')
    for key,expected in [('support_world',True),('exclusion_world',False)]:
     if result[key] is not None:
      assert (epos[c] in replay(model,result[key],q,q))==expected
      tot['oracle_world_replays']+=1
    if result['possible']:possible.append(c)
    if result['guaranteed']:guaranteed.append(c)
    constrained=constrained_oracle.query(epos[c],q,q,'overlap')
    if constrained['possible']:constrained_possible.append(c)
    if constrained['guaranteed']:constrained_guaranteed.append(c)
    assert not constrained['possible'] or result['possible']
    assert not result['guaranteed'] or constrained['guaranteed']
    for key,expected in [('support_world',True),('exclusion_world',False)]:
     if constrained[key] is not None:assert (epos[c] in replay(constrained_model,constrained[key],q,q))==expected
    tot['precedence_possible_changes']+=result['possible']!=constrained['possible']
    tot['precedence_guaranteed_changes']+=result['guaranteed']!=constrained['guaranteed']
    qs[c]=result;supports.append({'record_id':record['record_id'],'query_date':q,'query_iso':datetime.date.fromordinal(q).isoformat(),'claim_id':c,'event_order':events,'compiler_possible':cert.possible(q,q),'compiler_guaranteed':cert.guaranteed(q,q),'oracle':result,'known_order_constraints':order_constraints,'order_constrained_oracle':constrained})
    tot['support_mask_comparisons']+=2
   for k in (1,5):
    p=tuple(x.cid for x in select_context(index,ranking,q,q,k=k,policy='possible',unknown_ids=['fallback']))
    h=tuple(x.cid for x in select_context(index,ranking,q,q,k=k,policy='guaranteed',unknown_ids=['fallback']))
    i=tuple(x.cid for x in select_context(index,ranking,q,q,k=k,policy='interval',unknown_ids=['fallback']))
    stable=stable_lifecycle_context(index,ranking,q,q,k=k,unknown_ids=['fallback'])
    ctrl=stable_lifecycle_context(interval_index,ranking,q,q,k=k,unknown_ids=['fallback'])
    unit_positions={u['unit_id']:j for j,u in enumerate(units)}
    lazy=select_lazy([unit_positions[c] for c in ranking],units,index,(q,q),k)
    oracle_p=tuple([c for c in ranking if c=='fallback' or c in possible][:k]);oracle_h=tuple([c for c in ranking if c=='fallback' or c in guaranteed][:k])
    assert p==oracle_p and h==oracle_h and stable.stable==(p==h)
    assert lazy.possible_unit_ids==p and lazy.stable==stable.stable
    pair_id=None
    if not stable.stable:
     pivot=next(c for c in p if c!='fallback' and not qs[c]['guaranteed']);ws=[qs[pivot]['support_world'],qs[pivot]['exclusion_world']]
     contexts=[]
     for w in ws:
      active=replay(model,w,q,q);context=tuple(c for c in ranking if c=='fallback' or epos[c] in active)[:k];contexts.append(context)
     assert contexts[0]!=contexts[1]
     rendered=[[text[c] for c in ctx] for ctx in contexts];assert rendered[0]!=rendered[1]
     pair_id=f"{record['record_id']}:{q}:k{k}"
     witnesses.append({'pair_id':pair_id,'record_id':record['record_id'],'query_date':q,'k':k,'pivot':pivot,'event_order':events,'worlds':ws,'contexts':contexts,'rendered_contexts':rendered,'all_dates_feasible':True,'contexts_differ':True,'rendered_contexts_differ':True})
     tot['instability_witness_pairs']+=1
    cp=tuple([c for c in ranking if c=='fallback' or c in constrained_possible][:k]);ch=tuple([c for c in ranking if c=='fallback' or c in constrained_guaranteed][:k])
    d={'record_id':record['record_id'],'article_path':record['passage']['article_path'],'query_date':q,'query_iso':datetime.date.fromordinal(q).isoformat(),'k':k,'possible_context':p,'guaranteed_context':h,'interval_context':i,'stable':stable.stable,'order_constrained_possible_context':cp,'order_constrained_guaranteed_context':ch,'order_constrained_stable':cp==ch,'order_changes_stability':stable.stable!=(cp==ch),'interval_control_stable':ctrl.stable,'possible_differs_from_interval':p!=i,'rendered_possible_differs_from_interval':[text[c] for c in p]!=[text[c] for c in i],'stable_decision_differs':stable.stable!=ctrl.stable,'control_stable_but_replacement_unstable':ctrl.stable and not stable.stable,'instability_witness_pair':pair_id,'lazy_support_checks':lazy.support_checks}
    decisions.append(d)
    for name,value in [('decisions',1),('stable',stable.stable),('unstable',not stable.stable),('possible_differs_from_interval',p!=i),('stable_decision_differs',d['stable_decision_differs']),('control_stable_but_replacement_unstable',d['control_stable_but_replacement_unstable'])]:tot[name]+=value;rs[name]+=value
  by_record.append({'record_id':record['record_id'],'article_path':record['passage']['article_path'],'claims':len(claims),'directed_pairs':len(pairs),'point_queries':len(dates),**dict(rs)})
 write(out/'decisions.jsonl',decisions);write(out/'support_oracle.jsonl',supports);write(out/'instability_worlds.jsonl',witnesses)
 by_k={str(k):{field:sum(bool(d[field]) for d in decisions if d['k']==k) for field in ['stable','possible_differs_from_interval','stable_decision_differs','control_stable_but_replacement_unstable']}|{'decisions':sum(d['k']==k for d in decisions)} for k in (1,5)}
 summary={'scope':'Source-derived, manually annotated replacement diagnostic. Fixed source order. Point queries. Independent calendar-date bounds. No original QA labels. Not a representative retrieval benchmark.','records':len(records),'articles':len({r['passage']['article_path'] for r in records}),'claims':sum(len(r['claims']) for r in records),'directed_pairs':sum(len(r['directed_pairs']) for r in records),'point_queries':sum(r['point_queries'] for r in by_record),'counts':dict(tot),'by_k':by_k,'by_record':by_record,'compiler_oracle_mismatches':0,'lazy_mismatches':0,'all_saved_witnesses_replay':True,'order_constraints_infeasible':False,'oracle':'Complete integer difference-constraint feasibility over all days inside literal calendar bounds. No endpoint sampling is used as ground truth.'}
 (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 return summary

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=HERE/'runs');args=ap.parse_args()
 records=read(HERE/'accepted_records.jsonl')
 freeze=json.loads((HERE/'accepted_freeze.json').read_text());assert sha(HERE/'accepted_records.jsonl')==freeze['accepted_records_sha256']
 summary=evaluate(records,args.out)
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
