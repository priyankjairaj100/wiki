from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'data'/'dev_succession_candidates.jsonl'
prompt=(ROOT/'prompt.txt').read_text()
source=[json.loads(x) for x in SOURCE.read_text().splitlines()]
rows=[]
for p in source:
    title=p['article_path'].split('/wiki/',1)[-1].replace('_',' ')
    rows.append({'id':'succession-'+p['passage_id'],'system':'You extract source-supported historical states. Return valid JSON only.',
                 'prompt':prompt+'\nARTICLE TITLE: '+title+'\nPASSAGE:\n'+p['text'],
                 'max_tokens':1400,'response_format':{'type':'json_object'},
                 'metadata':{'passage_id':p['passage_id'],'article_path':p['article_path'],'source_sha256':hashlib.sha256(p['text'].encode()).hexdigest(),
                             'scope':'exploratory source-only DEV cue calibration','source_selection_rank':p['selection_rank']}})
(ROOT/'jobs.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
manifest={'source_file':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
          'jobs_sha256':hashlib.sha256((ROOT/'jobs.jsonl').read_bytes()).hexdigest(),'jobs':len(rows),'maximum_output_tokens_per_job':1400,
          'source_selection':'30 DEV paragraphs selected through source succession cues only','input_features':['article title','source paragraph'],
          'gold_labels_in_prompts':False,'evaluation_outcomes_in_prompts':False,'status':'frozen before model outputs','postprocessing':'exact source quote/name/date matching; no invented starts; role-centric keys; exact directed source succession only'}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
