"""Construct and replay source-grounded timelines for every ambiguous query."""
from __future__ import annotations
import argparse,collections,dataclasses,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read,dump,lines,sha,BM25,build_context
from pass3.extraction.source_adapter import build_pairs
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles
from pass3.theory.refinement import context_counterworlds,refinement_frontier,evaluate_world

def run(folder):
    folder=Path(folder);units=read(folder/'units.jsonl');unitmap={u['unit_id']:u for u in units};unitindices={u['unit_id']:i for i,u in enumerate(units)}
    records=read(folder/'claims.jsonl');claimmap={r['claim_id']:r for r in records};modeled={u['claim_id'] for u in units if u['claim_id']}
    life=compile_lifecycles([LifecycleClaim.from_record(claimmap[c]) for c in sorted(modeled)],build_pairs(records))
    unknown=[u['unit_id'] for u in units if not u['claim_id']];bm25=BM25(units)
    audits=read(folder/'mechanism_questions.jsonl');ambiguous={r['question_id'] for r in audits if r['claim_context_certificate'] is False}
    results=[];replaychecks=0
    with (folder/'predictions.jsonl').open() as f:
        for line in f:
            p=json.loads(line)
            if p['question_id'] not in ambiguous:continue
            a,b=p['query_window'];ranked,_=bm25.rank(p['question']);ranking=[units[i]['unit_id'] for i in ranked]
            frontier=refinement_frontier(life,ranking,a,b,k=5,unknown_ids=unknown)
            example=context_counterworlds(life,ranking,a,b,k=5,unknown_ids=unknown)
            assert example is not None
            row={'question_id':p['question_id'],'question':p['question'],'query_window':[a,b],'scope':example.scope,
              'pivot_id':example.pivot_id,'pivot_source':claimmap[example.pivot_id],
              'frontier':[{'claim_id':cid,'source':claimmap[cid]} for cid in frontier],
              'exclusion_reason':example.exclusion_reason,'exclusion_witness':example.exclusion_witness,'worlds':{}}
            for name,world in [('support',example.support_world),('exclusion',example.exclusion_world)]:
                # Replay after serialization; this checks the released numeric assignments.
                dates=json.loads(json.dumps(world.event_dates));replayed=evaluate_world(life,dates,ranking,a,b,k=5,unknown_ids=unknown)
                assert replayed.selected_context==world.selected_context
                assert replayed.supported_claims==world.supported_claims
                contexts=build_context([unitindices[c] for c in world.selected_context],units,{c:'realized_support' for c in modeled},5,768)
                row['worlds'][name]={'event_dates':dates,'supported_claim_ids':world.supported_claims,'selected_unit_ids':world.selected_context,'source_contexts':contexts}
                replaychecks+=1
            assert row['worlds']['support']['selected_unit_ids']!=row['worlds']['exclusion']['selected_unit_ids']
            row['rendered_contexts_differ']=[(c['unit_id'],c['start_char'],c['end_char_exclusive']) for c in row['worlds']['support']['source_contexts']]!=[(c['unit_id'],c['start_char'],c['end_char_exclusive']) for c in row['worlds']['exclusion']['source_contexts']]
            results.append(row)
    assert {r['question_id'] for r in results}==ambiguous
    lines(folder/'counterworlds.jsonl',results)
    summary={'queries':len(audits),'ambiguous_queries':len(ambiguous),'constructed_pairs':len(results),'replayed_worlds':replaychecks,'claim_contexts_differ':len(results),'rendered_contexts_differ':sum(r['rendered_contexts_differ'] for r in results),'frontier_sizes':dict(collections.Counter(len(r['frontier']) for r in results)),'exclusion_reasons':dict(collections.Counter(r['exclusion_reason'] for r in results)),'modeled_source_claims':len(life.claims),'events_per_world':len(life.events),'status':'passed','scope':'Actual source bounds with independent event dates and fixed fallback; world assignments are constructed audit examples, not measured event dates.','input_sha256':{str(p):sha(p) for p in [folder/'predictions.jsonl',folder/'claims.jsonl',folder/'units.jsonl',ROOT/'pass3/theory/refinement.py',Path(__file__)]},'counterworlds_sha256':sha(folder/'counterworlds.jsonl')}
    dump(folder/'counterworlds_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',required=True);a=p.parse_args();run(a.folder)
