#!/usr/bin/env python3
"""Verify frozen source membership, literal spans, outcomes, and feasible witnesses."""
import argparse,datetime,hashlib,json,pathlib,sys,tempfile
R=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from pass6.replacement.run_challenge import evaluate,read
from pass6.replacement.derive_order_view import evaluate_order
from pass3.extraction.source_adapter import parse_date
O=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,default=O/'verification.json');args=ap.parse_args()
 f=json.loads((O/'accepted_freeze.json').read_text());corrections={x['path']:x for x in json.loads((O/'implementation_corrections.json').read_text())['changes']}
 for path,h in f['files'].items():
  actual=sha(R/path)
  if actual!=h:assert path in corrections and corrections[path]['frozen_sha256']==h and corrections[path]['current_sha256']==actual,path
 # Earlier memberships remain fixed, even where added source exclusions apply.
 for fname in ['selection_freeze.json','sampling_freeze.json','expansion_freeze.json']:
  for path,h in json.loads((O/fname).read_text())['files'].items():assert sha(R/path)==h,(fname,path)
 samples=read(O/'expanded_sample.jsonl');assert len(samples)==384 and [p['review_index'] for p in samples]==list(range(384))
 initial=read(O/'sample.jsonl');assert [p['passage_id'] for p in initial]==[p['passage_id'] for p in samples[:128]]
 judgments=read(O/'source_judgments.jsonl')+read(O/'extra_judgments_a.jsonl')+read(O/'extra_judgments_b.jsonl');assert len(judgments)==384 and {j['review_index'] for j in judgments}==set(range(384))
 reviews=read(O/'independent_review.jsonl')+read(O/'extra_review_a.jsonl')+read(O/'extra_review_b.jsonl');accept={j['review_index'] for j in reviews if j['decision']=='accept'}
 records=read(O/'accepted_records.jsonl');assert {r['review_index'] for r in records}==accept
 prior=set(json.loads((O/'excluded_articles.json').read_text()));prior.update(['/wiki/The_News_Quiz','/wiki/Chicago_Stadium','/wiki/Warburg_Institute','/wiki/Ruud_Lubbers','/wiki/Zambia'])
 sources={}
 for split in ['dev','test']:
  for p in read(R/f'pass2/naturaldata/normalized/{split}_passages.jsonl'):sources[(split,p['passage_id'])]=p
 spans=0;date_checks=0;pairs=0
 def check_spans(obj,text):
  nonlocal spans
  if isinstance(obj,dict):
   if {'start','end','text'}<=obj.keys() and type(obj['start']) is int:
    assert text[obj['start']:obj['end']]==obj['text'];spans+=1
   for v in obj.values():check_spans(v,text)
  elif isinstance(obj,list):
   for v in obj:check_spans(v,text)
 for r in records:
  p=r['passage'];original=sources[(p['source_split'],p['passage_id'])]
  assert p['text']==original['text'] and p['article_path']==original['article_path']
  assert p['article_path'] not in prior
  assert p['passage_id']==samples[r['review_index']]['passage_id']
  check_spans(r,p['text']);ids={c['claim_id'] for c in r['claims']}
  for c in r['claims']:
   for d in [c['start']]+([c['end']] if c['end'] else []):
    parsed=parse_date(d['source_span']['text'],d['source_span']['start']);assert parsed==d;date_checks+=1
   assert c['unit_span']['start']<=c['start']['source_span']['start']<c['start']['source_span']['end']<=c['unit_span']['end']
   assert c['unit_span']['text'].strip()
  for edge in r['directed_pairs']:
   assert edge['witness_id'] in ids and edge['target_id'] in ids and edge['witness_id']!=edge['target_id'];pairs+=1
  assert set(map(tuple,r['known_precedence']))=={(e['target_id'],e['witness_id']) for e in r['directed_pairs']}
 with tempfile.TemporaryDirectory(prefix='replacement-replay-') as tmp:
  rerun=pathlib.Path(tmp);summary=evaluate(records,rerun)
  files=['decisions.jsonl','support_oracle.jsonl','instability_worlds.jsonl','summary.json']
  for name in files:assert (O/'runs'/name).read_bytes()==(rerun/name).read_bytes(),name
 order_manifest=json.loads((O/'order_view_manifest.json').read_text())
 for path,h in order_manifest['files'].items():assert sha(R/path)==h,path
 with tempfile.TemporaryDirectory(prefix='replacement-order-replay-') as tmp:
  order_out=pathlib.Path(tmp);order_summary=evaluate_order(records,order_out)
  for name,h in order_manifest['outputs'].items():
   assert sha(O/'order_runs'/name)==h,name
   assert (O/'order_runs'/name).read_bytes()==(order_out/name).read_bytes(),name
 baseline={(d['record_id'],d['query_date'],d['k']) for d in read(O/'runs/decisions.jsonl')}
 assert baseline=={(d['record_id'],d['query_date'],d['k']) for d in read(O/'order_runs/order_decisions.jsonl')}
 for row in read(O/'order_runs/order_support.jsonl'):
  assert not row['replacement']['possible'] or row['interval']['possible']
  assert not row['replacement']['guaranteed'] or row['interval']['guaranteed']
 report={'source_order_view_rerun_matches':True,'source_order_world_pairs':order_summary['feasible_instability_pairs'],'source_order_queries_unchanged':True,'status':'passed','source_membership_rows':len(samples),'source_judgments_retained':len(judgments),'accepted_records':len(records),'literal_spans_checked':spans,'calendar_dates_checked':date_checks,'directed_pairs_checked':pairs,'source_export_matches':len(records),'frozen_inputs_match':True,'documented_implementation_corrections':len(corrections),'complete_rerun_matches':True,'oracle_support_comparisons':summary['counts']['support_mask_comparisons'],'feasible_witness_pairs':summary['counts']['instability_witness_pairs'],'all_worlds_replay':True,'accepted_records_sha256':sha(O/'accepted_records.jsonl'),'outputs':{n:sha(O/'runs'/n) for n in files}}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
