# Pass 2 empirical findings

The complete-source evaluation changes the empirical interpretation.
Simple date policies almost saturate the annual retrieval task.
Keeping all accepted annual answers matters more than selecting one latest value.

## Frozen test

The test contains 2,993 previously unused source keys and 25,752 annual questions.
Every method sees 45,866 text-only observations from the complete source.
The source contains 34,963 original annual records across 4,057 keys.
The split excludes all 300 previously selected keys from test.

## Annual retrieval

All values below are percentages.

| Policy | Hit@1 | Answer recall@5 | Target-label stale exposure@5 |
|---|---:|---:|---:|
| BM25 | 64.64 | 80.84 | 45.89 |
| BM25 with recent ties | 84.04 | 90.10 | 40.50 |
| Development-selected age weighting | 99.81 | 99.98 | 24.07 |
| Date-first ranking | 99.81 | 99.98 | 0.00 |
| Original earliest predicate | 99.37 | 99.77 | 0.77 |
| Graphiti policy kernel | 99.78 | 99.93 | 0.00 |
| Query latest-value | 99.89 | 86.37 | 0.00 |
| Query latest-batch | 99.89 | 99.98 | 0.00 |

Latest-value and latest-batch have identical first-result accuracy.
Latest-value suppresses 13.63% of accepted values before context selection.
Its key-cluster 95% interval is [13.06%, 14.21%].

Latest-batch candidate recall is complete.
Its top-five answer recall can decrease when a source year contains more than five answers.
The observed maximum is seven.
The corpus also contains six ambiguous textual slots across thirteen source entities.
These slots produce identical questions despite distinct hidden source identifiers.
We retain every ambiguous item.

The original predicate and Graphiti use different matchers in the table.
A separate matched-input test removes this difference.
Graphiti and exact direct-first then produce identical endpoints for all 45,866 observations.
No new temporal-policy superiority follows from their table difference.

## Source labels

Among test years, 25.23% accept multiple answers.
Among changed first-listed answers, 36.58% retain the previous first answer.
Among changed complete answer sets, 86.91% retain at least one previous answer.

These are annual labels.
Multiple answers can reflect simultaneous roles or succession within one year.
The answer year is not a document publication or arrival time.
Absence from a later answer set does not supply an observed retirement event.

## Natural paragraphs

The independent TimeQA run searches 33,493 original paragraphs from 749 articles.
Its primary track contains 830 human questions with positive span annotations.
Its diagnostic track contains 2,613 template questions over the same articles.
The tracks overlap and must not be summed as independent evidence.

Latest-mentioned-year reranking raises human Hit@5 from 45.66% to 54.70%.
Its gain is 9.04 points, with article-cluster interval [5.54, 12.69].
The template diagnostic improves from 32.49% to 51.86%.

Year-envelope filtering removes 107 of 887 human answer spans.
Explicit-range filtering removes 63 spans.
These counts expose support loss from lexical temporal deletion.
They do not measure semantic entailment or generated-answer quality.

## Interpretation for the manuscript

Use the corpus results to establish strong baselines and source requirements.
Use independent possible-world checks to validate the uncertainty compiler.
Do not describe annual source records as uncertain event-start annotations.
Do not attribute baseline retrieval accuracy to the new uncertainty compiler.
The new theory needs its own source-grounded uncertainty experiment before an empirical superiority claim.
