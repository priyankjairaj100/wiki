# Revised reader results

Both fixed reader cohorts completed before scoring.
The study retains all 710 question and method conditions.
The primary cohort contains 60 questions from 55 articles.
The diagnostic cohort contains 11 questions from nine articles.
Four articles occur in both cohorts.
No question or request occurs in both cohorts.

The current study uses 234 distinct requests.
Exact historical reuse supplies 166 responses.
The new delta batch supplies 68 responses.
Primary requests comprise 146 reuses and 48 new executions.
Diagnostic requests comprise 20 reuses and 20 new executions.
The saved pass-4 batches and new delta contain 306 actual benchmark executions.

## Scores

| Method | Primary EM | Primary F1 | Diagnostic EM | Diagnostic F1 |
|---|---:|---:|---:|---:|
| earliest_completion | 20.00 | 20.00 | 18.18 | 18.18 |
| guaranteed_support | 20.00 | 20.00 | 18.18 | 18.18 |
| interval_outer_control | 20.00 | 20.00 | 9.09 | 9.09 |
| latest_completion | 20.00 | 20.00 | 9.09 | 9.09 |
| latest_mentioned_year_top20 | 21.67 | 21.67 | 9.09 | 15.15 |
| midpoint_completion | 20.00 | 20.00 | 9.09 | 9.09 |
| no_temporal_filter | 21.67 | 21.67 | 9.09 | 9.09 |
| original_bm25 | 16.67 | 16.67 | 9.09 | 9.09 |
| original_bm25_latestyear | 18.33 | 18.33 | 9.09 | 9.09 |
| possible_support | 20.00 | 20.00 | 9.09 | 9.09 |

The selected ranking exceeds original BM25 with year reranking by 3.33 primary F1 points.
The paired article interval is [-4.84, 11.67] points.
Possible and guaranteed support share every primary answer set.
Earliest and latest completion also share every primary answer set.

## Answer sensitivity

Possible and guaranteed support differ on four diagnostic questions.
Three changes have two valid parsed responses.
One change involves a parser failure.
Earliest and latest completion yield the same change counts.
Possible support and the interval control share every diagnostic answer set.
Guaranteed support exceeds possible support by 9.09 diagnostic F1 points.
The paired article interval is [0.00, 30.00] points.
The diagnostic uses previously selected questions and describes answer sensitivity.

The source review distinguishes the three jointly parsed changes.
Maher gains exact-set credit when the answer becomes the requested employer name.
The Atlético response changes from an unsupported coach name to abstention.
The Helen Clark response changes between two displayed role names.
The latter two changes receive zero strict credit under both methods.

## Parser outcomes

The unchanged parser rejects 69 of 194 primary requests.
These include 53 invalid JSON objects, four invalid citation indices, and 12 length-limited responses.
It rejects 11 of 40 diagnostic requests.
These include five invalid JSON objects and six length-limited responses.
All rejected responses remain empty predictions in the full denominator.

## Provenance

`reader_join_verification.json` checks each current response against its physical execution.
It verifies the full request, model identity, runtime, token fit, and server settings.
The two change audits cover every one of the 45 method pairs.
The qualitative review records the displayed source for each jointly parsed diagnostic change.
No response, label, question, or metric changed after generation.
