# Source-only ranking upgrade

The selected ranking is `title_residual`.
It uses the visible question and public source titles.
It does not read the question article identifier.
Every source unit stays in the complete ranking.

The linker finds the longest exact title token sequence in the question.
Matching articles receive priority.
BM25 then ranks each group after matched title token types leave the query.
This keeps subject names from dominating paragraph relevance.
A question without a title match uses the original global BM25.

This front end is a practical retrieval control.
It is not the paper's novel contribution.
Certificates apply to its fixed ranking exactly as before.

## Pilot selection

All six variants used the existing 176-question pilot and identical source units.
The selector maximized annotated span recall under five units and 768 source words.
No temporal policy ran in this ranking pilot.

| Ranking | Span recall | Parent-passage hit |
|---|---:|---:|
| Global BM25 | 38.64% | 46.02% |
| Global BM25, latest year in top 20 | 54.83% | 59.66% |
| Title priority, BM25 | 40.91% | 48.30% |
| Title priority, residual BM25 | **67.23%** | **70.45%** |
| Title priority, BM25, latest year | 59.09% | 64.77% |
| Title priority, residual BM25, latest year | 65.25% | 69.89% |

The pilot links all 176 questions to their annotated article.
That diagnostic uses labels only after ranking finishes.
Selection improves pilot span recall by 12.41 points over original recency.
The paired article bootstrap interval is [4.86, 20.68] points.
This interval describes calibration data, not independent confirmation.

`FREEZE.json` fixes the chosen variant and code hashes before pass-4 confirmation.
The existing validation and test sets have prior outcome exposure.
Later experiments must call them confirmation tracks.

## API

```python
from pass4.retrieval.ranking import TitleRanker
ranker = TitleRanker(units)
order, lexical_scores = ranker.rank(question)
order, lexical_scores, diagnostics = ranker.rank_with_metadata(question)
```

Each result contains every input unit index exactly once.
Input units must have deterministic source order.
The matched pipeline's `make_units` function supplies that order.
`rank(question, variant="bm25")` supplies the original lexical baseline.
`variant="bm25_latestyear"` supplies the original recency baseline.
`variant="title_residual_latestyear"` supplies recency on the improved common ranking.
All temporal masks should use the default ranking.

## Reproduce the pilot

```bash
python pass4/retrieval/pilot.py --output pass4/retrieval/reproduced_pilot
```

The run stores input hashes, exact contexts, selected unit identifiers, linking diagnostics, question scores, and aggregate statistics.
The feature module accepts source units and question strings only.
Scoring accepts the separately stored labels.

## Lazy context certificates

`lazy_certificate.py` selects and certifies the necessary ranking prefix.
It checks possible support while scanning.
It checks guaranteed support only for selected modeled units.
Fallback units stay eligible without temporal guarantees.
The algorithm returns the possible context, unresolved frontier, and stability decision.

```python
from pass4.retrieval.lazy_certificate import select_lazy
result = select_lazy(order, units, lifecycle_index, (query_start, query_end), k=5)
```

The scan takes O(j) time for j examined candidates.
It uses O(k) output storage and does not build full support masks.
This implements the existing stability theorem efficiently.
It does not change the contribution's novelty claim.

`profile_lazy.py` compares every result with independently computed full masks.
It also checks saved matched-run predictions when supplied.
The timing excludes extraction, compilation, ranking, rendering, and reading.
These are cached CPU microbenchmarks of selection only.

```bash
python pass4/retrieval/profile_lazy.py --units RUN/units.jsonl --claims RUN/claims.jsonl --queries QUERIES.jsonl --predictions RUN/predictions.jsonl --output pass4/retrieval/lazy_confirmation
```

`independent_score.py` provides a separate source-offset scoring implementation.
It verifies exact rendered text, source budgets, and annotated spans.
It reads predictions after retrieval and never invokes the ranker.

## Run one source-only query

```bash
python pass4/retrieval/query.py \
  --units pass4/pipeline/human/units.jsonl \
  --claims pass4/pipeline/human/claims.jsonl \
  --question 'What governmental role did Helen Elizabeth Clark assume from 1989 to Aug 1989?' \
  --ranking title_residual --k 5 --explain > query_result.json
```

The command accepts only source files and a visible question.
It returns selected source contexts, stability, the unresolved frontier, and selection counts.
The output uses the shared 768-word source budget.
The certificate concerns unit selection before word truncation.
An unparsed date window returns the fixed ranking without a temporal certificate.

`--explain` constructs two complete date assignments for an unstable context.
It replays each assignment and includes both resulting source contexts.
The output states whether the rendered contexts differ after truncation.
Compilation, relevance ranking, and explanation costs are separate from selection counts.

The preserved example matches the frozen human run exactly.
Its two complete timelines and context replays also match that run.
No answer labels enter the command or its verification.
See `query_example/input.json`, `output.json`, and `verification.json`.

## Secondary ranking analysis

`SECONDARY_RANKING_PROTOCOL.json` records the post-confirmation declaration.
`secondary_rankings.py` analyzes all six pilot variants without answer labels.
Its shared-order optimization matches all 1,056 pilot ranking outputs exactly.
The outputs retain complete-rank hashes, selected units, frontiers, and work counts.

`RESULTS.md` and `secondary_rankings_table.tex` summarize the recorded findings.
`primary_score_agreement.json` verifies both tracks against the primary scoring implementation.
