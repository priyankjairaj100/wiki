from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from pass3.extraction.source_adapter import parse_date
O=Path(__file__).resolve().parent
ps=[json.loads(x) for x in (O/'expanded_sample.jsonl').read_text().splitlines()]
specs={
130:('board seat of Virgin Australia Holdings',[('Mark Vaile','September 2008',None),('Angus Houston','December 2018',None)],[(1,0)],'The paragraph explicitly dates Vailes board appointment and Houstons replacement of Vaile.'),
160:('First Minister of Northern Ireland',[('Ian Paisley','8 May 2007',None),('Peter Robinson','5 June 2008',None)],[(1,0)],'The dated deputy appointments coordinate Paisleys becoming First Minister and service alongside Robinson, who succeeded Paisley. These dates apply to coordinated appointment clauses; independent review must confirm scope.'),
184:('Premier of Victoria',[('William Irvine','1902',None),('Thomas Bent','1904',None)],[(1,0)],'The paragraph explicitly dates Irvine becoming Premier and says he held office until 1904, when Bent succeeded him. The transition appears once.'),
229:('manager of FCI Levadia Tallinn',[('Igor Prins','March 2008',None),('Aleksandr Puštov','August 2010',None),('Sergei Hohlov-Simson','July 2011',None)],[(1,0),(2,1),(2,0)],'Three dated clauses describe the same managerial position and two explicit replacements. The final-to-first edge follows the explicit chronological succession chain.'),
239:('general editor of the Victoria County History',[('Louis Francis Salzman','1934',None),('Ralph Pugh','1949',None)],[(1,0)],'The source dates Salzmans succession in 1934 and says he held the post until 1949 and was succeeded by Pugh. The annotation links the coordinated succession to the stated tenure end.'),
246:('President of the Norwegian Association for Womens Rights',[('Torild Skard','2006',None),('Margunn Bjørnholt','2013',None),('Marit Nybakk','2016',None),('Karin M . Bruzelius','2018',None),('Anne Hege Grung','2020',None)],[(j,i) for j in range(1,5) for i in range(j)],'The paragraph dates Skards presidency and explicitly lists later presidents with their succession years. All later-to-earlier edges are within this ordered succession list. Skards 2013 end is represented once, through the successor event.'),
255:('host of Tonight',[('Steve Allen','1954',None),('Jack Paar','1956','1962')],[(1,0)],'The source dates the show beginning with Allen, explicitly dates Paars replacement in the when clause, and gives Paars separate departure year.')
}
uncertain={136:'Bruce follows Wallaces death within a long 1880 narrative, but his start year is not explicit.',147:'Friedlaenders dated departure does not explicitly date Furlers appointment.',177:'Podestas dated departure does not explicitly date Tandens appointment.',207:'The creation date of a title does not explicitly date its first holders appointment.',210:'The 2010 election concerns the prior holders announced retirement. The sons start date is not explicitly stated.',222:'The first replacement is an announcement. Later start years require season or event carryover.',223:'After the predecessors death does not explicitly assign the same day to the acting appointment.',231:'The later appointment does not explicitly replace the earlier named manager.',241:'Benkos replacement date is not explicit.'}
nonposition={128,132,137,138,140,142,145,146,148,149,150,151,154,155,156,158,159,161,164,168,169,171,172,174,178,179,181,182,185,186,187,189,190,191,194,195,197,198,199,202,203,205,206,209,212,213,215,216,217,218,219,220,221,226,227,230,232,233,234,235,236,238,240,242,244,249,250,252,253,254}
rows=[];jud=[]
for i in range(128,256):
 p=ps[i]
 if i==129:decision='exclude_exposure';reason='Chicago Stadium is a known prior source illustration.'
 elif i in specs:decision='candidate_accept';reason=specs[i][3]
 elif i in uncertain:decision='uncertain';reason=uncertain[i]
 elif i in nonposition:decision='reject';reason='No two dated holders of the same exclusive position are established. The cue concerns another relation or lacks required temporal grounding.'
 else:decision='reject';reason='The paragraph lacks an explicit dated start for at least one holder. Relative dates, seasons, and unrelated dated events do not supply a start.'
 jud.append({'review_index':i,'passage_id':p['passage_id'],'article_path':p['article_path'],'source_split':p['source_split'],'decision':decision,'reason':reason})
 if i not in specs:continue
 role,cs,es,note=specs[i];claims=[]
 for j,(name,raw,endraw) in enumerate(cs):
  pos=p['text'].index(raw)
  if i==184 and j==0:pos=p['text'].index(raw,p['text'].index('In 1902'))
  if i==246 and j>0:pos=p['text'].index(raw,p['text'].index(name))
  start=parse_date(raw,pos);end=parse_date(endraw,p['text'].index(endraw,pos+len(raw))) if endraw else None
  claims.append({'claim_id':f'r{i:03d}_c{j}','holder':name,'role':role,'start':start,'end':end,'temporal_kind':'validity_duration' if end else 'occurrence_start','source_span':{'start':0,'end':len(p['text']),'text':p['text']},'source_order':j})
 rows.append({'record_id':f'r{i:03d}','review_index':i,'passage':p,'role':role,'claims':claims,'directed_pairs':[{'witness_id':claims[d]['claim_id'],'target_id':claims[c]['claim_id'],'source_span':{'start':0,'end':len(p['text']),'text':p['text']},'reason':note} for d,c in es],'annotation_note':note,'known_precedence':[[claims[c]['claim_id'],claims[d]['claim_id']] for d,c in es],'status':'pending_independent_review','exposure_status':'eligible_for_independent_review'})
for name,data in [('extra_judgments_a.jsonl',jud),('extra_candidates_a.jsonl',rows)]:
 (O/name).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in data))
print({'reviewed':len(jud),'candidate_accepts':len(rows),'uncertain':len(uncertain)})
