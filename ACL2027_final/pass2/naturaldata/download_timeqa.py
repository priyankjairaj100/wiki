#!/usr/bin/env python3
"""Download immutable official TimeQA files and verify their recorded SHA256 hashes."""
import hashlib, json, pathlib, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
manifest=json.loads((ROOT/'source_manifest.json').read_text())
for record in [manifest['source_tree']]+manifest['files']:
    path=ROOT/record['path'];path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']:
        print('verified',record['path']);continue
    request=urllib.request.Request(record['source_url'],headers={'User-Agent':'TimeQA-reproduction/1.0'})
    data=urllib.request.urlopen(request,timeout=120).read()
    actual=hashlib.sha256(data).hexdigest()
    if actual!=record['sha256']:raise ValueError(f"SHA256 mismatch: {record['path']}")
    path.write_bytes(data);print('downloaded',record['path'])
