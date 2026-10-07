# Retrieval and certificate results

The ranker was selected on the existing 176-question pilot.
It links public source titles from the visible question.
It retains every corpus unit in a complete ranking.
The selected variant stays frozen for both confirmation tracks.

## Independent front-end scores

| Method | Development span recall | Human span recall |
|---|---:|---:|
| Original global BM25 | 37.84% | 43.90% |
| Original global recency | 52.98% | 52.39% |
| Frozen title residual | 66.30% | 57.39% |
| Title residual with recency | 65.33% | 63.59% |
| Possible support | 66.73% | 57.75% |
| Guaranteed support | 66.62% | 57.87% |

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
| Global BM25 | 413/530 | 77.92% | 108/124 | 87.10% | 2.91 | 2.55 |
| Global BM25 + year | 670/810 | 82.72% | 191/224 | 85.27% | 3.00 | 2.63 |
| Title BM25 | 363/465 | 78.06% | 98/110 | 89.09% | 2.94 | 2.60 |
| Title residual | 313/417 | 75.06% | 79/90 | 87.78% | 2.92 | 2.70 |
| Title BM25 + year | 529/646 | 81.89% | 155/175 | 88.57% | 2.95 | 2.65 |
| Title residual + year | 463/569 | 81.37% | 146/166 | 87.95% | 2.77 | 2.60 |

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

## Reader table reconstruction

`pass4/pipeline/build_reader_results.py` formats complete saved reader scores.
It does not run inference or change the frozen scoring rules.
It requires the primary 60-question cohort and the diagnostic 11-question cohort.
Each scoring directory must contain `summary.json`, `scored_questions.jsonl`, and `reader_parse_audit.jsonl`.

The builder verifies all 600 primary and 110 diagnostic method conditions.
It checks stored means, parse counts, cohort hashes, and frozen scoring code hashes.
It also checks every saved paired EM and F1 interval.
Incomplete inputs fail before any paper artifact is written.

After both frozen scorer runs finish, use their completed directories:

```bash
python pass4/pipeline/build_reader_results.py \
  --primary-score-dir pass4/protocol/reader_primary_scored \
  --diagnostic-score-dir pass4/protocol/reader_diagnostic_scored \
  --output-dir pass4/pipeline
cp pass4/pipeline/reader.tex pass4/paper/tables/reader.tex
cp pass4/pipeline/reader_main.tex pass4/paper/tables/reader_main.tex
```

Both scoring directories contain completed frozen cohorts.
Both generated tables report all ten methods without dropping failed conditions.
`reader_main.tex` reports strict F1 in three columns at the main-text table size.
`reader.tex` adds exact match and parse-failure counts for the appendix.
`paper_reader_results.json` preserves parse counts, condition counts, paired intervals, and answer-change statistics.
`reader_build_manifest.json` records exact input and output hashes.
The builder uses no runtime paths or timestamps.
Isolated reconstruction needs only this generator and the six saved scoring files.
