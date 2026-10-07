# Revised retrieval results

The source adapter was frozen before these runs.
The ranking, questions, and budgets remain fixed from pass 4.
The source revision uses previously inspected benchmark tracks.

## Complete checks

Independent replay checks all 31,780 method contexts.
It verifies all 15,545 context comparisons across five budgets.
It checks all 128 complete event assignments.
Every one of the 64 assignment pairs changes the rendered evidence.
Independent scoring reproduces all 158,900 per-question metric values.
The lazy selector matches full masks on all 3,109 parsed questions.

| Track | Questions | Parsed | Modeled contexts | Stable | Fallback contexts |
|---|---:|---:|---:|---:|---:|
| validation | 2348 | 2296 | 243 | 189 | 2053 |
| human | 830 | 813 | 66 | 56 | 747 |

## Exact annotated span recall

| Method | Template | Human |
|---|---:|---:|
| earliest_completion | 67.8663% | 58.4739% |
| guaranteed_support | 67.7598% | 58.3534% |
| interval_outer_control | 67.8876% | 58.4739% |
| latest_completion | 67.7811% | 58.3534% |
| latest_mentioned_year_top20 | 66.5460% | 64.2570% |
| midpoint_completion | 67.7598% | 58.3534% |
| no_temporal_filter | 67.6107% | 58.1124% |
| original_bm25 | 37.6278% | 44.7992% |
| original_bm25_latestyear | 53.2723% | 53.1124% |
| possible_support | 67.8876% | 58.4739% |

Possible support and the interval control return identical contexts on both tracks.
The three directed replacement pairs occur in the calibration source subset.
The benchmark differences mainly test occurrence bounds and explicit ends.

## Certificate work

The modeled cohorts contain 243 template contexts and 66 human contexts.
The certificates establish stability for 245 of these 309 contexts.
The remaining 64 contexts have explicit counterexamples.
Retirement explains 41 exclusions.
A start after the query explains 23 exclusions.
Sixty frontiers contain one claim.
Four frontiers contain two claims.

| Track | Mean candidates | Mean temporal tests | Full-mask tests |
|---|---:|---:|---:|
| validation | 5.2099 | 2.6296 | 986 |
| human | 5.1061 | 2.4394 | 928 |

These counts exclude source extraction, compilation, ranking, rendering, and answer generation.
They do not measure complete system latency.

## Six ranking variants

The secondary analysis retains every previously declared ranking variant.
All 18,654 query and ranking pairs match direct full-mask selection.
Each variant uses its own modeled-context denominator.
Across both tracks, the mean temporal test count ranges from 2.34 to 2.72.
The title-aware ranking with year reranking certifies 102 of 120 human modeled contexts.

See the saved JSON summaries for unrounded values and exact input hashes.
