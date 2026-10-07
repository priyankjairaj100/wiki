"""Reproduce the frozen schema-required calibration jobs without changing V1."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
schema=json.loads((ROOT/'output_schema_v2.json').read_text())
rows=[json.loads(x) for x in (ROOT/'jobs.jsonl').read_text().splitlines()]
for row in rows:
    row['id']=row['id'].replace('succession-','succession-schema-')
    row['response_format']={'type':'json_object','schema':schema}
    row['metadata']['adapter_variant']='schema-required-source-quotes-v2'
    row['prompt']='Copy each exact source quote before filling its extracted fields. All output records require a quote.\n\n'+row['prompt']
text=''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows)
expected=json.loads((ROOT/'manifest_schema_v2.json').read_text())['jobs_sha256']
actual=hashlib.sha256(text.encode()).hexdigest()
if actual!=expected:raise ValueError('Reproduced jobs differ from the frozen V2 manifest.')
(ROOT/'jobs_schema_v2.jsonl').write_text(text)
print(json.dumps({'jobs':len(rows),'sha256':actual,'matches_frozen_manifest':True}))
