#!/usr/bin/env python3
"""Execute a frozen request queue on two independent, identical local servers."""
from __future__ import annotations
import argparse, concurrent.futures, datetime, hashlib, json, os, platform, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass6.reader.run_structured import HERE,CACHE,read,save,lines
from pass4.inference.run_jsonl_final import LocalRunner,make_request,digest

def prepare():
 assert not (HERE/'scheduling_amendment.json').exists()
 protocol=json.loads((HERE/'protocol.json').read_text());assert digest(HERE/'run_structured.py')==protocol['runner_sha256']
 pilot=json.loads((HERE/'pilot_result.json').read_text());assert pilot['passed'] and pilot['valid']==6
 rows=read(HERE/'reader_input.jsonl');initial=read(HERE/'reader_output.jsonl')
 assert len(initial)==len({r['id'] for r in initial});assert [r['id'] for r in initial]==[r['id'] for r in rows[:len(initial)]]
 (HERE/'initial_output.jsonl').write_bytes((HERE/'reader_output.jsonl').read_bytes())
 pending=rows[len(initial):]
 memory={k:(Path('/sys/fs/cgroup')/k).read_text().strip() for k in ['memory.current','memory.max','memory.stat','cpu.max']}
 amendment={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'Use the eight available CPU cores to reduce elapsed time. No model, prompt, schema, parser, or decoder setting changes.','original_protocol_sha256':digest(HERE/'protocol.json'),'parallel_runner_sha256':digest(__file__),'input_sha256':digest(HERE/'reader_input.jsonl'),'initial_output_sha256':digest(HERE/'initial_output.jsonl'),'initial_completed_requests':len(initial),'initial_execution_stopped_by':'Interrupt sent through the execution service. Any in-flight request had no completed output and remains pending.','possible_interrupted_request':pending[0]['id'] if pending else None,'queue':'Preserve the original frozen request order. Assign remaining rows alternately to worker 0 and worker 1.','worker_count':2,'each_worker':'One independent server with the exact original four-thread and one-slot settings. Prompt caching remains disabled.','pending_requests':len(pending),'worker_requests':{},'memory_and_cpu_before_start':memory,'completed_responses_inspected_for_quality':False}
 for w in range(2):
  subset=pending[w::2];lines(HERE/f'worker_{w}_input.jsonl',subset);amendment['worker_requests'][str(w)]={'requests':len(subset),'input_sha256':digest(HERE/f'worker_{w}_input.jsonl'),'ids':[r['id'] for r in subset]}
 save(HERE/'scheduling_amendment.json',amendment)
 print(json.dumps({'initial':len(initial),'pending':len(pending),'workers':{k:v['requests'] for k,v in amendment['worker_requests'].items()}},indent=2),flush=True)

def worker(w,amendment):
 rows=read(HERE/f'worker_{w}_input.jsonl');assert digest(HERE/f'worker_{w}_input.jsonl')==amendment['worker_requests'][str(w)]['input_sha256']
 out=HERE/f'worker_{w}_output.jsonl';completed={r['id']:r for r in read(out)} if out.exists() else {}
 for row in rows:
  if row['id'] in completed:assert completed[row['id']]['request']==make_request(row,512,1729)
 session=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+f'_worker{w}'
 with LocalRunner(log_path=HERE/f'server_{session}.log',model=CACHE/'qwen2.5-3b-instruct-q4_k_m.gguf',server=CACHE/'llama-b11435/llama-server',threads=4,context=4096,batch=512,ubatch=512,seed=1729) as runner:
  save(HERE/f'server_{session}.json',{'command':runner.command,'properties':runner.properties,'load_seconds':runner.load_seconds,'platform':platform.platform(),'logical_cpus':os.cpu_count(),'protocol_sha256':digest(HERE/'protocol.json'),'scheduling_amendment_sha256':digest(HERE/'scheduling_amendment.json')})
  with out.open('a') as f:
   for i,row in enumerate(rows):
    if row['id'] in completed:continue
    result=runner.generate(row,512);result['execution_session']=session
    f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno());completed[row['id']]=result
    print(f"worker={w} {i+1}/{len(rows)} id={row['id']} seconds={result['wall_seconds']:.2f} tokens={result['response']['usage']['completion_tokens']} finish={result['finish_reason']}",flush=True)
  assert len(completed)==len(rows)
  save(HERE/f'worker_{w}_manifest.json',{'requests':len(rows),'output_rows':len(completed),'input_sha256':digest(HERE/f'worker_{w}_input.jsonl'),'output_sha256':digest(out),'protocol_sha256':digest(HERE/'protocol.json'),'scheduling_amendment_sha256':digest(HERE/'scheduling_amendment.json')})
 return len(completed)

def execute():
 protocol=json.loads((HERE/'protocol.json').read_text());amendment=json.loads((HERE/'scheduling_amendment.json').read_text())
 assert digest(HERE/'protocol.json')==amendment['original_protocol_sha256']
 assert digest(__file__)==amendment['parallel_runner_sha256']
 assert digest(HERE/'run_structured.py')==protocol['runner_sha256']
 assert digest(HERE/'reader_input.jsonl')==protocol['input_sha256']==amendment['input_sha256']
 assert digest(HERE/'initial_output.jsonl')==amendment['initial_output_sha256']
 for path,value in protocol['source_files'].items():assert digest(ROOT/path)==value,path
 assert digest(CACHE/'llama-b11435/llama-server')==protocol['runtime_binary_sha256']
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(worker,w,amendment) for w in range(2)]
  for future in futures:print('worker completed',future.result(),flush=True)
 sources=[HERE/'initial_output.jsonl',HERE/'worker_0_output.jsonl',HERE/'worker_1_output.jsonl']
 raw=[r for p in sources for r in read(p)];byid={r['id']:r for r in raw};rows=read(HERE/'reader_input.jsonl')
 assert len(raw)==len(byid)==len(rows)==234
 assert set(byid)=={r['id'] for r in rows}
 for r in rows:assert byid[r['id']]['request']==make_request(r,512,1729)
 lines(HERE/'reader_output.jsonl',[byid[r['id']] for r in rows])
 save(HERE/'execution_manifest.json',{'complete':True,'requests':len(rows),'output_rows':len(raw),'protocol_sha256':digest(HERE/'protocol.json'),'input_sha256':digest(HERE/'reader_input.jsonl'),'output_sha256':digest(HERE/'reader_output.jsonl'),'token_preflight_sha256':digest(HERE/'token_preflight.json'),'scheduling_amendment_sha256':digest(HERE/'scheduling_amendment.json'),'physical_batches':{str(p.relative_to(ROOT)):digest(p) for p in sources},'sessions':sorted({r['execution_session'] for r in raw}),'total_generation_wall_seconds':sum(r['wall_seconds'] for r in raw),'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--run',action='store_true');args=p.parse_args()
 if args.prepare:prepare()
 if args.run:execute()
