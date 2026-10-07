"""Rebuild pass4 paper tables from frozen runs and scoring outputs."""
from pathlib import Path
import json,hashlib,sys,collections
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.protocol.score_predictions import read,paired_bootstrap
OUT=ROOT/'pass4/paper/tables'
METHODS=[('original_bm25','Original BM25'),('original_bm25_latestyear','Original BM25 + latest year'),('no_temporal_filter','Title-aware ranking'),('earliest_completion',r'\quad + earliest completion'),('midpoint_completion',r'\quad + midpoint completion'),('latest_completion',r'\quad + latest completion'),('interval_outer_control',r'\quad + interval control'),('possible_support',r'\quad + possible support'),('guaranteed_support',r'\quad + guaranteed support'),('latest_mentioned_year_top20','Title-aware + latest year')]
def load(p):return json.loads((ROOT/p).read_text())
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 summaries={t:load(f'pass4/pipeline/{t}/scored/summary.json') for t in ['validation','human']}
 audits={t:load(f'pass4/protocol/{t if t=="human" else "validation"}_confirmation_audit.json') for t in summaries}
 values={t:{m:d['annotated_span_recall_at_5'] for m,d in s['metrics'].items()} for t,s in summaries.items()}
 rows=[]
 for m,label in METHODS:
  vs=[]
  for t in values:
   val=100*values[t][m];txt=f'{val:.2f}'
   if values[t][m]==max(values[t].values()):txt=r'\textbf{'+txt+'}'
   vs.append(txt)
  rows.append(label+' & '+' & '.join(vs)+r'\\')
 table=r'''\begin{table}[t]
\centering\small
\begin{tabular}{@{}lrr@{}}
\toprule
Method & Template & Human\\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\caption{Mean question-level annotated span recall (\%) within five excerpts and 768 source-text words. Temporal controls share the title-aware ranking. Latest-year controls change only ranking.}
\label{tab:matched}
\end{table}
'''
 (OUT/'matched.tex').write_text(table)
 rows=[]
 specs=[('Questions',lambda a:a['counts']['queries']),('Parsed query periods',lambda a:a['counts']['parsed']),('Contexts with modeled evidence',lambda a:a['counts']['parsed_modeled']),('Certified stable contexts',lambda a:a['counts']['parsed_modeled_stable']),('Unstable contexts',lambda a:a['counts']['parsed_modeled_unstable'])]
 for name,f in specs:rows.append(name+' & '+' & '.join(f'{f(a):,}' for a in audits.values())+r'\\')
 rows.append('Stable within modeled group & '+' & '.join(f"{100*a['counts']['parsed_modeled_stable']/a['counts']['parsed_modeled']:.2f}\\%" for a in audits.values())+r'\\')
 (OUT/'mechanism.tex').write_text(r'''\begin{table}[t]
\centering\small
\begin{tabular}{@{}lrr@{}}
\toprule
Certificate cohort & Template & Human\\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\caption{Stability for the frozen title-aware ranking. The modeled group contains parsed questions with at least one modeled excerpt in the possible context. All-fallback contexts have a separate denominator.}
\label{tab:mechanism}
\end{table}
''')
 rows=[]
 for t,name in [('validation','Template'),('human','Human')]:
  a=audits[t];n=a['counts']['parsed_modeled'];rows.append(f'{name} ($n={n}$) & '+' & '.join(f"{100*a['stable_at_budgets_fixed_modeled_cohort'][str(k)]['stable']/n:.1f}" for k in [1,3,5,10,20])+r'\\')
 (OUT/'budget.tex').write_text(r'''\begin{table}[t]
\centering\small
\begin{tabular}{@{}lrrrrr@{}}
\toprule
Excerpt budget $k$ & 1 & 3 & 5 & 10 & 20\\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\caption{Stable contexts (\%) as the unit budget grows. Each row retains the same modeled cohort selected at $k=5$. Selection precedes word truncation.}
\label{tab:budget}
\end{table}
''')
 contrasts={}
 for t in summaries:
  scored=read(ROOT/f'pass4/pipeline/{t}/scored/scored_questions.jsonl')
  contrasts[t]={}
  for a,b in [('no_temporal_filter','original_bm25_latestyear'),('latest_mentioned_year_top20','original_bm25_latestyear')]:
   contrasts[t][a+'__'+b]=paired_bootstrap(scored,a,b,'annotated_span_recall_at_5')
 result={'span_recall':values,'certificate_audits':audits,'frontend_contrasts':contrasts,'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/f'pass4/pipeline/{t}/scored/summary.json' for t in summaries]}}
 (ROOT/'pass4/pipeline/paper_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'frontend_contrasts':contrasts},indent=2))
if __name__=='__main__':main()
