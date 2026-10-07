# Pass-4 protocol and independent checks

The configuration and inputs were frozen before confirmation execution.
The freeze records 27 code and input files.
All recorded hashes remain unchanged.
The source extraction freeze also records its inherited succession parser.

The primary reader sample contains 60 human questions from 55 articles.
Its membership was selected before pass-4 retrieval and answer outcomes.
Every method uses the complete test source pool.
The reader design contains 600 question-method conditions.
The actual rendered requests collapse to 193 unique prompts.

The reader parser and metrics remain unchanged from pass 3.
A regression check used 24 archived questions and 52 actual generations.
All existing metrics matched exactly across 192 logical conditions.
Removing a complete question caused the new membership check to reject scoring.
This check verifies the scorer and is not a new benchmark result.

## Human confirmation

Independent replay checked all 8,300 saved method contexts.
It used direct incoming-event scans instead of compiler or counterworld functions.
Every selected unit and rendered source excerpt matched.
All source words remain represented without overlapping units.
All contexts respect the unit and source-word budgets.
All reader memberships match their frozen context signatures.

Query dates parse for 813 of 830 questions.
Ninety parsed possible contexts contain modeled evidence.
Seventy-nine of those contexts are stable at five units.
The certificate rate for this modeled cohort is 87.78 percent.
The other eleven contexts have distinct permitted timelines.
All 22 full assignments are legal and replay exactly.
Every timeline pair changes the rendered source excerpts.
Nine exclusions use retirement, while two use a start after the query.

The other 723 parsed contexts contain only fallback text.
Their stability follows from fixed fallback eligibility.
They do not contribute to the modeled-cohort certificate rate.

| Unit budget | Stable contexts | Fixed modeled cohort |
|---|---:|---:|
| 1 | 87 | 90 |
| 3 | 81 | 90 |
| 5 | 79 | 90 |
| 10 | 74 | 90 |
| 20 | 66 | 90 |

All 4,065 budget comparisons agree with direct possible-versus-guaranteed selection.

## Development confirmation

Independent replay checked all 23,480 saved method contexts.
Query dates parse for 2,296 of 2,348 questions.
The possible context contains modeled evidence for 417 parsed questions.
Exactly 313 of those contexts are stable at five units.
The modeled-cohort certificate rate is 75.06 percent.

All 104 unstable contexts have two legal full date assignments.
All 208 assignments replay exactly.
Every pair changes the rendered source excerpts.
Retirement explains 66 exclusions, and late starts explain 38.
The other 1,879 parsed contexts contain only fixed fallback text.

| Unit budget | Stable contexts | Fixed modeled cohort |
|---|---:|---:|
| 1 | 375 | 417 |
| 3 | 322 | 417 |
| 5 | 313 | 417 |
| 10 | 309 | 417 |
| 20 | 305 | 417 |

All 11,480 budget comparisons match direct possible-versus-guaranteed selection.
Across both tracks, independent checks cover 31,780 contexts and 230 complete date assignments.
Every one of the 115 timeline pairs changes rendered evidence.

## Reader diagnostic and resource amendment

The diagnostic includes all eleven human contexts with different possible and guaranteed rendered evidence.
Its membership was frozen before any completed pass-4 QA response.
It contains 110 method conditions and 45 additional requests.
It shares no questions or requests with the primary sample.
Exact query, prompt, source-context, and method membership checks passed.

The first 8,192-context reader request produced no completed response before interruption.
A second attempt used 4,096 context tokens and produced no completed QA response.
Constructed prompts then selected the final runtime settings.
The final run uses four threads and 2,048 context tokens.
Its prompt batch and microbatch contain 512 tokens.
Both polling settings are zero.
All 238 planned prompts fit the final context without truncation.
The model, prompts, output limit, sampling settings, parser, and question membership remain unchanged.
The original retrieval configuration and algorithm freeze remain unchanged.
`RESOURCE_AMENDMENT.json` links the executed reader configuration to the original freeze.

## Primary reader scores

All 193 primary requests completed under one final runtime configuration.
Independent checks verify model identity, decoding settings, server arguments, and exact request coverage.
All prompts fit within the configured context without truncation.
The largest reserved request uses 1,423 of 2,048 tokens.

All 600 logical conditions remain in the scored denominator.
Exact answer-set accuracy and strict set F1 coincide on this sample.

| Condition | Exact set accuracy | Strict set F1 |
|---|---:|---:|
| Selected ranking, no filter | 21.67% | 21.67% |
| Selected ranking, latest-year | 21.67% | 21.67% |
| Each temporal completion | 20.00% | 20.00% |
| Outer interval control | 20.00% | 20.00% |
| Possible support | 20.00% | 20.00% |
| Guaranteed support | 20.00% | 20.00% |
| Original BM25 | 18.33% | 18.33% |
| Original BM25, latest-year | 15.00% | 15.00% |

Selected no-filter ranking exceeds original BM25 with recency by 6.67 percentage points.
The paired article interval is [1.59, 13.56] points.
Earliest and latest completion produce identical scored answer sets on all 60 questions.
Possible and guaranteed support also produce identical answer sets.

The frozen parser rejects 75 of 193 unique requests.
These comprise 55 invalid complete JSON responses, six invalid citation indices, and fourteen length-limited responses.
They remain empty predictions under the unchanged scoring protocol.

A separate descriptive audit partitions answer changes by parse status.
Selected no-filter ranking and original recency produce sixteen different scored answer sets.
Four changes occur where both responses parse successfully.
The other twelve involve at least one parser failure.
This audit does not alter the primary cohort or any metric.

## Diagnostic reader scores

All 45 diagnostic requests completed under the same final runtime.
The eleven questions come from nine articles and yield 110 method conditions.
Every request fits the context without truncation.
Thirteen unique responses fail the unchanged parser and remain empty predictions.

Earliest completion and guaranteed support achieve 18.18 percent exact-set accuracy and 24.24 percent strict F1.
Midpoint completion, latest completion, the interval control, and possible support achieve zero exact-set accuracy and 6.06 percent F1.
Original BM25 achieves 9.09 percent for both metrics.
The no-filter and both recency conditions score zero on both metrics.
This cohort was selected for context disagreement and is a descriptive mechanism diagnostic.

Earliest versus latest completion changes six of eleven scored answer sets.
Possible versus guaranteed support changes the same six.
Three changes occur among six question pairs where both responses parse successfully.
The other three involve a parser failure.
Possible support and the interval control produce identical scored answer sets.

A source review distinguishes the three jointly parsed changes.
Maher's answer changes from a role phrase to the requested employer name, gaining exact-set credit.
An Atlético answer changes from an unsupported coach name to abstention.
Helen Clark's answer changes between roles stated in different excerpts.
The latter two changes receive zero strict credit under both methods.
These cases establish answer sensitivity without implying three factual corrections.

Both completed cohorts cover 71 distinct questions and 238 actual generations.
All 710 method conditions retain their original denominators.
