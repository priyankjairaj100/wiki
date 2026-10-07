#!/usr/bin/env python3
"""Audit released TempLAMA renderings against complete source answer sets."""
import collections,hashlib,json,os,pathlib,sys
from run_evidence import DEFAULT_SOURCE,HERE,write_json
source=pathlib.Path(os.environ.get('TEMPLAMA_SOURCE',str(HERE.parent/'external/TempLAMA_test_with_aliases.json'))); out=HERE/'results'
claims=[json.loads(l) for l in (DEFAULT_SOURCE/'data/templama/claims.jsonl').read_text().splitlines()]
keys={c['meta']['key'] for c in claims}; originals=collections.defaultdict(list)
for line in source.open():
 row=json.loads(line); k=row['id'].rsplit('_',1)[0]
 if k in keys: originals[k].append(row)
rows=[]; transitions=[]; safe=[]; stats=collections.defaultdict(collections.Counter)
for key,group in originals.items():
 group.sort(key=lambda row:row['date']); previous_first=None
 all_single=all(len({a['wikidata_id'] for a in row['answer']})==1 for row in group)
 if all_single:safe.append(key)
 for row in group:
  answers=row['answer']; aset={a['wikidata_id'] for a in answers}; first=answers[0]['wikidata_id'] if answers else None
  rows.append(dict(key=key,date=row['date'],query=row['query'],answer_qids=sorted(aset),answers=answers,first_answer_qid=first,all_years_single_valued=all_single))
  relation=key.rsplit('_',1)[1]; stats[relation]['rows']+=1; stats[relation]['multi_rows']+=len(aset)>1
  if previous_first is not None and previous_first!=first:
   transitions.append(dict(key=key,date=row['date'],old_first=previous_first,new_first=first,old_still_valid=previous_first in aset,answers=sorted(aset)))
  previous_first=first
# Check exact rebuild from first answer source semantics.
rebuilt=[]
for key in sorted(originals):
 prev=None
 for row in sorted(originals[key],key=lambda row:row['date']):
  ans=row['answer']
  if not ans:continue
  a=ans[0]; qid=a['wikidata_id']; names=a.get('original_name') or a.get('name') or ['']; name=names[0] if isinstance(names,list) else names
  if not name or qid==prev:continue
  rebuilt.append((key,row['date'],qid,name,row['query'].replace('_X_',name).strip()));prev=qid
provided={(c['meta']['key'],c['meta']['year'],c['meta']['answer_qid'],c['value'],c['text']) for c in claims}
rebuilt_set={(key,date,qid,name,text if text.endswith(('.','!','?')) else text+'.') for key,date,qid,name,text in rebuilt}
write_json(out/'templama_source_rows.json',rows)
write_json(out/'templama_source_transitions.json',transitions)
write_json(out/'templama_single_value_keys.json',sorted(safe))
summary=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),n_released_keys=len(keys),n_found_keys=len(originals),n_source_rows=len(rows),
 multi_answer_rows=sum(len(r['answer_qids'])>1 for r in rows),keys_with_any_multi_answer=len(keys)-len(safe),keys_single_answer_every_year=len(safe),
 first_answer_transitions=len(transitions),first_answer_transitions_where_old_answer_remains=sum(t['old_still_valid'] for t in transitions),
 keys_with_such_transitions=len({t['key'] for t in transitions if t['old_still_valid']}),rendered_claims_exactly_match_rebuild=provided==rebuilt_set,
 relations=dict(stats),note='A first-listed answer change is not a retirement when the old answer remains in the complete source answer set.')
write_json(out/'templama_source_audit.json',summary)
print(json.dumps(summary,indent=2))
