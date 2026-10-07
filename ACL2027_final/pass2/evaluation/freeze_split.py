#!/usr/bin/env python3
"""Create immutable key-disjoint development/test split before new method runs."""
import collections,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]
source=ROOT/'work/external/TempLAMA_official_test.json'
prior=ROOT/'inputs/supplement/wikigraphrag-code-and-data/data/templama/claims.jsonl'
rows=[json.loads(l) for l in source.open()]
old={r['meta']['key'] for r in map(json.loads,prior.open())}
keys={r['id'].rsplit('_',1)[0] for r in rows}
namespace='ACL2027-PASS2-TEMPLAMA-KEY-SPLIT-V1'
# Unseen keys are deterministically partitioned 20/80. Old keys never enter test.
partition={k:('legacy_dev' if k in old else 'development' if int(hashlib.sha256((namespace+'|'+k).encode()).hexdigest(),16)%5==0 else 'test') for k in sorted(keys)}
counts={part:{'keys':sum(p==part for p in partition.values()),'rows':sum(partition[r['id'].rsplit('_',1)[0]]==part for r in rows),'answer_observations':sum(len(r['answer']) for r in rows if partition[r['id'].rsplit('_',1)[0]]==part)} for part in ('legacy_dev','development','test')}
manifest={'protocol':'all-positive-source-observations-v1','split_namespace':namespace,'assignment':'sha256(namespace|source_key) modulo 5: 0=development, otherwise test; 300 prior keys excluded from test','source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_rows':len(rows),'source_keys':len(keys),'answer_observations':sum(len(r['answer']) for r in rows),'prior_selected_keys_sha256':hashlib.sha256('\n'.join(sorted(old)).encode()).hexdigest(),'counts':counts,'keys':partition,'inference_fields':['opaque observation id','rendered text','source date'],'gold_fields_for_scoring_only':['source key','Wikidata answer ID','relation ID','complete source answer set'],'limitations':['Source answer sets are benchmark labels; source-record absence is not an event that retires a claim.','Methods may rank recent positive evidence. These ranks do not certify real-world invalidity.','Benchmark template inventory is available to all parsing methods; source keys and answer IDs are unavailable at inference.'],'freeze_script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
p=HERE/'split_manifest.json'
if p.exists():
 assert json.loads(p.read_text())==manifest,'Existing frozen split differs; refusing to overwrite.'
else:p.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k not in ('keys','limitations','gold_fields_for_scoring_only')},indent=2))
