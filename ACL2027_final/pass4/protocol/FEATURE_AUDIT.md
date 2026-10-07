# Independent feature and method audit

This audit covers the pass-4 runner and frozen title ranker.
The source adapter receives a separate semantic audit.

## Allowed inputs

The ranker accepts one visible question string.
Its title inventory comes from public source titles.
It does not accept the question's gold article identifier.
It preserves a complete order over the declared corpus.
Title linking changes priority and does not remove unmatched articles.
The query date parser receives only visible question text.

The runner rejects query records with annotation metadata.
Each query record has exactly `question_id` and `question`.
The identifier remains an uninterpreted output key.
The source compiler receives frozen claims and source spans.
The inference runner does not load answer labels or histories.

## Matched method semantics

All ten conditions use the same disjoint source units.
All eight selected-front-end conditions share one relevance order before their declared policy.
The latest-year condition reorders its common top 20 candidates.
The two original-BM25 conditions provide explicit ranking controls.
They still use the same new units, metadata, and source budget.

Unknown fallback units stay eligible in every condition.
Possible and guaranteed masks follow the same lifecycle compiler.
The outer interval control uses start bounds and explicit end bounds.
It ignores cross-claim replacement pairs.
Completed dates apply the direct replacement rule to their assigned dates.
Queries without parsed windows use the common unfiltered source eligibility.

Every context contains at most five units.
The renderer clips source text to 768 whitespace tokens.
Each clipped excerpt preserves its actual source offsets.
Every method receives the same temporal status metadata for a given source unit and query.
Reader prompts contain source bounds, rather than imputed completion dates.

## Provenance requirements found during review

The runner must hash `pass3/pipeline/run_matched.py`.
The ranker imports its BM25 and query parsing functions.
The runner must also hash `pass3/theory/refinement.py`.
Its counterworld construction affects reported explanations.
The freeze utility includes both files.

Reader deduplication must preserve all question-method memberships.
Identical prompts can occur for different query identifiers.
One saved question identifier per prompt is insufficient in that case.
A separate membership record resolves this issue.

## Reporting requirements

The selected ranker was chosen on the calibration pilot.
It is a retrieval front end, not part of the temporal certificate theorem.
A ranking gain does not establish a compiler accuracy gain.
Compare temporal policies on the same selected order.
Compare rankings on identical source units.
Do not attribute differences from pass-3 units solely to ranking.

The reader sample contains 60 questions from 55 articles.
Use all 600 logical method conditions if all ten methods run.
Report actual unique generations separately.
Certificate and counterworld counts use the full confirmation track.
