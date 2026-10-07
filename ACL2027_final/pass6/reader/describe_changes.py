#!/usr/bin/env python3
"""Export every diagnostic answer change with both contexts and fixed answer scores."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.protocol.score_predictions import normalize
HERE=ROOT/'pass6/reader'
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 folder=HERE/'human_diagnostic';pred={r['question_id']:r for r in read(folder/'scored/predictions_with_reader.jsonl')};score={r['question_id']:r for r in read(folder/'scored/scored_questions.jsonl')};queries={r['question_id']:r for r in read(folder/'queries.jsonl')};labels={r['question_id']:r for r in read(ROOT/'pass3/protocol/human_test_confirmation_labels.jsonl')};old={r['question_id']:r for r in read(ROOT/'pass5/protocol/reader_diagnostic_scored/predictions_with_reader.jsonl')}
 assert len(pred)==len(score)==len(queries)==11
 changed=[];categories={'improved':0,'degraded':0,'unchanged_strict_f1':0}
 for q in sorted(pred):
  a=pred[q]['methods']['possible_support'];b=pred[q]['methods']['guaranteed_support']
  if {normalize(x) for x in a['answers']}=={normalize(x) for x in b['answers']}:continue
  modes={}
  for name,item in [('possible_support',a),('guaranteed_support',b)]:
   modes[name]={'answers':item['answers'],'valid':item['reader_parse_ok'],'evidence_indices':item['reader_evidence'],'contexts':item['contexts'],'strict_set_f1':score[q]['methods'][name]['annotated_answer_set_f1'],'exact_match':score[q]['methods'][name]['exact_annotated_answer_set'],'historical_answers':old[q]['methods'][name]['answers'],'historical_valid':old[q]['methods'][name]['reader_parse_ok']}
  delta=modes['guaranteed_support']['strict_set_f1']-modes['possible_support']['strict_set_f1'];category='improved' if delta>0 else 'degraded' if delta<0 else 'unchanged_strict_f1';categories[category]+=1
  changed.append({'question_id':q,'question':queries[q]['question'],'gold_answers':labels[q]['answers'],'guaranteed_minus_possible_strict_f1':delta,'category':category,'modes':modes})
 result={'scope':'Descriptive review of every changed diagnostic answer set. No question or outcome selection. Strict score direction uses the fixed answer labels.','questions':11,'changed_answer_sets':len(changed),'changes_by_score_direction':categories,'changes':changed}
 (args.output/'diagnostic_changed_answers.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 lines=['# Every changed diagnostic answer set','','The table compares guaranteed support with possible support. It includes every changed answer set.','','| Question | Possible answers | Guaranteed answers | Gold answers | Strict F1 change |','|---|---|---|---|---:|']
 def cell(xs):return '; '.join(xs).replace('|','\\|').replace('\n',' ') or '(empty)'
 for r in changed:lines.append('| '+r['question'].replace('|','\\|')+' | '+cell(r['modes']['possible_support']['answers'])+' | '+cell(r['modes']['guaranteed_support']['answers'])+' | '+cell(r['gold_answers'])+' | '+f"{r['guaranteed_minus_possible_strict_f1']*100:+.2f}"+' |')
 (args.output/'diagnostic_changed_answers.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'changed':len(changed),'directions':categories}))
if __name__=='__main__':main()
