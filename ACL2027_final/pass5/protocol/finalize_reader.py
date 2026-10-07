#!/usr/bin/env python3
"""Verify exact reuse, merge complete reader cohorts, and optionally score them."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass5.protocol.prepare_reader import read,save,lines,sha,digest,identity,check_execution
from pass4.inference.run_jsonl_final import make_request

def run(args):
 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
 subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,env=env,check=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--delta-output',type=Path,default=ROOT/'pass5/inference/delta/reader_output.jsonl');ap.add_argument('--score',action='store_true');ap.add_argument('--verify-only',action='store_true');ap.add_argument('--report',type=Path);args=ap.parse_args();os.chdir(ROOT)
 frozen=json.loads((ROOT/'pass5/inference/reuse_manifest.json').read_text());assert frozen['execution_identity']==identity()
 for path,value in {**frozen['historical_sources'],**frozen['files']}.items():assert sha(ROOT/path)==value,path
 for cohort in frozen['cohorts'].values():
  for path,value in cohort['inputs'].items():assert sha(ROOT/path)==value,path
 lineage=read(ROOT/'pass5/inference/reader_lineage.jsonl');sources={}
 for path in sorted({r['source_path'] for r in lineage}):
  p=ROOT/path;folder=p.parent
  if path.startswith('pass5/'):
   assert p.resolve()==args.delta_output.resolve()
   if not args.verify_only:(folder/'reader_input.jsonl').write_bytes((ROOT/'pass5/inference/delta_input.jsonl').read_bytes())
  source_rows=check_execution(folder);sources[path]={r['id']:r for r in source_rows}
  # Every physical batch must provide token-fit evidence, exact settings, and a matching server log.
  manifest=json.loads((folder/'reader_output.manifest.json').read_text());preflight=json.loads((folder/'reader_output.token_preflight.json').read_text());log=(folder/'reader_output.server.log').read_text()
  assert sha(folder/'reader_output.token_preflight.json')==manifest['token_preflight_sha256'];assert preflight['all_fit'] and preflight['context_tokens']==2048 and preflight['max_reserved_tokens']<=2048
  assert {r['id'] for r in source_rows}<={r['id'] for r in preflight['counts']}
  assert all(r['max_tokens']==96 and r['reserved_with_margin']<=2048 for r in preflight['counts'])
  assert 'n_threads = 4' in log and 'n_ctx_slot = 2048' in log
 byid={r['job_id']:r for r in lineage};assert len(byid)==len(lineage)==frozen['current_unique_requests']
 report={'all_checks_passed':True,'execution_identity':identity(),'historical_completed_requests':frozen['historical_completed_requests'],'current_unique_requests':frozen['current_unique_requests'],'reused_exact':frozen['reused_exact'],'new_delta':frozen['new_delta'],'total_historical_and_new_executions':frozen['historical_completed_requests']+frozen['new_delta'],'cohorts':{}}
 for name,counts in frozen['cohorts'].items():
  folder=ROOT/f'pass5/inference/{name}';jobs=read(folder/'reader_jobs.jsonl');inputs={r['id']:r for r in read(folder/'reader_input.jsonl')};merged=[]
  for j in jobs:
   jid=j['job_id'];rec=byid[jid];response=sources[rec['source_path']][rec['source_id']];request=make_request(inputs[jid],max_tokens=96,seed=1729)
   assert response['id']==jid and response['request']==request
   assert digest(request)==rec['request_sha256']==response['request_sha256']
   assert digest({'request':request,'execution':identity()})==rec['execution_request_key']
   merged.append(response)
  assert len(merged)==counts['unique_requests']
  out=folder/'reader_output.jsonl'
  if args.verify_only:assert read(out)==merged
  else:lines(out,merged)
  manifest={'type':'Complete cohort assembled from verified actual requests','rows':len(merged),'output_rows':len(merged),'output_sha256':sha(out),'input_sha256':sha(folder/'reader_input.jsonl'),'reused_exact':counts['reused_exact'],'new_delta':counts['new_delta'],'lineage_sha256':sha(ROOT/'pass5/inference/reader_lineage.jsonl'),'execution_identity':identity()}
  if args.verify_only:assert json.loads((folder/'reader_output.manifest.json').read_text())==manifest
  else:save(folder/'reader_output.manifest.json',manifest)
  report['cohorts'][name]={**counts,'merged_output_sha256':sha(out),'exact_record_reconstruction':True}
 if args.report:save(args.report,report)
 elif not args.verify_only:save(ROOT/'pass5/protocol/reader_join_verification.json',report)
 if args.score:
  assert not args.verify_only
  for name,role,track in [('human','primary','human_confirmation'),('human_diagnostic','diagnostic','context_sensitive_diagnostic')]:
   folder=f'pass5/inference/{name}';out=f'pass5/protocol/reader_{role}_scored'
   run(['pass5/protocol/score_reader.py','--jobs',folder+'/reader_jobs.jsonl','--outputs',folder+'/reader_output.jsonl','--membership',folder+'/reader_memberships.jsonl','--cohort-queries',folder+'/queries.jsonl','--predictions','pass5/pipeline/human/predictions.jsonl','--labels','pass3/protocol/human_test_confirmation_labels.jsonl','--passages','pass3/protocol/test_source_passages.jsonl','--config','pass5/protocol/config.json','--output',out,'--track',track])
   run(['pass5/protocol/audit_answer_changes.py','--predictions',out+'/predictions_with_reader.jsonl','--output',f'pass5/protocol/reader_{role}_change_audit.json'])
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
