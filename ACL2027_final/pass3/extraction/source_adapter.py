#!/usr/bin/env python3
"""Source-only temporal occurrence adapter. No answer annotations are accepted.

Bounds are closed Gregorian day ordinals. Source date precision determines
bounds. Validity durations retain two endpoints. No width is invented for
'before', 'after', 'around', 'early', or season expressions.
"""
from __future__ import annotations
import argparse, calendar, collections, datetime as dt, hashlib, json, pathlib, re
from urllib.parse import unquote

VERSION = 'source-occurrence-v1'
MONTHS = {m.casefold():i for i,m in enumerate(calendar.month_name) if m}
for i,m in enumerate(calendar.month_abbr):
    if m: MONTHS[m.casefold()] = i
MONTH = '(?:' + '|'.join(sorted(MONTHS,key=len,reverse=True)) + ')'
YEAR = r'(?:1[0-9]{3}|20[0-9]{2})'
DATE = rf'(?:[0-3]?[0-9]\s+{MONTH}\s+{YEAR}|{MONTH}\s+[0-3]?[0-9]\s*,?\s*{YEAR}|{MONTH}\s+{YEAR}|{YEAR})'
DATE_RE = re.compile(rf'(?<![\w–-]){DATE}(?![\w–-])',re.I)
ROLE = r'(?:head coach|manager|president|chairman|chairwoman|chairperson|chief executive(?: officer)?|CEO|director|captain|leader|prime minister|premier|speaker|minister|secretary|professor|lecturer|ambassador|mayor|governor|archbishop|bishop|rector|chancellor|dean|editor|moderator|host)'
VERB = r'(?:was appointed(?: as)?|was named(?: as)?|became|joined|rejoined|signed for|signed with|moved to|transferred to)'
STOP = re.compile(r'\s+(?:,|;|\.|but\b|and (?:then|he|she|was|were|became|served|joined|started|received|left|rejoined|signed|met|entered|a |an )\b|where\b|which\b|who\b|after\b|before\b|during\b|when\b|eventually\b|following\b|on (?:loan|an? |non-contract)\b|with\b|by\b|as a free agent\b|for (?:£|the remainder|the rest)|to (?:play|study|edit)\b|succeeding\b)',re.I)


def stable_id(*parts):
    return hashlib.sha256('\0'.join(map(str,parts)).encode()).hexdigest()[:24]


def span(text,start,end):
    return {'start':start,'end':end,'text':text[start:end]}


def parse_date(raw,start=0):
    """Parse a fully stated date. Relative and approximate expressions fail."""
    cleaned=re.sub(r'\s*,\s*',' ',raw).strip(); tok=cleaned.split()
    try:
        if len(tok)==1:
            year=int(tok[0]); month=None; day=None; precision='year'
        elif len(tok)==2:
            month=MONTHS[tok[0].casefold()];year=int(tok[1]);day=None;precision='month'
        elif len(tok)==3 and tok[0].isdigit():
            day=int(tok[0]);month=MONTHS[tok[1].casefold()];year=int(tok[2]);precision='day'
        elif len(tok)==3:
            month=MONTHS[tok[0].casefold()];day=int(tok[1]);year=int(tok[2]);precision='day'
        else:return None
        if day is not None:lo=hi=dt.date(year,month,day)
        elif month is not None:lo=dt.date(year,month,1);hi=dt.date(year,month,calendar.monthrange(year,month)[1])
        else:lo=dt.date(year,1,1);hi=dt.date(year,12,31)
    except (ValueError,KeyError):return None
    return {'lower':lo.toordinal(),'upper':hi.toordinal(),'lower_iso':lo.isoformat(),'upper_iso':hi.isoformat(),'precision':precision,'source_span':{'start':start,'end':start+len(raw),'text':raw}}


def sentences(text):
    offset=0
    for m in re.finditer(r'(?<=[.!?])\s+(?=[A-Z])',text):
        if m.start()>offset:yield offset,text[offset:m.start()]
        offset=m.end()
    if offset<len(text):yield offset,text[offset:]


def article_name(p):
    return re.sub(r'\s*\([^)]*\)\s*$','',unquote(p['article_path'].split('/wiki/',1)[-1]).replace('_',' ')).strip()


def aliases(name):
    options={name}
    # A single final token is an alias only for a name-shaped article title.
    bits=name.split()
    if 2<=len(bits)<=5 and ',' not in name and all(b[:1].isupper() or b.casefold() in {'de','van','von','del','da','di','the'} for b in bits):
        if len(bits[-1])>=4:options.add(bits[-1])
    return sorted(options,key=len,reverse=True)


def subject_pattern(name,person=False):
    opts=aliases(name) if person else [name]
    return '(?:'+'|'.join(re.escape(x) for x in opts)+(r'|[Hh]e|[Ss]he)' if person else ')')

def add_source_context(passages):
    person_articles=set()
    for p in passages:
        if p.get('paragraph_index',999)>2:continue
        text=p['text']
        if re.search(r'\b(?:born|birth)\b',text,re.I) or re.search(r'\(\s*'+DATE+r'\s*[–-]\s*'+DATE,text,re.I):
            person_articles.add(p['article_path'])
    return [dict(p,article_person_evidence=p['article_path'] in person_articles) for p in passages]


def clean_value(text,abs_start):
    a=len(text)-len(text.lstrip()); text=text.lstrip();abs_start+=a
    text=re.sub(r'\s+[.!?]\s*$','',text).strip()
    m=STOP.search(text)
    if m:text=text[:m.start()].rstrip()
    text=re.sub(r'\s*\([^)]*$','',text).rstrip()
    return text,abs_start,abs_start+len(text)


def norm(s):
    return re.sub(r'\W+',' ',s.casefold()).strip()


def _record(p,offset,s,subject_s,subject_a,verb_s,value_s,value_a,start,*,end=None,rule,excluded=None):
    name=article_name(p);subject_c=name
    # A clipped qualifier cannot turn a temporary state into an open state.
    # Relative durations induce dependent endpoint bounds and remain unmodeled.
    if end is None and re.search(r'\b(?:loan|contract|until|for the (?:remainder|rest)|for (?:one|two|three|four|five|six|seven|eight|nine|ten|[0-9]+)[ -](?:months?|years?))\b',s,re.I):return []
    if re.search(r'\b(?:after|before|during|when|while)\b',value_s,re.I):return []
    if re.search(r'\b(?:from|until|for)\s+'+YEAR,value_s,re.I):return []
    if verb_s.casefold()=='was' and re.match(r'(?:admitted|stationed)\b',value_s,re.I):return []
    if re.search(r'\b(?:and|but)\s+(?:served|was|worked|became|joined|had|has|is)\b',value_s,re.I):return []
    value_s,va,vb=clean_value(value_s,value_a)
    if not value_s or len(value_s)>180 or len(value_s.split())>24:return []
    if re.search(r'\b[0-9]+$',value_s):return []
    if re.search(r'\b(?:not|never|would|could|may|might)\b',s[:max(0,va-offset)],re.I):return []
    if verb_s.casefold() in {'became','was named','was named as','was elected','was elected as','was appointed','was appointed as'} and not re.match(rf'(?:a |an |the )?{ROLE}\b',value_s,re.I):return []
    if re.search(r'\b(?:rivals|various|several|many|their|his|her|same|latter|former|another|other|staff|ranks|team)\b',value_s,re.I):return []
    if verb_s.casefold() in {'joined','rejoined','signed for','signed with','played for'}:slot='membership'
    elif verb_s.casefold() in {'moved to','transferred to'}:slot='destination'
    elif verb_s.casefold() in {'worked for'}:slot='employer'
    elif verb_s.casefold()=='was' and value_s.casefold().startswith('married to '):
        slot='spouse';va+=len('married to ');value_s=value_s[len('married to '):];vb=va+len(value_s)
    else:slot='position'
    temporal_kind='validity_duration' if end else 'occurrence_start'
    subject_span=span(p['text'],subject_a,subject_a+len(subject_s))
    subject={'surface':subject_s,'canonical':subject_c,'source_span':subject_span,'resolution':'article_title_pronoun' if subject_s.casefold() in {'he','she'} else 'article_title_alias','article_title':name}
    rec={'claim_id':stable_id(p['passage_id'],offset,rule,slot,value_s,start['source_span']['start']),
         'passage_id':p['passage_id'],'article_path':p['article_path'],'source_span':span(p['text'],offset,offset+len(s)),
         'subject':subject,'slot':slot,'value':value_s,'value_span':span(p['text'],va,vb),'predicate_span':None,
         'temporal_kind':temporal_kind,'start':start,'end':end,'rule':rule,'replacement_policy':'explicit_succession_only',
         'compiler_eligible':end is None or end['lower']>start['upper'],'state_text':f'{subject_c}: {slot} = {value_s}.',
         'exclusion_assertion':excluded,'adapter_version':VERSION}
    bound_spans=[subject_span,rec['value_span'],start['source_span']]+([end['source_span']] if end else [])
    atomic_start=min(x['start'] for x in bound_spans)
    atomic_end=max(x['end'] for x in bound_spans)
    # Keep the preposition that connects a leading date to its event.
    if atomic_start-offset<6:atomic_start=offset
    rec['atomic_span']=span(p['text'],atomic_start,atomic_end)
    rec['coverage_scope']='atomic_clause_only'
    rec['unparsed_source_policy']='Keep all source text outside atomic_span as unmodeled evidence.'
    verb_match=re.search(re.escape(verb_s),p['text'][atomic_start:atomic_end],re.I)
    if verb_match:rec['predicate_span']=span(p['text'],atomic_start+verb_match.start(),atomic_start+verb_match.end())
    if end and end['lower']<=start['upper']:rec['compiler_exclusion_reason']='Start and end bounds overlap; endpoint dependence requires separate handling.'
    return [rec]


def extract_passage(p):
    """Extract records using only passage text and the source article title.

    This function never reads a question, relation annotation, answer, or gold date.
    Unmatched source text remains unparsed. Pronoun resolution is explicit metadata.
    """
    required={'passage_id','article_path','text'}
    if not required<=p.keys():raise ValueError(f'Missing passage fields: {required-p.keys()}')
    text=p['text'];name=article_name(p);sub=subject_pattern(name,p.get('article_person_evidence',False));out=[]
    for offset,s in sentences(text):
        # Simple date-led event: In March 2001, she joined X.
        pat=rf'^(?:In|On)\s+(?P<date>{DATE})\s*,?\s+(?P<subject>{sub})\s+(?P<verb>{VERB})\s+(?P<value>.+)$'
        m=re.match(pat,s,re.I)
        if m:
            d=parse_date(m['date'],offset+m.start('date'))
            if d:out+=_record(p,offset,s,m['subject'],offset+m.start('subject'),m['verb'],m['value'],offset+m.start('value'),d,rule='date_led_occurrence')
            continue
        # Simple event followed directly by its date, before any other clause.
        pat=rf'^(?P<subject>{sub})\s+(?P<verb>{VERB})\s+(?P<value>[^,;.!?]+?)\s+(?:in|on)\s+(?P<date>{DATE})(?=\s*(?:[,;.!?]|$))'
        m=re.match(pat,s,re.I)
        if m:
            d=parse_date(m['date'],offset+m.start('date'))
            if d:out+=_record(p,offset,s,m['subject'],offset+m.start('subject'),m['verb'],m['value'],offset+m.start('value'),d,rule='date_suffix_occurrence')
            continue
        # A tenure interval is two uncertain endpoints, never one broad start.
        tenure_verb=r'(?:served as|worked as|worked for|played for|was)'
        pat=rf'^(?P<subject>{sub})\s+(?P<verb>{tenure_verb})\s+(?P<value>[^;.!?]+?)\s+from\s+(?P<start>{DATE})\s+(?:to|until|[–-])\s*(?P<end>{DATE})(?=\s*(?:[,;.!?]|and\b|$))'
        m=re.match(pat,s,re.I)
        if not m:
            pat=rf'^From\s+(?P<start>{DATE})\s+(?:to|until|[–-])\s*(?P<end>{DATE})\s*,?\s+(?P<subject>{sub})\s+(?P<verb>{tenure_verb})\s+(?P<value>.+)$'
            m=re.match(pat,s,re.I)
        if m:
            start=parse_date(m['start'],offset+m.start('start'));end=parse_date(m['end'],offset+m.start('end'))
            if start and end:
                if start['lower']<=end['upper']:out+=_record(p,offset,s,m['subject'],offset+m.start('subject'),m['verb'],m['value'],offset+m.start('value'),start,end=end,rule='explicit_tenure')
    # Retain one record per exact source atomic extraction.
    unique={r['claim_id']:r for r in out}
    return list(unique.values())


def build_pairs(claims):
    """Accept only validated, directed source exclusions.

    The deterministic adapter does not infer exclusivity from slot identity.
    Model-assisted records can supply excluded_claim_ids with source evidence.
    validate_model_records() must validate these records before pair creation.
    """
    ids={c['claim_id'] for c in claims};out=[]
    for c in claims:
        e=c.get('exclusion_assertion')
        if not e:continue
        if e.get('kind')!='explicit_succession':continue
        for target in e.get('excluded_claim_ids',[]):
            if target not in ids:raise ValueError('An excluded claim must exist.')
            if target!=c['claim_id']:out.append((c['claim_id'],target))
    return sorted(set(out))


def validate_model_records(records,passages):
    """Check grounding and date-bound consistency. This does not prove entailment."""
    by_id={p['passage_id']:p for p in passages};ids=set()
    for r in records:
        if r['claim_id'] in ids:raise ValueError('Duplicate claim identifier.')
        ids.add(r['claim_id']);p=by_id[r['passage_id']];text=p['text']
        if r['article_path']!=p['article_path']:raise ValueError('Article mismatch.')
        spans=[r['source_span'],r['value_span'],r['subject']['source_span'],r['start']['source_span']]
        if r.get('atomic_span'):spans.append(r['atomic_span'])
        if r.get('predicate_span'):spans.append(r['predicate_span'])
        if r.get('end'):spans.append(r['end']['source_span'])
        e=r.get('exclusion_assertion')
        if e:spans.append(e['source_span'])
        for x in spans:
            if not isinstance(x['start'],int) or not isinstance(x['end'],int) or not 0<=x['start']<x['end']<=len(text):raise ValueError('Invalid source offsets.')
            if text[x['start']:x['end']]!=x['text']:raise ValueError('Source span mismatch.')
        for x in [r['start']]+([r['end']] if r.get('end') else []):
            parsed=parse_date(x['source_span']['text'],x['source_span']['start'])
            if parsed is None:raise ValueError('An exact calendar expression is required.')
            if any(x[k]!=parsed[k] for k in ('lower','upper','precision')):raise ValueError('Date bounds disagree with source precision.')
        if r['value']!=r['value_span']['text']:raise ValueError('Value must preserve the source text.')
        if r['temporal_kind']=='validity_duration' and not r.get('end'):raise ValueError('Duration requires a distinct end.')
        if r['temporal_kind']=='occurrence_start' and r.get('end'):raise ValueError('A duration must not be called an occurrence only.')
        if e and e['kind']!='explicit_succession':raise ValueError('Unknown exclusion kind.')
    build_pairs(records)
    return True


def run_dev(source_dir,out_dir,article_manifest=None):
    root=pathlib.Path(source_dir);out=pathlib.Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    overlap=set(json.loads((root/'timeqa_audit.json').read_text())['split_overlap']['overlap_article_paths'])
    passages=[json.loads(line) for line in (root/'normalized/dev_passages.jsonl').read_text().splitlines()]
    passages=[p for p in passages if p['article_path'] not in overlap]
    if article_manifest:
        manifest=json.loads(pathlib.Path(article_manifest).read_text())
        allowed=set(manifest['pilot_article_paths'] if isinstance(manifest,dict) else manifest)
        passages=[p for p in passages if p['article_path'] in allowed]
    passages=add_source_context(passages)
    claims=[c for p in passages for c in extract_passage(p)];validate_model_records(claims,passages)
    with (out/'dev_claims.jsonl').open('w') as f:
        for c in claims:f.write(json.dumps(c,ensure_ascii=False)+'\n')
    with (out/'dev_source_passages.jsonl').open('w') as f:
        used={c['passage_id'] for c in claims}
        for p in passages:
            if p['passage_id'] in used:f.write(json.dumps(p,ensure_ascii=False)+'\n')
    summary={'adapter_version':VERSION,'source_split':'article-disjoint TimeQA development only','input_passages':len(passages),'input_articles':len({p['article_path'] for p in passages}),
             'claims':len(claims),'covered_passages':len({c['passage_id'] for c in claims}),'covered_articles':len({c['article_path'] for c in claims}),
             'temporal_kinds':dict(collections.Counter(c['temporal_kind'] for c in claims)),'start_precision':dict(collections.Counter(c['start']['precision'] for c in claims)),
             'slots':dict(collections.Counter(c['slot'] for c in claims)),'rules':dict(collections.Counter(c['rule'] for c in claims)),
             'coreference':dict(collections.Counter(c['subject']['resolution'] for c in claims)),
             'compiler_eligible':sum(c['compiler_eligible'] for c in claims),'directed_replacement_pairs':len(build_pairs(claims)),
             'input_features':['source text','source article title','opaque passage identifier'],'answer_annotation_reads':0,
             'scope':'Extraction counts are not accuracy estimates. Exact source offsets do not prove correct entity resolution or entailment.'}
    (out/'dev_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Hash-based sample has no answer labels or method outcomes.
    sample=sorted(claims,key=lambda c:stable_id('audit-v1',c['claim_id']))[:min(60,len(claims))]
    with (out/'blind_audit_records.jsonl').open('w') as f:
        for i,c in enumerate(sample):
            row={'audit_id':f'E{i+1:03d}','article_path':c['article_path'],'source_text':c['source_span']['text'],'extraction':c,
                 'audit':{'subject_correct':None,'slot_correct':None,'value_correct':None,'event_date_correct':None,'temporal_kind_correct':None,'replacement_supported':None,'notes':''}}
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',default='pass2/naturaldata');ap.add_argument('--out-dir',default='pass3/extraction/results');ap.add_argument('--article-manifest');a=ap.parse_args();run_dev(a.source_dir,a.out_dir,a.article_manifest)
