# Pass 3: matched natural-source evaluation

The protocol separates source extraction, retrieval decisions, and answer scoring.
All temporal methods share the extracted claims and directed replacement pairs.
All compiler conditions preserve the same lexical order and context budget.

## Frozen split

Run `python pass3/protocol/freeze_protocol.py` to reproduce the split.
The script selects 50 development articles by seeded SHA256 order.
These articles provide 176 pilot questions.
The initial remaining split had 679 articles and 2,475 validation questions.
A later amendment removed all additional calibration articles before validation outcomes.
Validation now contains 644 articles and 2,348 questions.
Run `python pass3/protocol/amend_calibration_split.py` after the initial split script.
The original split remains under `v1_original_split/`.
Eight articles shared between the original development and test corpora remain excluded.

The human track contains 830 published questions from 251 articles.
Earlier work inspected baseline results for these questions.
This track provides confirmation, not an untouched test.
The development questions use the official templates.
They are separate from the human questions.

Query files contain visible question text and stable identifiers.
Source files contain article paths, passage text, passage IDs, and paragraph order.
Separate label files contain answer strings and source anchors.
Inference must not load the label files.

## Comparison

The eight conditions use identical evidence.
Seven conditions differ only in their temporal selection rule.
The recent-year control reorders the same lexical candidates.

1. No temporal filter.
2. Earliest date completion.
3. Midpoint date completion.
4. Latest date completion.
5. Simple outer interval control.
6. Exact possible support.
7. Exact guaranteed support.
8. Latest-mentioned-year reranking within the common top 20 source units.

The interval control also uses explicit end evidence.
Its rule does not use directed replacement pairs.
This control separates interval parsing benefits from the compiler's benefits.

Every condition keeps unresolved source text through a common fallback rule.
The guaranteed condition must not mark this text as guaranteed.
The context certificate refers to modeled claims and fixed directed decisions.
A certificate does not establish the source extractor's correctness.

## Pre-reader mechanism audit

Run every temporal method before reader inference.
Report the full query denominator before each selected slice.
Count parsed queries, extracted starts, accepted pairs, and unresolved fallback text.
Report claim contexts and paragraph contexts separately.
Duplicate claims can map to one paragraph.
Different claim contexts can therefore produce the same reader input.

Compare the three completed timelines with possible and guaranteed support.
Count context disagreements before any model reads them.
A high certificate rate can save date refinement work.
It does not imply an answer quality gain.
A low extraction rate identifies an extraction problem.
A near-zero disagreement rate limits the benchmark's power to test date uncertainty.

## Source and answer scoring

`score_predictions.py` scores the frozen query set without silent exclusions.
Every method must supply each question.
The script checks exact source-span coverage and distinct annotated string coverage.
Each context contains at most five atomic source excerpts.
The shared budget permits 768 whitespace tokens.
Exact offsets identify the source text actually shown to the reader.
A parent passage hit is a secondary score only.
It also scores complete predicted answer lists when readers provide them.
Whole answer-set equality differs from target containment.

Answer labels can contain aliases and sequential values.
The reported unit is an annotated answer string.
It is not a newly verified set of distinct real-world entities.
Soft scores use maximum one-to-one token matching.
This prevents duplicate predictions from receiving duplicate credit.

Paired intervals resample articles, preserving each article's questions.
The interval control is the primary comparator.
The same script can compare other prespecified methods.

## Blinded source audit

The audit checks claims, temporal bounds, and replacement decisions from source text.
Hide benchmark answers, selected methods, and comparative outcomes from the reviewer.
Use source offsets to verify each quoted span.
Freeze the audit sample by ID hashes before reviewing any sample.

Record one of `supported`, `unsupported`, or `unclear` for each premise.
Also record the source span and a short reason.
A model reviewer supplies a model audit, not human ground truth.
A source anchor match alone cannot supply this label.

Call a removed item `valid support` only after independent source verification.
Before verification, call it `annotated support removed`.
Keep both quantities separate in tables.

## Strict reader scoring

`parse_reader.py` was frozen before response inspection.
It accepts a complete JSON object, optionally inside one code fence.
It rejects narrative repair, invalid field types, invalid citations, and truncated generations.
Failed outputs receive empty answers and a failure flag.
No question leaves the scoring denominator because of a parser failure.

`score_reader.py` verifies each actual request against its frozen prompt.
It checks every method condition and exact context signature.
Primary and completion-sensitive cohorts remain separate.
The diagnostic cohort includes all nine completion-sensitive pilot queries.
That cohort cannot provide an independent benchmark accuracy estimate.
