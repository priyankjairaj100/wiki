#!/usr/bin/env python3
"""Narrow source-cue calibration adapter for explicit succession clauses.

This adapter is separate from the frozen primary TimeQA extraction. It reads
source-only calibration paragraphs. It never converts ordinary appointments
into retirement and never invents a previous holder's start.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from pass3.extraction.source_adapter import DATE,parse_date,span,stable_id

NAME=r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]*(?:\s+(?:(?:de|van|von|der|den|da|di|du)\s+)?[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]*){0,5}"
ROLE=r'(?:director|president|chairman|chairperson|chief executive|CEO|leader|head coach|head football coach|manager|moderator)(?: of (?:the )?[A-Z][^,;.]+?)?'
P_SUFFIX=re.compile(rf'(?P<new>{NAME})\s+(?:succeeded|replaced)\s+(?P<old>{NAME})\s+as\s+(?P<role>{ROLE})\s+in\s+(?P<date>{DATE})(?=\s*(?:[,;.]|$))')
P_PREFIX=re.compile(rf'\bIn\s+(?P<date>{DATE})\s*,?\s+(?P<new>{NAME})\s+(?:succeeded|replaced)\s+(?P<old>{NAME})\s+as\s+(?P<role>{ROLE})(?=\s*(?:[,;.]|$))')
P_PASSIVE=re.compile(rf'(?P<old>{NAME})\s+was\s+(?:succeeded|replaced)\s+by\s+(?P<new>{NAME})\s+in\s+(?P<date>{DATE})(?=\s*(?:[,;.]|$))')
P_COORD=re.compile(rf'^\s*,\s*and\s+in\s+(?P<date>{DATE})\s+was\s+(?:succeeded|replaced)\s+by\s+(?P<new>{NAME})(?=\s*(?:[,;.]|$))')
P_UNTIL=re.compile(rf'^\s*,\s*holding this position until\s+(?P<date>{DATE})\s+when\s+(?:she|he)\s+was\s+(?:succeeded|replaced)\s+by\s+(?P<new>{NAME})(?=\s*(?:[,;.]|$))')


def norm(x):return re.sub(r'\W+',' ',x.casefold()).strip()

def alias(a,b):
    a,b=norm(a),norm(b)
    return a==b or (len(a.split())==1 and b.endswith(' '+a)) or (len(b.split())==1 and a.endswith(' '+b))

def scope(role,title):
    parts=re.split(r'\s+of\s+(?:the\s+)?',role,maxsplit=1)
    if len(parts)==2:return parts[1],parts[0]
    # Article scope is explicit metadata, not a globally resolved organization.
    # Its semantic suitability must pass the separate source audit.
    return title,role


def extract(p):
    text=p['text'];title=p['article_path'].split('/wiki/',1)[-1].replace('_',' ')
    assertions=[];seen=set()
    def emit(new,old,role,organization,date,a,b,rule,end_same_event=False):
        if date is None:return
        key=(a,b,new,old,date['lower'],date['upper'])
        if key in seen:return
        seen.add(key)
        assertions.append({'assertion_id':stable_id(p['passage_id'],*key),'passage_id':p['passage_id'],'article_path':p['article_path'],
                           'previous':old,'next':new,'role':role,'organization':organization,'slot_key':norm(organization)+' :: '+norm(role),
                           'date':date,'source_span':span(text,a,b),'rule':rule,'previous_end_is_same_source_event':end_same_event,
                           'semantic_audit_required':True})
    for pattern in (P_SUFFIX,P_PREFIX):
        for m in pattern.finditer(text):
            organization,role=scope(m['role'],title)
            date=parse_date(m['date'],m.start('date'))
            emit(m['new'],m['old'],role,organization,date,m.start(),m.end(),'explicit_active_succession')
            # Coordinate passive clauses retain the same grammatical subject.
            # Only an immediately adjacent, fully dated construction is accepted.
            for suffix,end_event in ((P_COORD,False),(P_UNTIL,True)):
                follow=suffix.match(text[m.end():])
                if follow:
                    end=m.end()+follow.end();startdate=m.end()+follow.start('date')
                    emit(follow['new'],m['new'],role,organization,parse_date(follow['date'],startdate),m.start(),end,
                         'adjacent_explicit_passive_succession',end_event)
    # Resolve an omitted role only from a unique prior named state in this paragraph.
    for m in P_PASSIVE.finditer(text):
        prior=[e for e in assertions if e['source_span']['end']<=m.start() and alias(e['next'],m['old'])]
        keys={e['slot_key'] for e in prior}
        if len(keys)!=1:continue
        ref=max(prior,key=lambda e:e['source_span']['end'])
        emit(m['new'],m['old'],ref['role'],ref['organization'],parse_date(m['date'],m.start('date')),m.start(),m.end(),'named_passive_with_unique_prior_role')
    return sorted(assertions,key=lambda e:(e['source_span']['start'],e['source_span']['end']))


def run(source,out_dir):
    source=pathlib.Path(source);out=pathlib.Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    ps=[json.loads(x) for x in source.read_text().splitlines()]
    assertions=[e for p in ps for e in extract(p)]
    claims=[]
    for e in assertions:
        claims.append({'claim_id':stable_id(e['assertion_id'],'next'),'passage_id':e['passage_id'],'article_path':e['article_path'],'holder':e['next'],
                       'slot_key':e['slot_key'],'role':e['role'],'organization':e['organization'],'start':e['date'],'end':None,'temporal_kind':'occurrence_start',
                       'source_span':e['source_span'],'source_assertion':e['assertion_id'],'semantic_audit_required':True})
    pairs=[];unresolved=[]
    for e in assertions:
        target=[c for c in claims if c['passage_id']==e['passage_id'] and c['slot_key']==e['slot_key'] and alias(c['holder'],e['previous']) and c['start']['upper']<e['date']['lower']]
        witness=[c for c in claims if c['source_assertion']==e['assertion_id']][0]
        if len(target)==1:
            pairs.append({'witness_id':witness['claim_id'],'target_id':target[0]['claim_id'],'source_assertion':e['assertion_id'],'source_span':e['source_span'],
                          'reason':'Explicit source succession and one named earlier occurrence in the same role scope.','semantic_audit_required':True})
        else:unresolved.append({'source_assertion':e['assertion_id'],'reason':'No unique earlier source occurrence. No start date is invented.','candidate_count':len(target)})
    def write(name,rows):(out/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    write('assertions.jsonl',assertions);write('claims.jsonl',claims);write('pairs.jsonl',pairs);write('unresolved.jsonl',unresolved)
    summary={'source_paragraphs':len(ps),'assertions':len(assertions),'claims':len(claims),'directed_pair_candidates':len(pairs),'articles_with_claims':len({c['article_path'] for c in claims}),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'adapter_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
             'scope':'Source-only cue calibration. This separate deterministic adapter is not the learned model or frozen primary adapter. All candidates require semantic source audit. No QA score.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',default=str(ROOT.parent/'data/dev_succession_candidates.jsonl'));ap.add_argument('--out',default=str(ROOT/'succession_rule_results'));a=ap.parse_args();run(a.source,a.out)
