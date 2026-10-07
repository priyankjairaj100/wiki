#!/usr/bin/env python3
"""Build paper reader tables from the complete, portable result card."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ALL=[('original_bm25','Original BM25'),('original_bm25_latestyear','Original + year'),('no_temporal_filter','Title-aware'),('earliest_completion','Earliest completion'),('midpoint_completion','Midpoint completion'),('latest_completion','Latest completion'),('interval_outer_control','Interval control'),('possible_support','Possible support'),('guaranteed_support','Guaranteed support'),('latest_mentioned_year_top20','Title-aware + year')]
MAIN=[('original_bm25_latestyear','Original + year'),('no_temporal_filter','Title-aware'),('latest_mentioned_year_top20','Title-aware + year'),('possible_support','Possible support'),('guaranteed_support','Guaranteed support')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def contrast(scores,left,right):
 for group in ['prespecified_frontend_intervals','reader_pairwise_article_intervals']:
  values=scores.get(group,{})
  if left+'__'+right in values:return values[left+'__'+right]['annotated_answer_set_f1']
  if right+'__'+left in values:
   row=values[right+'__'+left]['annotated_answer_set_f1'];return {**row,'delta':-row['delta'],'ci95':[-row['ci95'][1],-row['ci95'][0]]}
 raise KeyError((left,right))
def main():
 p=argparse.ArgumentParser();p.add_argument('--result-card',type=Path,default=HERE/'result_card.json');p.add_argument('--output',type=Path,default=HERE/'paper');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 card=json.loads(args.result_card.read_text());verify=card['verification'];assert verify['all_checks_passed'] and verify['requests']==234
 cohorts=card['cohorts'];assert cohorts['primary']['scores']['n_questions']==60 and cohorts['diagnostic']['scores']['n_questions']==11
 assert cohorts['primary']['scores']['n_logical_conditions']==600 and cohorts['diagnostic']['scores']['n_logical_conditions']==110
 def value(role,method,metric):return 100*cohorts[role]['scores']['metrics'][method][metric]
 def begin(cols):return [r'\begin{table}[t]',r'\centering\small',r'\begin{tabular}{@{}'+cols+r'@{}}',r'\toprule']
 maintex=begin('lrr')+[r'Method & Primary & Diagnostic\\',r'\midrule']
 for method,label in MAIN:maintex.append(label+' & '+' & '.join(f"{value(r,method,'annotated_answer_set_f1'):.2f}" for r in ['primary','diagnostic'])+r'\\')
 caption=(r'Strict answer-set F1 (\%). Temporal policies use title-aware BM25 without the year bonus.')
 maintex += [r'\bottomrule',r'\end{tabular}',r'\caption{'+caption+'}',r'\label{tab:reader_main}',r'\end{table}','']
 appendix=begin('lrrrrr')+[r' & \multicolumn{2}{c}{Primary} & \multicolumn{2}{c}{Diagnostic} & \\',r'Method & EM & F1 & EM & F1 & Valid\\',r'\midrule']
 for method,label in ALL:
  vals=[value(role,method,metric) for role in ['primary','diagnostic'] for metric in ['exact_annotated_answer_set','annotated_answer_set_f1']]
  invalid=sum(cohorts[role]['scores']['parse_failures_by_method'][method] for role in ['primary','diagnostic'])
  appendix.append(label+' & '+' & '.join(f'{v:.2f}' for v in vals)+f' & {71-invalid}/71'+r'\\')
 appendix += [r'\bottomrule',r'\end{tabular}',r'\caption{Complete structured reader results. EM and strict answer-set F1 are percentages. Valid counts use question-method conditions. All conditions remain in the denominators.}',r'\label{tab:reader-structured}',r'\end{table}','']
 # The appendix table is wide and should use a double-column float.
 appendix[0]=r'\begin{table*}[t]';appendix[-2]=r'\end{table*}'
 primary=cohorts['primary'];diagnostic=cohorts['diagnostic'];change=diagnostic['changes']['contrasts']['guaranteed_support__possible_support'];structure=diagnostic['cardinality']['structural_context_changes']['guaranteed_support__possible_support']
 d=contrast(diagnostic['scores'],'guaranteed_support','possible_support');front=contrast(primary['scores'],'no_temporal_filter','original_bm25_latestyear')
 values={'primary_requests':primary['scores']['n_unique_generations_used'],'diagnostic_requests':diagnostic['scores']['n_unique_generations_used'],'valid_requests':verify['valid'],'unique_requests':234,'primary_possible_guaranteed_different_contexts':primary['cardinality']['structural_context_changes']['guaranteed_support__possible_support']['different_requests'],'diagnostic_possible_guaranteed_different_contexts':structure['different_requests'],'diagnostic_answer_changes':change['all_answer_set_changes'],'diagnostic_changed_both_valid':change['answer_changes_with_both_outputs_parsed'],'diagnostic_guaranteed_minus_possible_f1':d,'primary_title_minus_original_year_f1':front,'primary_target_cardinalities':primary['cardinality']['target_cardinality_questions'],'metric_rows':{role:{m:{'em':value(role,m,'exact_annotated_answer_set'),'f1':value(role,m,'annotated_answer_set_f1')} for m,_ in ALL} for role in ['primary','diagnostic']}}
 assert values['primary_possible_guaranteed_different_contexts']==0
 assert values['primary_target_cardinalities']=={'1':56,'2':4}
 valid_change_text=(f"All {change['answer_changes_with_both_outputs_parsed']} changes have valid responses. " if change['answer_changes_with_both_outputs_parsed']==change['all_answer_set_changes'] else f"Of these, {change['answer_changes_with_both_outputs_parsed']} changes have valid responses. ")
 words=(
  'We test answer sensitivity with Qwen2.5-3B and the same 4-bit weights. '
  'Every question and source excerpt remains unchanged. '
  'Schema constraints enforce JSON and valid citation indices. '
  'The completion budget increases to 512 tokens. '
  f"The fixed parser accepts {verify['valid']} of 234 outputs. "
  r'Table~\ref{tab:reader_main} reports both complete cohorts. '
  'Possible and guaranteed support use identical contexts for all 60 primary questions. '
  'Their answers therefore coincide under the fixed decoder. '
  f"{structure['different_requests']} of eleven historical diagnostic questions have different contexts, producing {change['all_answer_set_changes']} changed answer sets. "
  + valid_change_text +
  f"Guaranteed minus possible F1 is {100*d['delta']:+.2f} points, with interval [{100*d['ci95'][0]:.2f}, {100*d['ci95'][1]:.2f}]. "
  'The primary sample contains 56 single-answer questions and four two-answer questions. '
  'The earlier decoder recorded no partial strict matches in the primary sample. '
  'This explains its equal EM and F1 values.'
 )
 for name,text in [('reader_main.tex','\n'.join(maintex)),('reader_appendix.tex','\n'.join(appendix)),('reader_results_draft.tex',words+'\n')]: (args.output/name).write_text(text)
 (args.output/'reader_numbers.json').write_text(json.dumps(values,indent=2)+'\n')
 manifest={'result_card_sha256':sha(args.result_card),'builder_sha256':sha(__file__),'draft_word_count':len(words.split()),'outputs':{name:sha(args.output/name) for name in ['reader_main.tex','reader_appendix.tex','reader_results_draft.tex','reader_numbers.json']}}
 (args.output/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
