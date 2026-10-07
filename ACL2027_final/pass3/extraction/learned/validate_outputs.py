#!/usr/bin/env python3
"""Validate frozen model extraction against literal source evidence.

This checks source strings and date precision. It does not prove entailment.
Semantic acceptance remains a separate source audit. No gold labels enter.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[2]))
from pass3.extraction.source_adapter import parse_date,stable_id


def norm(s):return re.sub(r'\W+',' ',s.casefold()).strip()

def source_span(text,value):
    if not isinstance(value,str) or not value.strip():raise ValueError('missing_or_nonstring_quote')
    start=text.find(value)
    if start<0:raise ValueError('quote_not_literal')
    return {'start':start,'end':start+len(value),'text':value}


def date_field(value,quote,p):
    if value is None or value=='null' or value=='':return None
    if not isinstance(value,str):raise ValueError('date_not_literal_string')
    parsed=parse_date(value)
    if parsed is None:raise ValueError('unsupported_date_expression')
    match=re.search(r'(?<![\w–-])'+re.escape(value)+r'(?![\w–-])',quote['text'])
    if match is None:raise ValueError('date_not_in_quote_or_partial_season')
    prefix=quote['text'][:match.start()]
    if re.search(r'\b(?:around|about|before|after|early|late|approximately|circa|by)\s*$',prefix,re.I):
        raise ValueError('unbounded_or_approximate_date')
    return parse_date(value,quote['start']+match.start())


def check_strings(row,p,fields):
    text=p['text'];title=p['article_path'].split('/wiki/',1)[-1].replace('_',' ')
    quote=source_span(text,row.get('quote'))
    for field in fields:
        value=row.get(field)
        if not isinstance(value,str) or not value.strip():raise ValueError('missing_'+field)
        if value not in text and not (field=='organization' and value==title):raise ValueError(field+'_not_literal')
    return quote


def model_key(row):return norm(row['organization'])+' :: '+norm(row['role'])

def names_match(a,b):
    na,nb=norm(a),norm(b)
    return na==nb or (min(len(na.split()),len(nb.split()))==1 and (na.endswith(' '+nb) or nb.endswith(' '+na)))


def validate(raw_path,source_path,out_dir):
    out=pathlib.Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    sources={p['passage_id']:p for p in map(json.loads,pathlib.Path(source_path).read_text().splitlines())}
    raw=[json.loads(x) for x in pathlib.Path(raw_path).read_text().splitlines()]
    states=[];successions=[];failures=[];jobs=[]
    for response in raw:
        pid=response['metadata']['passage_id'];p=sources[pid]
        job={'passage_id':pid,'finish_reason':response['finish_reason'],'states_returned':0,'successions_returned':0,'states_grounded':0,'successions_grounded':0}
        if response['metadata']['source_sha256']!=hashlib.sha256(p['text'].encode()).hexdigest():raise ValueError('Source changed since inference.')
        try:payload=json.loads(response['generation'])
        except (ValueError,TypeError) as exc:
            failures.append({'passage_id':pid,'kind':'response','reason':'invalid_json','detail':str(exc)});jobs.append(job);continue
        if not isinstance(payload,dict):
            failures.append({'passage_id':pid,'kind':'response','reason':'json_not_object'});jobs.append(job);continue
        for kind,fields,store in [('states',['holder','role','organization'],states),('successions',['previous','next','role','organization'],successions)]:
            rows=payload.get(kind,[])
            if not isinstance(rows,list):
                failures.append({'passage_id':pid,'kind':kind,'reason':'field_not_array'});continue
            job[kind+'_returned']=len(rows)
            for index,row in enumerate(rows):
                record_id=stable_id(pid,kind,index)
                try:
                    if not isinstance(row,dict):raise ValueError('record_not_object')
                    quote=check_strings(row,p,fields)
                    if kind=='states':
                        start=date_field(row.get('start'),quote,p);end=date_field(row.get('end'),quote,p)
                        if start and end and start['lower']>end['upper']:raise ValueError('end_before_start')
                        if re.search(r'\b(?:contract|loan)\b',quote['text'],re.I):raise ValueError('planned_term_not_observed_tenure')
                        record={'record_id':record_id,'passage_id':pid,'article_path':p['article_path'],'kind':'state','holder':row['holder'],'role':row['role'],'organization':row['organization'],'slot_key':model_key(row),'start':start,'end':end,'source_span':quote,'raw_extraction':row,
                                'compiler_eligible':start is not None and (end is None or end['lower']>start['upper']),
                                'semantic_audit_required':True,'holder_in_quote':row['holder'] in quote['text'],'role_in_quote':row['role'] in quote['text']}
                    else:
                        if not re.search(r'\b(?:succeeded|replaced|successor)\b',quote['text'],re.I):raise ValueError('no_explicit_succession_cue')
                        if norm(row['previous'])==norm(row['next']):raise ValueError('identical_previous_and_next')
                        date=date_field(row.get('date'),quote,p)
                        record={'record_id':record_id,'passage_id':pid,'article_path':p['article_path'],'kind':'succession','previous':row['previous'],'next':row['next'],'role':row['role'],'organization':row['organization'],'slot_key':model_key(row),'date':date,'source_span':quote,'raw_extraction':row,
                                'semantic_audit_required':True,'previous_in_quote':row['previous'] in quote['text'],'next_in_quote':row['next'] in quote['text'],'role_in_quote':row['role'] in quote['text']}
                    store.append(record);job[kind+'_grounded']+=1
                except (ValueError,KeyError,TypeError) as exc:
                    failures.append({'record_id':record_id,'passage_id':pid,'kind':kind,'reason':str(exc),'raw_extraction':row})
        jobs.append(job)
    # Compiler candidates use dates supported by state or succession quotes.
    # Unknown predecessor starts are never invented.
    claims={}
    for s in states:
        if not s['compiler_eligible']:continue
        key=(s['passage_id'],s['slot_key'],norm(s['holder']),s['start']['lower'],s['start']['upper'])
        c={'claim_id':stable_id(*key),'passage_id':s['passage_id'],'article_path':s['article_path'],'slot_key':s['slot_key'],'holder':s['holder'],'role':s['role'],'organization':s['organization'],'start':s['start'],'end':s['end'],'text':s['source_span']['text'],'source_records':[s['record_id']],'semantic_audit_required':True}
        if key in claims:claims[key]['source_records'].append(s['record_id'])
        else:claims[key]=c
    for e in successions:
        if e['date'] is None:continue
        key=(e['passage_id'],e['slot_key'],norm(e['next']),e['date']['lower'],e['date']['upper'])
        if key in claims:claims[key]['source_records'].append(e['record_id'])
        else:claims[key]={'claim_id':stable_id(*key),'passage_id':e['passage_id'],'article_path':e['article_path'],'slot_key':e['slot_key'],'holder':e['next'],'role':e['role'],'organization':e['organization'],'start':e['date'],'end':None,'text':e['source_span']['text'],'source_records':[e['record_id']],'semantic_audit_required':True}
    claim_rows=list(claims.values());pairs=[];pair_failures=[]
    for e in successions:
        if e['date'] is None:
            pair_failures.append({'source_record':e['record_id'],'reason':'succession_date_unknown'});continue
        candidates=[c for c in claim_rows if c['passage_id']==e['passage_id'] and c['slot_key']==e['slot_key']]
        old=[c for c in candidates if names_match(c['holder'],e['previous']) and c['start']['lower']<=e['date']['upper']]
        new=[c for c in candidates if names_match(c['holder'],e['next']) and c['start']['lower']==e['date']['lower'] and c['start']['upper']==e['date']['upper']]
        if len(old)!=1 or len(new)!=1:
            pair_failures.append({'source_record':e['record_id'],'reason':'unknown_or_ambiguous_occurrence','previous_candidates':[c['claim_id'] for c in old],'next_candidates':[c['claim_id'] for c in new]});continue
        if old[0]['claim_id']==new[0]['claim_id']:continue
        pairs.append({'witness_id':new[0]['claim_id'],'target_id':old[0]['claim_id'],'source_record':e['record_id'],'source_span':e['source_span'],'premise':'Explicit source succession under a shared role-centric slot.','semantic_audit_required':True})
    def write(name,rows):
        (out/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    for name,rows in [('grounded_states.jsonl',states),('grounded_successions.jsonl',successions),('grounding_failures.jsonl',failures),('compiler_candidates.jsonl',claim_rows),('pair_candidates.jsonl',pairs),('pair_failures.jsonl',pair_failures),('job_validation.jsonl',jobs)]:write(name,rows)
    summary={'jobs':len(jobs),'states_returned':sum(x['states_returned'] for x in jobs),'successions_returned':sum(x['successions_returned'] for x in jobs),'literal_grounded_states':len(states),'literal_grounded_successions':len(successions),'grounding_failures':len(failures),'failure_reasons':dict(collections.Counter(f['reason'] for f in failures)),
             'compiler_candidates':len(claim_rows),'pair_candidates':len(pairs),'pair_failures':dict(collections.Counter(x['reason'] for x in pair_failures)),
             'source_sha256':hashlib.sha256(pathlib.Path(source_path).read_bytes()).hexdigest(),'raw_outputs_sha256':hashlib.sha256(pathlib.Path(raw_path).read_bytes()).hexdigest(),
             'scope':'Exploratory source-only DEV extraction. Literal grounding is not semantic correctness. All compiler and pair candidates require a separate source audit. No QA performance claim.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--raw',default=str(ROOT/'raw_outputs.jsonl'));a.add_argument('--source',default=str(ROOT.parents[1]/'data/dev_succession_candidates.jsonl'));a.add_argument('--out',default=str(ROOT/'validated'));args=a.parse_args();validate(args.raw,args.source,args.out)
