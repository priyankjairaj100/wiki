#!/usr/bin/env python3
"""Verify structured executions and score every frozen reader condition."""
from __future__ import annotations
import argparse,collections,hashlib,itertools,json,os,statistics,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));HERE=ROOT/'pass6/reader';DEST=HERE
from pass4.inference.run_jsonl_final import digest,make_request
from pass3.protocol.parse_reader import parse_response
from pass3.protocol.score_predictions import normalize,paired_bootstrap

def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x]
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def run(args):
 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
 p=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(p.stdout)
 return p.stdout

def verify():
 frozen=json.loads((HERE/'protocol.json').read_text());manifest=json.loads((HERE/'execution_manifest.json').read_text())
 analysis_plan=json.loads((HERE/'analysis_plan.json').read_text())
 for path,value in analysis_plan['files'].items():assert digest(ROOT/path)==value,path
 assert digest(HERE/'run_structured.py')==frozen['runner_sha256']
 assert digest(HERE/'reader_input.jsonl')==manifest['input_sha256']==frozen['input_sha256']
 assert digest(HERE/'reader_output.jsonl')==manifest['output_sha256']
 assert digest(HERE/'protocol.json')==manifest['protocol_sha256']
 for p,h in frozen['source_files'].items():assert digest(ROOT/p)==h,p
 rows=read(HERE/'reader_output.jsonl');inputs={r['id']:r for r in read(HERE/'reader_input.jsonl')}
 assert len(rows)==len({r['id'] for r in rows})==len(inputs)==234
 assert set(inputs)=={r['id'] for r in rows}
 amendment=json.loads((HERE/'scheduling_amendment.json').read_text())
 assert digest(HERE/'scheduling_amendment.json')==manifest['scheduling_amendment_sha256']
 assert digest(HERE/'run_parallel.py')==amendment['parallel_runner_sha256']
 assert amendment['original_protocol_sha256']==manifest['protocol_sha256']
 assert digest(HERE/'initial_output.jsonl')==amendment['initial_output_sha256']
 physical=[]
 for path,value in manifest['physical_batches'].items():
  assert digest(ROOT/path)==value,path
  physical.extend(read(ROOT/path))
 assert len(physical)==234 and len({r['id'] for r in physical})==234
 assert {r['id']:r for r in physical}=={r['id']:r for r in rows}
 expected_flags={'-c':'4096','-t':'4','-tb':'4','--parallel':'1','-b':'512','-ub':'512','--poll':'0','--poll-batch':'0','--seed':'1729','--temp':'0','--n-gpu-layers':'0'}
 for session in manifest['sessions']:
  runtime=json.loads((HERE/('server_'+session+'.json')).read_text());command=runtime['command']
  for flag,value in expected_flags.items():assert command.count(flag)==1 and command[command.index(flag)+1]==value,(session,flag)
  assert runtime['properties']['build_info']=='b11435-43fe9c642'
  assert runtime['protocol_sha256']==manifest['protocol_sha256']
 parsed={}
 for r in rows:
  assert r['request']==make_request(inputs[r['id']],512,1729)
  assert r['request_sha256']==hashlib.sha256(json.dumps(r['request'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
  assert r['model_sha256']==frozen['model_sha256'] and r['model_revision']==frozen['model_revision']
  assert r['response']['system_fingerprint']=='b11435-43fe9c642'
  assert r['response']['choices'][0]['message']['content']==r['generation']
  assert r['response']['choices'][0]['finish_reason']==r['finish_reason']
  parsed[r['id']]=parse_response(r['generation'],len(r['metadata']['contexts']),r['finish_reason'])
  s=r['request']['response_format']['schema'];assert s['properties']['evidence']['items']['enum']==list(range(1,len(r['metadata']['contexts'])+1))
 preflight=json.loads((HERE/'token_preflight.json').read_text());assert preflight['all_fit'] and preflight['max_reserved_tokens']<=4096
 result={'all_checks_passed':True,'requests':len(rows),'valid':sum(x['parse_ok'] for x in parsed.values()),'failures':sum(not x['parse_ok'] for x in parsed.values()),'failure_reasons':dict(collections.Counter(x['parse_failure'] for x in parsed.values() if not x['parse_ok'])),'finish_reasons':dict(collections.Counter(r['finish_reason'] for r in rows)),'tokens':{'mean_prompt':statistics.mean(r['response']['usage']['prompt_tokens'] for r in rows),'mean_completion':statistics.mean(r['response']['usage']['completion_tokens'] for r in rows),'max_completion':max(r['response']['usage']['completion_tokens'] for r in rows),'over_96_completion_tokens':sum(r['response']['usage']['completion_tokens']>96 for r in rows),'max_reserved':preflight['max_reserved_tokens']},'generation_wall_seconds':sum(r['wall_seconds'] for r in rows),'unique_predicted_cardinalities':dict(collections.Counter(len({normalize(a) for a in p['answers'] if normalize(a)}) for p in parsed.values())),'hashes':{'protocol':digest(HERE/'protocol.json'),'inputs':digest(HERE/'reader_input.jsonl'),'outputs':digest(HERE/'reader_output.jsonl'),'analyzer':digest(__file__)}}
 save(DEST/'verification.json',result)
 return result

def analyze_cohort(cohort,role,track):
 folder=HERE/cohort;target=DEST/cohort;target.mkdir(parents=True,exist_ok=True);out=target/'scored'
 log=run(['pass5/protocol/score_reader.py','--jobs',folder/'reader_jobs.jsonl','--outputs',HERE/'reader_output.jsonl','--membership',folder/'reader_memberships.jsonl','--cohort-queries',folder/'queries.jsonl','--predictions','pass5/pipeline/human/predictions.jsonl','--labels','pass3/protocol/human_test_confirmation_labels.jsonl','--passages','pass3/protocol/test_source_passages.jsonl','--config','pass5/protocol/config.json','--output',out,'--track',track]);(target/'score.log').write_text(log)
 log=run(['pass5/protocol/audit_answer_changes.py','--predictions',out/'predictions_with_reader.jsonl','--output',target/'answer_changes.json']);(target/'change_audit.log').write_text(log)
 current={r['question_id']:r for r in read(out/'predictions_with_reader.jsonl')};old={r['question_id']:r for r in read(ROOT/f'pass5/protocol/reader_{role}_scored/predictions_with_reader.jsonl')};scores={r['question_id']:r for r in read(out/'scored_questions.jsonl')};oldscore={r['question_id']:r for r in read(ROOT/f'pass5/protocol/reader_{role}_scored/scored_questions.jsonl')}
 assert set(current)==set(old)==set(scores)==set(oldscore)
 labels={r['question_id']:r for r in read(ROOT/'pass3/protocol/human_test_confirmation_labels.jsonl') if r['question_id'] in current}
 methods=sorted(next(iter(current.values()))['methods'])
 # Independent set arithmetic checks every scored answer condition.
 for q,prediction in current.items():
  gold={normalize(x) for x in labels[q]['answers'] if normalize(x)}
  assert gold
  for method,item in prediction['methods'].items():
   guess={normalize(x) for x in item['answers'] if normalize(x)}
   exact=float(guess==gold);f1=2*len(guess & gold)/(len(guess)+len(gold))
   observed=scores[q]['methods'][method]
   assert observed['exact_annotated_answer_set']==exact,(q,method,'exact')
   assert abs(observed['annotated_answer_set_f1']-f1)<1e-12,(q,method,'strict_f1')
   assert observed['predicted_answer_count']==len(guess),(q,method,'cardinality')
 targets={q:len({normalize(x) for x in labels[q]['answers'] if normalize(x)}) for q in current}
 cardinality={};decoding={};detailed=[]
 for method in methods:
  groups={}
  for q,r in current.items():
   n=targets[q];p=r['methods'][method];s=scores[q]['methods'][method]
   g=groups.setdefault(str(n),{'questions':0,'valid':0,'predicted_cardinalities':collections.Counter(),'exact':0,'strict_f1_sum':0,'soft_f1_sum':0,'partial_strict_matches':0})
   g['questions']+=1;g['valid']+=p['reader_parse_ok'];g['predicted_cardinalities'][s['predicted_answer_count']]+=1;g['exact']+=s['exact_annotated_answer_set'];g['strict_f1_sum']+=s['annotated_answer_set_f1'];g['soft_f1_sum']+=s['annotated_answer_soft_f1'];g['partial_strict_matches']+=0<s['annotated_answer_set_f1']<1
   detailed.append({'question_id':q,'method':method,'target_cardinality':n,'predicted_cardinality':s['predicted_answer_count'],'target_answers':labels[q]['answers'],'predicted_answers':p['answers'],'valid':p['reader_parse_ok'],'exact_match':s['exact_annotated_answer_set'],'strict_set_f1':s['annotated_answer_set_f1'],'soft_set_f1':s['annotated_answer_soft_f1']})
  for g in groups.values():
   g['predicted_cardinalities']=dict(g['predicted_cardinalities']);g['exact_percent']=100*g.pop('exact')/g['questions'];g['strict_f1_percent']=100*g.pop('strict_f1_sum')/g['questions'];g['soft_f1_percent']=100*g.pop('soft_f1_sum')/g['questions']
  cardinality[method]=groups
  paired=[{'article_path':scores[q]['article_path'],'methods':{'new':scores[q]['methods'][method],'old':oldscore[q]['methods'][method]}} for q in sorted(current)]
  decoding[method]={'old_valid':sum(old[q]['methods'][method]['reader_parse_ok'] for q in current),'new_valid':sum(current[q]['methods'][method]['reader_parse_ok'] for q in current),'answer_set_changes':sum({normalize(x) for x in old[q]['methods'][method]['answers']}!={normalize(x) for x in current[q]['methods'][method]['answers']} for q in current),'old_new_both_valid':sum(old[q]['methods'][method]['reader_parse_ok'] and current[q]['methods'][method]['reader_parse_ok'] for q in current),'new_minus_old':{metric:paired_bootstrap(paired,'new','old',metric) for metric in ['exact_annotated_answer_set','annotated_answer_set_f1']}}
 structural={}
 for a,b in itertools.combinations(methods,2):
  members={(r['question_id'],r['method']):r for r in read(folder/'reader_memberships.jsonl')}
  structural[a+'__'+b]={'questions':len(current),'different_requests':sum(members[q,a]['job_id']!=members[q,b]['job_id'] for q in current),'different_context_signatures':sum(members[q,a]['context_signature']!=members[q,b]['context_signature'] for q in current)}
 result={'cohort':cohort,'questions':len(current),'target_cardinality_questions':dict(collections.Counter(targets.values())),'by_method_and_target_cardinality':cardinality,'new_versus_historical_decoding':decoding,'structural_context_changes':structural,'inputs':{name:digest(path) for name,path in [('new_scored_questions',out/'scored_questions.jsonl'),('new_predictions',out/'predictions_with_reader.jsonl'),('old_scored_questions',ROOT/f'pass5/protocol/reader_{role}_scored/scored_questions.jsonl'),('labels',ROOT/'pass3/protocol/human_test_confirmation_labels.jsonl')]}}
 save(target/'cardinality_and_replication.json',result)
 (target/'answer_cardinality_rows.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in detailed))
 return {'scores':json.loads((out/'summary.json').read_text()),'cardinality':result,'changes':json.loads((target/'answer_changes.json').read_text())}

def report(result,verified):
 methods=[('original_bm25','Original BM25'),('original_bm25_latestyear','Original + year'),('no_temporal_filter','Title-aware'),('earliest_completion','Earliest completion'),('midpoint_completion','Midpoint completion'),('latest_completion','Latest completion'),('interval_outer_control','Interval control'),('possible_support','Possible support'),('guaranteed_support','Guaranteed support'),('latest_mentioned_year_top20','Title-aware + year')]
 text=['# Structured reader replication','',f"All {verified['requests']} fixed requests completed. The unchanged parser accepted {verified['valid']}. These requests cover 710 method conditions.",'','The study preserves all question text and source excerpts. It changes the output interface and completion budget.','The same 3B model uses schema constraints and a 512-token budget. Valid citation numbers are part of each schema.','The schema cannot establish whether an answer follows from its cited excerpt.','','| Method | Primary EM | Primary strict F1 | Diagnostic EM | Diagnostic strict F1 |','|---|---:|---:|---:|---:|']
 latex=[r'\begin{table}[t]',r'\centering\footnotesize',r'\setlength{\tabcolsep}{3pt}',r'\begin{tabular}{@{}lrrrr@{}}',r'\toprule',r' & \multicolumn{2}{c}{Primary} & \multicolumn{2}{c}{Diagnostic}\\',r'Method & EM & F1 & EM & F1\\',r'\midrule']
 for m,label in methods:
  vals=[100*result[r]['scores']['metrics'][m][metric] for r in ['primary','diagnostic'] for metric in ['exact_annotated_answer_set','annotated_answer_set_f1']]
  text.append('| '+label+' | '+' | '.join(f'{v:.2f}' for v in vals)+' |');latex.append(label+' & '+' & '.join(f'{v:.2f}' for v in vals)+r'\\')
 text+=['','The primary cohort has 60 questions. The diagnostic has eleven questions selected before this replication.','The diagnostic selection used earlier context differences. It is not a random test sample.','']
 for role in ['primary','diagnostic']:
  r=result[role];s=r['scores'];c=r['cardinality'];changes=r['changes']['contrasts']['guaranteed_support__possible_support'];struct=c['structural_context_changes']['guaranteed_support__possible_support']
  text += [f"## {role.title()} cohort",'',f"Parser failures: {s['parse_failures_unique']}/{s['n_unique_generations_used']} unique requests.",f"Target answer cardinality: `{json.dumps(c['target_cardinality_questions'],sort_keys=True)}`.",f"Possible and guaranteed support use different requests for {struct['different_requests']}/{s['n_questions']} questions.",f"These policies change {changes['all_answer_set_changes']}/{s['n_questions']} answer sets.",f"All changed answers with valid outputs: {changes['answer_changes_with_both_outputs_parsed']}.",'']
 latex += [r'\bottomrule',r'\end{tabular}',r'\caption{Structured reader replication on unchanged contexts. EM and strict answer-set F1 are percentages. The primary sample has 60 questions. The historical diagnostic has eleven. The unchanged parser accepts '+str(verified['valid'])+r' of '+str(verified['requests'])+r' requests.}',r'\label{tab:structured_reader}',r'\end{table}','']
 (DEST/'RESULTS.md').write_text('\n'.join(text)+'\n');(DEST/'reader_structured.tex').write_text('\n'.join(latex))
 save(DEST/'summary.json',{'verification':verified,'cohorts':result})
 def portable(x):
  if isinstance(x,dict):return {k:portable(v) for k,v in x.items() if k not in {'input_sha256','inputs','hashes'}}
  if isinstance(x,list):return [portable(v) for v in x]
  return x
 save(DEST/'result_card.json',portable({'verification':verified,'cohorts':result}))

def main():
 global DEST
 p=argparse.ArgumentParser();p.add_argument('--cohort',choices=['human','human_diagnostic']);p.add_argument('--output',type=Path,default=HERE);args=p.parse_args();DEST=args.output.resolve();DEST.mkdir(parents=True,exist_ok=True)
 if args.cohort:
  role='primary' if args.cohort=='human' else 'diagnostic';track='human_confirmation' if role=='primary' else 'context_sensitive_diagnostic';r=analyze_cohort(args.cohort,role,track);print(json.dumps({'cohort':role,'parse_failures':r['scores']['parse_failures_unique'],'metrics':r['scores']['metrics']},indent=2));return
 verified=verify();result={}
 for c,r,t in [('human','primary','human_confirmation'),('human_diagnostic','diagnostic','context_sensitive_diagnostic')]:result[r]=analyze_cohort(c,r,t)
 report(result,verified);print(json.dumps({'verification':verified,'cohorts':{r:{'questions':v['scores']['n_questions'],'failures':v['scores']['parse_failures_unique']} for r,v in result.items()}},indent=2))
if __name__=='__main__':main()
