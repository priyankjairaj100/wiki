#!/usr/bin/env python3
"""Full original TempLAMA: positive observations, text-only inference, key-held-out evaluation.

No source absence creates an inference event. Source answer sets are used only
for scoring. Latest-batch is a retrieval policy, not a truth certificate.
"""
from __future__ import annotations
import bisect,collections,dataclasses,hashlib,json,math,pathlib,random,re,sys,time
import numpy as np
import scipy.sparse as sp
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[1]
OUT=HERE/'results'; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'inputs/supplement/wikigraphrag-code-and-data'))
from wikigraphrag.core.claim import Claim
from wikigraphrag.detect import extract_features,same_subject_relation,changed_value
sys.path.insert(0,str(ROOT/'pass2/baselines'))
TOKEN=re.compile(r'\w+',re.UNICODE)
def tokens(t):return TOKEN.findall(t.lower())
def norm(t):return ' '.join(t.casefold().split()).strip(' .')
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
@dataclasses.dataclass(frozen=True)
class Observation:
 cid:str; text:str; timestamp:int
@dataclasses.dataclass(frozen=True)
class Parsed:
 slot:tuple[str,str]|None; value:str|None
# Public benchmark templates. No entity, value, or source key is supplied to parser.
TEMPLATES=[('team',r'(.+?) plays for (.+)\.'),('position',r'(.+?) holds the position of (.+)\.'),('education',r'(.+?) attended (.+)\.'),('chair',r'(.+?) is the chair of (.+)\.'),('party',r'(.+?) is a member of the (.+)\.'),('employer',r'(.+?) works for (.+)\.'),('government',r'(.+?) is the head of the government of (.+)\.'),('coach',r'(.+?) is the head coach of (.+)\.'),('owner',r'(.+?) is owned by (.+)\.')]
PATTERNS=[(name,re.compile(pattern),name in ('chair','government','coach')) for name,pattern in TEMPLATES]
def parse(text):
 for name,pattern,inverse in PATTERNS:
  m=pattern.fullmatch(text.strip())
  if m:
   a,b=m.groups(); subject,value=(b,a) if inverse else (a,b)
   return Parsed((name,norm(subject)),norm(value))
 return Parsed(None,None)

def audit(rows,partition):
 groups=collections.defaultdict(list)
 for row in rows:groups[row['id'].rsplit('_',1)[0]].append(row)
 events=[]; summaries={}
 for key,group in groups.items():
  group.sort(key=lambda x:int(x['date'])); previous=None; ever=set(); absent=set()
  for row in group:
   values={a['wikidata_id'] for a in row['answer']}
   if previous is not None:
    old={a['wikidata_id'] for a in previous['answer']}; added=values-old; removed=old-values
    events.append({'key':key,'split':partition[key],'previous_date':previous['date'],'date':row['date'],'added':sorted(added),'absent_from_next_label':sorted(removed),'retained':sorted(old&values),'recurring':sorted(values&absent),'first_changed':previous['answer'][0]['wikidata_id']!=row['answer'][0]['wikidata_id'],'previous_first_retained':previous['answer'][0]['wikidata_id'] in values,'gap_years':int(row['date'])-int(previous['date'])})
    absent|=removed; absent-=values
   ever|=values; previous=row
 for part in ('all','legacy_dev','development','test'):
  rr=[r for r in rows if part=='all' or partition[r['id'].rsplit('_',1)[0]]==part]
  ee=[e for e in events if part=='all' or e['split']==part]
  summaries[part]={'rows':len(rr),'keys':len({r['id'].rsplit('_',1)[0] for r in rr}),'answer_observations':sum(len(r['answer']) for r in rr),'multi_answer_rows':sum(len({a['wikidata_id'] for a in r['answer']})>1 for r in rr),'keys_ever_multi_answer':len({r['id'].rsplit('_',1)[0] for r in rr if len({a['wikidata_id'] for a in r['answer']})>1}),'max_answers':max(map(lambda r:len({a['wikidata_id'] for a in r['answer']}),rr)),'adjacent_observed_transitions':len(ee),'label_set_changed':sum(bool(e['added'] or e['absent_from_next_label']) for e in ee),'addition_only':sum(bool(e['added']) and not e['absent_from_next_label'] for e in ee),'removal_only':sum(not e['added'] and bool(e['absent_from_next_label']) for e in ee),'add_and_remove':sum(bool(e['added']) and bool(e['absent_from_next_label']) for e in ee),'changed_with_retained_value':sum(bool(e['added'] or e['absent_from_next_label']) and bool(e['retained']) for e in ee),'first_answer_changed':sum(e['first_changed'] for e in ee),'first_changed_previous_remains':sum(e['first_changed'] and e['previous_first_retained'] for e in ee),'recurrence_events':sum(bool(e['recurring']) for e in ee),'recurrence_keys':len({e['key'] for e in ee if e['recurring']}),'gapped_transitions':sum(e['gap_years']>1 for e in ee)}
 dump(OUT/'source_audit.json',{'notes':['All original answer IDs are retained.','Removal denotes absence from a later benchmark label; it is not an observed retirement event.','A recurrence denotes present, then absent, then present in observed source labels.'], 'counts':summaries,'relations':{rel:{'rows':sum(r['relation']==rel for r in rows),'multi_answer_rows':sum(r['relation']==rel and len(r['answer'])>1 for r in rows)} for rel in sorted({r['relation'] for r in rows})}})
 with (OUT/'source_transitions.jsonl').open('w') as f:
  for e in events:f.write(json.dumps(e,ensure_ascii=False)+'\n')
 return groups

def original_endpoints(obs):
 """Exact original predicate using a lossless inverted subject candidate index."""
 texts=list(dict.fromkeys(o.text for o in obs)); ti={t:i for i,t in enumerate(texts)}
 fs=[extract_features(Claim(cid=str(i),text=t,timestamp=0)) for i,t in enumerate(texts)]
 pp=collections.defaultdict(set); cp=collections.defaultdict(set)
 for i,f in enumerate(fs):
  for p in f.phrases:pp[p].add(i)
  for c in f.content:cp[c].add(i)
 pairs=[]; candidate_count=0
 for i,f in enumerate(fs):
  cand=set()
  # Both sides with proper names require a shared full phrase. Fallback needs a content token.
  for p in f.phrases:cand.update(pp[p])
  for c in f.content:cand.update(j for j in cp[c] if f.proper_noun_count<1 or fs[j].proper_noun_count<1)
  for j in cand:
   if j<=i:continue
   candidate_count+=1
   if same_subject_relation(f,fs[j]) and changed_value(f,fs[j]):pairs.append((i,j))
 dates=collections.defaultdict(list)
 for o in obs:dates[ti[o.text]].append(o.timestamp)
 dates={k:sorted(set(v)) for k,v in dates.items()}; neighbors=collections.defaultdict(list)
 for i,j in pairs:neighbors[i].append(j); neighbors[j].append(i)
 first=np.full(len(obs),np.inf); last=np.full(len(obs),np.inf)
 for i,o in enumerate(obs):
  future=[]
  for j in neighbors[ti[o.text]]:
   ds=dates[j]; pos=bisect.bisect_right(ds,o.timestamp)
   if pos<len(ds):future.extend((ds[pos],ds[-1]))
  if future:first[i]=min(future); last[i]=max(future)
 return first,last,{'unique_texts':len(texts),'candidate_pairs':candidate_count,'positive_text_pairs':len(pairs),'lossless_index':'Shared proper phrase or fallback shared content token; all original predicate matches retained.'}

def bm25_index(obs):
 docs=[collections.Counter(tokens(o.text)) for o in obs]; vocab={t:i for i,t in enumerate(sorted({t for d in docs for t in d}))}
 lengths=np.array([sum(d.values()) for d in docs]); avg=lengths.mean(); df=collections.Counter(t for d in docs for t in d)
 rr=[]; cc=[]; vv=[]
 for i,d in enumerate(docs):
  for t,f in d.items():
   rr.append(i);cc.append(vocab[t]);vv.append(math.log(1+(len(obs)-df[t]+.5)/(df[t]+.5))*f*2.5/(f+1.5*(.25+.75*lengths[i]/avg)))
 mat=sp.csr_matrix((vv,(rr,cc)),shape=(len(obs),len(vocab)))
 return mat,vocab

def main():
 started=time.time(); split=json.loads((HERE/'split_manifest.json').read_text()); partition=split['keys']
 source=ROOT/split['source']; assert hashlib.sha256(source.read_bytes()).hexdigest()==split['source_sha256']
 rows=[json.loads(l) for l in source.open()]; groups=audit(rows,partition)
 obs=[]; gold=[]; parsed=[]
 for row in rows:
  key=row['id'].rsplit('_',1)[0]
  for j,a in enumerate(row['answer']):
   name=a['name']; name=name[0] if isinstance(name,list) else name
   text=row['query'].replace('_X_',name); cid=hashlib.sha256((row['id']+'|'+str(j)).encode()).hexdigest()[:20]
   obs.append(Observation(cid,text,int(row['date'])));gold.append((key,a['wikidata_id']));parsed.append(parse(text))
 dates=np.array([o.timestamp for o in obs]); slots=collections.defaultdict(list)
 for i,p in enumerate(parsed):
  if p.slot is not None:slots[p.slot].append(i)
 parsed_query={k:parse(g[0]['query']) for k,g in groups.items()}
 source_to_slots={k:{parsed[i].slot for i,(kk,v) in enumerate(gold) if kk==k} for k in []}
 observed_map=collections.defaultdict(set)
 for i,(k,v) in enumerate(gold):observed_map[k].add(parsed[i].slot)
 collision=collections.defaultdict(set)
 for k,ps in observed_map.items():
  for p in ps:collision[p].add(k)
 diag={'observation_parse_success':sum(p.slot is not None for p in parsed),'query_parse_success':sum(p.slot is not None for p in parsed_query.values()),'observations':len(obs),'keys':len(groups),'source_keys_split_by_parser':sum(len(p)>1 for p in observed_map.values()),'parser_slots_merging_source_keys':sum(len(v)>1 for v in collision.values())}
 dump(OUT/'parser_collisions.json', [{'parsed_slot':slot,'source_keys':sorted(ks),'queries':[groups[k][0]['query'] for k in sorted(ks)]} for slot,ks in collision.items() if len(ks)>1])
 print('parse',diag,flush=True)
 first,last,old_diag=original_endpoints(obs); print('old predicate compiled',old_diag,flush=True)
 end_latest=np.full(len(obs),np.inf)
 for ids in slots.values():
  ds=sorted({dates[i] for i in ids})
  for i in ids:
   pos=bisect.bisect_right(ds,dates[i])
   if pos<len(ds):end_latest[i]=ds[pos]
 endpoints={'old_earliest':first,'old_latest_witness':last,'exact_latest_batch':end_latest}
 graphiti_file=ROOT/'pass2/baselines/policies.py'
 if graphiti_file.exists():
  from policies import graphiti_endpoints
  result=graphiti_endpoints(obs,parsed)
  ep,gdiag=result; endpoints['graphiti_policy']=np.array(ep); dump(OUT/'graphiti_diagnostics.json',gdiag)
 mat,vocab=bm25_index(obs); print('BM25 ready',flush=True)
 # One ranking per question; no test tuning. Fixed query-aware half-life grid.
 half_lives=[.5,1,2,5,10,math.inf]
 age_names={h:('age_inf' if math.isinf(h) else 'age_'+str(h).replace('.','p')) for h in half_lives}
 methods=['bm25','bm25_recent_tie','date_top5','date_full_pool','query_latest_single','query_latest_batch','query_history_union']+list(endpoints)+list(age_names.values())
 # Capacity heuristic uses only development observations, excludes legacy and test keys.
 dev_capacity=collections.defaultdict(lambda:1)
 for k,group in groups.items():
  if partition[k]!='development':continue
  p=parsed_query[k]
  for row in group:dev_capacity[p.slot[0]]=max(dev_capacity[p.slot[0]],len({a['wikidata_id'] for a in row['answer']}))
 methods += ['dev_capacity_latest_values','query_history_distinct']
 records=[]; key_stats={}; source_state={k:{int(r['date']):{a['wikidata_id'] for a in r['answer']} for r in g} for k,g in groups.items()}
 source_dates={k:sorted(v) for k,v in source_state.items()}
 gold_ids=collections.defaultdict(list)
 for i,(k,v) in enumerate(gold):gold_ids[k].append(i)
 # Every method sees the same complete text-only observation pool.
 for ki,(key,group) in enumerate(groups.items()):
  q=group[0]['query'].replace('_X_','').strip(); qt=collections.Counter(tokens(q))
  inds=[vocab[t] for t in qt if t in vocab]; weights=np.array([qt[t] for t in qt if t in vocab])
  score=np.asarray(mat[:,inds].dot(weights)).ravel(); rank=np.lexsort((np.arange(len(obs)),-score))
  query_slot=parsed_query[key].slot; ids=np.array(slots.get(query_slot,[]),dtype=int); target_ids=np.array(gold_ids[key],dtype=int)
  for row in group:
   cutoff=int(row['date']); allowed={a['wikidata_id'] for a in row['answer']}; eligible=rank[dates[rank]<=cutoff]
   keyed=ids[dates[ids]<=cutoff]; max_date=max(dates[keyed]) if len(keyed) else -math.inf
   batch=keyed[dates[keyed]==max_date]; batch=batch[np.lexsort((batch,-score[batch]))]
   keyed_rank=keyed[np.lexsort((keyed,-score[keyed]))]
   orders={'bm25':eligible,'bm25_recent_tie':eligible[np.lexsort((eligible,-dates[eligible],-score[eligible]))],'date_top5':np.array(sorted(eligible[:5],key=lambda i:(-dates[i],-score[i],i)),dtype=int),'date_full_pool':eligible[np.lexsort((eligible,-score[eligible],-dates[eligible]))],'query_latest_single':batch[:1],'query_latest_batch':batch,'query_history_union':keyed_rank}
   for name,end in endpoints.items():orders[name]=eligible[cutoff<end[eligible]]
   for h,name in age_names.items():
    age_score=score[eligible] if math.isinf(h) else score[eligible]*np.exp2(-(cutoff-dates[eligible])/h)
    orders[name]=eligible[np.lexsort((eligible,-age_score))]
   by_recent=keyed[np.lexsort((keyed,-score[keyed],-dates[keyed]))]; seen=set(); selected=[]
   for i in by_recent:
    val=parsed[i].value
    if val not in seen:seen.add(val);selected.append(i)
    if len(selected)>=dev_capacity[query_slot[0]]:break
   orders['dev_capacity_latest_values']=np.array(selected,dtype=int)
   distinct=[]; seen=set()
   for i in by_recent:
    val=parsed[i].value
    if val not in seen:seen.add(val);distinct.append(i)
   orders['query_history_distinct']=np.array(distinct,dtype=int)
   result={'source_id':row['id'],'key':key,'split':partition[key],'date':cutoff,'kind':'latest' if cutoff==max(source_dates[key]) else 'historical','question':q,'answer_qids':sorted(allowed),'multi_answer':len(allowed)>1,'methods':{}}
   for name,order in orders.items():
    top=order[:5].tolist(); relevant_values={gold[i][1] for i in top if gold[i][0]==key}
    active_target=target_ids[dates[target_ids]<=cutoff]
    if name in endpoints:active_target=active_target[cutoff<endpoints[name][active_target]]
    elif name in ('query_latest_single','query_latest_batch','dev_capacity_latest_values','query_history_distinct','date_top5'):
     active_target=[i for i in order if gold[i][0]==key]
    all_values={gold[i][1] for i in active_target}
    valid_values=relevant_values&allowed; stale_values=relevant_values-allowed
    hits=[gold[i][0]==key and gold[i][1] in allowed for i in top]
    stale_any=False
    for i in top:
     kk,v=gold[i]; ds=source_dates[kk]; pos=bisect.bisect_right(ds,cutoff)-1
     if pos>=0 and v not in source_state[kk][ds[pos]]:stale_any=True
    result['methods'][name]={'cids':[obs[i].cid for i in top],'hit1':int(bool(hits) and hits[0]),'hit5':int(any(hits)),'value_recall5':len(valid_values)/len(allowed),'candidate_value_recall':len(all_values&allowed)/len(allowed),'valid_value_suppression':len(allowed-all_values)/len(allowed),'stale_value_exposure5':int(bool(stale_values)),'any_key_label_stale_exposure5':int(stale_any),'wrong_key1':int(bool(top) and gold[top[0]][0]!=key),'precision5':sum(hits)/len(top) if top else 0,'candidate_count':len(order)}
   records.append(result)
  if (ki+1)%250==0:print('keys',ki+1,'/',len(groups),'seconds',round(time.time()-started),flush=True)
 # Select age policy once on key-macro development hit@1. Tie favors longer half-life.
 age_dev={h:[] for h in half_lives}
 for k in groups:
  if partition[k]!='development':continue
  kr=[r for r in records if r['key']==k]
  for h in half_lives:age_dev[h].append(sum(r['methods'][age_names[h]]['hit1'] for r in kr)/len(kr))
 selected_h=max(half_lives,key=lambda h:(sum(age_dev[h])/len(age_dev[h]),h)); selected_age=age_names[selected_h]
 for row in records:row['methods']['age_development_selected']=row['methods'][selected_age]
 metrics=['hit1','hit5','value_recall5','candidate_value_recall','valid_value_suppression','stale_value_exposure5','any_key_label_stale_exposure5','wrong_key1','precision5']
 summaries={}
 for splitname in ('legacy_dev','development','test'):
  part=[r for r in records if r['split']==splitname]; summaries[splitname]={}
  for subset,rr in [('all',part),('historical',[r for r in part if r['kind']=='historical']),('latest',[r for r in part if r['kind']=='latest']),('multi_answer',[r for r in part if r['multi_answer']]),('single_answer',[r for r in part if not r['multi_answer']])]:
   summaries[splitname][subset]={'n':len(rr),'n_keys':len({r['key'] for r in rr}),'methods':{m:{metric:float(np.mean([r['methods'][m][metric] for r in rr])) for metric in metrics} for m in list(methods)+['age_development_selected']}}
 dump(OUT/'full_results.json',{'protocol':'all-positive-source-observations-v1','source_sha256':split['source_sha256'],'split_manifest_sha256':hashlib.sha256((HERE/'split_manifest.json').read_bytes()).hexdigest(),'inference':['opaque cid','rendered source text','year'],'parsing':diag,'original_predicate':old_diag,'pool_observations':len(obs),'source_query_rows':len(rows),'age_selection':{'objective':'mean over development keys of mean snapshot Hit@1','grid_half_life_years':[str(h) for h in half_lives],'selected_half_life_years':str(selected_h),'development_scores':{str(h):sum(age_dev[h])/len(age_dev[h]) for h in half_lives}},'dev_capacity':dict(dev_capacity),'results':summaries,'runtime_seconds':time.time()-started})
 with (OUT/'predictions.jsonl').open('w') as f:
  for r in records:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
 with (OUT/'observations.jsonl').open('w') as f:
  for o,p in zip(obs,parsed):f.write(json.dumps({**dataclasses.asdict(o),'parsed':dataclasses.asdict(p)},ensure_ascii=False)+'\n')
 with (OUT/'evaluation_labels.jsonl').open('w') as f:
  for o,(k,v) in zip(obs,gold):f.write(json.dumps({'cid':o.cid,'key':k,'answer_qid':v})+'\n')
 print('completed',len(records),'queries',round(time.time()-started),'seconds',flush=True)
if __name__=='__main__':main()
