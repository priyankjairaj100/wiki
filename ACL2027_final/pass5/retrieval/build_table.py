"""Render the complete six-ranking result table from saved summaries."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
NAMES=[('bm25','Global BM25'),('bm25_latestyear','Global BM25 + year'),('title_bm25','Title BM25'),('title_residual','Title-aware'),('title_bm25_latestyear','Title BM25 + year'),('title_residual_latestyear','Title-aware + year')]
def main():
 s={t:json.loads((ROOT/f'pass5/retrieval/secondary_{t}/summary.json').read_text()) for t in ['validation','human']}
 rows=[r'\begin{table*}[t]',r'\centering\small',r'\begin{tabular}{lrrrr}',r'\toprule',r'Ranking & Template & Human & Template & Human \\',r' & stable/modeled & stable/modeled & tests & tests \\',r'\midrule']
 for key,name in NAMES:
  dev=s['validation']['variants'][key]['own_modeled_contexts'];hum=s['human']['variants'][key]['own_modeled_contexts']
  rows.append(f"{name} & {dev['stable']}/{dev['queries']} & {hum['stable']}/{hum['queries']} & {dev['mean_support_checks']:.2f} & {hum['mean_support_checks']:.2f} "+r'\\')
 rows += [r'\bottomrule',r'\end{tabular}',r'\caption{Secondary certificate analysis across all six prespecified rankings. Each stability denominator contains modeled evidence under that ranking. Tests count temporal predicate calls within that modeled cohort.}',r'\label{tab:ranking-portability}',r'\end{table*}']
 p=ROOT/'pass5/paper/tables/ranking_portability.tex';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(rows)+'\n')
if __name__=='__main__':main()
