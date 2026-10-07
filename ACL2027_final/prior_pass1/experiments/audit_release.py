#!/usr/bin/env python3
"""Validate released hashes, rerun detection, and record benchmark provenance."""
import collections, hashlib, json, pathlib, sys
from run_evidence import DEFAULT_SOURCE,HERE,write_json,norm
sys.path.insert(0,str(DEFAULT_SOURCE))
from wikigraphrag.core.claim import Claim
from wikigraphrag.data.io import load_claims
from wikigraphrag.detect import SupersessionDetector
from wikigraphrag.eval.detection import evaluate_detection,gold_superseded
from wikigraphrag.detect.baselines import NewestDocWinsDetector
from experiments.run_pooled import _prf,_isolated,_pooled

out=HERE/'results'; out.mkdir(exist_ok=True)
man=json.loads((DEFAULT_SOURCE/'results/MANIFEST.json').read_text()); checks=[]
for name,info in man['datasets'].items():
 p=DEFAULT_SOURCE/info['path']; checks.append(dict(path=info['path'],ok=hashlib.sha256(p.read_bytes()).hexdigest()==info['sha256']))
for name,h in man['result_files'].items():
 p=DEFAULT_SOURCE/name; checks.append(dict(path=name,ok=p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==h))
write_json(out/'release_integrity.json',dict(n_files=len(checks),all_verified=all(x['ok'] for x in checks),checks=checks))
rows=[]
for p in sorted((DEFAULT_SOURCE/'data').glob('*/claims.jsonl')):
 cs=load_claims(str(p)); r=evaluate_detection(cs); r.pop('edges'); name=p.parent.name
 oldpath=DEFAULT_SOURCE/f'results/detection_{name}.json'
 old=json.loads(oldpath.read_text()) if oldpath.exists() else {}
 compared={key:dict(cached=old[key],rerun=r[key],matches=old[key]==r[key]) for key in ('precision','recall','f1','tp','fp','fn') if key in old}
 group=collections.defaultdict(list)
 for c in cs: group[c.gold_key].append(c)
 ties=0; recurrence=0
 for g in group.values():
  bytime=collections.defaultdict(set)
  for c in g: bytime[c.timestamp].add(norm(c.value))
  ties+=sum(len(v)>1 for v in bytime.values())
  seq=[]
  for c in sorted(g,key=lambda c:c.timestamp or 0):
   v=norm(c.value)
   if not seq or seq[-1]!=v:seq.append(v)
  recurrence+=len(set(seq))<len(seq)
 rows.append(dict(dataset=name,n_claims=len(cs),n_keys=len(group),n_distinct_dates=len({c.timestamp for c in cs}),ties=ties,recurring_keys=recurrence,detection=r,cached_comparison=compared,
      literal_value_absent=sum(norm(c.value) not in norm(c.text) for c in cs),literal_subject_absent=sum(norm(c.subject) not in norm(c.text) for c in cs)))
write_json(out/'detection_replay.json',rows)
pools=[]
for names in [['wikidata','freshrag','realworld'],['wikidata','freshrag','realworld','templama']]:
 cs=[c for name in names for c in load_claims(str(DEFAULT_SOURCE/'data'/name/'claims.jsonl'))]; gold=gold_superseded(cs)
 res={rule:{'isolated':_prf(_isolated(cs,det),gold),'pooled':_prf(_pooled(cs,det),gold)} for rule,det in [('heuristic',SupersessionDetector()),('newest_doc_wins',NewestDocWinsDetector())]}
 cached=json.loads((DEFAULT_SOURCE/('results/pooled_'+'_'.join(names)+'.json')).read_text())
 pools.append(dict(datasets=names,n_claims=len(cs),results=res,cached_results_match=res==cached['results']))
write_json(out/'pooled_detection_replay.json',pools)
caches=[]
for p in sorted((DEFAULT_SOURCE/'data/cache').glob('*.jsonl')):
 data=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]
 caches.append(dict(path=str(p.relative_to(DEFAULT_SOURCE)),n_rows=len(data),fields=sorted({k for row in data for k in row}),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
write_json(out/'cache_inventory.json',caches)
print(json.dumps(dict(integrity=all(x['ok'] for x in checks),detection_datasets=len(rows),detection_compared=sum(bool(x['cached_comparison']) for x in rows),pooled_all_match=all(x['cached_results_match'] for x in pools),caches=caches),indent=2))
