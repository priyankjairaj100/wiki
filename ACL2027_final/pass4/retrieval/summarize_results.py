"""Build compact presentation tables from the recorded retrieval runs."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
names={'bm25':'Global BM25','bm25_latestyear':'Global BM25 + year','title_bm25':'Title BM25','title_residual':'Title residual','title_bm25_latestyear':'Title BM25 + year','title_residual_latestyear':'Title residual + year'}
s={track:json.loads((HERE/f'secondary_{track}/summary.json').read_text()) for track in ['validation','human']}
rows=[];tex=[]
for variant,name in names.items():
 d=s['validation']['variants'][variant]['own_modeled_contexts'];h=s['human']['variants'][variant]['own_modeled_contexts']
 rows.append(f"| {name} | {d['stable']}/{d['queries']} | {100*d['stable']/d['queries']:.2f}% | {h['stable']}/{h['queries']} | {100*h['stable']/h['queries']:.2f}% | {d['mean_support_checks']:.2f} | {h['mean_support_checks']:.2f} |")
 tex.append(f"{name} & {d['stable']}/{d['queries']} & {h['stable']}/{h['queries']} & {d['mean_support_checks']:.2f} & {h['mean_support_checks']:.2f} \\\\")
(HERE/'secondary_rankings_table.tex').write_text('\\begin{tabular}{lrrrr}\n\\toprule\nRanking & Dev stable/modeled & Human stable/modeled & Dev checks & Human checks \\\\\n\\midrule\n'+'\n'.join(tex)+'\n\\bottomrule\n\\end{tabular}\n')
text='''# Retrieval and certificate results

The ranker was selected on the existing 176-question pilot.
It links public source titles from the visible question.
It retains every corpus unit in a complete ranking.
The selected variant stays frozen for both confirmation tracks.

## Independent front-end scores

| Method | Development span recall | Human span recall |
|---|---:|---:|
'''
a={track:json.loads((HERE/f'independent_{track}/summary.json').read_text()) for track in ['validation','human']}
for method,name in [('original_bm25','Original global BM25'),('original_bm25_latestyear','Original global recency'),('no_temporal_filter','Frozen title residual'),('latest_mentioned_year_top20','Title residual with recency'),('possible_support','Possible support'),('guaranteed_support','Guaranteed support')]:
 text+=f"| {name} | {a['validation']['metrics'][method]['span_recall']*100:.2f}% | {a['human']['metrics'][method]['span_recall']*100:.2f}% |\n"
text+='''
These gains belong to the retrieval front end.
The temporal contribution is exact context certification and constructive explanation.
The independent scorer checks source offsets and actual rendered text.
Its span scores match the primary scorer for all ten methods.

## Secondary ranking portability

This analysis was declared after human confirmation scores were observed.
It evaluates all six prespecified variants and reads no answer labels.
Each row uses the same parsed-query cohort within its track.
The table conditions stability and work on each ranking's modeled contexts.
These contexts contain at least one modeled claim; fallback text can remain.

| Ranking | Dev stable/modeled | Dev stability | Human stable/modeled | Human stability | Dev checks | Human checks |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'\n'
text+='''
The JSON summaries also report fixed main-ranking and union cohorts.
Those cohorts hold query membership fixed across rankings.
Main modeled cohorts contain 417 development queries and 90 human queries.
The union cohorts contain 860 development queries and 249 human queries.

## Lazy execution

All 3,109 parsed confirmation queries match the stored full-mask decisions.
The remaining 69 questions have unparsed query windows.
They receive no temporal certificate.

For modeled contexts, development queries need 2.92 certificate checks on average.
Human queries need 2.70 checks.
Full masks need 1,584 and 1,488 checks, respectively.
Both modeled cohorts therefore reduce certificate checks by over 99.8%.
Ranking, compilation, rendering, and reading fall outside these counts.

The shared CPU timing measurements appear in the run summaries.
Support-check counts are the primary efficiency evidence.
`RUNTIME_NOTE.md` records the concurrent workload.

## Reusable query interface

`query.py` returns actual source excerpts, a stability decision, and the unresolved frontier.
Its optional explanation supplies two complete timelines and replays their contexts.
`query_example/` preserves one natural human question and its verified output.
'''
(HERE/'RESULTS.md').write_text(text)
print(HERE/'RESULTS.md')
