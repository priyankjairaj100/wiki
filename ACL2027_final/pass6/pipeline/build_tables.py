#!/usr/bin/env python3
"""Rebuild revision tables from saved result cards without model inference."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def build(output):
 output.mkdir(parents=True,exist_ok=True)
 a=json.loads((ROOT/'pass6/modeling/lazy_baseline_results.json').read_text())
 rows=[]
 for k,v in a['by_budget'].items():
  lazy=v['lazy_oracle_claim_queries'];hybrid=v['hybrid_oracle_claim_queries']
  rows.append(f'{k} & {lazy:,} & {hybrid:,} & {100*(1-hybrid/lazy):.2f}'+r'\\')
 v=a['counts'];lazy=v['lazy_oracle_claim_queries'];hybrid=v['hybrid_oracle_claim_queries']
 rows+= [r'\midrule',r'\textbf{All} & '+f'\\textbf{{{lazy:,}}} & \\textbf{{{hybrid:,}}} & \\textbf{{{100*(1-hybrid/lazy):.2f}}}'+r'\\']
 text=r'''\begin{table}[t]
\centering\small
\begin{tabular}{@{}rrrr@{}}
\toprule
Budget & Lazy exact & Hybrid & Saved (\%)\\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\caption{Exact claim queries on 120 constrained models and 28 windows. Both methods stop after filling the possible context. Each budget covers 3,360 requests. Their contexts and stability decisions agree throughout.}
\label{tab:hybrid}
\end{table}
'''
 (output/'hybrid.tex').write_text(text)
 a=json.loads((ROOT/'pass6/replacement/order_runs/order_summary.json').read_text())
 rows=[]
 for k,v in a['by_k'].items():
  rows.append(f"{k} & {v['queries']} & {v['possible_differs_from_interval']} & {v['control_stable_but_replacement_unstable']} & {v['stable']} "+r'\\')
 text=r'''\begin{table}[t]
\centering
\small
\setlength{\tabcolsep}{5pt}
\begin{tabular}{rrrrr}
\toprule
$k$ & Queries & Changed & Missed & Stable \\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\caption{Source-derived replacement challenge. Changed counts possible contexts differing from interval control. Missed counts replacement-sensitive contexts that interval control marks stable. Stable counts certified contexts with replacement. Both policies enforce known source order.}
\label{tab:replacement}
\end{table}
'''
 (output/'replacement.tex').write_text(text)
 print(json.dumps({'tables':2,'status':'generated'}))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
