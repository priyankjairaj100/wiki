#!/usr/bin/env python3
"""Verify the revised release without downloads or new model inference.

The unchanged pass5 verifier checks the current release manifest and prior results.
New components then regenerate their outputs in separate temporary directories.
Verification records stay under reproduced_pass6. Frozen files remain unchanged.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
PLAN = ROOT / 'pass6/release/VERIFICATION_PLAN.json'

def load(path):return json.loads(Path(path).read_text())
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()
def require(condition,message):
    if not condition:raise RuntimeError(message)
def clean(value,ignored_keys):
    if isinstance(value,dict):return {k:clean(v,ignored_keys) for k,v in value.items() if k not in ignored_keys}
    if isinstance(value,list):return [clean(v,ignored_keys) for v in value]
    return value

def checked_relative(name):
    path=Path(name)
    require(not path.is_absolute() and '..' not in path.parts,'Unsafe relative path: '+name)
    return path

class RevisionVerification:
    def __init__(self,full=False):
        parent=ROOT/'reproduced_pass6';parent.mkdir(exist_ok=True)
        self.output=Path(tempfile.mkdtemp(prefix='verification_',dir=parent))
        self.log=(self.output/'verification.log').open('w',buffering=1)
        self.full=full;self.started=time.monotonic()
        self.report={'revision':'pass6','status':'running','full_retrieval_replay':full,'model_inference_started':False,'checks':{}}
        self.env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTHONOPTIMIZE':'0','PYTHONPATH':str(ROOT),'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
    def note(self,message):print(message,flush=True);self.log.write(message+'\n')
    def run(self,arguments):
        self.note('RUN '+' '.join(map(str,arguments)))
        result=subprocess.run([sys.executable,*map(str,arguments)],cwd=ROOT,env=self.env,stdout=self.log,stderr=subprocess.STDOUT)
        require(result.returncode==0,'Command failed: '+str(arguments[0])+'. See '+str(self.output/'verification.log'))
    def plan(self):
        plan=load(PLAN)
        require(plan.get('status')=='ready','The pass6 verification plan is not finalized.')
        names=[c['name'] for c in plan['components']]
        require(len(names)==len(set(names)) and set(plan['required_components'])<=set(names),'The verification plan omits a required component.')
        self.plan_record=plan
    def legacy(self):
        before=set((ROOT/'reproduced_pass5').glob('verification_*/verification.json')) if (ROOT/'reproduced_pass5').exists() else set()
        self.run(['verify_submission.py']+(['--full'] if self.full else []))
        after=set((ROOT/'reproduced_pass5').glob('verification_*/verification.json'))
        created=after-before
        require(len(created)==1,'Expected one new pass5 verification report.')
        path=created.pop();record=load(path)
        require(record['status']=='passed','Prior result verification failed.')
        self.report['checks']['release_manifest']=record['checks']['release_manifest']
        self.report['checks']['pass5_regression']={'report_sha256':digest(path),'verification':record}
        manifest_path=ROOT/record['checks']['release_manifest']['manifest_name'];manifest=load(manifest_path)
        require(manifest['files'].get('verify_revision.py')==digest(ROOT/'verify_revision.py'),'Revision verifier is absent from the current manifest.')
        require(manifest['files'].get('pass6/release/VERIFICATION_PLAN.json')==digest(PLAN),'Revision verification plan is absent from the manifest.')
        self.files=manifest['files'];self.manifest_path=manifest_path;self.manifest_sha256=digest(manifest_path)
    def components(self):
        records={}
        for component in self.plan_record['components']:
            name=component['name'];checked_relative(name)
            out=self.output/'components'/name;out.mkdir(parents=True)
            commands=component.get('commands') or [component['command']]
            for command in commands:
                require(any('{output}' in arg for arg in command),'Component must write to its isolated output directory: '+name)
                script=str(checked_relative(command[0]));require(script in self.files,'Component script is outside the manifest: '+script)
                expanded=[arg.replace('{output}',str(out)) for arg in command]
                self.run(expanded)
            checks=[]
            for artifact in component['artifacts']:
                saved_name=str(checked_relative(artifact['saved']));fresh_name=checked_relative(artifact['generated'])
                require(saved_name in self.files,'Saved result is absent from the manifest: '+saved_name)
                saved=ROOT/saved_name;fresh=out/fresh_name
                require(fresh.is_file(),'Missing regenerated result: '+str(fresh_name))
                mode=artifact.get('comparison','bytes');ignored=artifact.get('ignore_keys',[])
                if mode=='bytes':require(saved.read_bytes()==fresh.read_bytes(),'Byte comparison failed: '+saved_name)
                elif mode=='json':require(clean(load(saved),ignored)==clean(load(fresh),ignored),'JSON comparison failed: '+saved_name)
                elif mode=='jsonl':
                    parse=lambda path:[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
                    require(clean(parse(saved),ignored)==clean(parse(fresh),ignored),'JSONL comparison failed: '+saved_name)
                else:raise RuntimeError('Unknown comparison: '+mode)
                checks.append({'saved':saved_name,'generated':str(fresh_name),'comparison':mode,'ignored_keys':ignored,'saved_sha256':digest(saved),'generated_sha256':digest(fresh),'match':True})
            require(checks,'Component has no declared output checks: '+name)
            records[name]={'passed':True,'artifacts':checks}
            self.note('PASS component '+name)
        self.report['checks']['revision_components']=records
        self.report['checks']['verification_plan_sha256']=digest(PLAN)
        require(digest(self.manifest_path)==self.manifest_sha256,'The manifest changed during verification.')
        for name,expected in self.files.items():
            require(digest(ROOT/checked_relative(name))==expected,'A released file changed during verification: '+name)
        self.report['checks']['released_files_unchanged']={'files':len(self.files),'all_match':True}
    def finish(self,error=None):
        self.report.update(status='failed' if error else 'passed',completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-self.started,3))
        if error:self.report['error']=str(error)
        (self.output/'verification.json').write_text(json.dumps(self.report,indent=2)+'\n')
        self.note(('FAIL: '+str(error) if error else 'PASS')+'. Verification outputs: '+str(self.output));self.log.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full',action='store_true',help='Also replay prior retrieval contexts. No model inference.')
    a=p.parse_args();v=RevisionVerification(a.full)
    try:v.plan();v.legacy();v.components()
    except Exception as error:v.finish(error);return 1
    v.finish();return 0
if __name__=='__main__':raise SystemExit(main())
