#!/usr/bin/env python3
"""Aggregate recorded source judgments; preserve every individual decision."""
import collections, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def read(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (HERE/'judgments_freeze.json').exists(),'Final judgments are already frozen.'
 freeze=json.loads((HERE/'freeze.json').read_text())
 for item in freeze['inputs'].values():assert sha(ROOT/item['path'])==item['sha256'],item['path']
 sample=read(HERE/'sample.jsonl'); rows=[]
 for p in sorted(HERE.glob('review_*.jsonl')): rows+=read(p)
 by={r['claim_id']:r for r in rows};assert len(by)==len(rows)==len(sample)==60
 expected={r['claim']['claim_id']for r in sample};assert set(by)==expected
 ordered=[]
 for n,s in enumerate(sample,1):
  r=by[s['claim']['claim_id']]
  assert r['core_status']in ['accept','reject','uncertain']
  assert r['end_status']in ['accept','reject','uncertain','not_supplied']
  assert r['omitted_end_status']in ['none','explicit_omission','uncertain']
  assert bool(s['claim'].get('end'))==(r['end_status']!='not_supplied')
  assert r.get('core_note') and r.get('lifecycle_note')
  ordered.append({'sample_number':n,'split':s['split'],'article_path':s['claim']['article_path'],**r})
 (HERE/'judgments.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n'for r in ordered))
 literal=json.loads((HERE/'literal_checks.json').read_text());freeze=json.loads((HERE/'freeze.json').read_text())
 report={'review_type':'Model-assisted review of complete source paragraphs','human_annotations':False,'claims':60,'articles':len({r['article_path']for r in ordered}),'split_counts':dict(collections.Counter(r['split']for r in ordered)),'core_event_counts':dict(collections.Counter(r['core_status']for r in ordered)),'supplied_end_counts':dict(collections.Counter(r['end_status']for r in ordered)),'omitted_end_counts':dict(collections.Counter(r['omitted_end_status']for r in ordered)),'omitted_end_counts_in_accepted_events':dict(collections.Counter(r['omitted_end_status']for r in ordered if r['core_status']=='accept')),'literal_checks':literal,'source_only_review':True,'post_audit_adapter_tuning':False,'prior_lost_results_reused':False,'prior_exposure_reconstruction_complete':False,'recorded_excluded_articles':freeze['excluded_article_count'],'scope':'New recorded sample outside documented exposure. Full membership of the lost prior audit is unavailable. These judgments do not estimate extraction recall or corpus-wide precision.'}
 (HERE/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
 files=['PROTOCOL.md','select_sample.py','check_literal.py','finalize_review.py','freeze.json','sample.jsonl','sample_membership.json','exposure_registry.json','literal_checks.json','source_export_match.json','judgments.jsonl','summary.json','README.md','show_sample.py']+[p.name for p in sorted(HERE.glob('review_*.jsonl'))]
 (HERE/'judgments_freeze.json').write_text(json.dumps({'status':'Final, no post-audit tuning','created_utc':datetime.now(timezone.utc).isoformat(),'files':{n:sha(HERE/n)for n in files}},indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
