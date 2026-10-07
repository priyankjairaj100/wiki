#!/usr/bin/env python3
"""Keep fixed reader cohorts and reuse only identical requests and execution identities."""
import collections,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass5.pipeline.run_matched import prompt_for
from pass4.inference.run_jsonl_final import make_request

def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def lines(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in o))
def identity():
 freeze=json.loads((ROOT/'pass4/inference/provenance/primary_reader_freeze_final.json').read_text())
 keys=['model_repository','model_revision','model_sha256','runtime_release','runtime_commit','max_tokens','temperature','seed','cache_prompt','json_grammar','threads','batch_threads','context_tokens','parallel_slots','gpu_layers','batch_tokens','ubatch_tokens','poll','poll_batch']
 return {k:freeze[k] for k in keys}
def check_execution(folder):
 ident=identity();m=json.loads((folder/'reader_output.manifest.json').read_text());rows=read(folder/'reader_output.jsonl')
 assert sha(folder/'reader_output.jsonl')==m['output_sha256'] and sha(folder/'reader_input.jsonl')==m['input_sha256']
 assert len(rows)==m['rows']==m['output_rows'];assert len({r['id'] for r in rows})==len(rows)
 cmd=m['server_command'];flags={'-c':'context_tokens','-t':'threads','-tb':'batch_threads','-b':'batch_tokens','-ub':'ubatch_tokens','--poll':'poll','--poll-batch':'poll_batch','--parallel':'parallel_slots','--n-gpu-layers':'gpu_layers','--seed':'seed','--temp':'temperature'}
 for flag,key in flags.items():assert cmd.count(flag)==1 and cmd[cmd.index(flag)+1]==str(ident[key]),flag
 inputs={r['id']:r for r in read(folder/'reader_input.jsonl')};assert set(inputs)=={r['id'] for r in rows}
 for row in rows:
  assert row['request']==make_request(inputs[row['id']],max_tokens=96,seed=1729)
  assert row['request_sha256']==digest(row['request'])
  for key in ['model_repository','model_revision','model_sha256','runtime_release']:assert row[key]==ident[key]
  fingerprint=row['response'].get('system_fingerprint','');assert ident['runtime_release'] in fingerprint and ident['runtime_commit'][:9] in fingerprint
 return rows

def main():
 if (ROOT/'pass5/inference/reuse_manifest.json').exists():raise FileExistsError('Reader requests already frozen')
 ident=identity();predictions={r['question_id']:r for r in read(ROOT/'pass5/pipeline/human/predictions.jsonl')};alljobs={};cohorts={};allmembers=[]
 for name,qpath in [('human','pass5/protocol/reader_primary_queries.jsonl'),('human_diagnostic','pass4/pipeline/human_diagnostic/queries.jsonl')]:
  queries=read(ROOT/qpath);jobs={};members=[]
  for q in queries:
   p=predictions[q['question_id']];assert p['question']==q['question']
   for method,m in p['methods'].items():
    prompt=prompt_for(q,m['contexts']);jid=hashlib.sha256(prompt.encode()).hexdigest()
    j=jobs.setdefault(jid,{'job_id':jid,'question_id':q['question_id'],'question':q['question'],'prompt':prompt,'methods':[],'context_signature':m['context_signature'],'contexts':m['contexts']});j['methods'].append(method)
    members.append({'question_id':q['question_id'],'method':method,'job_id':jid,'context_signature':m['context_signature']})
  folder=ROOT/f'pass5/inference/{name}';lines(folder/'reader_jobs.jsonl',jobs.values());lines(folder/'reader_memberships.jsonl',members)
  (folder/'queries.jsonl').write_bytes((ROOT/qpath).read_bytes())
  inputs=[{'id':j['job_id'],'prompt':j['prompt'],'max_tokens':96,'metadata':{k:v for k,v in j.items() if k!='prompt'}} for j in jobs.values()];lines(folder/'reader_input.jsonl',inputs)
  cohorts[name]={'questions':len(queries),'conditions':len(members),'unique_requests':len(jobs),'query_sha256':sha(ROOT/qpath),'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [folder/'reader_jobs.jsonl',folder/'reader_memberships.jsonl',folder/'reader_input.jsonl',folder/'queries.jsonl']}}
  for j in jobs.values():
   if j['job_id'] in alljobs:assert alljobs[j['job_id']]['prompt']==j['prompt']
   alljobs[j['job_id']]=j
  allmembers+=members
 # Restore public pipeline diagnostic interface without selecting a revised cohort.
 diag=ROOT/'pass5/pipeline/human_diagnostic';diag.mkdir(parents=True,exist_ok=True)
 for name in ['reader_jobs.jsonl','reader_memberships.jsonl','queries.jsonl']:(diag/name).write_bytes((ROOT/'pass5/inference/human_diagnostic'/name).read_bytes())
 old={};hist_sources={}
 for name in ['human','human_diagnostic']:
  folder=ROOT/f'pass4/inference/{name}';rows=check_execution(folder);path=str((folder/'reader_output.jsonl').relative_to(ROOT));hist_sources[path]=sha(folder/'reader_output.jsonl')
  for row in rows:
   key=digest({'request':row['request'],'execution':ident});assert key not in old;old[key]=(path,row)
 lineage=[];delta=[];delta_jobs=[]
 for jid,j in alljobs.items():
  inp={'id':jid,'prompt':j['prompt'],'max_tokens':96,'metadata':{k:v for k,v in j.items() if k!='prompt'}};request=make_request(inp,max_tokens=96,seed=1729);key=digest({'request':request,'execution':ident})
  prior=old.get(key);record={'job_id':jid,'request_sha256':digest(request),'execution_request_key':key,'kind':'reused_exact' if prior else 'new_delta','source_path':prior[0] if prior else 'pass5/inference/delta/reader_output.jsonl','source_id':prior[1]['id'] if prior else jid}
  if prior:assert prior[1]['id']==jid and prior[1]['request']==request
  else:delta.append(inp);delta_jobs.append(j)
  lineage.append(record)
 lines(ROOT/'pass5/inference/delta_input.jsonl',delta);lines(ROOT/'pass5/inference/delta_jobs.jsonl',delta_jobs);lines(ROOT/'pass5/inference/reader_lineage.jsonl',lineage)
 byid={r['job_id']:r for r in lineage}
 for name,c in cohorts.items():
  ids={j['job_id'] for j in read(ROOT/f'pass5/inference/{name}/reader_jobs.jsonl')};c['reused_exact']=sum(byid[i]['kind']=='reused_exact' for i in ids);c['new_delta']=sum(byid[i]['kind']=='new_delta' for i in ids)
 result={'study':'Post-audit source revision on unchanged questions; historical and new actual outputs are distinguished.','execution_identity':ident,'historical_sources':hist_sources,'historical_completed_requests':len(old),'current_unique_requests':len(alljobs),'reused_exact':len(alljobs)-len(delta),'new_delta':len(delta),'cohorts':cohorts,'files':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'pass5/inference/delta_input.jsonl',ROOT/'pass5/inference/delta_jobs.jsonl',ROOT/'pass5/inference/reader_lineage.jsonl',Path(__file__)]}}
 save(ROOT/'pass5/inference/reuse_manifest.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
