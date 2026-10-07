"""Frozen source annotations. No questions, answers, or certificate results enter."""
from pathlib import Path
import json,hashlib,datetime,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.extraction.source_adapter import parse_date
O=Path(__file__).resolve().parent
ps=[json.loads(x) for x in (O/'sample.jsonl').read_text().splitlines()]
# Each source judgment records why a cue is insufficient for this diagnostic.
reasons={}
def reject(ids,reason):
 for i in ids:reasons[i]=reason
reject([0,7,11,12,13,14,15,16,20,21,25,26,30,32,39,42,43,45,47,49,51,54,55,56,57,58,63,65,72,73,74,76,80,81,83,85,88,89,92,94,97,98,99,104,105,106,108,112,116,117,120,121,123,125,126], 'The paragraph does not establish both required starts for one dated replacement pair. A relative, missing, projected, or ambiguous start remains unmodeled.')
reject([1,4,6,8,10,36], 'At least one required start is relative, absent, or belongs to a different role. No date is inferred.')
reject([2,3,17,22,23,28,35,37,38,40,44,46,48,52,53,59,60,61,62,64,66,67,69,70,71,75,77,78,79,82,84,86,87,90,91,93,95,96,100,101,102,103,110,111,113,114,115,118,119,122,124,127], 'The cue does not establish two dated holders of one exclusive position. The paragraph describes another relation, an undated event, or a non-position replacement.')
reject([24], 'The first holder served after a stated event. The event date does not fix the start date.')
reject([29], 'The replacement concerns ships, outside this position-holder diagnostic.')
# Reviewed literal dates. Discourse carryover is explicit in the notes.
specs={
5: ('coach of Águila', [('Agustín Castillo','December 2007',None),('Pablo Centrone','December 2008',None)],[(1,0)], 'The article title resolves he. Both appointments and the second replacement have explicit month dates.'),
9: ('Member of the Legislative Assembly for Riverton',[('Mike Nahan','2008',None),('Jags Krishnan','2021',None)],[(1,0)], 'The phrase until 2021, when he was succeeded binds the end and successor start to one event. This event appears once, as the successor start.'),
18: ('ruler of the Restored Taungoo Dynasty',[('Anaukpetlun','1605','1628'),('Thalun','1629','1648')],[(1,0)], 'The source identifies Thalun as successor and supplies both reign intervals. The separate end in 1628 remains modeled.'),
19: ('co-host position formerly held by Jon Jafari',[('Jon Jafari','2012',None),('Dan Avidan','2013',None)],[(1,0)], 'The source dates creation with Jafari in 2012 and explicitly says Avidan succeeded Jafari after his 2013 departure. The separate co-host Hanson is not a replacement witness.'),
27: ('coach of Marathón',[('Ramón Maradiaga','January 2012',None),('Manuel Keosseián','August 2012',None)],[(1,0)], 'Both named coaching starts and the directed replacement have explicit month dates.'),
31: ('sanjak-bey of the Sanjak of Bosnia',[('Jahja Pasha','1494',None),('Firuz Bey','1495','1496')],[(1,0)], 'The source names predecessor and successor. The prior reign ends in abbreviated 95. That end is the same transition year as the successor start, retained once. No independent duplicate endpoint is created.'),
33: ('manager of FC Flora',[('Martin Reim','2010',None),('Marko Lelov','December 2012','July 2013')],[(1,0)], 'The first dated replacement introduces Reim. The second replaces Reim with Lelov. Hurts replacement date is not stated and is not invented.'),
34: ('editor of First Things',[('Nuechterlein','October 2010',None),('R . R . Reno','April 2011',None)],[(1,0)], 'Nuechterlein returns as interim editor when Bottum leaves in October 2010. Reno becomes the third editor in April 2011. The ordered exclusive role establishes the transition.'),
41: ('Grand Duke of Lithuania',[('Jogaila','1377',None),('Kęstutis','1381',None)],[(1,0)], 'Algirdas death and succession supply the first year. In 1381 Kęstutis imprisons Jogaila and makes himself Grand Duke. Both dates use source discourse carryover.'),
50: ('Governor of the Straits Settlements',[('Cecil Clementi','5 February 1930',None),('Sir Andrew Caldecott','17 February 1934',None),('Sir Shenton Thomas','9 November 1934',None)],[(1,0),(2,1)], 'Clementis term ends on the stated date and he hands over to Caldecott. Thomas fills the same Governor position on the later stated date. The handover end is represented once.'),
68: ('chair of The News Quiz',[('Barry Norman','1977',None),('Barry Took, first tenure','1979','1981'),('Simon Hoggart, first tenure','1981','1986'),('Barry Took, second tenure','1986','1995'),('Simon Hoggart, second tenure','1996','March 2006'),('Sandi Toksvig','September 2006',None),('Miles Jupp','September 2015','2019'),('Nish Kumar','2020',None),('Angela Barnes','2020',None),('Andy Zaltzman','2020',None)],[(j,i) for j in range(1,10) for i in range(j)], 'The paragraph supplies an ordered sequence of chairs. Later chairs replace earlier tenures transitively within that explicit sequence. The three 2020 starts inherit the stated year. Series 101, 102, and 103 establish strict order. End of 2019 uses a conservative calendar-year bound. Earlier separate reign ends remain explicit.'),
107: ('Ambassador to the United States',[('John de Chastelain','1993',None),('Raymond Chrétien','1994',None)],[(1,0)], 'The paragraph dates the first appointment and explicitly vacates the same office for the successor in the 1994 sentence.'),
109: ('national secretary of Liga Veneta Repubblica',[('Beggiato','2003',None),('Comencini','2004',None)],[(1,0)], 'The source dates Beggiatos appointment and the later 2004 congress removes his group. Comencini is elected national secretary in the same episode. The temporal link uses discourse carryover.')
}
assert set(reasons)|set(specs)==set(range(128)),set(range(128))-set(reasons)-set(specs)

def date(p,raw,start=0):
 pos=p['text'].index(raw,start);d=parse_date(raw,pos);assert d is not None
 return d
out=[];judgments=[]
for i,p in enumerate(ps):
 j={'review_index':i,'passage_id':p['passage_id'],'article_path':p['article_path'],'source_split':p['source_split'],'status':'candidate_accept' if i in specs else 'reject','reason':specs[i][3] if i in specs else reasons[i]}
 judgments.append(j)
 if i not in specs:continue
 role,cs,edges,note=specs[i];claims=[]
 for n,(holder,st,en) in enumerate(cs):
  start=date(p,st);end=date(p,en) if en else None
  # Pick a literal date occurrence in the corresponding source tenure, where repeated.
  if i==31 and n==0:start=date(p,'1494')
  if i==68:
   anchors=['first broadcast','Barry Took from','Simon Hoggart from','Barry Took again','Simon Hoggart from 1996','Hoggart was replaced','in turn was replaced','Three different hosts','Three different hosts','Three different hosts']
   start=date(p,st,p['text'].index(anchors[n]));end=date(p,en,start['source_span']['end']) if en else None
  cid=f'r{i:03d}_c{n}'
  claims.append({'claim_id':cid,'holder':holder,'role':role,'start':start,'end':end,'temporal_kind':'validity_duration' if end else 'occurrence_start','source_span':{'start':0,'end':len(p['text']),'text':p['text']},'source_order':n})
 record={'record_id':f'r{i:03d}','review_index':i,'passage':p,'role':role,'claims':claims,'directed_pairs':[{'witness_id':claims[j]['claim_id'],'target_id':claims[k]['claim_id'],'source_span':{'start':0,'end':len(p['text']),'text':p['text']},'reason':note} for j,k in edges],'annotation_note':note,'known_precedence':[[claims[k]['claim_id'],claims[j]['claim_id']] for j,k in edges], 'status':'pending_independent_review'}
 out.append(record)
(O/'source_judgments.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in judgments))
(O/'annotated_candidates.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in out))
print(json.dumps({'reviewed':len(judgments),'candidate_accepts':len(out),'claims':sum(len(x['claims']) for x in out),'pairs':sum(len(x['directed_pairs']) for x in out)},indent=2))
