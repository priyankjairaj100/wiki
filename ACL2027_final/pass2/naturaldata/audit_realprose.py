#!/usr/bin/env python3
"""Audit supplied RealProse claims against their supplied text, without changing labels."""
import json, pathlib, re, hashlib, collections, argparse
R=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source',type=pathlib.Path);args=parser.parse_args()
candidates=[R.parents[1]/'inputs/supplement/wikigraphrag-code-and-data/data/realprose/claims.jsonl', R.parents[1]/'original/data/realprose/claims.jsonl']
source=args.source or next((p for p in candidates if p.exists()),candidates[0])
rows=[json.loads(l) for l in source.open()]
# Read the supplied excerpts manually. These excerpts do not state the assigned subject-role pair.
unsupported={0:'The excerpt only identifies a businessman and philanthropist.',85:'The excerpt names Everton, not Manchester United.',86:'The excerpt names no club.',87:'The excerpt names no club.',88:'The excerpt names Beşiktaş, not Manchester United.',89:'The excerpt names no club.',90:'The excerpt names AC Milan, not Manchester United.',91:'The excerpt names a FIFA role, not the Arsenal manager role.',92:'The excerpt names Aston Villa, not Arsenal.',94:'The excerpt names no club.',95:'The excerpt names no club.',96:'The excerpt names no club.',97:'The excerpt names Al Qadsiah, not Liverpool.',98:'The excerpt names a Red Bull role, not the Liverpool manager role.',100:'The excerpt names no club.',101:'The excerpt names Real Betis, not Manchester City.',102:'The excerpt names no club.'}
report=[]
for r in rows:
 n=int(r['cid'].split(':')[1]);yr=str(int(r['timestamp']))
 report.append({'claim_id':r['cid'],'subject':r['subject'],'relation':r['relation'],'value':r['value'],'assigned_timestamp':r['timestamp'],'source_title':r['meta']['title'],'source_text':r['text'],'assigned_start_year_occurs_in_text':bool(re.search(r'(?<!\d)'+yr+r'(?!\d)',r['text'])),'manual_unsupported_subject_role':n in unsupported,'manual_note':unsupported.get(n),'source_revision_id_supplied':False,'source_publication_date_supplied':False,'start_year_conflict': 'Assigned 2003; excerpt says President from 2004 to 2011.' if n==119 else None})
(R/'realprose_source_audit.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in report))
summary={'claims':len(rows),'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'manually_identified_excerpts_without_assigned_subject_role':len(unsupported),'claim_ids_without_assigned_subject_role':[f'rp:{n}' for n in unsupported],'assigned_start_year_absent_from_excerpt':sum(not x['assigned_start_year_occurs_in_text'] for x in report),'direct_start_year_conflicts':['rp:119'],'source_revision_ids_present':0,'source_publication_dates_present':0,'interpretation':'This audit concerns evidence in the provided excerpts, not truth of the corresponding real-world facts. Lexical year presence is not temporal entailment. The 17 omissions are manually identified examples, not a complete semantic audit.','benchmark_use':'Use as a legacy controlled detection check. Do not describe all 132 records as independently source-supported dated claims.'}
(R/'realprose_source_audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
