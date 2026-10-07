#!/usr/bin/env python3
"""Retrieve source excerpts and certify their sensitivity to date precision.

Inputs contain source units, source-derived claims, and the visible question.
No answer labels or question metadata are accepted.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read,parse_query,build_context
from pass3.extraction.source_adapter import build_pairs
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles
from pass3.theory.refinement import pivot_date_assignments,evaluate_world
from pass4.retrieval.ranking import TitleRanker,VARIANTS
from pass4.retrieval.lazy_certificate import select_lazy

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def query(units,records,question,ranking='title_residual',k=5,explain=False):
    if isinstance(k,bool) or not isinstance(k,int) or k<0:raise ValueError('k must be a nonnegative integer')
    ids=[u['unit_id'] for u in units]
    if len(ids)!=len(set(ids)):raise ValueError('Source-unit identifiers must be unique')
    modeled=[u['claim_id'] for u in units if u.get('claim_id') is not None]
    if len(modeled)!=len(set(modeled)):raise ValueError('Each modeled claim must have exactly one source unit')
    record_ids=[c['claim_id'] for c in records]
    if len(record_ids)!=len(set(record_ids)) or set(record_ids)!=set(modeled):
        raise ValueError('Claims must match the modeled source units exactly')
    if any(u['claim_id']!=u['unit_id'] for u in units if u.get('claim_id') is not None):
        raise ValueError('A modeled source-unit identifier must equal its claim identifier')
    start=time.perf_counter();pairs=build_pairs(records);life=compile_lifecycles([LifecycleClaim.from_record(c) for c in records],pairs);compiled=time.perf_counter()-start
    start=time.perf_counter();ranker=TitleRanker(units);order,_,link=ranker.rank_with_metadata(question,ranking);ranked=time.perf_counter()-start
    window=parse_query(question);unitindex={u['unit_id']:i for i,u in enumerate(units)}
    result={'question':question,'ranking':ranking,'query_window':list(window) if window else None,'date_scale':'Gregorian day ordinals','source_model':{'units':len(units),'modeled_claims':len(life.claims),'explicit_ends':len(life.explicit_end_ids),'source_replacement_pairs':len(pairs)},'title_link':link,'budget':{'unit_limit':k,'source_word_limit':768},'certificate_scope':'Fixed ranked unit selection under the modeled independent event dates and fixed fallback policy, before source-word truncation.','stage_seconds':{'compile_lifecycles':compiled,'build_and_query_relevance_index':ranked}}
    if window is None:
        chosen=order[:k];result.update(selected_unit_ids=[units[i]['unit_id'] for i in chosen],contexts=build_context(chosen,units,{},k,768),stable=None,unresolved_frontier=[],selection_work={'status':'Visible query time did not parse; the fixed relevance context is returned without a temporal certificate.'})
        return result
    start=time.perf_counter();selected=select_lazy(order,units,life,window,k);result['stage_seconds']['lazy_selection']=time.perf_counter()-start
    state=asdict(selected);state['support_checks']=selected.support_checks
    status={cid:('unresolved' if cid in selected.unresolved_frontier else 'guaranteed') for cid in selected.possible_unit_ids if cid in life.claims}
    result.update(selected_unit_ids=list(selected.possible_unit_ids),contexts=build_context([unitindex[c] for c in selected.possible_unit_ids],units,status,k,768),stable=selected.stable,unresolved_frontier=list(selected.unresolved_frontier),selection_work={key:value for key,value in state.items() if key not in {'possible_unit_ids','unresolved_frontier','stable'}})
    result['selection_work']['excludes']=['source extraction','lifecycle compilation','relevance index construction and ranking','context rendering','counterworld construction and replay','reader inference']
    if explain and not selected.stable:
        start=time.perf_counter();pivot=selected.unresolved_frontier[0];a,b=window
        assignments=pivot_date_assignments(life.certificates[pivot],life.events,a,b)
        ranked_ids=[units[i]['unit_id'] for i in order];unknown=[u['unit_id'] for u in units if u.get('claim_id') is None]
        worlds={}
        for name,dates in [('support',assignments.support_dates),('exclusion',assignments.exclusion_dates)]:
            world=evaluate_world(life,dates,ranked_ids,a,b,k=k,unknown_ids=unknown)
            world_status={cid:life.certificates[cid].status(a,b) for cid in world.selected_context if cid in life.claims}
            contexts=build_context([unitindex[c] for c in world.selected_context],units,world_status,k,768)
            worlds[name]={'event_dates':dict(dates),'selected_unit_ids':list(world.selected_context),'contexts':contexts}
        assert worlds['support']['selected_unit_ids']!=worlds['exclusion']['selected_unit_ids']
        signature=lambda w:[(c['unit_id'],c['start_char'],c['end_char_exclusive'],c['text']) for c in w['contexts']]
        result['explanation']={'pivot_id':pivot,'reason':assignments.exclusion_reason,'witness_id':assignments.exclusion_witness,'worlds':worlds,'replayed_worlds':2,'rendered_contexts_differ':signature(worlds['support'])!=signature(worlds['exclusion'])}
        result['stage_seconds']['counterworld_construction_and_replay']=time.perf_counter()-start
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--units',required=True);p.add_argument('--claims',required=True);p.add_argument('--question',required=True);p.add_argument('--ranking',choices=VARIANTS,default='title_residual');p.add_argument('--k',type=int,default=5);p.add_argument('--explain',action='store_true');args=p.parse_args()
    result=query(read(args.units),read(args.claims),args.question,args.ranking,args.k,args.explain)
    result['input_sha256']={'units':sha(args.units),'claims':sha(args.claims)}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
