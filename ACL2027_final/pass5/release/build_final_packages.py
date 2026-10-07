#!/usr/bin/env python3
"""Build the final paper and four source archives after bound verification.

Refresh the root manifest only after all edits. Then run verify_submission.py.
Package only when that exact manifest passes. No model inference starts here.
PDF identity checks require PyMuPDF (the fitz module).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RELEASE = 'ACL2027_final'
REVIEW_ROOT = 'ACL2027_submission'
LIMIT = 200_000_000
DEFAULT_IDENTITY_PATTERNS = [r'Priyank\s+(?:Jairaj|Jayraj)', r'Poonam\s+Goyal', r'Navneet\s+Goyal', r'priyankjairaj100', r'priyankjayraj', r'BITS\s+Pilani']
SKIP_DIRS = {'__pycache__','cache','.git','.venv','node_modules','access_probes','citation_primary_cache'}
AUX_SUFFIXES = {'.aux','.bbl','.blg','.out','.toc','.fls','.fdb_latexmk','.pyc'}
SOFTWARE_SUFFIXES = {'.py','.md','.txt','.tex','.bib','.bst','.sty','.bat','.sh','.yml','.yaml','.toml','.ini','.cfg','.svg'}

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def require(condition,message):
    if not condition:raise RuntimeError(message)

def private_files():
    for path in sorted(ROOT.rglob('*')):
        rel=path.relative_to(ROOT)
        if any(p in SKIP_DIRS or p.startswith('.') or p.startswith('reproduced') for p in rel.parts):continue
        if not path.is_file() or path.is_symlink() or path.suffix in AUX_SUFFIXES or path.name.endswith('.synctex.gz'):continue
        if str(rel) in {'MANIFEST.json','RELEASE_VERIFICATION.json'}:continue
        if path.suffix in {'.gguf','.so'} or '.so.' in path.name:raise RuntimeError('Unexpected runtime asset: '+str(rel))
        yield path

def review_selected(relative):
    """Select final evidence and required historical dependencies, using relative paths."""
    p=Path(relative);s=p.as_posix()
    if s in {'verify_submission.py','requirements.txt'}:return True
    if s.startswith('pass5/'):
        return not (s.startswith('pass5/release/') or s.startswith('pass5/audit/release/') or s.startswith('pass5/audit/venue/'))
    if s.startswith('pass4/'):
        if s.startswith('pass4/audit/source/'):return True
        return not (s.startswith('pass4/paper/') or s.startswith('pass4/audit/') or p.name in {'README.md','REVISION_NOTES.md'})
    if s.startswith('pass3/'):
        if s.startswith('pass3/theory/'):return True
        if s.startswith('pass3/protocol/'):return p.name != 'PAPER_REVIEW.md'
        if s.startswith('pass3/extraction/'):return True
        if s.startswith('pass3/inference/'):return True
        if s.startswith('pass3/pipeline/') and len(p.parts)==3:return True
        return False
    if s.startswith('pass2/'):
        return p.parts[1] in {'theory','baselines','evaluation','naturaldata','independent'}
    if s.startswith('work/external/') or s.startswith('prior_pass1/external/'):
        return p.suffix not in {'.pdf','.html'}
    if s.startswith('prior_pass1/engine/') or s=='prior_pass1/LICENSE':return True
    return False

def category(relative):
    p=Path(relative)
    if '/paper/' in '/'+relative:return 'software'
    if p.suffix in SOFTWARE_SUFFIXES or 'LICENSE' in p.name or p.name=='NOTICE':return 'software'
    return 'data'

def write_atomic(destination, writer):
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.'+destination.name+'-',dir=destination.parent)
    try:
        with os.fdopen(fd,'wb') as f:writer(f);f.flush();os.fsync(f.fileno())
        os.replace(name,destination)
        descriptor=os.open(destination.parent,os.O_DIRECTORY)
        try:os.fsync(descriptor)
        finally:os.close(descriptor)
    finally:
        if os.path.exists(name):os.unlink(name)

def refresh_manifest():
    value={'release':RELEASE,'files':{str(p.relative_to(ROOT)):digest(p) for p in private_files()}}
    write_atomic(ROOT/'MANIFEST.json',lambda f:f.write((json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()))
    print(json.dumps({'manifest_files':len(value['files']),'sha256':digest(ROOT/'MANIFEST.json')}),flush=True)

def verify_manifest():
    m=json.loads((ROOT/'MANIFEST.json').read_text())
    require(m.get('release')==RELEASE,'Refresh the final manifest first.')
    names={str(p.relative_to(ROOT)) for p in private_files()}
    require(names==set(m['files']),'Manifest membership changed. Refresh and verify again.')
    for name,expected in m['files'].items():
        path=Path(name);require(not path.is_absolute() and '..' not in path.parts,'Unsafe manifest path.')
        require(digest(ROOT/name)==expected,'Release hash mismatch: '+name)
    return m

def make_zip(path,members):
    """Hash the bytes written, then check archive CRCs."""
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for source,name,expected in members:
            data=Path(source).read_bytes()
            require(hashlib.sha256(data).hexdigest()==expected,'Input changed during packaging: '+name)
            info=zipfile.ZipInfo(name,date_time=(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with path.open('rb') as f:os.fsync(f.fileno())
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None,'Archive CRC failure.')
        require(len(z.namelist())==len(set(z.namelist())),'Duplicate ZIP members.')
    return len(members)

def copy_atomic(source,destination):
    with Path(source).open('rb') as f:write_atomic(destination,lambda g:shutil.copyfileobj(f,g,4*1024*1024))
    require(digest(source)==digest(destination),'Final copy checksum differs.')

def review_members(manifest,stage,patterns,verification=None):
    files={n:h for n,h in manifest['files'].items() if review_selected(n)}
    source_map={n:ROOT/n for n in files}
    aliases={'README_SUBMISSION.md':'pass5/release/README_SUBMISSION.md','AI_ASSISTANCE.md':'pass5/release/AI_ASSISTANCE.md','THIRD_PARTY_NOTICES.md':'pass5/release/THIRD_PARTY_NOTICES.md'}
    for name,original in aliases.items():
        require(original in manifest['files'],'Missing review documentation: '+original)
        files[name]=manifest['files'][original];source_map[name]=ROOT/original
    if verification is not None:
        # Keep the bound check results, but remove local path strings from review records.
        value=json.loads(Path(verification).read_text())
        def portable(value):
            if isinstance(value,dict):
                return {str(k).replace(str(ROOT),'[project]'):portable(v) for k,v in value.items()}
            if isinstance(value,list):return [portable(v) for v in value]
            if isinstance(value,str):return value.replace(str(ROOT),'[project]')
            return value
        report=stage/'RELEASE_VERIFICATION.json';report.write_text(json.dumps(portable(value),indent=2)+'\n')
        files['RELEASE_VERIFICATION.json']=digest(report);source_map['RELEASE_VERIFICATION.json']=report
    compiled=[re.compile(p,re.I) for p in patterns]
    findings=[]
    pdfs_scanned=[]
    for name,path in source_map.items():
        raw=path.read_bytes()
        if path.suffix.lower()=='.pdf':
            import fitz
            with fitz.open(stream=raw,filetype='pdf') as document:
                require(not document.needs_pass,'Cannot scan encrypted PDF: '+name)
                surfaces={'metadata':json.dumps(document.metadata,ensure_ascii=False),
                          'xml_metadata':document.get_xml_metadata(),
                          'page_text':'\n'.join(page.get_text() for page in document)}
                pdfs_scanned.append({'path':name,'pages':len(document),'text_and_metadata_scanned':True})
        elif path.suffix.lower() in {'.png','.jpg','.jpeg','.zip','.gz'}:
            surfaces={}
        else:
            surfaces={'text':raw.decode('utf-8',errors='replace')}
        surfaces['filename']=name
        for index,pattern in enumerate(compiled):
            for surface,text in surfaces.items():
                if pattern.search(text):findings.append({'path':name,'surface':surface,'pattern_index':index})
    require(not findings,'Identity scan failed: '+json.dumps(findings))
    review_manifest={'release':RELEASE,'root':REVIEW_ROOT,'source_manifest_sha256':digest(ROOT/'MANIFEST.json'),
                     'files':files,'archive_category':{n:category(n) for n in files}}
    record=stage/'SUBMISSION_MANIFEST.json';record.write_text(json.dumps(review_manifest,indent=2,ensure_ascii=False)+'\n')
    common=[(record,REVIEW_ROOT+'/SUBMISSION_MANIFEST.json',digest(record))]
    selections={c:list(common) for c in ['software','data']}
    for name in sorted(files):selections[category(name)].append((source_map[name],REVIEW_ROOT+'/'+name,files[name]))
    return selections,{'selected_files':len(files),'identity_patterns_checked':len(compiled),'identity_matches':findings,'pdf_identity_scans':pdfs_scanned}

def package(output,verification,patterns):
    manifest=verify_manifest();manifest_sha=digest(ROOT/'MANIFEST.json')
    report=json.loads(Path(verification).read_text())
    require(report.get('status')=='passed','Verification did not pass.')
    require(report.get('checks',{}).get('release_manifest',{}).get('sha256')==manifest_sha,'Verification is not bound to this manifest.')
    paper=ROOT/'pass5/paper';checks=json.loads((ROOT/'pass5/audit/release/PAPER_CHECKS.json').read_text())
    require(checks.get('main_pages')==8,'Paper must have eight main pages.')
    require(checks.get('pdf_sha256')==digest(paper/'main.pdf'),'Paper changed after layout verification.')
    require(checks.get('limitations_start_page')==9,'Limitations must follow eight full main pages.')
    output=Path(output).resolve();require(not output.is_relative_to(ROOT),'Output must be outside the project.')
    output.mkdir(parents=True,exist_ok=True)
    outputs=[]
    with tempfile.TemporaryDirectory(prefix='acl-final-package-') as temp:
        stage=Path(temp)
        selections,scan=review_members(manifest,stage,patterns,verification)
        names=[RELEASE+'_paper.pdf',RELEASE+'_overleaf.zip',RELEASE+'_source_and_runs.zip',RELEASE+'_software.zip',RELEASE+'_data.zip']
        copy_atomic(paper/'main.pdf',stage/names[0])
        overleaf=[]
        for path in sorted(paper.rglob('*')):
            if path.is_file() and path.suffix in {'.tex','.bib','.bst','.sty','.pdf','.svg','.png','.txt'}:
                relative=str(path.relative_to(ROOT));overleaf.append((path,str(path.relative_to(paper)),manifest['files'][relative]))
        make_zip(stage/names[1],overleaf)
        private=[(ROOT/n,RELEASE+'/'+n,h) for n,h in sorted(manifest['files'].items())]
        private += [(ROOT/'MANIFEST.json',RELEASE+'/MANIFEST.json',manifest_sha), (Path(verification),RELEASE+'/RELEASE_VERIFICATION.json',digest(verification))]
        make_zip(stage/names[2],private)
        for role,name in [('software',names[3]),('data',names[4])]:
            make_zip(stage/name,selections[role])
            require((stage/name).stat().st_size<LIMIT,role+' ZIP exceeds 200 MB.')
        verify_manifest()
        for name in names:
            destination=output/name;copy_atomic(stage/name,destination)
            outputs.append({'path':str(destination),'bytes':destination.stat().st_size,'sha256':digest(destination)})
    receipt={'release':RELEASE,'verified_manifest_sha256':manifest_sha,'verification_sha256':digest(verification),'review_selection':scan,'outputs':outputs}
    write_atomic(output/(RELEASE+'_deliverables.json'),lambda f:f.write((json.dumps(receipt,indent=2)+'\n').encode()))
    print(json.dumps(receipt,indent=2),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--refresh-manifest',action='store_true');p.add_argument('--package',action='store_true');p.add_argument('--output',type=Path,default=ROOT.parent/'deliverables_final');p.add_argument('--verification',type=Path);p.add_argument('--identity-pattern',action='append',default=list(DEFAULT_IDENTITY_PATTERNS))
    a=p.parse_args()
    if not a.refresh_manifest and not a.package:p.error('Choose --refresh-manifest or --package.')
    if a.refresh_manifest:refresh_manifest()
    if a.package:
        if not a.verification:p.error('--verification is required for packaging.')
        package(a.output,a.verification,a.identity_pattern)
if __name__=='__main__':main()
