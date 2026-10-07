#!/usr/bin/env python3
"""Run the frozen source revision on unchanged query cohorts."""
import argparse,collections,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TRACKS={'human':('test','human_test_confirmation'),'validation':('dev','dev_validation')}
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x]
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2)+'\n')
def run(args):
 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
 print('RUN',' '.join(map(str,args)),flush=True);subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,env=env,check=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=[*TRACKS,'freeze','checks'],required=True);a=p.parse_args();os.chdir(ROOT)
 if a.phase=='freeze':
  files=['pass3/extraction/succession_rules.py','pass5/extraction/test_source_adapter.py','pass5/extraction/verify_partitions.py','pass3/extraction/source_adapter.py','pass4/retrieval/profile_lazy.py','pass4/retrieval/lazy_certificate.py','pass5/extraction/source_adapter.py','pass4/extraction/source_adapter.py','pass4/extraction/freeze_manifest.json','pass5/extraction/freeze_manifest.json','pass4/inference/run_jsonl_final.py','pass4/inference/provenance/primary_reader_freeze_final.json','pass5/protocol/score_reader.py','pass5/protocol/audit_confirmation.py','pass5/protocol/audit_answer_changes.py','pass5/protocol/prepare_reader.py','pass5/protocol/finalize_reader.py','pass5/pipeline/run_revision.py']
  args=['pass5/protocol/freeze_configuration.py','--run-id','acl2027-pass5-source-revision-v1','--note','Source-audit revision on the same previously inspected questions. No untouched-test claim.','--output','pass5/protocol/ALGORITHM_FREEZE.json']
  for f in files:args+=['--extra-code',f]
  for track,(source,q) in TRACKS.items():args+=['--source-input',f'pass3/protocol/{source}_source_passages.jsonl','--source-input',f'pass5/extraction/{source}_frozen/claims.jsonl','--query-input',f'pass5/protocol/{q}_queries.jsonl']
  args+=['--query-input','pass5/protocol/reader_primary_queries.jsonl','--query-input','pass4/pipeline/human_diagnostic/queries.jsonl'];run(args);return
 run(['pass5/protocol/verify_freeze.py','--output','pass5/protocol/freeze_verification.json'])
 if a.phase in TRACKS:
  source,queries=TRACKS[a.phase];out=f'pass5/pipeline/{a.phase}'
  args=['pass5/pipeline/run_matched.py','--passages',f'pass3/protocol/{source}_source_passages.jsonl','--queries',f'pass5/protocol/{queries}_queries.jsonl','--claims',f'pass5/extraction/{source}_frozen/claims.jsonl','--config','pass5/protocol/config.json','--output',out,'--track',source.upper()]
  if a.phase=='human':args+=['--reader-queries','pass5/protocol/reader_primary_queries.jsonl']
  run(args)
  run(['pass3/protocol/score_predictions.py','--predictions',out+'/predictions.jsonl','--labels',f'pass3/protocol/{queries}_labels.jsonl','--passages',f'pass3/protocol/{source}_source_passages.jsonl','--config','pass5/protocol/config.json','--output',out+'/scored'])
 else:
  results={}
  for track,(source,queries) in TRACKS.items():
   out=f'pass5/pipeline/{track}'; audit=f'pass5/protocol/{track}_confirmation_audit.json'
   run(['pass5/protocol/audit_confirmation.py','--folder',out,'--passages',f'pass3/protocol/{source}_source_passages.jsonl','--queries',f'pass5/protocol/{queries}_queries.jsonl','--output',audit])
   run(['pass4/retrieval/independent_score.py','--predictions',out+'/predictions.jsonl','--labels',f'pass3/protocol/{queries}_labels.jsonl','--passages',f'pass3/protocol/{source}_source_passages.jsonl','--output',f'pass5/pipeline/independent_{track}'])
   run(['pass4/retrieval/profile_lazy.py','--units',out+'/units.jsonl','--claims',out+'/claims.jsonl','--queries',f'pass5/protocol/{queries}_queries.jsonl','--predictions',out+'/predictions.jsonl','--repetitions','5','--output',f'pass5/pipeline/lazy_{track}'])
   raw=read(ROOT/out/'scored/scored_questions.jsonl');ind=read(ROOT/f'pass5/pipeline/independent_{track}/question_scores.jsonl');by={r['question_id']:r for r in raw};n=0
   for row in ind:
    for m,v in row['scores'].items():
     for k,key in {'span_recall':'annotated_span_recall_at_5','all_spans':'all_annotated_spans_covered_at_5','parent_hit':'parent_passage_hit_at_5','words':'tokens_used','units':'units_used'}.items():
      assert abs(v[k]-by[row['question_id']]['methods'][m][key])<1e-12;n+=1
   mechanism=json.loads((ROOT/out/'mechanism_summary.json').read_text());checked=json.loads((ROOT/audit).read_text());scores=json.loads((ROOT/out/'scored/summary.json').read_text());frontier=collections.Counter(len(r['frontier']) for r in read(ROOT/out/'counterworlds.jsonl'))
   results[track]={'mechanism':mechanism,'audit':checked,'scores':scores,'independent_values_checked':n,'frontier_sizes':dict(frontier),'lazy':json.loads((ROOT/f'pass5/pipeline/lazy_{track}/summary.json').read_text())}
  save(ROOT/'pass5/pipeline/revision_results.json',results)
if __name__=='__main__':main()
