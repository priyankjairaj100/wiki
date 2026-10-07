#!/usr/bin/env python3
"""Verify paired review archives from a fresh folder with an unrelated name."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--software',type=Path,required=True)
    p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--full',action='store_true')
    a=p.parse_args();archive_reports={};seen={}
    with tempfile.TemporaryDirectory(prefix='acl-review-portability-') as name:
        stage=Path(name)
        for role,path in [('software',a.software),('data',a.data)]:
            if path.stat().st_size>=200_000_000:raise RuntimeError(role+' exceeds 200 MB.')
            with zipfile.ZipFile(path) as z:
                if z.testzip():raise RuntimeError(role+' CRC check failed.')
                for info in z.infolist():
                    member=Path(info.filename)
                    if member.is_absolute() or '..' in member.parts or member.parts[0]!='ACL2027_submission':raise RuntimeError('Unsafe archive member.')
                    if info.is_dir():continue
                    payload=z.read(info);digest=hashlib.sha256(payload).hexdigest()
                    if info.filename in seen and seen[info.filename]!=digest:raise RuntimeError('Shared archive member differs.')
                    seen[info.filename]=digest
                    destination=stage/member;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(payload)
                archive_reports[role]={'bytes':path.stat().st_size,'sha256':sha(path),'members':len(z.infolist()),'crc_passed':True}
        project=stage/'arbitrary_project_name';(stage/'ACL2027_submission').rename(project)
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
        command=[sys.executable,'verify_revision.py']+(['--full'] if a.full else [])
        result=subprocess.run(command,cwd=project,env=env,check=False)
        reports=list((project/'reproduced_pass6').glob('verification_*/verification.json'))
        if result.returncode or len(reports)!=1:raise RuntimeError('Review verification failed.')
        report=json.loads(reports[0].read_text())
        if report['status']!='passed':raise RuntimeError('Review verification did not pass.')
        output={'status':'passed','fresh_extraction':True,'arbitrary_project_name':True,'full_retrieval_replay':a.full,'archives':archive_reports,'verification':report}
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'status':'passed','output':str(a.output),'archives':archive_reports},indent=2))
if __name__=='__main__':main()
