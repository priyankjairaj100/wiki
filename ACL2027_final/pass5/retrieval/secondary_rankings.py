#!/usr/bin/env python3
"""Evaluate all six existing rank variants without labels or answer responses."""
import argparse,datetime as dt,hashlib,json,statistics,sys
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass4.retrieval.secondary_rankings import orders_for
from pass4.retrieval.ranking import TitleRanker,VARIANTS
from pass4.retrieval.lazy_certificate import select_lazy
from pass4.retrieval.profile_lazy import full_masks
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles
from pass3.extraction.source_adapter import build_pairs
from pass3.pipeline.run_matched import parse_query

def read(p):return [json.loads(s) for s in Path(p).read_text().splitlines() if s]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--track',choices=['human','validation'],required=True);a=p.parse_args();folder=ROOT/f'pass5/pipeline/{a.track}'
 q='human_test_confirmation' if a.track=='human' else 'dev_validation';qpath=ROOT/f'pass5/protocol/{q}_queries.jsonl';out=ROOT/f'pass5/retrieval/secondary_{a.track}';out.mkdir(parents=True,exist_ok=True)
 paths=[Path(__file__),ROOT/'pass5/retrieval/SECONDARY_RANKING_PROTOCOL.json',ROOT/'pass4/retrieval/secondary_rankings.py',ROOT/'pass4/retrieval/ranking.py',ROOT/'pass4/retrieval/lazy_certificate.py',ROOT/'pass4/retrieval/profile_lazy.py',folder/'claims.jsonl',folder/'units.jsonl',qpath]
 inputs={str(p.relative_to(ROOT)):sha(p) for p in paths};(out/'input_manifest.json').write_text(json.dumps(inputs,indent=2)+'\n')
 units=read(folder/'units.jsonl');records=read(folder/'claims.jsonl');queries=read(qpath);index=compile_lifecycles([LifecycleClaim.from_record(r) for r in records],build_pairs(records));ranker=TitleRanker(units);rows=[];equivalence=0;direct=0
 for pos,q in enumerate(queries):
  window=parse_query(q['question'])
  if window is None:continue
  orders,meta=orders_for(ranker,q['question']);variants={}
  for name in VARIANTS:
   order=orders[name]
   if len(rows)<6:assert order==ranker.rank(q['question'],name)[0];equivalence+=1
   result=select_lazy(order,units,index,window,5);expected=full_masks(order,units,index,window,5)
   assert result.possible_unit_ids==expected[0] and result.unresolved_frontier==expected[1] and result.stable==expected[2];direct+=1
   item=asdict(result);item['support_checks']=result.support_checks;variants[name]=item
  rows.append({'question_id':q['question_id'],'query_window':window,'variants':variants})
  if len(rows)%250==0:print(a.track,len(rows),flush=True)
 main=[r for r in rows if r['variants']['title_residual']['selected_modeled']];union=[r for r in rows if any(x['selected_modeled'] for x in r['variants'].values())]
 def metric(subset,name):
  values=[r['variants'][name] for r in subset];n=len(values)
  return {'queries':n,'stable':sum(r['stable'] for r in values),'modeled_contexts':sum(r['selected_modeled']>0 for r in values),'mean_examined_candidates':statistics.mean(r['examined_candidates'] for r in values) if n else None,'mean_support_checks':statistics.mean(r['support_checks'] for r in values) if n else None}
 summary={'analysis':'Source-audit revision of all six previously declared ranking variants; no labels or answer outputs read.','queries':len(queries),'parsed_queries':len(rows),'unparsed_queries':len(queries)-len(rows),'fixed_main_modeled_cohort':len(main),'fixed_union_modeled_cohort':len(union),'modeled_claims':len(records),'full_mask_checks_per_query':2*len(records),'ranking_equivalence_checks':equivalence,'direct_mask_equivalence_checks':direct,'variants':{v:{'all_parsed':metric(rows,v),'own_modeled_contexts':metric([r for r in rows if r['variants'][v]['selected_modeled']],v),'fixed_main_modeled_cohort':metric(main,v),'fixed_union_modeled_cohort':metric(union,v)} for v in VARIANTS},'input_sha256':inputs}
 assert all(sha(ROOT/p)==h for p,h in inputs.items());(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'questions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
