#!/usr/bin/env python3
"""Check citation coverage against the independently read primary-source audit."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
PAPER=ROOT/'pass5/paper'
HERE=Path(__file__).resolve().parent
bib=(PAPER/'refs.bib').read_text()
keys=re.findall(r'@\w+\s*\{\s*([^,]+),',bib)
audit=json.loads((HERE/'primary_audit.json').read_text())
audited={x['key'] for x in audit['references']}
commands=[]
for p in sorted(PAPER.rglob('*.tex')):
 s=re.sub(r'(?<!\\)%[^\n]*','',p.read_text())
 for m in re.finditer(r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}',s):
  commands.append({'file':p.relative_to(ROOT).as_posix(),'line':s.count('\n',0,m.start())+1,'keys':[k.strip() for k in m[1].split(',')],'command':m[0]})
cited={k for c in commands for k in c['keys']}
r={'bibliography_sha256':hashlib.sha256((PAPER/'refs.bib').read_bytes()).hexdigest(),'references':len(keys),'citation_commands':len(commands),'unique_cited_keys':len(cited),'unknown_citations':sorted(cited-set(keys)),'uncited_references':sorted(set(keys)-cited),'unaudited_references':sorted(set(keys)-audited),'duplicate_keys':sorted({k for k in keys if keys.count(k)>1}),'commands':commands}
r['status']='passed' if not any(r[k] for k in ['unknown_citations','uncited_references','unaudited_references','duplicate_keys']) else 'failed'
(HERE/'citation_inventory.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='commands'},indent=2))
raise SystemExit(r['status']!='passed')
