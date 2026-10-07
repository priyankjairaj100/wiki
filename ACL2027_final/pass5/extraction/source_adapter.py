#!/usr/bin/env python3
"""Source-only, clause-scoped lifecycle extraction, revision 3.

Only calendar expressions bound to an explicit occurrence or duration enter
this adapter. Every record retains exact source offsets. No QA fields enter.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pass3.extraction import source_adapter as v1
from pass3.extraction import succession_rules as succession
DATE=v1.DATE;parse_date=v1.parse_date;span=v1.span;stable_id=v1.stable_id
VERSION='source-clause-v3'
ADVERB=r'(?:(?:also|previously|concurrently|later|subsequently|again|briefly|formerly)\s+)*'
TENURE=r'(?:has served as|had served as|was appointed as|was appointed|served as|served in|served on|worked as|worked for|played for|was|chaired|represented|headed|managed|coached|taught at|taught in|studied at|attended|lived in|resided in)'
OCCURRENCE=r'(?:was appointed(?: as)?|was named(?: as)?|became|joined|rejoined|signed for|signed with|moved to|transferred to)'
INTERVAL=rf'(?:(?:from\s+(?P<start>{DATE})\s*(?:to|through|until|[–-])\s*(?P<end>{DATE}))|(?:between\s+(?P<bstart>{DATE})\s+and\s+(?P<bend>{DATE})))'
NAME=succession.NAME.replace("’.-", "’.\u2024-")
ROLE_START=re.compile(r'^(?:(?:a|an|the|first|second|third|\d+(?:st|nd|rd|th)|female|male|acting|deputy|assistant|associate|senior|junior|interim|federal|provincial|shadow|national|regional|city|state|Union|Australian|British|metropolitan|vice|Vice-)\s+)*(?:'+v1.ROLE[3:-1]+r'|member|MP|researcher|scientist|rabbi|alderman|councillor|councilwoman|councilman|commissioner|auditor|representative|judge|justice|journalist|civil servant|head|general|officer)\b',re.I)


# Parsing replaces protected periods with one character. Offsets never move.
MASK='\u2024'
ABBREVIATIONS=re.compile(r'\b(?:St|Dr|Mr|Mrs|Ms|Prof)\s*\.(?=\s+[A-Z])|\b(?:[A-Z]\s*\.\s*){2,}(?=[A-Z]|\s|,|$)|\b[A-Z]\s*\.(?=\s+[A-Z][a-z])|\b[1-9]\s*\.(?=\s+Liga\b)')
FINITE=r'(?:was|were|is|are|has|had|became|joined|rejoined|served|worked|played|moved|signed|returned|resigned|retired|left|died|married|belonged|held|led|scored|studied|attended|graduated|received|continued|remained|taught|helped|decided|accepted|announced|transferred|succeeded)'
DISCOURSE={'In','On','From','Between','After','Before','During','Although','Following','The','A','An','However','Eventually','Later','Upon'}

def parsing_view(text):
    chars=list(text)
    for m in ABBREVIATIONS.finditer(text):
        for i in range(m.start(),m.end()):
            if chars[i]=='.':chars[i]=MASK
    return ''.join(chars)

def restore_literals(obj,text):
    if isinstance(obj,dict):
        if {'start','end','text'} <= obj.keys() and isinstance(obj['start'],int):
            obj['text']=text[obj['start']:obj['end']]
        for x in obj.values():restore_literals(x,text)
    elif isinstance(obj,list):
        for x in obj:restore_literals(x,text)

def local_antecedent(p,pos):
    """Resolve only named grammatical subjects earlier in this paragraph."""
    if not p.get('article_person_evidence'):return None
    text=p['text'][:pos];found=[]
    pat=rf'(?<![\w])(?P<name>(?:(?:de|van|von)\s+)?{NAME})\s+(?:also\s+|again\s+|later\s+|previously\s+)?(?={FINITE}\b)'
    for m in re.finditer(pat,text):
        surface=m['name']
        if surface.split()[0] in DISCOURSE:continue
        if surface.casefold() in {'he','she','it','they'}:continue
        if re.search(r'\band\s*$',text[max(0,m.start()-8):m.start()],re.I):return None
        is_alias=surface.casefold() in {a.casefold() for a in subject_options(p)}
        if not is_alias:
            following=text[m.end():]
            personal=rf'(?:belonged|served|joined|rejoined|married|died|studied|graduated|retired|resigned|became|was (?:born|appointed|named|a |an |the |{v1.ROLE}))\b'
            if not re.match(personal,following,re.I):continue
        canonical=v1.article_name(p) if is_alias else surface
        found.append({'canonical':canonical,'source_span':span(p['text'],m.start('name'),m.end('name'))})
    return found[-1] if found else None

def leading_boundary(sentence,start):
    prefix=sentence[:start].strip()
    if not prefix:return True
    if re.search(r'(?:[;.!?]|\band|\bbut)\s*$',prefix,re.I):return True
    return bool(re.fullmatch(r'(?:Eventually|Later|Subsequently|Previously|However|Then)\s*,?',prefix,re.I))

def clean_value(value,start):
    value,va,vb=v1.clean_value(value,start)
    cut=re.search(r'\s+and\s+(?:continued|remained|stayed|worked|held|taught|led)\b',value,re.I)
    if cut:value=value[:cut.start()].rstrip();vb=va+len(value)
    return value,va,vb

def norm(value):return re.sub(r'\W+',' ',value.casefold()).strip()

def same_holder(a,b):return succession.alias(a,b)

BOUNDED=re.compile(r'\b(?:on trial|trial (?:had )?expired|for (?:(?:about|approximately) )?(?:(?:a|an) )?(?:one|two|three|four|five|six|seven|eight|nine|ten|[0-9]+)?[ -]?(?:months?|years?)(?:[ -]term)?|at the end of the (?:year|[^.;]*season)|(?:days?|weeks?|months?) later[^.;]*(?:termination|terminated|left|resigned)|(?:contract|trial)[^.;]*(?:expired|terminated|termination))\b',re.I)

def link_and_filter(p,claims):
    """Attach literal dated ends to unique local starts, then reject bounded unknowns."""
    text=p['text'];candidates=[]
    for c in claims:
        # One duration cannot allocate different tenures to coordinated roles.
        roles=re.findall(r'\b(?:secretary|president|minister|director|professor|chairman|manager)\b',c['value'],re.I)
        if len(roles)>1 and re.search(r'\band\b',c['value'],re.I):continue
        candidates.append(c)
    # End mentions are read in textual order. Already closed starts are excluded.
    patterns=[
       rf'(?P<holder>{NAME}|[Hh]e|[Ss]he)\s+(?:was\s+)?(?P<cue>resigned(?:\s+from\s+[^.;]+?)?|sacked|dismissed|retired|left(?:\s+[^.;]+?)?)\s+(?:in|on)\s+(?P<date>(?i:{DATE}))',
       rf'(?P<holder>[Hh]is|[Hh]er)\s+(?P<cue>term|tenure|presidency|position)\s+ended\s+(?:in|on)\s+(?P<date>(?i:{DATE}))',
       rf'(?P<cue>end of)\s+(?P<holder>his|her)\s+(?:term|tenure|presidency)\s+(?:in|on)\s+(?P<date>(?i:{DATE}))',
       rf'(?P<holder>[Hh]e|[Ss]he|{NAME})\s+held\s+(?:his|her|the)\s+(?P<cue>position|post|office)\s+until\s+(?P<date>(?i:{DATE}))',
       rf'(?P<holder>that)\s+(?P<cue>disbanded|dissolved)\s+(?:in|on)\s+(?P<date>(?i:{DATE}))',
    ]
    mentions=[]
    for pat in patterns:
        mentions.extend(re.finditer(pat,text))
    mentions.sort(key=lambda m:(m.start(),m.end()))
    used=set()
    for m in mentions:
        end=parse_date(m['date'],m.start('date'))
        if not end:continue
        holder=m['holder'];cue=m['cue'];dissolve=cue.casefold() in {'disbanded','dissolved'}
        if holder.casefold() in {'he','she','his','her'}:
            prior=local_antecedent(p,m.start('holder'));holder=prior['canonical'] if prior else None
        eligible=[c for c in candidates if c.get('end') is None and c['atomic_span']['end']<=m.start() and c['start']['upper']<end['lower']]
        if dissolve:eligible=[c for c in eligible if c['slot']=='membership']
        else:eligible=[c for c in eligible if holder and same_holder(c['subject']['canonical'],holder)]
        target=re.search(r'\bfrom\s+(.+)$',cue,re.I)
        if target:eligible=[c for c in eligible if norm(target[1]) in norm(c['value'])]
        elif cue.casefold() in {'sacked','dismissed','term','tenure','presidency','position','post','office','end of'}:
            eligible=[c for c in eligible if c['slot']=='position']
        if len(eligible)!=1:continue
        c=eligible[0];key=(m.start('date'),m.end('date'),c['claim_id'])
        if key in used:continue
        used.add(key);c['end']=end;c['temporal_kind']='validity_duration'
        c['end_attachment']={'source_span':span(text,m.start(),m.end()),'reason':'Unique compatible earlier open occurrence in this paragraph.','rule':'paragraph_calendar_end'}
    selected=[]
    for c in candidates:
        if c.get('end') is not None:selected.append(c);continue
        containing=[(o,s) for o,s in v1.sentences(text) if o<=c['atomic_span']['start']<o+len(s)]
        if containing and BOUNDED.search(containing[0][1]):continue
        # An unresolved ending can target one compatible local occurrence only.
        reject=False
        for o,s in v1.sentences(text):
            if o<c['atomic_span']['end'] or not BOUNDED.search(s):continue
            prior=[x for x in candidates if x.get('end') is None and x['atomic_span']['end']<=o and same_holder(x['subject']['canonical'],c['subject']['canonical'])]
            related=any(term in s.casefold() for term in ('his ','her ','he ','she ','the club','the contract','the trial'))
            if related and len(prior)==1 and prior[0]['claim_id']==c['claim_id']:reject=True;break
        if not reject:selected.append(c)
    return selected



def subject_options(p):
    name=v1.article_name(p);opts=set(v1.aliases(name))
    if p.get('article_person_evidence'):
        base=name.split(',')[0].strip();opts.add(base)
        if len(base.split())>=2:opts.add(base.split()[-1])
        opts.update(('he','she','He','She'))
    return sorted({parsing_view(x) for x in opts},key=len,reverse=True)


def subject(p,surface,start):
    name=v1.article_name(p)
    if surface.casefold() in {'he','she'}:
        antecedent=local_antecedent(p,start)
        if antecedent is None:
            return {'surface':surface,'canonical':None,'source_span':span(p['text'],start,start+len(surface)),
                    'resolution':'unresolved_local_pronoun','article_title':name}
        canonical=antecedent['canonical'];resolution='paragraph_local_explicit_subject'
    else:
        canonical=name if surface.casefold() in {x.casefold() for x in subject_options(p) if x.casefold() not in {'he','she'}} else surface
        resolution='article_title_alias' if canonical==name else 'explicit_named_subject'
    result={'surface':surface,'canonical':canonical,'source_span':span(p['text'],start,start+len(surface)),
            'resolution':resolution,'article_title':name}
    if surface.casefold() in {'he','she'}:result['antecedent_span']=antecedent['source_span']
    return result


def make_record(p,sa,sb,sub,verb,value,va,start,end,rule,atomic_a=None,atomic_b=None):
    text=p['text'];raw=text[sa:sb]
    if sub.get('canonical') is None:return None
    # Event modifiers and projected durations do not imply observed lifetimes.
    if re.search(r'\b(?:would|could|may|might|never|not)\b',text[sa:va],re.I):return None
    value=value.strip();vb=va+len(value)
    if re.search(r'(?:\b(?:and|or)|[0-9])\s*$',value,re.I):return None
    if value.count('(')!=value.count(')'):return None
    if re.search(r',\s*(?:which|who|making|including|where|when)\b',value,re.I):return None
    if sub['surface'].casefold() in {'he','she','it','they','we','i'} and not p.get('article_person_evidence'):return None
    if not value or len(value)>260 or len(value.split())>40:return None
    if re.fullmatch(r'(?:St|Dr|Mr|Mrs|Ms|Prof|No)',value,re.I):return None
    if re.search(r'\b(?:deployed|leaving|making|replaced|created|appointed|elected)\b',value,re.I):return None
    if end is None and re.search(r'\b(?:for the (?:remainder|rest)|for (?:one|two|three|four|five|six|seven|eight|nine|ten|[0-9]+)[ -](?:months?|years?))\b',raw,re.I):return None
    if re.search(r'\b(?:after|before|when|while|during|became|joined|served|was|were|had|has|is)\b',value,re.I):return None
    if re.search(r'\b(?:his|her|their|its|the same|this|that|latter|former|various|several)\b',value,re.I):return None
    if re.search(r'\b(?:in|on|from|until|since|between)\s+'+DATE,value,re.I):return None
    if re.search(r'\b(?:loan|contract)\b',raw,re.I) and end is None:return None
    if end and end['lower']<=start['upper']:return None
    if end is None and rule!='explicit_succession_start' and re.search(r'\b(?:until|through|quit|resigned|retired|left|departed|remained|stayed)\b',raw,re.I):return None
    if verb.casefold() in {'was','was appointed','was appointed as','was named','was named as','became'}:
        if not ROLE_START.match(value):return None
    if verb.casefold() in {'joined','rejoined','signed for','signed with','played for'}:slot='membership'
    elif verb.casefold() in {'moved to','transferred to','lived in','resided in'}:slot='location'
    elif verb.casefold()=='worked for':slot='employer'
    elif verb.casefold() in {'attended','studied at'}:slot='education'
    else:slot='position'
    aa=sa if atomic_a is None else atomic_a;ab=sb if atomic_b is None else atomic_b
    c={'claim_id':stable_id(VERSION,p['passage_id'],aa,ab,rule,value,start['source_span']['start']), 'passage_id':p['passage_id'],'article_path':p['article_path'],
       'source_span':span(text,sa,sb),'subject':sub,'slot':slot,'value':value,'value_span':span(text,va,vb),'predicate_span':None,
       'temporal_kind':'validity_duration' if end else 'occurrence_start','start':start,'end':end,'rule':rule,
       'replacement_policy':'explicit_succession_only','compiler_eligible':True,'state_text':f"{sub['canonical']}: {slot} = {value}.",
       'exclusion_assertion':None,'adapter_version':VERSION,'atomic_span':span(text,aa,ab),'coverage_scope':'atomic_clause_only',
       'unparsed_source_policy':'Keep all source text outside atomic_span as unmodeled evidence.'}
    vm=re.search(re.escape(verb),text[aa:ab],re.I)
    if vm:c['predicate_span']=span(text,aa+vm.start(),aa+vm.end())
    return c


def extract_clauses(p):
    text=p['text'];opts=subject_options(p);explicit='(?:'+'|'.join(re.escape(x) for x in opts)+')'
    # Explicit named subjects add organization-article tenures without pronoun guesses.
    subpat='(?:'+explicit+'|'+NAME+')'
    # Name matching is case-sensitive; auxiliary verbs remain case-insensitive.
    out=[]
    for offset,s in v1.sentences(text):
        tenure=rf'(?P<subject>{subpat})\s+(?i:{ADVERB})(?P<verb>(?i:{TENURE}))\s+(?P<value>[^;.!?]+?)\s+(?i:{INTERVAL})(?=\s*(?:[,;.!?)]|and\b|$))'
        for m in re.finditer(tenure,s):
            a,b=offset+m.start(),offset+m.end();su=subject(p,m['subject'],offset+m.start('subject'))
            # Prevent name regex from incorporating discourse words or a date prefix.
            if m['subject'].split()[0] in {'In','On','From','Between','After','Before','During','Although','Following'}:continue
            key='start' if m['start'] else 'bstart';endkey='end' if m['end'] else 'bend'
            start=parse_date(m[key],offset+m.start(key));end=parse_date(m[endkey],offset+m.start(endkey))
            if not start or not end:continue
            c=make_record(p,a,b,su,m['verb'],m['value'],offset+m.start('value'),start,end,'clause_explicit_tenure')
            if c:out.append(c)
            # A directly coordinated role retains the same subject and predicate.
            tail=s[m.end():]
            coord=rf'^\s*,?\s+and\s+(?:as\s+)?(?P<value>[^;.!?]+?)\s+(?i:{INTERVAL})(?=\s*(?:[,;.!?)]|$))'
            cm=re.match(coord,tail)
            if cm and c and su['canonical']==v1.article_name(p):
                ks='start' if cm['start'] else 'bstart';ke='end' if cm['end'] else 'bend';base=offset+m.end()
                st=parse_date(cm[ks],base+cm.start(ks));en=parse_date(cm[ke],base+cm.start(ke))
                if st and en:
                    cc=make_record(p,a,base+cm.end(),{**su,'resolution':'coordinated_explicit_subject'},m['verb'],cm['value'],base+cm.start('value'),st,en,'coordinated_explicit_tenure',atomic_a=base,atomic_b=base+cm.end())
                    if cc:out.append(cc)
        # Date-led tenure. Commas in roles stay inside the grounded value.
        lead=rf'\b(?i:{INTERVAL})\s*,?\s+(?P<subject>{subpat})\s+(?i:{ADVERB})(?P<verb>(?i:{TENURE}))\s+(?P<value>[^;.!?]+)'
        for m in re.finditer(lead,s):
            if not leading_boundary(s,m.start()):continue
            value=m['value'];cut=re.search(r'\s*,\s+(?:and|but|when|where|which|despite|a |the )|\s+and\s+(?:was|served|continued|remained|stayed|became|joined|worked|president|chairman)|\s+from\s+'+DATE,value,re.I)
            if cut:value=value[:cut.start()]
            value=value.rstrip(' ,')
            ks='start' if m['start'] else 'bstart';ke='end' if m['end'] else 'bend'
            st=parse_date(m[ks],offset+m.start(ks));en=parse_date(m[ke],offset+m.start(ke))
            if st and en:
                su=subject(p,m['subject'],offset+m.start('subject'))
                c=make_record(p,offset+m.start(),offset+m.start('value')+len(value),su,m['verb'],value,offset+m.start('value'),st,en,'leading_explicit_tenure')
                if c:out.append(c)
        # Relative biography: an explicitly named title subject followed by who.
        if p.get('article_person_evidence'):
            for m in re.finditer(rf'\bwho\s+(?i:{ADVERB})(?P<verb>(?i:{TENURE}))\s+(?P<value>[^;.!?]+?)\s+(?i:{INTERVAL})(?=\s*(?:[,;.!?)]|$))',s):
                prefix=s[:m.start()];matches=list(re.finditer(explicit,prefix,re.I))
                if not matches:continue
                sm=matches[0]
                if sm.group().casefold() in {'he','she'}:continue
                # Relative person references elsewhere in the sentence remain unresolved.
                if re.search(r'\b(?:father|mother|brother|sister|son|daughter|wife|husband)\b',prefix,re.I):continue
                if sm.start()>2:
                    leadname=prefix[:sm.end()]
                    if len(leadname)>100 or not re.fullmatch(NAME,leadname):continue
                ks='start' if m['start'] else 'bstart';ke='end' if m['end'] else 'bend'
                st=parse_date(m[ks],offset+m.start(ks));en=parse_date(m[ke],offset+m.start(ke))
                if st and en:
                    su=subject(p,sm.group(),offset+sm.start())
                    su['canonical']=v1.article_name(p);su['resolution']='relative_biography_title_alias'
                    c=make_record(p,offset+sm.start(),offset+m.end(),su,m['verb'],m['value'],offset+m.start('value'),st,en,'relative_biography_tenure',atomic_a=offset+m.start())
                    if c:out.append(c)
    return out


def extract_occurrences(p):
    text=p['text'];opts=subject_options(p);subpat='(?:'+'|'.join(re.escape(x) for x in opts)+')';out=[]
    for offset,s in v1.sentences(text):
        patterns=[
          (rf'(?P<subject>{subpat})\s+(?i:{ADVERB})(?P<verb>(?i:{OCCURRENCE}))\s+(?P<value>[^,;.!?]+?)\s+(?i:in|on)\s+(?P<date>{DATE})(?=\s*(?:[,;.!?]|$))','modified_suffix_occurrence'),
          (rf'(?i:In|On)\s+(?P<date>{DATE})\s*,?\s+(?P<subject>{subpat})\s+(?i:{ADVERB})(?P<verb>(?i:{OCCURRENCE}))\s+(?P<value>.+)','modified_leading_occurrence')]
        for pat,rule in patterns:
            for m in re.finditer(pat,s):
                if rule=='modified_leading_occurrence' and not leading_boundary(s,m.start()):continue
                value=m['value']
                if rule=='modified_leading_occurrence':
                    value,va,vb=clean_value(value,offset+m.start('value'))
                else:va=offset+m.start('value');vb=va+len(value)
                # All remaining explicit end cues in this sentence invalidate an open extraction.
                if re.search(r'\b(?:until|through|quit|resigned|retired|left|departed|remained|stayed)\b',s[m.start():],re.I):continue
                date=parse_date(m['date'],offset+m.start('date'))
                if date:
                    su=subject(p,m['subject'],offset+m.start('subject'))
                    end=max(vb,date['source_span']['end'])
                    c=make_record(p,offset+m.start(),end,su,m['verb'],value,va,date,None,rule)
                    if c:out.append(c)
    return out


def extract_passage(p):
    base=[]
    for c in v1.extract_passage(p):
        value=c['value'];raw=c['source_span']['text']
        if re.search(r'\b'+DATE+r'\b',value,re.I):continue
        if re.search(r'\b(?:created|appointed|elected|became|joined|served|worked|received)\b',value,re.I):continue
        if c.get('end') is None and re.search(r'\b(?:until|through|quit|resigned|retired|left|departed|remained|stayed)\b',raw,re.I):continue
        su=subject(p,c['subject']['surface'],c['subject']['source_span']['start'])
        if su.get('canonical') is None:continue
        c['subject']=su
        c['state_text']=f"{su['canonical']}: {c['slot']} = {c['value']}."
        if c['rule']=='date_led_occurrence' and not leading_boundary(p['text'],c['atomic_span']['start']):continue
        base.append(c)
    new=extract_clauses(p)+extract_occurrences(p)
    # Prefer complete explicit tenures over narrower duplicate records.
    proposals=sorted(new+base,key=lambda c:(0 if c.get('end') else 1,0 if c['adapter_version']==VERSION else 1,c['atomic_span']['start'],-len(c['atomic_span']['text'])))
    chosen=[]
    for c in proposals:
        a,b=c['atomic_span']['start'],c['atomic_span']['end']
        if any(a<x['atomic_span']['end'] and x['atomic_span']['start']<b for x in chosen):continue
        chosen.append(c)
    return link_and_filter(p,sorted(chosen,key=lambda c:c['atomic_span']['start']))


def extract_succession(p):
    """Reuse the audited explicit succession grammar, with disjoint local spans."""
    if not re.search(r'\b(?:succeeded|replaced)\b',p['text']):return []
    assertions=succession.extract(p);out=[];text=p['text']
    for e in assertions:
        # A bare role in a biography has no identified organizational scope.
        if p.get('article_person_evidence') and e['organization']==p['article_path'].split('/wiki/',1)[-1].replace('_',' '):continue
        region=e['source_span'];new_matches=list(re.finditer(re.escape(e['next']),text[region['start']:region['end']]))
        if not new_matches:continue
        nm=new_matches[-1];na=region['start']+nm.start()
        role_matches=list(re.finditer(re.escape(e['role']),text[:region['end']],re.I))
        if not role_matches:continue
        rm=role_matches[-1];va=rm.start();value=text[rm.start():rm.end()]
        aa=region['start'];ab=region['end']
        if e['rule']=='adjacent_explicit_passive_succession':
            earlier=[q['source_span']['end'] for q in assertions if q['source_span']['start']==aa and q['source_span']['end']<ab]
            if not earlier:continue
            aa=max(earlier)
        if not aa<=na<na+len(e['next'])<=ab:continue
        c=make_record(p,region['start'],region['end'],subject(p,e['next'],na),'served as',value,va,e['date'],None,'explicit_succession_start',atomic_a=aa,atomic_b=ab)
        if not c:continue
        c['succession_assertion']=e;c['role_scope']=e['slot_key'];out.append(c)
    return out


def extract_all(passages):
    out=[]
    for original in v1.add_source_context(passages):
        p=dict(original,text=parsing_view(original['text']))
        ordinary=extract_passage(p);successors=extract_succession(p)
        # Succession spans include the source's explicit relation. Preserve their
        # local clauses and leave conflicting ordinary proposals unmodeled.
        chosen=successors+[c for c in ordinary if not any(c['atomic_span']['start']<d['atomic_span']['end'] and d['atomic_span']['start']<c['atomic_span']['end'] for d in successors)]
        for c in successors:
            e=c['succession_assertion']
            targets=[d for d in successors if d['role_scope']==c['role_scope'] and succession.alias(d['subject']['surface'],e['previous']) and d['start']['upper']<c['start']['lower']]
            if len(targets)==1:
                c['exclusion_assertion']={'kind':'explicit_succession','excluded_claim_ids':[targets[0]['claim_id']], 'source_span':e['source_span'],'reason':'Explicit source succession and one earlier named occurrence in the same paragraph and role scope.'}
        for c in sorted(chosen,key=lambda c:c['atomic_span']['start']):
            restore_literals(c,original['text'])
            c['value']=c['value_span']['text']
            c['subject']['surface']=c['subject']['source_span']['text']
            c['subject']['canonical']=c['subject']['canonical'].replace(MASK,'.')
            c['state_text']=f"{c['subject']['canonical']}: {c['slot']} = {c['value']}."
            c['adapter_version']=VERSION
            out.append(c)
    return out


def run(source,out):
    source=pathlib.Path(source);out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    ps=[json.loads(x) for x in source.read_text().splitlines()];claims=extract_all(ps);v1.validate_model_records(claims,ps)
    (out/'claims.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in claims))
    summary={'adapter_version':VERSION,'input_passages':len(ps),'input_articles':len({p['article_path'] for p in ps}),'claims':len(claims),'new_claims':sum(c['adapter_version']==VERSION for c in claims),'explicit_ends':sum(c.get('end') is not None for c in claims),'covered_passages':len({c['passage_id'] for c in claims}),'rules':dict(collections.Counter(c['rule'] for c in claims)),'directed_pairs':len(v1.build_pairs(claims)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'adapter_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'answer_annotation_reads':0}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();run(a.source,a.out)
