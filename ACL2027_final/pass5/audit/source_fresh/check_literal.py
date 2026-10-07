#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def spans(x,path=''):
 if isinstance(x,dict):
  if {'start','end','text'}<=x.keys() and isinstance(x['text'],str):yield path,x
  for k,v in x.items():yield from spans(v,path+'.'+k)
 elif isinstance(x,list):
  for k,v in enumerate(x):yield from spans(v,path+f'[{k}]')
def main():
 freeze=json.loads((HERE/'freeze.json').read_text())
 for item in freeze['inputs'].values():assert digest(ROOT/item['path'])==item['sha256'],item['path']
 rows=[json.loads(x)for x in(HERE/'sample.jsonl').read_text().splitlines()];issues=[];count=0;ends=0
 for r in rows:
  c=r['claim'];s=r['source_paragraph'];assert c['article_path']==s['article_path']
  if c.get('end'):ends+=1
  for field,span in spans(c):
   count+=1;a=span['start'];b=span['end']
   if not(type(a)is int and type(b)is int and 0<=a<b<=len(s['text'])and s['text'][a:b]==span['text']):issues.append({'claim_id':c['claim_id'],'field':field})
 report={'claims_checked':len(rows),'spans_checked':count,'spans_matching':count-len(issues),'issues':issues,'supplied_ends':ends,'sample_sha256':digest(HERE/'sample.jsonl'),'freeze_inputs_unchanged':True}
 (HERE/'literal_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
 assert not issues
if __name__=='__main__':main()
