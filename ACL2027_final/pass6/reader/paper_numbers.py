#!/usr/bin/env python3
"""Print the pre-existing paper contrasts from complete structured reader results."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.protocol.score_predictions import paired_bootstrap
HERE=ROOT/'pass6/reader'
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x]
def main():
 summary=json.loads((HERE/'summary.json').read_text());result={'verification':summary['verification'],'cohorts':{}}
 for role,cohort in [('primary','human'),('diagnostic','human_diagnostic')]:
  c=summary['cohorts'][role];s=c['scores'];rows=read(HERE/cohort/'scored/scored_questions.jsonl')
  contrasts={}
  for a,b in [('no_temporal_filter','original_bm25_latestyear'),('guaranteed_support','possible_support'),('latest_mentioned_year_top20','no_temporal_filter')]:
   raw=paired_bootstrap(rows,a,b,'annotated_answer_set_f1');contrasts[a+'__'+b]={'delta_pp':100*raw['delta'],'ci95_pp':[100*x for x in raw['ci95']],'article_clusters':raw['article_clusters'],'repetitions':raw['repetitions'],'seed':raw['seed']}
  result['cohorts'][role]={'requests':s['n_unique_generations_used'],'failures':s['parse_failures_unique'],'questions':s['n_questions'],'f1_percent':{m:100*v['annotated_answer_set_f1'] for m,v in s['metrics'].items()},'contrasts':contrasts,'possible_guaranteed_changes':c['changes']['contrasts']['guaranteed_support__possible_support'],'target_cardinalities':c['cardinality']['target_cardinality_questions'],'partial_strict_matches_by_method':{m:sum(g['partial_strict_matches'] for g in groups.values()) for m,groups in c['cardinality']['by_method_and_target_cardinality'].items()}}
 (HERE/'paper_numbers.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
