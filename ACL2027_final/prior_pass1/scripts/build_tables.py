from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'experiments/results'; OUT=ROOT/'paper/tables'; OUT.mkdir(exist_ok=True)
def get(name): return json.loads((R/name).read_text())
def table(name,cols,head,rows,caption,label,wide=False):
 env='table*' if wide else 'table'
 s='\\begin{'+env+'}[t]\n\\centering\n\\small\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+head+' \\\\\n\\midrule\n'
 s+='\n'.join(' & '.join(str(c) for c in row)+' \\\\' for row in rows)
 s+='\n\\bottomrule\n\\end{tabular}\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\end{'+env+'}\n'
 (OUT/(name+'.tex')).write_text(s)
names={'wikidata':'Wikidata','templama':'TempLAMA','realprose':'Wikipedia prose'}
cards={name:get(name+'_results.json') for name in names}
rows=[]
for name in names:
 d=cards[name]; rows.append([names[name],d['n_claims'],d['n_query_keys'],d['results']['historical']['n'],d['results']['current']['n']])
table('datasets','lrrrr',r'Corpus & Claims & \shortstack{Query\\keys} & Past & Current',rows,'Evaluation pools and query counts. Past queries use distinct adjacent source dates. TempLAMA uses complete source answer sets for scoring.','tab:datasets')
prefix={d['dataset']:d for d in get('prefix_summary.json')['cards']}
rows=[]
for name in names:
 d=prefix[name]['event_cutoffs']; rows.append([names[name],d['n_cutoffs'],d['component_mismatch_cutoffs'],d['direct_mismatch_cutoffs']])
table('prefix','lrrr','Corpus & Cutoffs & Closure & Direct',rows,'Cutoffs where future-dated records change past eligibility. Both constructions use the same frozen pair rules. Zero denotes prefix consistency.','tab:prefix')
sens={d['dataset']:d for d in get('sensitivity_summary.json')['cards']}
rows=[]
for name in names:
 d=sens[name]['summary']['all_pairs']; rows.append([names[name],d['n'],d['component_max_affected'],d['direct_max_affected']])
table('sensitivity','lrrr','Corpus & Pairs & Closure & Direct',rows,'Maximum distinct claims affected by deleting one observed positive pair. Counts include valid and erroneous pairs. All event cutoffs are checked.','tab:sensitivity')
s=get('templama_source_set_results.json')['results']
methods=[('bm25','BM25'),('date_top5','Date within top five'),('date_full_pool','Global date'),('exact_group_latest','Exact-group latest'),('component','Text-CC intervals'),('direct_first','Direct certificates')]
rows=[]
for key,label in methods:
 h=s['historical']['methods'][key];c=s['current']['methods'][key]
 rows.append([label,f"{100*h['hit1']:.2f}",f"{100*h['stale_exposure5']:.2f}",f"{100*c['hit1']:.2f}",f"{100*c['stale_exposure5']:.2f}"])
table('retrieval','lrrrr','& \\multicolumn{2}{c}{Historical ($n=447$)} & \\multicolumn{2}{c}{Current ($n=300$)} \\\\ \nMethod & Hit@1 $\\uparrow$ & Stale@5 $\\downarrow$ & Hit@1 $\\uparrow$ & Stale@5 $\\downarrow$',rows,'TempLAMA evidence selection, in percent. Complete yearly answer sets define correct and stale values. All methods use the same 747 claims. Direct certificates preserve the fixed BM25 ranking after filtering. These are retrieval results, not generated-answer scores.','tab:retrieval',True)
engine=json.loads((ROOT/'engine/runs/certificate_tests.json').read_text())
e={d['dataset']:d for d in engine['packaged_data_equivalence']}
rows=[]
for name in names:
 d=e[name];c=cards[name]; exhaustive=c['n_time_ordered_comparisons'];p=d['compiler_stats']['pair_tests']
 rows.append([names[name],f'{exhaustive:,}',f'{p:,}',f'{exhaustive/p:.2f}'])
table('compiler','lrrr','Corpus & All pairs & Compiler & Ratio',rows,'Pair tests for exhaustive and indexed construction. The ratio measures work reduction, not wall-clock speed. Outputs match the exhaustive oracle exactly.','tab:compiler')
legacy=ROOT/'original/results'
rows=[]
for name in ['wikidata','templama','realprose']:
 d=json.loads((legacy/f'qa_{name}_qwen.json').read_text());m=d['current_answer_em'];rows.append([names[name],d['n_questions'],f"{100*m['flat']:.2f}",f"{100*m['lifecycle']:.2f}"])
table('legacy_reader','lrrr','Corpus & $n$ & Flat & Original mask',rows,'Archived Qwen contained-value accuracy, in percent. These runs use the original single-target labels and ranking. They are inherited results, not fresh model evaluations.','tab:legacy-reader')
