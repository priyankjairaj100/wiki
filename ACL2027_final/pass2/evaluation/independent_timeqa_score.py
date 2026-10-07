#!/usr/bin/env python3
"""Independently rescore published passage IDs against original normalized spans."""
import collections,hashlib,json,pathlib
H=pathlib.Path(__file__).resolve().parent;R=H.parents[1]
D=R/'pass2/naturaldata/normalized';B=R/'pass2/baselines/timeqa_results'
read=lambda p:[json.loads(l) for l in p.open()]
passages={r['passage_id']:r for r in read(D/'test_passages.jsonl')}
summary=json.loads((B/'results.json').read_text());report={}
for track,name in [('official_templates','test_annotations.jsonl'),('human_questions','human_test_questions.jsonl')]:
 rows=read(D/name);positive={}
 for r in rows:
  spans=[s for s in r['gold_answer_spans'] if s['answer'].strip() and s['end_char_exclusive']>s['start_char']]
  if spans:positive[r['question_id']]=spans
 preds=read(B/(track+'_predictions.jsonl')); assert len(preds)==len(positive)
 assert len({r['question_id'] for r in preds})==len(preds)
 assert {r['question_id'] for r in preds}==set(positive)
 methods=set(summary['results'][track]['methods']); totals=collections.defaultdict(collections.Counter); comparisons=0
 for row in preds:
  assert set(row['methods'])==methods
  spans=positive[row['question_id']]; gold={s['passage_id'] for s in spans}; assert len(spans)==row['n_gold_spans']
  for s in spans:
   txt=passages[s['passage_id']]['text']; assert txt[s['start_char']:s['end_char_exclusive']]==s['answer']
  for method,pred in row['methods'].items():
   top=pred['top5']; assert len(top)==len(set(top));assert len(top)<=5;assert set(top)<=set(passages)
   scores={'annotated_passage_hit1':int(bool(top) and top[0] in gold),'annotated_passage_hit5':int(bool(set(top)&gold)),'annotated_span_recall5':sum(s['passage_id'] in top for s in spans)/len(spans),'all_annotated_spans5':int(all(s['passage_id'] in top for s in spans))}
   for m,value in scores.items():assert abs(pred[m]-value)<1e-14;totals[method][m]+=value;comparisons+=1
 for method,vals in totals.items():
  for metric,total in vals.items():assert abs(total/len(preds)-summary['results'][track]['methods'][method][metric])<1e-12
 report[track]={'queries':len(preds),'methods':len(methods),'per_query_metric_comparisons':comparisons,'all_scores_match':True,'all_answer_substrings_match':True,'all_prediction_ids_present':True,'prediction_sha256':hashlib.sha256((B/(track+'_predictions.jsonl')).read_bytes()).hexdigest()}
(H/'results/independent_timeqa_score.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
