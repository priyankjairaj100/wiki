#!/usr/bin/env python3
"""Reproducible CPU audit and full-pool temporal retrieval.

Inference receives only cid, text, and timestamp. Gold fields create evaluation
queries and score evidence; they never enter the matcher, masks, or ranking.
All conditions share standard-library BM25 (k1=1.5, b=.75, positive IDF).
No model generations or synthetic benchmark observations are produced.
"""
from __future__ import annotations
import argparse, collections, dataclasses, hashlib, json, math, os, pathlib, random, re, statistics, sys, time

HERE=pathlib.Path(__file__).resolve().parent
DEFAULT_SOURCE=pathlib.Path(os.environ.get('EVIDENCE_SOURCE',str(HERE.parents[1]/'inputs/supplement/wikigraphrag-code-and-data')))
TOKEN=re.compile(r'\w+',re.UNICODE)

def tokens(text): return TOKEN.findall(text.lower())
def norm(s): return ' '.join((s or '').lower().split())
def write_json(path,obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')

class BM25:
    def __init__(self,cs):
        self.docs=[collections.Counter(tokens(c.text)) for c in cs]
        self.length=[sum(d.values()) for d in self.docs]
        self.avg=sum(self.length)/max(1,len(cs)); self.n=len(cs)
        df=collections.Counter(t for d in self.docs for t in d)
        self.idf={t:math.log(1+(self.n-n+.5)/(n+.5)) for t,n in df.items()}
    def rank(self,q):
        qt=collections.Counter(tokens(q)); scores=[]
        for i,d in enumerate(self.docs):
            score=sum(qn*self.idf.get(t,0)*d[t]*2.5/(d[t]+1.5*(.25+.75*self.length[i]/self.avg)) for t,qn in qt.items() if d[t])
            scores.append(score)
        return sorted(range(self.n),key=lambda i:(-scores[i],i)),scores

class UF:
    def __init__(self,n): self.p=list(range(n))
    def find(self,a):
        while a!=self.p[a]: self.p[a]=self.p[self.p[a]]; a=self.p[a]
        return a
    def union(self,a,b): self.p[self.find(a)]=self.find(b)

def compile_masks(cs,extract_features,same_subject_relation,changed_value):
    started=time.perf_counter(); fs=[extract_features(c) for c in cs]
    n=len(cs); first=[math.inf]*n; last=[math.inf]*n; witness=[None]*n; newest=[None]*n
    pairs=[]; comparisons=0
    for i,c in enumerate(cs):
        if c.timestamp is None: continue
        for j,d in enumerate(cs):
            if d.timestamp is None or d.timestamp<=c.timestamp: continue
            comparisons+=1
            if same_subject_relation(fs[j],fs[i]) and changed_value(fs[j],fs[i]):
                pairs.append((i,j))
                if d.timestamp<first[i]: first[i]=d.timestamp; witness[i]=j
                if newest[i] is None or d.timestamp>last[i]: last[i]=d.timestamp; newest[i]=j
    elapsed=time.perf_counter()-started
    uf=UF(n)
    for i,j in enumerate(newest):
        if j is not None: uf.union(i,j)
    comp=collections.defaultdict(list); exact=collections.defaultdict(list)
    for i,c in enumerate(cs):
        comp[uf.find(i)].append(i)
        f=fs[i]; exact[(f.frame,f.phrases)].append(i)
    def next_dates(groups,distinct):
        ends=[math.inf]*n
        def fv(i):
            f=fs[i]; return ('number',f.numbers) if f.numbers else ('text',f.value_tokens)
        for group in groups.values():
            for i in group:
                later=[cs[j].timestamp for j in group if cs[j].timestamp is not None and cs[i].timestamp is not None and cs[j].timestamp>cs[i].timestamp and (not distinct or fv(i)!=fv(j))]
                if later: ends[i]=min(later)
        return ends
    return dict(first=first,last=last,witness=witness,newest=newest,pairs=pairs,features=fs,
                component=next_dates(comp,True),component_latest=next_dates(comp,False),
                exact=next_dates(exact,False),components=comp,exact_groups=exact,
                seconds=elapsed,comparisons=comparisons)

def gold_ends(cs):
    groups=collections.defaultdict(list)
    for i,c in enumerate(cs): groups[c.gold_key].append(i)
    ends=[math.inf]*len(cs)
    for key,group in groups.items():
        for i in group:
            later=[cs[j].timestamp for j in group if cs[j].timestamp is not None and cs[i].timestamp is not None and cs[j].timestamp>cs[i].timestamp and norm(cs[j].value)!=norm(cs[i].value)]
            if later: ends[i]=min(later)
    return groups,ends

def question(group):
    c=group[0]
    template=c.meta.get('query','') if c.meta else ''
    if '_X_' in template: return template.replace('_X_','').strip()
    relation=c.relation
    if relation=='chief executive officer': relation='CEO'
    return f'What is the {relation} of {c.subject}?'

def make_probes(cs,groups):
    probes=[]; now=max(c.timestamp for c in cs if c.timestamp is not None)+1
    for key,ids in groups.items():
        group=[cs[i] for i in ids]; dates=sorted({c.timestamp for c in group if c.timestamp is not None})
        if len(dates)<2: continue
        q=question(group)
        for a,b in zip(dates,dates[1:]): probes.append((key,q,(a+b)/2,'historical'))
        probes.append((key,q,now,'current'))
    return probes

def prf(pred,gold):
    tp=len(pred&gold); fp=len(pred-gold); fn=len(gold-pred)
    p=tp/(tp+fp) if tp+fp else 1; r=tp/(tp+fn) if tp+fn else 1
    return dict(tp=tp,fp=fp,fn=fn,precision=p,recall=r,f1=2*p*r/(p+r) if p+r else 0)

def bootstrap_delta(records,a,b,repetitions=5000):
    groups=collections.defaultdict(list)
    for row in records:
        groups[tuple(row['key'])].append(row['methods'][a]['hit1']-row['methods'][b]['hit1'])
    values=list(groups.values()); rng=random.Random(20261006)
    draws=[]
    for _ in range(repetitions):
        chosen=[values[rng.randrange(len(values))] for _ in values]
        draws.append(sum(sum(v) for v in chosen)/sum(len(v) for v in chosen))
    draws.sort(); differences=[x for v in values for x in v]
    return dict(delta=sum(differences)/len(differences),ci95=[draws[int(.025*repetitions)],draws[int(.975*repetitions)]],n_keys=len(values),repetitions=repetitions,seed=20261006)

def run_one(name,source,out,imports):
    Claim,load_claims,extract_features,same_subject_relation,changed_value,SupersessionDetector=imports
    gold=load_claims(str(source/'data'/name/'claims.jsonl'))
    visible=[Claim(cid=c.cid,text=c.text,timestamp=c.timestamp) for c in gold]
    idx=BM25(visible); compiled=compile_masks(visible,extract_features,same_subject_relation,changed_value)
    groups,gend=gold_ends(gold); probes=make_probes(gold,groups)
    ends={'direct_first':compiled['first'],'direct_last':compiled['last'],'component':compiled['component'],
          'component_latest':compiled['component_latest'],'exact_group_latest':compiled['exact'],'oracle':gend}
    ranking={key:idx.rank(q) for key,q,t,kind in probes}
    records=[]; methods=['bm25','date_top5','date_full_pool']+list(ends)
    for key,q,t,kind in probes:
        rank,scores=ranking[key]
        eligible=[i for i in rank if visible[i].timestamp is not None and visible[i].timestamp<=t]
        orders={'bm25':eligible,'date_top5':sorted(eligible[:5],key=lambda i:(-visible[i].timestamp,-scores[i],i)),
                'date_full_pool':sorted(eligible,key=lambda i:(-visible[i].timestamp,-scores[i],i))}
        for method,end in ends.items(): orders[method]=[i for i in eligible if t<end[i]]
        live={i for i in groups[key] if visible[i].timestamp<=t<gend[i]}
        values={norm(gold[i].value) for i in live}
        row=dict(dataset=name,key=key,question=q,cutoff=t,kind=kind,gold_live=[gold[i].cid for i in sorted(live)],methods={})
        for method,order in orders.items():
            top=order[:5]; j=top[0] if top else None
            row['methods'][method]=dict(cids=[gold[i].cid for i in top],hit1=int(j in live),hit5=int(bool(set(top)&live)),
              value_hit1=int(j is not None and gold[j].gold_key==key and norm(gold[j].value) in values),
              stale_exposure5=int(any(t>=gend[i] for i in top)),relevant_precision5=len(set(top)&live)/len(top) if top else 0,
              wrong_key1=int(j is not None and gold[j].gold_key!=key))
        records.append(row)
    summary={}
    for kind in ('historical','current'):
        rows=[r for r in records if r['kind']==kind]
        if not rows: continue
        summary[kind]={'n':len(rows),'n_keys':len({tuple(r['key']) for r in rows}),'methods':{m:{metric:sum(r['methods'][m][metric] for r in rows)/len(rows) for metric in ('hit1','hit5','value_hit1','stale_exposure5','relevant_precision5','wrong_key1')} for m in methods},
                       'comparisons':{m:bootstrap_delta(rows,'direct_first',m) for m in ('bm25','component','exact_group_latest','direct_last')}}
    ties=[]; recurring=[]
    for key,ids in groups.items():
        bydate=collections.defaultdict(set)
        for i in ids: bydate[gold[i].timestamp].add(norm(gold[i].value))
        ties += [dict(key=key,time=t,values=sorted(v)) for t,v in bydate.items() if len(v)>1]
        seq=[]
        for i in sorted(ids,key=lambda i:(gold[i].timestamp or -math.inf,i)):
            v=norm(gold[i].value)
            if not seq or seq[-1]!=v: seq.append(v)
        if len(set(seq))<len(seq): recurring.append(dict(key=key,values=seq))
    original=SupersessionDetector().detect(visible)
    original_stale={e.older for e in original}; our_stale={visible[i].cid for i,x in enumerate(compiled['first']) if x<math.inf}
    gold_stale={gold[i].cid for i,x in enumerate(gend) if x<math.inf}
    equivalence=[]
    for cutoff in sorted({c.timestamp for c in visible if c.timestamp is not None}):
        direct={i for i,j in compiled['pairs'] if visible[j].timestamp<=cutoff}
        represented={i for i,e in enumerate(compiled['first']) if e<=cutoff}
        equivalence.append(direct==represented)
    cross_pairs=[(i,j) for i,j in compiled['pairs'] if gold[i].gold_key!=gold[j].gold_key]
    fractured=sum(len({next(k for k,v in compiled['components'].items() if i in v) for i in ids})>1 for ids in groups.values())
    mixed=sum(len({gold[i].gold_key for i in ids})>1 for ids in compiled['components'].values())
    card=dict(dataset=name,n_claims=len(gold),n_keys=len(groups),n_query_keys=len(ranking),n_tie_batches=len(ties),n_recurring_keys=len(recurring),
      original_detection=prf(original_stale,gold_stale),current_mask_exactly_reproduced=original_stale==our_stale,
      all_cutoff_direct_equivalence=all(equivalence),n_cutoffs_checked=len(equivalence),n_pairs=len(compiled['pairs']),n_cross_key_pairs=len(cross_pairs),
      n_components=len(compiled['components']),n_mixed_components=mixed,n_fragmented_gold_keys=fractured,
      compilation_seconds=compiled['seconds'],n_time_ordered_comparisons=compiled['comparisons'],results=summary)
    write_json(out/(name+'_results.json'),card)
    with (out/(name+'_predictions.jsonl')).open('w') as f:
        for row in records: f.write(json.dumps(row,ensure_ascii=False)+'\n')
    write_json(out/(name+'_diagnostics.json'),dict(tie_batches=ties,recurring_keys=recurring,cross_key_pairs=[dict(older=gold[i].cid,newer=gold[j].cid,older_text=gold[i].text,newer_text=gold[j].text) for i,j in cross_pairs]))
    print(name,json.dumps({k:{m:round(v['hit1'],4) for m,v in s['methods'].items()} for k,s in summary.items()}),flush=True)
    return card

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=pathlib.Path,default=DEFAULT_SOURCE); ap.add_argument('--output',type=pathlib.Path,default=HERE/'results'); ap.add_argument('--datasets',nargs='+',default=['wikidata','templama','wikidata_prose','realprose','realwiki','realworld']); args=ap.parse_args()
    sys.path.insert(0,str(args.source))
    from wikigraphrag.core.claim import Claim
    from wikigraphrag.data.io import load_claims
    from wikigraphrag.detect import extract_features,same_subject_relation,changed_value,SupersessionDetector
    imports=(Claim,load_claims,extract_features,same_subject_relation,changed_value,SupersessionDetector)
    args.output.mkdir(parents=True,exist_ok=True)
    cards=[run_one(name,args.source,args.output,imports) for name in args.datasets]
    write_json(args.output/'summary.json',dict(protocol='full-pool-lexical-evidence-v1',seed=20261006,bm25=dict(k1=1.5,b=.75,idf='log(1+(N-df+.5)/(df+.5))'),notes=['Inference sees only cid, text, timestamp.','Queries use benchmark templates or subject/relation labels, never answer values.','Oracle uses gold keys and values only as an explicit ceiling.','Historical cutoffs are midpoints between distinct within-key source dates.','Current cutoff follows the latest source date in the corpus.','hit1/hit5 score key-relevant live evidence, not generated answers.','Confidence intervals resample entire gold-key clusters.','Date-top5 reorders five BM25 results; date-full-pool sorts all eligible records.','All exact-key date ties survive. No tie order is treated as factual.'],cards=cards))
    hashes={str(p.relative_to(args.source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((args.source/'data').glob('*/claims.jsonl'))}
    hashes['run_evidence.py']=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
    write_json(args.output/'input_hashes.json',hashes)
if __name__=='__main__': main()
