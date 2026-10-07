#!/usr/bin/env python3
"""Verify the portable pass-3 release without model downloads or new inference."""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true',help='Also rerun frozen pilot retrieval. No model inference.');args=ap.parse_args()
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
for name,want in manifest['files'].items():
 p=ROOT/name
 if not p.is_file() or digest(p)!=want:raise SystemExit('Saved hash mismatch: '+name)
print(f"Verified {len(manifest['files'])} saved files.",flush=True)
out=ROOT/'reproduced_pass3';out.mkdir(exist_ok=True)
stage=Path(tempfile.mkdtemp(prefix='workspace_',dir=out))
def copy(rel):
 p=ROOT/rel;q=stage/rel;q.parent.mkdir(parents=True,exist_ok=True)
 if p.is_dir():shutil.copytree(p,q,ignore=shutil.ignore_patterns('__pycache__','*.log'))
 else:shutil.copy2(p,q)
for rel in ['pass2/theory','pass3/theory','pass3/extraction','pass3/audit','pass3/protocol']:
 copy(rel)
for run in ['pilot_final','validation']:
 for name in ['conditioned_mechanism.json','stable_budget_summary.json']:
  rel=f'pass3/pipeline/{run}/{name}'
  if (ROOT/rel).exists():copy(rel)
copy('pass3/paper/tables')
with (out/'verification.log').open('w') as log:
 def run(command):
  print(' '.join(command),flush=True)
  proc=subprocess.run(command,cwd=stage,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env={**os.environ,"PYTHONPATH":str(stage)})
  log.write(' '.join(command)+'\n'+proc.stdout+'\n');log.flush()
  if proc.returncode:print(proc.stdout[-4000:]);raise SystemExit(proc.returncode)
 for rel in ['pass3/theory/test_lifecycle.py','pass3/theory/test_refinement.py',
             'pass3/extraction/test_source_adapter.py','pass3/extraction/test_succession_rules.py',
             'pass3/extraction/learned/test_validation.py','pass3/protocol/test_scoring.py',
             'pass3/audit/build_paper_tables.py']:
  run([sys.executable,rel])
 for name in ['matched.tex','mechanism.tex','budget.tex']:
  if (ROOT/'pass3/paper/tables'/name).read_bytes()!=(stage/'pass3/paper/tables'/name).read_bytes():
   raise SystemExit('Table reconstruction differs: '+name)
 if args.full:
  for rel in ['pass3/pipeline/run_matched.py','pass3/pipeline/audit_run.py']:
   copy(rel)
  run([sys.executable,'pass3/pipeline/run_matched.py','--config','pass3/protocol/config_pilot.json',
       '--output','pass3/pipeline/pilot_reproduced'])
  run([sys.executable,'pass3/pipeline/audit_run.py','--folder','pass3/pipeline/pilot_reproduced'])
  def contexts(p):
   result={}
   with p.open() as f:
    for line in f:
     r=json.loads(line)
     result[r['question_id']]={m:v['context_signature'] for m,v in r['methods'].items()}
   return result
  if contexts(stage/'pass3/pipeline/pilot_reproduced/predictions.jsonl')!=contexts(ROOT/'pass3/pipeline/pilot_final/predictions.jsonl'):
   raise SystemExit('Pilot context reproduction differs.')
print('PASS. Verification outputs: '+str(out),flush=True)
