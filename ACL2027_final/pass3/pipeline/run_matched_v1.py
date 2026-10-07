"""Matched source-only excerpt retrieval. Gold labels are a separate scoring input.

Every substantive source character belongs to one disjoint source unit.
The same frozen BM25 ranking feeds every temporal mask. All source units share
one global pool. Annotation article IDs do not restrict candidates.
"""
from __future__ import annotations
import argparse, collections, datetime as dt, hashlib, json, math, re, sys, time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pass3.extraction.source_adapter import add_source_context, extract_passage, validate_model_records, build_pairs, DATE_RE, parse_date, article_name
from pass3.theory.lifecycle import LifecycleClaim, compile_lifecycles, completion_certificates
TOKEN=re.compile(r'\w+',re.UNICODE)
YEAR=re.compile(r'(?<!\d)(1\d{3}|20\d{2})(?!\d)')
POLICIES={'no_temporal_filter':'no_filter','earliest_completion':'earliest','midpoint_completion':'midpoint','latest_completion':'latest','interval_outer_control':'interval','possible_support':'possible','guaranteed_support':'guaranteed','latest_mentioned_year_top20':'latest_year'}

def read(path): return [json.loads(x) for x in Path(path).read_text().splitlines() if x]
def dump(path,obj): Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def lines(path,rows): Path(path).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def tok(s):return TOKEN.findall(s.casefold())

def parse_query(question):
    matches=list(DATE_RE.finditer(question))
    dates=[parse_date(m.group(),m.start()) for m in matches]
    if not dates or any(x is None for x in dates) or len(dates)>2:return None
    if len(dates)==1:
        # Explicit unbounded requests remain unresolved instead of acquiring an invented bound.
        prefix=question[max(0,matches[0].start()-12):matches[0].start()].casefold()
        if re.search(r'\b(before|after|since|until|around)\s*$',prefix):return None
        return dates[0]['lower'],dates[0]['upper']
    between=question[matches[0].end():matches[1].start()]
    if not re.fullmatch(r'\s*(?:to|and|until|through|[–-])\s*',between,re.I):return None
    a,b=dates[0]['lower'],dates[1]['upper']
    return (a,b) if a<=b else None


def make_units(passages,records):
    byp=collections.defaultdict(list);rejected=[]
    for rec in records:
        try: LifecycleClaim.from_record(rec)
        except (ValueError,KeyError) as e:
            rejected.append({'claim_id':rec['claim_id'],'reason':str(e)});continue
        if not rec.get('atomic_span'):
            rejected.append({'claim_id':rec['claim_id'],'reason':'No atomic span'});continue
        byp[rec['passage_id']].append(rec)
    units=[];modeled=[]
    def append(p,a,b,c=None):
        text=p['text']
        while a<b and text[a].isspace():a+=1
        while b>a and text[b-1].isspace():b-=1
        if not TOKEN.search(text[a:b]):return
        cid=c['claim_id'] if c else 'fallback:'+p['passage_id']+':'+str(a)+':'+str(b)
        units.append({'unit_id':cid,'claim_id':c['claim_id'] if c else None,'passage_id':p['passage_id'],'article_path':p['article_path'],'title':article_name(p),'start_char':a,'end_char_exclusive':b,'text':text[a:b],'kind':'modeled' if c else 'fallback','start':c['start'] if c else None,'end':c.get('end') if c else None})
    for p in passages:
        recs=sorted(byp[p['passage_id']],key=lambda x:(x['atomic_span']['start'],x['atomic_span']['end'],x['claim_id']))
        conflicted=set()
        for i,c in enumerate(recs):
            for d in recs[i+1:]:
                if d['atomic_span']['start']>=c['atomic_span']['end']:break
                conflicted.update((c['claim_id'],d['claim_id']))
        recs=[c for c in recs if c['claim_id'] not in conflicted]
        rejected.extend({'claim_id':cid,'reason':'Overlapping atomic extraction; retained as fallback'} for cid in sorted(conflicted))
        cursor=0
        for c in recs:
            a,b=c['atomic_span']['start'],c['atomic_span']['end']
            assert p['text'][a:b]==c['atomic_span']['text']
            append(p,cursor,a);append(p,a,b,c);modeled.append(c);cursor=b
        append(p,cursor,len(p['text']))
    units.sort(key=lambda x:(x['passage_id'],x['start_char'],x['unit_id']))
    return units,modeled,rejected

class BM25:
    def __init__(self,units,k1=1.5,b=.75):
        self.units=units;self.k1=k1;self.b=b
        counts=[collections.Counter(tok(x['title']+' '+x['text'])) for x in units]
        lengths=np.array([sum(c.values()) for c in counts]);avg=float(lengths.mean())
        denom=k1*(1-b+b*lengths/avg);posting=collections.defaultdict(list)
        for i,c in enumerate(counts):
            for word,freq in c.items():posting[word].append((i,freq))
        self.postings={}
        for word,entries in posting.items():
            ids=np.array([e[0] for e in entries],dtype=np.int32);freq=np.array([e[1] for e in entries],dtype=float)
            idf=math.log(1+(len(units)-len(entries)+.5)/(len(entries)+.5))
            self.postings[word]=(ids,idf*freq*(k1+1)/(freq+denom[ids]))
    def rank(self,question):
        scores=np.zeros(len(self.units),dtype=float)
        for term in set(tok(question)):
            if term in self.postings:
                ids,vals=self.postings[term];scores[ids]+=vals
        return np.argsort(-scores,kind='stable').tolist(),scores

def clip_unit(unit,remaining):
    words=list(re.finditer(r'\S+',unit['text']))
    if not words or remaining<=0:return None
    end=len(unit['text']) if len(words)<=remaining else words[remaining-1].end()
    return {**unit,'end_char_exclusive':unit['start_char']+end,'text':unit['text'][:end]}

def build_context(chosen,units,status,k,budget):
    out=[];remaining=budget
    for i in chosen[:k]:
        u=clip_unit(units[i],remaining)
        if u is None:break
        u['temporal_status']=status.get(u['claim_id'],'unknown') if u['claim_id'] else 'unknown'
        remaining-=len(u['text'].split());out.append(u)
    return out

def prompt_for(query,contexts):
    blocks=[]
    for n,c in enumerate(contexts,1):
        # The reader gets original date bounds, never filled-in dates or gold labels.
        meta={'source_title':c['title'],'temporal_status':c['temporal_status']}
        if c.get('start'):meta['start_bounds']=[c['start']['lower_iso'],c['start']['upper_iso']]
        if c.get('end'):meta['end_bounds']=[c['end']['lower_iso'],c['end']['upper_iso']]
        blocks.append(f'[{n}] '+json.dumps(meta,ensure_ascii=False)+'\n'+c['text'])
    return ('Answer the question using only the supplied source excerpts. Return all distinct answers supported for the requested time. '
      'Do not use outside knowledge. If the excerpts do not support an answer, return an empty list. '
      'Date bounds describe source precision. Unknown means that the temporal adapter did not model that excerpt. '
      'Return only JSON with keys "answers" (list of strings) and "evidence" (list of excerpt numbers).\n\n'
      'QUESTION: '+query['question']+'\n\nSOURCE EXCERPTS:\n'+'\n\n'.join(blocks))

def run(args):
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True);started=time.time()
    config=json.loads(Path(args.config).read_text());passages=read(args.passages);queries=read(args.queries)
    source_paths=[args.config,args.passages,args.queries,Path(__file__),ROOT/'pass3/extraction/source_adapter.py',ROOT/'pass3/theory/lifecycle.py',ROOT/'pass2/theory/uncertain_time.py']+([args.claims] if args.claims else [])
    initial_hashes={str(x):sha(x) for x in source_paths}
    dump(out/'input_manifest.json',initial_hashes)
    if args.claims:records=read(args.claims)
    else:
        records=[c for p in add_source_context(passages) for c in extract_passage(p)]
    validate_model_records(records,passages)
    units,modeled,rejected=make_units(passages,records)
    records_byid={c['claim_id']:c for c in modeled};modeledids=set(records_byid)
    pairs=build_pairs(records)
    if any(a not in modeledids or b not in modeledids for a,b in pairs):raise ValueError('A pair endpoint fell outside modeled units; resolve before certification.')
    life=compile_lifecycles([LifecycleClaim.from_record(c) for c in modeled],pairs)
    exact={p:completion_certificates(life,p) for p in ['earliest','midpoint','latest']}
    lines(out/'claims.jsonl',records);lines(out/'units.jsonl',units);dump(out/'rejected_claims.json',rejected)
    index=BM25(units,config['ranking']['k1'],config['ranking']['b']);k=config['contexts']['unit_limit'];budget=config['contexts']['word_limit']
    allpred=[];audit=[];jobmap={};selection_seed=config['selection_seed']+'-reader-first24'
    reader_qids={q['question_id'] for q in sorted(queries,key=lambda q:digest(selection_seed+q['question_id']))[:args.reader_limit]}
    lines(out/'reader_selected_queries.jsonl',[q for q in queries if q['question_id'] in reader_qids])
    for qi,q in enumerate(queries):
        ranked,scores=index.rank(q['question']);window=parse_query(q['question']);status={};masks={}
        for name,policy in POLICIES.items():
            if name not in config['methods']:continue
            keep=set()
            if window:
                a,b=window
                for cid,c in life.claims.items():
                    cert=life.certificates[cid];status[cid]=cert.status(a,b)
                    if policy in {'no_filter','latest_year'}:yes=True
                    elif policy=='possible':yes=cert.possible(a,b)
                    elif policy=='guaranteed':yes=cert.guaranteed(a,b)
                    elif policy=='interval':yes=c.lower<=b and (c.end_upper is None or a<c.end_upper)
                    else:yes=exact[policy][cid].possible(a,b)
                    if yes:keep.add(cid)
            else:keep=modeledids.copy()
            masks[name]=keep
        methods={};claimcontexts={};signatures={}
        for name,policy in POLICIES.items():
            if name not in config['methods']:continue
            order=ranked
            if policy=='latest_year' and window:
                year=dt.date.fromordinal(window[1]).year
                def latestyear(i):
                    ys=[int(y) for y in YEAR.findall(units[i]['text']) if int(y)<=year]
                    return max(ys,default=0)
                order=sorted(ranked[:20],key=lambda i:-latestyear(i))+ranked[20:]
            chosen=[i for i in order if units[i]['claim_id'] is None or units[i]['claim_id'] in masks[name]][:k]
            claimcontexts[name]=[units[i]['unit_id'] for i in chosen]
            contexts=build_context(chosen,units,status,k,budget)
            context_signature=digest(json.dumps([(u['unit_id'],u['start_char'],u['end_char_exclusive'],u['temporal_status']) for u in contexts]))
            signatures[name]=context_signature
            methods[name]={'contexts':contexts,'selected_unit_ids':claimcontexts[name],'context_signature':context_signature,
                'fallback_units':sum(c['kind']=='fallback' for c in contexts),'modeled_units':sum(c['kind']=='modeled' for c in contexts),
                'filtered_unit_ids':sorted(modeledids-masks[name]),
                'filtered_contexts':[{'passage_id':records_byid[cid]['passage_id'],'start_char':records_byid[cid]['atomic_span']['start'],'end_char_exclusive':records_byid[cid]['atomic_span']['end']} for cid in sorted(modeledids-masks[name])]}
            if q['question_id'] in reader_qids:
                prompt=prompt_for(q,contexts);jobid=digest(prompt)
                job=jobmap.setdefault(jobid,{'job_id':jobid,'question_id':q['question_id'],'question':q['question'],'prompt':prompt,'methods':[],'context_signature':context_signature,'provenance':{'source_passages':str(args.passages),'source_sha256':sha(args.passages),'query_sha256':sha(args.queries),'corpus':'full DEV source pool','feature_gold_reads':0},'contexts':contexts})
                job['methods'].append(name)
        top20=ranked[:20];top20modeled=[units[i]['claim_id'] for i in top20 if units[i]['claim_id']]
        stable=claimcontexts['possible_support']==claimcontexts['guaranteed_support']
        completion=['earliest_completion','midpoint_completion','latest_completion']
        row={'question_id':q['question_id'],'article_path':q['article_path'],'query_time_parsed':window is not None,'query_window':window,
            'temporal_extraction_active':bool(top20modeled),'uncertain_start_active':any(life.claims[c].lower<life.claims[c].upper for c in top20modeled),
            'replacement_active':any(b in top20modeled for a,b in pairs),'claim_context_certificate':stable if window else None,
            'reader_context_certificate':signatures['possible_support']==signatures['guaranteed_support'] if window else None,
            'all_three_completion_context_agreement':len({signatures[m] for m in completion})==1,
            'completion_contexts_differ_from_possible':any(signatures[m]!=signatures['possible_support'] for m in completion),
            'completion_sensitive':len({signatures[m] for m in completion})>1,
            'possible_differs_interval':signatures['possible_support']!=signatures['interval_outer_control'],
            'possible_differs_no_filter':signatures['possible_support']!=signatures['no_temporal_filter'],
            'modeled_mask_counts':{m:len(s) for m,s in masks.items()},'context_signatures':signatures,
            'top20_modeled_ids':top20modeled,'shown_fallback_fraction':{m:v['fallback_units']/len(v['contexts']) if v['contexts'] else 0 for m,v in methods.items()}}
        audit.append(row);allpred.append({'question_id':q['question_id'],'question':q['question'],'query_window':window,'methods':methods})
        if (qi+1)%50==0:print('retrieved',qi+1,'/',len(queries),flush=True)
    lines(out/'predictions.jsonl',allpred);lines(out/'mechanism_questions.jsonl',audit);lines(out/'reader_jobs.jsonl',jobmap.values())
    flags=['query_time_parsed','temporal_extraction_active','uncertain_start_active','replacement_active','claim_context_certificate','reader_context_certificate','all_three_completion_context_agreement','completion_contexts_differ_from_possible','completion_sensitive','possible_differs_interval','possible_differs_no_filter']
    def summary(rows):return {'n_queries':len(rows),'counts':{f:sum(r[f] is True for r in rows) for f in flags},'fallback_fraction':{m:sum(r['shown_fallback_fraction'][m] for r in rows)/len(rows) if rows else None for m in config['methods']}}
    result={'corpus':{'passages':len(passages),'articles':len({p['article_path'] for p in passages}),'units':len(units),'extracted_claims':len(records),'modeled_claims':len(modeled),'rejected_claims':len(rejected),'accepted_pairs':len(pairs),'explicit_end_events':len(life.explicit_end_ids),'bounded_claim_fraction':len(modeled)/len(units)},'all_questions':summary(audit),'slices':{f:summary([r for r in audit if r[f]]) for f in ['temporal_extraction_active','uncertain_start_active','replacement_active','completion_sensitive']},'reader_jobs':len(jobmap),'reader_queries':len(reader_qids),'feature_gold_reads':0,'elapsed_seconds':time.time()-started}
    dump(out/'mechanism_summary.json',result)
    assert all(sha(path)==value for path,value in initial_hashes.items()), 'An input changed while inference was running.'
    dump(out/'manifest.json',{'inputs':initial_hashes,'artifacts':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'},'command':' '.join(sys.argv)})
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--passages',default='pass3/protocol/dev_source_passages.jsonl');p.add_argument('--queries',default='pass3/protocol/dev_pilot_queries.jsonl');p.add_argument('--config',default='pass3/protocol/config.json');p.add_argument('--claims');p.add_argument('--output',default='pass3/pipeline/pilot');p.add_argument('--reader-limit',type=int,default=24);run(p.parse_args())
