#!/usr/bin/env python3
"""Audit indistinguishable text queries without treating entity IDs as inference input."""
import collections,json,pathlib
H=pathlib.Path(__file__).resolve().parent;R=H.parents[1]
split=json.loads((H/'split_manifest.json').read_text())['keys']
rows=[json.loads(l) for l in (R/'work/external/TempLAMA_official_test.json').open()]
groups=collections.defaultdict(list)
for r in rows:groups[(r['query'],r['date'])].append(r)
out=[]
for (query,date),group in groups.items():
 keys={r['id'].rsplit('_',1)[0] for r in group}
 if len(keys)<2:continue
 counts=collections.Counter(a['wikidata_id'] for r in group for a in r['answer'])
 out.append({'query':query,'date':date,'source_ids':[r['id'] for r in group],'source_keys':sorted(keys),'splits':[split[r['id'].rsplit('_',1)[0]] for r in group],'answers':[[a['wikidata_id'] for a in r['answer']] for r in group],'single_answer_max_correct':max(counts.values())})
summary={'indistinguishable_query_date_groups':len(out),'source_rows_in_groups':sum(len(g['source_ids']) for g in out),'source_keys':len({k for g in out for k in g['source_keys']}),'test_source_rows_in_groups':sum(g['splits'].count('test') for g in out),'test_source_keys':len({sid.rsplit('_',1)[0] for g in out for sid in g['source_ids'] if split[sid.rsplit('_',1)[0]]=='test'}),'notes':['The query text and year are identical for multiple source entities.','Inference does not receive the hidden entity ID.','We retain these items in the main evaluation and publish their identities.']}
(H/'results/ambiguity_audit.json').write_text(json.dumps({'summary':summary,'groups':out},indent=2,ensure_ascii=False)+'\n')
print(json.dumps(summary,indent=2))
