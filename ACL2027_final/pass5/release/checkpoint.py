#!/usr/bin/env python3
"""Save current work without model assets, caches, or a final-release claim."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, tempfile, zipfile
ROOT = Path(__file__).resolve().parents[2]
SKIP = {'__pycache__','cache','.git','.venv','node_modules','access_probes'}
def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.resolve().is_relative_to(ROOT): raise SystemExit('Checkpoint must be outside the project.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='acl-checkpoint-',suffix='.zip');os.close(fd)
    tmp=Path(tmp)
    try:
        files={}
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
            for f in sorted(ROOT.rglob('*')):
                r=f.relative_to(ROOT)
                if not f.is_file() or f.is_symlink() or any(x in SKIP or x.startswith('.') or x.startswith('reproduced') for x in r.parts): continue
                if f.suffix in {'.gguf','.so','.pyc'} or '.so.' in f.name: continue
                data=f.read_bytes(); files[str(r)]=hashlib.sha256(data).hexdigest();z.writestr('ACL2027_working/'+str(r),data)
            z.writestr('ACL2027_working/CHECKPOINT_FILES.json',json.dumps({'kind':'working checkpoint, not final release','files':files},indent=2)+'\n')
        with zipfile.ZipFile(tmp) as z:
            if z.testzip(): raise RuntimeError('CRC failure')
        with tmp.open('rb') as f: os.fsync(f.fileno())
        destination=a.output.with_name(a.output.name+'.writing')
        with tmp.open('rb') as source,destination.open('wb') as target:
            shutil.copyfileobj(source,target,4*1024*1024);target.flush();os.fsync(target.fileno())
        os.replace(destination,a.output)
        print(json.dumps({'path':str(a.output.resolve()),'bytes':a.output.stat().st_size,'files':len(files),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}))
    finally: tmp.unlink(missing_ok=True)
if __name__=='__main__':main()
