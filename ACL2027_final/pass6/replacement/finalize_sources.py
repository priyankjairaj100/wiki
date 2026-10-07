from pathlib import Path
import json,hashlib,datetime,collections,sys
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(n):return [json.loads(x) for x in (O/n).read_text().splitlines()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reviews=read('independent_review.jsonl')+read('extra_review_a.jsonl')+read('extra_review_b.jsonl');good={x['review_index'] for x in reviews if x['decision']=='accept'}
allrows=read('annotated_candidates.jsonl')+read('extra_candidates_a.jsonl')+read('extra_candidates_b.jsonl')
rows=[r for r in allrows if r['review_index'] in good and r['exposure_status']=='eligible_for_independent_review']
segments={
5:[('In December 2007','Luis Ramírez Zapata .'),('In December 2008','Pablo Centrone .')],
9:[('Nahan was also','from 2008'),('2021 , when','Jags Krishnan .')],
18:[('Bayinnaungs grandson','take over Burma .'),('Anaukpetluns successor','war torn country .')],
27:[('He was revealed as','January 2012'),('but was replaced','August 2012 .')],
31:[('His predecessor Jahja Pasha','Bosnia ( 1494–95 )'),('From 1495','Sanjak of Bosnia .')],
33:[('In 2010','Martin Reim .'),('After the season','results in the league .')],
107:[('In 1993','Brian Mulroney .'),('In 1994','Raymond Chrétien .')],
130:[('In September 2008','Holdings ( ) .'),('He was replaced','December 2018 .')],
184:[('In 1902','holding office until 1904'),('1904 , when','Thomas Bent .')],
229:[('In March 2008','took over as manager .'),('In August 2010','Aleksandr Puštov .'),('In July 2011','Sergei Hohlov-Simson .')],
239:[('In 1934','the Victoria County History .'),('He held the post','Ralph Pugh .')],
246:[('During the presidency','Norwegian womens movement .'),('Skard was succeeded','Bjørnholt in 2013'),('by the Norwegian Parliaments','Nybakk in 2016'),('by Supreme Court Justice','Bruzelius in 2018'),('by Professor Anne','Grung in 2020 .')],
255:[('Originating in 1954','Jerry Lester and Dagmar .'),('Tonight was successful','Paar left the show in 1962 .')],
262:[('In October 2005','served in that role'),('November 2009 , when','Arturo Valenzuela .')],
277:[('On 29 December 2009','Dominique Bijotat .'),('He left his position','Didier Tholot .')],
321:[('In 2001','as a manager .'),('in November 2001','Pasi Rautiainen .'),('After the season','June 2003 .')],
323:[('Jennifer Egan','president of PEN America in 2018 .'),('Egan was succeeded','December 2 , 2020 .')],
334:[('Ramsbotham entered','Board of Education .'),('He remained in this office','July 1941 .')],
346:[('Arbeiter was sacked','take over as manager .'),('In December 2017','January 2018 .')],
349:[('James was subsequently','North Dorset in 1970'),('1979 , when','Sir Nicholas Baker .')]
}
assert set(segments)=={r['review_index'] for r in rows}
for r in rows:
 i=r['review_index'];text=r['passage']['text'];assert len(segments[i])==len(r['claims'])
 for c,(left,right) in zip(r['claims'],segments[i]):
  a=text.index(left);b=text.index(right,a)+len(right)
  c['unit_span']={'start':a,'end':b,'text':text[a:b]}
  assert a<=c['start']['source_span']['start']<c['start']['source_span']['end']<=b,(i,c['claim_id'],'date outside excerpt')
 for e in r['directed_pairs']:
  d=int(e['witness_id'].rsplit('c',1)[1]);c=int(e['target_id'].rsplit('c',1)[1])
  e['derivation']='ordered_succession_closure' if d-c>1 else 'explicit_consecutive_replacement'
 r['status']='accepted_by_two_source_reviews';r['source_panel']='initial128' if i<128 else 'additional256'
rows.sort(key=lambda r:r['review_index'])
(O/'accepted_records.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
deps=['accepted_records.jsonl','independent_review.jsonl','extra_review_a.jsonl','extra_review_b.jsonl','source_judgments.jsonl','extra_judgments_a.jsonl','extra_judgments_b.jsonl','RENDERING_PROTOCOL.md','ORACLE_ADDENDUM.md','run_challenge.py','finalize_sources.py']
paths=[O/n for n in deps]+[R/'pass3/theory/lifecycle.py',R/'pass2/theory/uncertain_time.py',R/'pass4/retrieval/lazy_certificate.py',R/'pass6/modeling/constraint_oracle.py']
freeze={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'Before all certificate outcomes','accepted_records_sha256':sha(O/'accepted_records.jsonl'),'files':{str(p.relative_to(R)):sha(p) for p in paths}}
(O/'accepted_freeze.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
summary={'screened':384,'initial_panel':128,'additional_panel':256,'first_review_candidate_graphs':len(allrows),'second_review_accepts':len(rows),'records':len(rows),'articles':len({r['passage']['article_path'] for r in rows}),'claims':sum(len(r['claims']) for r in rows),'edges':sum(len(r['directed_pairs']) for r in rows),'edge_derivations':dict(collections.Counter(e['derivation'] for r in rows for e in r['directed_pairs'])),'panels':dict(collections.Counter(r['source_panel'] for r in rows)),'splits':dict(collections.Counter(r['passage']['source_split'] for r in rows)),'accepted_indices':[r['review_index'] for r in rows],'source_constraints_overlap':[r['record_id'] for r in rows if any(next(c for c in r['claims'] if c['claim_id']==d)['start']['lower']<=next(c for c in r['claims'] if c['claim_id']==t)['start']['upper'] for d,t in [(e['witness_id'],e['target_id']) for e in r['directed_pairs']])], 'unseen_status_claimed':False,'known_exposure_exclusions_documented':True}
(O/'source_summary.json').write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2))
