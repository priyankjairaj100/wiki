#!/usr/bin/env python3
"""Render a source-only review range for the model-assisted reviewer."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('first',type=int);p.add_argument('last',type=int);a=p.parse_args()
rows=[json.loads(x) for x in Path(__file__).with_name('sample.jsonl').read_text().splitlines()]
for n,r in enumerate(rows,1):
 if not a.first<=n<=a.last:continue
 c=r['claim'];keep={k:c.get(k) for k in ['claim_id','subject','slot','value','rule','start','end','source_span','atomic_span']}
 print('\nRECORD',n,r['split'],c['article_path']);print(json.dumps(keep,ensure_ascii=False));print('FULL PARAGRAPH:',r['source_paragraph']['text'])
