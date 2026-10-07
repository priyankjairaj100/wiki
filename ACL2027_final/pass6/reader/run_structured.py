#!/usr/bin/env python3
"""Freeze and execute the same reader prompts with schema-constrained decoding."""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, platform, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pass4.inference.run_jsonl_final import LocalRunner, make_request, json_request, digest, MODEL_REPO, MODEL_REVISION, MODEL_SHA256
from pass3.protocol.parse_reader import parse_response
HERE=ROOT/'pass6/reader'
CACHE=ROOT.parent/'acl2027_inference_cache'

def read(p): return [json.loads(x) for x in Path(p).read_text().splitlines() if x]
def save(p,obj):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_suffix(p.suffix+'.partial')
 with tmp.open('w') as f: f.write(json.dumps(obj,indent=2,ensure_ascii=False)+'\n'); f.flush(); os.fsync(f.fileno())
 tmp.replace(p)
def lines(p,rows):
 with Path(p).open('w') as f:
  for row in rows: f.write(json.dumps(row,ensure_ascii=False)+'\n')
  f.flush();os.fsync(f.fileno())
def prepare():
 if (HERE/'protocol.json').exists(): raise FileExistsError('Protocol already frozen')
 jobs={}; sources={}; cohorts={}
 for cohort in ['human','human_diagnostic']:
  folder=ROOT/'pass5/inference'/cohort
  for name in ['reader_jobs.jsonl','reader_memberships.jsonl','queries.jsonl']:
   p=folder/name; sources[str(p.relative_to(ROOT))]=digest(p)
   dst=HERE/cohort/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
  js=read(folder/'reader_jobs.jsonl');cohorts[cohort]={'questions':len(read(folder/'queries.jsonl')),'conditions':len(read(folder/'reader_memberships.jsonl')),'requests':len(js)}
  for j in js:
   assert hashlib.sha256(j['prompt'].encode()).hexdigest()==j['job_id']
   assert j['job_id'] not in jobs
   jobs[j['job_id']]=j
 rows=[]
 for jid,j in sorted(jobs.items()):
  schema={'type':'object','properties':{'answers':{'type':'array','items':{'type':'string','minLength':1}},'evidence':{'type':'array','items':{'type':'integer','enum':list(range(1,len(j['contexts'])+1))}}},'required':['answers','evidence'],'additionalProperties':False}
  rows.append({'id':jid,'prompt':j['prompt'],'max_tokens':512,'response_format':{'type':'json_object','schema':schema},'metadata':{k:v for k,v in j.items() if k!='prompt'}})
 lines(HERE/'reader_input.jsonl',rows)
 protocol={'name':'Structured reader replication on unchanged source contexts','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cohorts':cohorts,'requests':len(rows),'selection':'All 234 unique requests from the unchanged 60-question primary and 11-question historical diagnostic cohorts. No new question selection.','source_files':sources,'input_sha256':digest(HERE/'reader_input.jsonl'),'runner_sha256':digest(__file__),'model_repository':MODEL_REPO,'model_revision':MODEL_REVISION,'model_sha256':MODEL_SHA256,'runtime_release':'b11435','runtime_commit':'43fe9c64281ef735046adc025e9e7559a1f659a5','runtime_binary_sha256':digest(CACHE/'llama-b11435/llama-server'),'decoder':{'max_tokens':512,'temperature':0,'seed':1729,'cache_prompt':False,'json_schema':True,'evidence_indices':'Constrained to the supplied excerpt numbers.','answers':'Arbitrary nonempty strings; no answer vocabulary or count constraint.','threads':4,'batch_threads':4,'context_tokens':4096,'batch_tokens':512,'ubatch_tokens':512,'parallel_slots':1,'gpu_layers':0},'pilot':{'selection':'Six lexicographically smallest prompt SHA256 identifiers.','ids':[r['id'] for r in rows[:6]],'gate':'All six complete with stop and pass the unchanged frozen parser. No answer labels or quality scores are inspected before the full run.','action_if_gate_passes':'Continue once over every remaining request with identical settings.','action_if_gate_fails':'Stop. Preserve pilot records. Diagnose configuration or truncation before creating a separately versioned protocol.'},'analysis':'Use the existing strict parser, aliases, paired question scores, and article bootstrap. Include every condition. Compare validity, EM, strict set F1, changed answers among jointly parsed pairs, and target/prediction cardinalities. Do not select settings or rerun requests for better answer scores.','primary_sources':['https://github.com/ggml-org/llama.cpp/blob/43fe9c64281ef735046adc025e9e7559a1f659a5/tools/server/README.md','https://github.com/ggml-org/llama.cpp/blob/43fe9c64281ef735046adc025e9e7559a1f659a5/grammars/README.md']}
 assert len(rows)==234
 save(HERE/'protocol.json',protocol)
 print(json.dumps({'protocol_sha256':digest(HERE/'protocol.json'),'requests':len(rows),'cohorts':cohorts},indent=2),flush=True)

def execute():
 protocol=json.loads((HERE/'protocol.json').read_text());assert digest(__file__)==protocol['runner_sha256']; assert digest(HERE/'reader_input.jsonl')==protocol['input_sha256']
 for p,h in protocol['source_files'].items():assert digest(ROOT/p)==h,p
 assert digest(CACHE/'llama-b11435/llama-server')==protocol['runtime_binary_sha256']
 rows=read(HERE/'reader_input.jsonl');out=HERE/'reader_output.jsonl'
 completed={r['id']:r for r in read(out)} if out.exists() else {}
 for r in rows:
  if r['id'] in completed:assert completed[r['id']]['request']==make_request(r,512,1729)
 session=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 with LocalRunner(log_path=HERE/f'server_{session}.log',model=CACHE/'qwen2.5-3b-instruct-q4_k_m.gguf',server=CACHE/'llama-b11435/llama-server',threads=4,context=4096,batch=512,ubatch=512,seed=1729) as runner:
  save(HERE/f'server_{session}.json',{'command':runner.command,'properties':runner.properties,'load_seconds':runner.load_seconds,'platform':platform.platform(),'logical_cpus':os.cpu_count(),'protocol_sha256':digest(HERE/'protocol.json')})
  counts=[]
  for r in rows:
   request=make_request(r,512,1729)
   rendered=json_request(runner.url+'/apply-template',{'messages':request['messages']})['prompt']
   tokens=json_request(runner.url+'/tokenize',{'content':rendered,'add_special':True,'parse_special':True})['tokens']
   reserved=len(tokens)+512+16
   assert reserved<=4096,(r['id'],reserved)
   counts.append({'id':r['id'],'prompt_tokens':len(tokens),'max_tokens':512,'reserved_with_margin':reserved})
  save(HERE/'token_preflight.json',{'requests':len(counts),'context_tokens':4096,'margin_tokens':16,'max_reserved_tokens':max(x['reserved_with_margin'] for x in counts),'all_fit':True,'counts':counts})
  print('All 234 prompts fit the fixed context.',flush=True)
  with out.open('a') as f:
   for i,r in enumerate(rows):
    if r['id'] not in completed:
     result=runner.generate(r,512);result['execution_session']=session
     f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno());completed[r['id']]=result
     print(f"{i+1}/{len(rows)} {r['id']} {result['wall_seconds']:.2f}s tokens={result['response']['usage']['completion_tokens']} finish={result['finish_reason']}",flush=True)
    if i==5:
     pilot=[completed[x] for x in protocol['pilot']['ids']]
     parse=[parse_response(x['generation'],len(x['metadata']['contexts']),x['finish_reason']) for x in pilot]
     ok=all(p['parse_ok'] for p in parse)
     summary={'passed':ok,'requests':6,'valid':sum(p['parse_ok'] for p in parse),'finish_reasons':[x['finish_reason'] for x in pilot],'completion_tokens':[x['response']['usage']['completion_tokens'] for x in pilot],'wall_seconds':[x['wall_seconds'] for x in pilot],'mean_seconds':sum(x['wall_seconds'] for x in pilot)/6,'projected_total_minutes':sum(x['wall_seconds'] for x in pilot)/6*234/60,'quality_scores_inspected':False}
     save(HERE/'pilot_result.json',summary);print('PILOT '+json.dumps(summary),flush=True)
     if not ok: raise RuntimeError('Frozen format pilot gate failed')
  assert len(completed)==len(rows)
  save(HERE/'execution_manifest.json',{'complete':True,'requests':len(rows),'output_rows':len(completed),'protocol_sha256':digest(HERE/'protocol.json'),'input_sha256':digest(HERE/'reader_input.jsonl'),'output_sha256':digest(out),'token_preflight_sha256':digest(HERE/'token_preflight.json'),'sessions':sorted({r['execution_session'] for r in completed.values()}),'total_generation_wall_seconds':sum(r['wall_seconds'] for r in completed.values()),'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--run',action='store_true');args=p.parse_args()
 if args.prepare:prepare()
 if args.run:execute()
