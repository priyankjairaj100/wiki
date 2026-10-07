"""Build manuscript tables only from saved, independently scored runs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'pass3/paper/tables'; OUT.mkdir(parents=True,exist_ok=True)
metrics=json.loads((ROOT/'pass3/protocol/independent_validation/summary.json').read_text())['metrics']
methods=[('no_temporal_filter','No temporal filter'),('earliest_completion','Earliest completion'),('midpoint_completion','Midpoint completion'),('latest_completion','Latest completion'),('interval_outer_control','Interval control'),('possible_support','Possible support'),('guaranteed_support','Guaranteed support'),('latest_mentioned_year_top20','Latest-year ranking')]
rows=[]
for key,name in methods:
 x=metrics[key]
 rows.append(f"{name} & {100*x['annotated_span_recall_at_5']:.2f} & {100*x['all_annotated_strings_covered_at_5']:.2f} \\\\")
head=r'''\begin{table}[t]
\centering\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}lrr@{}}
\toprule
Policy & Span recall & All strings\\
\midrule
'''
tail=r'''
\bottomrule
\end{tabular}
\caption{Validation evidence coverage on 2,348 questions. Values are percentages. Every policy shares the same source units and context budget. Latest-year ranking reorders the lexical candidates.}
\label{tab:matched}
\end{table}
'''
(OUT/'matched.tex').write_text(head+'\n'.join(rows)+tail)
m=[json.loads((ROOT/f'pass3/pipeline/{f}/conditioned_mechanism.json').read_text()) for f in ['pilot_final','validation']]
specs=[('All questions','all_questions','n_questions'),('Parsed windows','all_questions','n_parsed'),('Modeled context, parsed','possible_context_has_modeled_unit','n_parsed'),('Certified within this group','possible_context_has_modeled_unit','stable_claim_contexts'),('Unstable within this group','possible_context_has_modeled_unit','completion_sensitive'),('Parsed all-fallback context','possible_context_all_fallback','n_parsed')]
rows=[f"{label} & {m[0][group][key]:,} & {m[1][group][key]:,} \\\\" for label,group,key in specs]
(OUT/'mechanism.tex').write_text(r'''\begin{table}[t]
\centering\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}lrr@{}}
\toprule
Context diagnostic & Pilot & Validation\\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\caption{Exact context decisions under the fixed fallback policy. Modeled-context rows require at least one modeled claim in the possible top-five context.}
\label{tab:mechanism}
\end{table}
''')
print('Rebuilt matched.tex and mechanism.tex from saved JSON.')

budget=json.loads((ROOT/'pass3/pipeline/validation/stable_budget_summary.json').read_text())
b=budget['fixed_modeled_top5_cohort']['budgets']
values=' & '.join(f"{100*b[str(k)]['rate']:.2f}" for k in [1,3,5,10,20])
(OUT/'budget.tex').write_text(r'''\begin{table}[t]
\centering\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}lrrrrr@{}}
\toprule
Budget $k$ & 1 & 3 & 5 & 10 & 20 \\
\midrule
Stable (\%) & '''+values+r''' \\
\bottomrule
\end{tabular}
\caption{Budget sensitivity on the fixed group of 375 parsed validation questions with modeled evidence at $k=5$. The unit-level certificate precedes source-text truncation.}
\label{tab:budget}
\end{table}
''')
print('Rebuilt budget.tex from saved JSON.')
