# Independent pass-3 scoring

## Retrieval cohorts

The frozen pilot contains 176 questions from 50 articles.
The amended validation contains 2,348 questions from 644 articles.
Calibration exclusions removed 127 validation questions across 35 articles before comparative outcomes.
The original split remains available for audit.

Each result uses at most five atomic source excerpts and 768 whitespace tokens.
Exact source offsets determine whether the shown text includes each annotated answer span.
All methods receive the same extracted claims and source corpus.

| Method | Pilot string recall | Validation string recall |
|---|---:|---:|
| No temporal filter | 38.64% | 38.49% |
| Earliest completion | 39.49% | 39.20% |
| Midpoint completion | 39.49% | 39.07% |
| Latest completion | 38.92% | 39.03% |
| Simple interval control | 38.92% | 39.07% |
| Possible support | 38.92% | 39.07% |
| Guaranteed support | 39.49% | 39.15% |
| Recent-year reranking | 54.83% | 53.51% |

Possible support matches the interval control throughout these cohorts.
The frozen adapter supplies no accepted cross-claim replacement pairs.
The comparison therefore measures uncertain starts and explicit ends.
It cannot establish a cross-claim replacement gain.

The guaranteed method gains 0.085 percentage points over the interval control on validation.
Its paired article interval is [-0.085, 0.259] points.
Recent-year reranking gains 14.44 points, with interval [12.05, 16.86].
The interval control gains 0.575 points over no filtering, with interval [0.253, 0.963].
All intervals use 2,000 paired article resamples.

## Actual reader pilot

The primary cohort contains 24 questions selected by a fixed question-ID hash.
These questions cover 21 articles.
Eight methods produce 192 logical conditions and 52 distinct prompts.
Identical prompts reuse the same actual generation.

The reader is Qwen2.5-1.5B-Instruct, using the pinned Q4_K_M artifact.
Every generation uses temperature zero and the same output budget.
The parser was fixed before inspecting responses.
All 52 primary outputs passed that parser.

Every method obtains 29.17% complete answer-set accuracy.
Every method obtains 31.94% strict annotated answer-set F1.
The completion, interval, possible, and guaranteed methods produce identical answer sets on every primary question.
Recent-year reranking changes 14 answer sets, but its strict aggregate scores remain equal.

This pilot establishes a working reader interface.
It provides no answer accuracy gain for the compiler.
The exact parser, prompts, outputs, request hashes, and paired intervals are retained.

## Completion-sensitive diagnostic

The diagnostic includes all nine pilot questions whose completion contexts differ.
It spans seven articles and contains 72 method conditions.
It uses 28 distinct prompts, including six reused primary prompts.
The run adds 22 actual generations.
All diagnostic outputs passed the same fixed parser.

Earliest and latest completion produce different answer sets on four questions.
Possible and guaranteed support also differ on four questions.
Possible support and the interval control never differ.
All methods obtain 33.33% strict answer-set F1 in this selected diagnostic.

The changed answers include weak reader outputs.
A changed answer does not establish a corrected answer or better reasoning.
This diagnostic measures downstream sensitivity only.
Do not pool it with the primary cohort for a benchmark accuracy claim.

Two diagnostic questions also occur in the primary cohort.
The combined execution covers 31 distinct questions and 74 actual generations.

## Retained outputs

- `independent_pilot_retrieval/summary.json`
- `independent_validation/summary.json`
- `independent_pilot_reader/summary.json`
- `independent_mechanism_reader/summary.json`
- `reader_parser_freeze.json`
- `split_amendment.json`

Each directory also contains per-question scores and source hashes.
Reader directories preserve parsed answers and parsing flags for every method condition.
