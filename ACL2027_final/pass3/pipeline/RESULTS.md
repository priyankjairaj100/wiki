# Pass 3 pipeline results

The accepted runs are `pilot_final/` and `validation/`.
Earlier pilot folders contain superseded parser debugging runs.

## Source pool

- 32,332 source paragraphs from 740 articles.
- 32,976 disjoint source units.
- 481 modeled source claims, or 1.46% of units.
- 221 explicit end events.
- No accepted directed replacement pairs.
- No rejected lifecycle records after the final source adapter.

Every substantive source character remains available in the unit pool.
Fallback units retain their unresolved status under every method.
All shown contexts meet the five-unit and 768-token budgets.
The exact source-offset audit passes for every method context.

## Pilot

The pilot includes 176 queries from 50 articles.
The parser resolves 173 query windows.
Nine queries have different completion contexts.
Possible support changes 24 contexts relative to unfiltered retrieval.
Possible support matches the outer interval control in every context.

Possible contexts contain modeled units for 32 parsed queries.
The certificate resolves 23 of these contexts, or 71.9%.
The global certificate count is 164 of 173 parsed queries.
This global count includes 141 contexts with only fallback text.

Annotated span recall is 38.92% for possible support and the outer interval control.
Unfiltered retrieval reaches 38.64%.
Earliest completion, midpoint completion, and guaranteed support reach 39.49%.
The latest-year control reaches 54.83%.

The primary reader cohort contains 24 queries selected by a seeded hash.
Fifty-two unique prompts cover eight methods.
The separate mechanism cohort contains all nine queries with different completion contexts.
It adds 22 prompts and reuses six primary prompts.
Reader results are stored and scored outside this directory.

## Frozen validation

The validation run contains 2,348 queries from 644 articles.
The protocol excludes articles inspected during source calibration.
The parser resolves 2,296 query windows.
The certificate resolves 2,227 contexts.
Sixty-nine contexts remain ambiguous.

Possible contexts contain modeled evidence for 375 parsed queries.
The certificate resolves 306 of these contexts, or 81.6%.
Among 543 parsed queries with modeled lexical top-five evidence, 474 contexts are stable.
The corresponding rate is 87.29%.

Possible support changes 218 contexts relative to unfiltered retrieval.
It matches the outer interval control in every context.
Independent scoring reports annotated string recall of 39.07% for both methods.
Guaranteed support reaches 39.15%.
The latest-year control reaches 53.51%.
These retrieval results do not establish an answer-quality advantage.

## Constructive ambiguity

Every ambiguous validation query has two stored timelines with different contexts.
All 138 timelines respect the extracted date bounds.
All 138 timelines replay exactly through the direct evaluator.
Each timeline assigns 702 modeled events.
All 69 pairs also produce different rendered source excerpts.

The refinement frontier contains one claim for 67 queries.
It contains two claims for the other two queries.
Retirement at the query start explains 47 exclusions.
A start after the query end explains 22 exclusions.

These timelines demonstrate uncertainty under the stated event model.
They do not claim to recover observed historical dates.
The source records and complete assignments remain in `validation/counterworlds.jsonl`.

## Reproduction checks

A later implementation correction sorts BM25 query tokens before accumulation.
Selection also stops after five accepted units.
These changes reproduce all 20,192 stored method contexts exactly.
The original code remains in `run_matched_v1.py`.
Each accepted run preserves its configuration and input hashes.
The deterministic equivalence reports remain with the accepted runs.

For release, include both accepted run folders and the source scripts.
The earlier `pilot/` and `pilot_frozen/` folders can remain outside the release.

## Stable budget diagnostic

This diagnostic keeps the 375-query modeled-context cohort fixed.
It varies the source-unit budget before token clipping.

| Source units | Stable contexts | Stable rate |
|---:|---:|---:|
| 1 | 346/375 | 92.3% |
| 3 | 320/375 | 85.3% |
| 5 | 306/375 | 81.6% |
| 10 | 304/375 | 81.1% |
| 20 | 299/375 | 79.7% |

The first unresolved rank exactly predicts context stability at every tested budget.
All 11,480 direct context comparisons agree.
The five-unit decisions match all 2,296 original parsed-query certificates.
The run requires no model inference and reads no answer labels.
