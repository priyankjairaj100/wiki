#!/usr/bin/env python3
"""Freeze a source-only audit sample. Do not inspect benchmark labels."""
import argparse, collections, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SEED = 'pass5-restored-independent-source-audit-v1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.suffix == '.jsonl' else json.loads(p.read_text())
def walk(x):
    if isinstance(x, dict):
        yield x
        for y in x.values(): yield from walk(y)
    elif isinstance(x, list):
        for y in x: yield from walk(y)
def write(name,x): (OUT/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--dev-sources',required=True);p.add_argument('--test-sources',required=True);p.add_argument('--dev-claims',required=True);p.add_argument('--test-claims',required=True);p.add_argument('--adapter',required=True);a=p.parse_args()
    assert not (OUT/'sample.jsonl').exists(), 'Sample already frozen; do not replace it.'
    paths=[ROOT/'pass4/extraction/calibration_sources.jsonl',ROOT/'pass2/naturaldata/realprose_source_audit.jsonl']
    paths += list((ROOT/'pass4/audit/source').glob('*review.jsonl'))
    paths += [ROOT/'pass4/audit/source/confirmation/semantic_review.jsonl']
    paths += [ROOT/'pass3/data'/name for name in ['pilot_extraction_audit.json','pilot_extraction_audit_pre_freeze.json','dev_source_audit.json']]
    # These six source-only jobs were actually executed and reviewed.
    paths += [ROOT/'pass3/extraction/learned/jobs_completed_six.jsonl',ROOT/'pass3/extraction/learned/jobs_schema_v2_completed_six.jsonl']
    paths += [ROOT/'pass3/data/dev_succession_candidates.jsonl']
    exposure=collections.defaultdict(set)
    for f in paths:
        for row in walk(load(f)):
            if row.get('article_path'): exposure[row['article_path']].add(str(f.relative_to(ROOT)))
            if row.get('source_title'): exposure['/wiki/'+row['source_title'].replace(' ','_')].add(str(f.relative_to(ROOT)))
    lost_known=['Crewe_Alexandra_F.C.','Alexander_Van_der_Bellen','John_Foster_Dulles','Allen_Dulles','Miraš_Dedeić','Miras_Dedeic','Northampton_Town_F.C.','Klaus_Fuchs','Rubens','Rubens_(footballer)']
    for title in lost_known: exposure['/wiki/'+title].add('Recovered summary of lost audit')
    inputs={'adapter':ROOT/a.adapter,'protocol':OUT/'PROTOCOL.md','adapter_freeze':ROOT/'pass5/extraction/freeze_manifest.json'}
    for name, expected in load(inputs['adapter_freeze'])['files'].items():
        dep=ROOT/name;assert sha(dep)==expected,name
        inputs['dependency:'+name]=dep
    sample=[];pop={};unknown_exposure=[]
    for split,count in [('dev',20),('test',40)]:
        cf=ROOT/getattr(a,split+'_claims');sf=ROOT/getattr(a,split+'_sources');inputs[split+'_claims']=cf;inputs[split+'_sources']=sf
        sources={r['passage_id']:r for r in load(sf)}
        claims=load(cf)
        for c in claims:
            if any(s in c['article_path'].casefold() for s in ['rubens','pope','dedei','dedeić','dulles','van_der_bellen','crewe_alexandra','northampton_town','klaus_fuchs']):
                exposure[c['article_path']].add('Recovered summary of lost audit, conservative title match')
        eligible=[c for c in claims if c['article_path'] not in exposure]
        key=lambda c:hashlib.sha256((SEED+'\0'+split+'\0'+c['claim_id']).encode()).hexdigest()
        assert len(eligible)>=count
        selected=sorted(eligible,key=key)[:count];pop[split]={'eligible_claims':len(eligible),'claims':len(claims),'selected':count}
        for c in selected: sample.append({'split':split,'selection_hash':key(c),'claim':c,'source_paragraph':sources[c['passage_id']]})
    write('exposure_registry.json',{'articles':{k:sorted(v) for k,v in sorted(exposure.items())},'files':{str(f.relative_to(ROOT)):sha(f) for f in paths},'notes':'Union of saved completed reviews, calibration inputs, reviewed source jobs, and identifiable articles from lost review.'})
    (OUT/'sample.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in sample))
    write('sample_membership.json',{'seed':SEED,'claims':[{'split':r['split'],'claim_id':r['claim']['claim_id'],'article_path':r['claim']['article_path'],'selection_hash':r['selection_hash']} for r in sample]})
    inputs['exposure_registry']=OUT/'exposure_registry.json';inputs['membership']=OUT/'sample_membership.json';inputs['sample']=OUT/'sample.jsonl'
    write('freeze.json',{'phase':'Before paragraph review','created_utc':datetime.now(timezone.utc).isoformat(),'inputs':{k:{'path':str(v.relative_to(ROOT)),'sha256':sha(v)} for k,v in inputs.items()},'populations':pop,'excluded_article_count':len(exposure),'sample_articles':len({r['claim']['article_path'] for r in sample}),'current_question_or_answer_reads':0,'prior_lost_results_reused':False,'prior_exposure_reconstruction_complete':False})
    print(json.dumps({'population':pop,'exposure_articles':len(exposure),'selected_articles':len({r['claim']['article_path'] for r in sample})}))
if __name__=='__main__':main()
