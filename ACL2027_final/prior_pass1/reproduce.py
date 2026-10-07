#!/usr/bin/env python3
"""Verify or reproduce the saved research pass without network or model calls."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent

def run(command,log,**kwargs):
    print(' '.join(str(x) for x in command),flush=True)
    result=subprocess.run([str(x) for x in command],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,**kwargs)
    log.write(result.stdout);log.flush()
    if result.returncode:
        print(result.stdout[-6000:]);raise SystemExit(result.returncode)

ap=argparse.ArgumentParser();ap.add_argument('--quick',action='store_true');args=ap.parse_args()
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
failures=[]
for name,expected in manifest['files'].items():
    p=ROOT/name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected: failures.append(name)
if failures: raise SystemExit('File verification failed: '+', '.join(failures))
print(f"Verified {len(manifest['files'])} saved files.",flush=True)
out=ROOT/'reproduced';out.mkdir(exist_ok=True)
with (out/'run.log').open('w',encoding='utf-8') as log:
    run([sys.executable,ROOT/'engine/run_certificate_tests.py','--package-root',ROOT/'original','--output',out/'certificate_tests.json'],log)
    run([sys.executable,ROOT/'theory/test_bitemporal.py'],log)
    if not args.quick:
        target=out/'experiments';target.mkdir(exist_ok=True)
        for p in (ROOT/'experiments').glob('*.py'):shutil.copy2(p,target/p.name)
        run([sys.executable,target/'run_all.py','--source',ROOT/'original','--templama-source',ROOT/'external/TempLAMA_test_with_aliases.json'],log)
        for name in ['templama_source_set_results.json','prefix_summary.json','sensitivity_summary.json']:
            before=json.loads((ROOT/'experiments/results'/name).read_text())
            after=json.loads((target/'results'/name).read_text())
            if before!=after:raise SystemExit('Reproduction differs: '+name)
        print('Primary source-set results and stability results match exactly.',flush=True)
print('PASS. Reproduced outputs are in reproduced/.',flush=True)
