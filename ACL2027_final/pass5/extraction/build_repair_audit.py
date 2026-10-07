#!/usr/bin/env python3
"""Compare frozen source versions without QA fields or reader outcomes."""
from __future__ import annotations
import collections,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]

def read(path):return [json.loads(x) for x in path.read_text().splitlines()]
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def signature(c):return (c['passage_id'],c['start']['source_span']['start'],c['subject']['source_span']['start'])
def semantics(c):
    return {k:c.get(k) for k in ['atomic_span','source_span','subject','slot','value','start','end']}
def semantic_core(c):
    d=semantics(c);d['subject']={k:c['subject'].get(k) for k in ['canonical','surface','source_span']};return d

def main():
    all_summaries=[]
    for split in ['dev','test']:
        old=read(ROOT/f'pass4/extraction/{split}_frozen/claims.jsonl')
        new=read(ROOT/f'pass5/extraction/{split}_frozen/claims.jsonl')
        by=collections.defaultdict(list)
        for c in new:by[signature(c)].append(c)
        rows=[];matched=set()
        for c in old:
            matches=by[signature(c)]
            if len(matches)>1:
                matches=[x for x in matches if x['value_span']['start']==c['value_span']['start']]
            if len(matches)==1:
                n=matches[0];matched.add(n['claim_id'])
                status='retained' if semantic_core(c)==semantic_core(n) else 'repaired'
                changes=[k for k in semantic_core(c) if semantic_core(c)[k]!=semantic_core(n)[k]]
                rows.append({'old_claim_id':c['claim_id'],'new_claim_id':n['claim_id'],'article_path':c['article_path'],'passage_id':c['passage_id'],'status':status,'changed_fields':changes})
            else:
                rows.append({'old_claim_id':c['claim_id'],'new_claim_id':None,'article_path':c['article_path'],'passage_id':c['passage_id'],'status':'fallback','reason':'No uniquely matched modeled occurrence survives the frozen source rules.'})
        for c in new:
            if c['claim_id'] not in matched:rows.append({'old_claim_id':None,'new_claim_id':c['claim_id'],'article_path':c['article_path'],'passage_id':c['passage_id'],'status':'newly_grounded'})
        out=ROOT/f'pass5/extraction/{split}_frozen'
        content=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
        (out/'old_to_new.jsonl').write_text(content)
        (out/'repair_decisions.jsonl').write_text(content)
        summary={'track':split,'old_claims':len(old),'new_claims':len(new),'mapping_counts':dict(collections.Counter(r['status'] for r in rows)),'paragraph_calendar_end_links':sum('end_attachment' in c for c in new),'answer_annotation_reads':0,'interpretation':'Mapping counts describe output changes. They are not accuracy estimates. Matched keys use paragraph, date span, and subject span.'}
        write(out/'repair_summary.json',summary);all_summaries.append(summary)
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for split in ['dev','test'] for p in sorted((ROOT/f'pass5/extraction/{split}_frozen').glob('*')) if p.is_file()}
    write(ROOT/'pass5/extraction/output_manifest.json',{'source_freeze_sha256':hashlib.sha256((ROOT/'pass5/extraction/freeze_manifest.json').read_bytes()).hexdigest(),'files':files})
    print(json.dumps(all_summaries,indent=2))

if __name__=='__main__':main()
