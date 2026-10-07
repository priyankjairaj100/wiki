#!/usr/bin/env python3
"""Audit released labels; preserve originals and create predeclared usable subsets."""
import json, pathlib, hashlib, collections
R=pathlib.Path(__file__).resolve().parent;N=R/'normalized'
def read(name):return [json.loads(l) for l in (N/name).open()]
def save(name,rows):
 with (N/name).open('w') as f:
  for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
A=json.loads((R/'timeqa_audit.json').read_text());overlap=set(A['split_overlap']['overlap_article_paths'])
for split in ['dev','test']:
 qs=read(f'{split}_annotations.jsonl');hs={h['history_id']:h for h in read(f'{split}_histories.jsonl')};ps={p['passage_id']:p for p in read(f'{split}_passages.jsonl')}
 nonempty=[q for q in qs if any(s['answer'].strip() for s in q['gold_answer_spans'])]
 save(f'{split}_nonempty_annotations.jsonl',nonempty)
 A['splits'][split]['zero_length_empty_answer_annotations']=len(qs)-len(nonempty)
 A['splits'][split]['annotations_with_nonempty_gold_spans']=len(nonempty)
 A['splits'][split]['gold_span_semantics']='Exact string anchors supplied by the benchmark. They are not verified temporal entailment labels.'
 A['splits'][split]['multi_answer_count_semantics']='Distinct literal answer strings. These can be aliases, concurrent values, or sequential answers to a range question.'
 A['splits'][split]['annotations_with_only_short_gold_paragraphs_under_50_characters']=sum(all(len(ps[s['passage_id']]['text'])<50 for s in q['gold_answer_spans']) for q in nonempty)
 if split=='dev':
  keep=[q for q in nonempty if hs[q['history_id']]['article_url'].removeprefix('https://en.wikipedia.org') not in overlap]
  save('dev_disjoint_nonempty_annotations.jsonl',keep)
  A['dev_disjoint_nonempty']={'annotations':len(keep),'histories':len({q['history_id'] for q in keep}),'removed_article_paths':sorted(overlap),'rule':'Remove all dev histories whose article occurs in test; then exclude questions without a nonempty gold span. Do not tune on test.'}
human=read('human_test_questions.jsonl');hp=[q for q in human if any(s['answer'].strip() for s in q['gold_answer_spans'])];save('human_test_nonempty_questions.jsonl',hp)
A['human_test']['zero_length_empty_answer_questions']=len(human)-len(hp);A['human_test']['questions_with_nonempty_gold_spans']=len(hp)
A['scope']+=' Answer sets include aliases and answers occurring at different points inside a queried range. Adjacency statistics describe labels, not independently verified retirement events.'
(R/'timeqa_audit.json').write_text(json.dumps(A,indent=2,ensure_ascii=False)+'\n')
ps={p['passage_id']:p for p in read('test_passages.jsonl')};hqs={q['question_id']:q for q in human}
items=[
 ('concurrent_tenants','/wiki/Chicago_Stadium#P466#annotation2','550f4fec99622e188e6d83a9',['The Stadium hosted the Chicago Blackhawks of the NHL from 1929 to 1994 and the Chicago Bulls of the NBA from 1967 to 1994 .'],'Both team intervals cover the human question range, 1967 to 1988. The newer team does not replace the older team.','The paragraph directly supports two distinct tenants during the requested period.'),
 ('range_answers_and_returns','/wiki/The_News_Quiz#P371#annotation1','fd2cc23c5915a9eb329f39f1',['The News Quiz was first broadcast in 1977 with Barry Norman as chairman .','Subsequently , it was chaired by Barry Took from 1979 to 1981 , Simon Hoggart from 1981 to 1986 , Barry Took again from 1986 to 1995 , and then again by Simon Hoggart from 1996 until March 2006 .'],'A range question includes several successive hosts. Barry Took also returns after another host. Answer-set size does not imply concurrency.','Use the source dates directly; the question asks about a range, not a single cutoff.'),
 ('precision_mismatch','/wiki/Ruud_Lubbers#P108#annotation1','185e96a97c5886c480bfb116',['from February 1995 until December 2000','serving from 1 January 2001 until 20 February 2005'],'The prose gives month-level university employment dates and day-level refugee-agency dates. The question uses 1995 to 2001.','Two employers appear together, but do not claim university employment continued through all of 2001.'),
 ('uncertain_start','/wiki/Arnolfini_Portrait#P127#annotation0','4f310f468b1764de25da6ef0',['At some point before 1516 it came into the possession of Don Diego de Guevara'],'The sentence bounds a start from above. It does not identify the exact acquisition year.','Use this as a source-text uncertainty example only. The released question also has an unrelated Carlos II gold anchor.'),
 ('approximate_start','/wiki/Jan_Anthonie_Coxie#P937#annotation2','001bfee524e9f42310e972f3',['moved around 1713 to Milan','He would remain active in Lombardia until his death , probably in Milan , in 1720 .'],'The source marks the move date as approximate and the death location as probable.','The source does not define a numeric error radius. Do not assign an invented uncertainty interval.')]
examples=[]
for name,qid,pid,quotes,lesson,scope in items:
 p=ps[pid];q=hqs[qid];spans=[]
 for quote in quotes:
  start=p['text'].index(quote);spans.append({'text':quote,'start_char':start,'end_char_exclusive':start+len(quote)})
 examples.append({'example_id':name,'question_id':qid,'question_text':q['question_text'],'question_date_range':q['date_range'],'published_answer_strings':q['answers'],'gold_answer_spans':q['gold_answer_spans'],'passage_id':pid,'article_url':p['article_url'],'paragraph_index':p['paragraph_index'],'source_paragraph_text':p['text'],'source_spans':spans,'lesson':lesson,'claim_scope':scope})
(R/'source_grounded_examples.json').write_text(json.dumps(examples,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:A[k] for k in ['dev_disjoint_nonempty','human_test']},indent=2));print('examples',len(examples))
