# Final pass-4 scientific and story review

Reviewed the current main body before diagnostic reader integration. This is a read-only review of the manuscript. No paper files were changed.

## Finding

No new material theoretical error was found. The central story is now coherent: incomplete event dates need further verification only when they can change selected evidence. The source adapter supplies a temporal model. The compiler answers exact support queries for that model. The fixed ranking converts those decisions into stability or replayable alternatives.

The strongest accurate contribution order remains:

1. Exact window support from at most two direct replacement witnesses, with a sharp direct-subset bound.
2. Linear certification of context stability and construction of two admissible timelines when it fails.
3. Necessary support decisions for stabilizing date refinement, plus the distinction from hard arbitrary possible membership.
4. A complete source pipeline that measures modeled coverage, retrieval quality, replay, and answer sensitivity separately.

The text correctly separates the model-specific compiler from the general fixed-order stability identity. It also restricts the hardness claim to input-dependent budgets. It does not imply that individually possible claims must coexist in one timeline. The explicit-end reduction retains its strict separation requirement. Fallback eligibility remains a fixed operational policy, outside temporal support guarantees.

## Small optional wording improvement

In Results, replace:

> The remaining contexts require a support decision to change before date refinement can establish stability.

with:

> The remaining contexts contain selected support decisions that date refinement must resolve.

This describes a change in support classification without suggesting that refinement changes the underlying historical fact. It also aligns with the refinement theorem's necessary-resolution statement.

## Reader integration

The primary results support a reader benefit for the selected ranking relative to the prespecified original recency baseline. They do not show a reader accuracy benefit from temporal filtering. The current main paragraph preserves this distinction.

For the diagnostic, report three different quantities separately:

- Distinct source contexts: the cohort criterion, with eleven questions selected before generation.
- Parsed answer-set changes: include all questions under the frozen parser, with failed responses receiving empty sets.
- Both-valid answer-set changes: changes where both responses satisfy the frozen format contract.

Recommended concise structure after final scoring:

> The eleven-question diagnostic targets differing possible and guaranteed contexts. Their parsed answer sets differ on X questions. Both responses satisfy the format contract on Y comparisons, including Z answer-set changes.

Then add the actual exact-match or strict-F1 figures if they provide useful information. If Z is zero, use:

> No answer-set change remains among the Y comparisons with two valid responses.

If X is zero, use:

> Possible and guaranteed support return identical parsed answer sets across this diagnostic.

Do not call X semantic changes, corrected answers, or effects of a better temporal decision. Even Z measures changed extracted strings, not semantic equivalence or correctness. Keep all failures in the reported accuracy denominator. The appendix should retain unique-generation parse failures and per-method condition failures, which have different denominators.

## Readability and presentation

An independent scan found no main-body prose line exceeding twenty words after removing citation commands and treating mathematical expressions as units. The source-grounded example precedes formal notation. The guaranteed-support quantifier distinction has a concrete counterexample. The opening avoids technical machinery until the practical decision is clear.

The final diagnostic paragraph should replace its pending marker. Its complete ten-method table belongs in the appendix, preserving the main body's focus. Final PDF inspection remains necessary after that integration.

## Completed-reader integration review

Rechecked both reader sections and both ten-method tables against the complete primary and diagnostic scoring summaries and descriptive change audits.

- Every displayed EM and strict-F1 value matches the saved metrics after rounding.
- The primary selected-ranking gain is 6.67 points, with interval [1.59, 13.56].
- The diagnostic guaranteed-minus-possible gain is 18.18 points, with interval [0.00, 40.00]. This correctly reverses the stored possible-minus-guaranteed contrast.
- Diagnostic possible/guaranteed and earliest/latest contrasts each change six answer sets. Three changes occur among six comparisons with two valid responses. The changed question identifiers also match across the two contrasts.
- The primary temporal contrasts have zero changes; the corresponding both-valid count is 38.
- The primary ranking comparison has sixteen changes: four among twenty-three both-valid comparisons and twelve involving a format failure.
- Deduplicating parse audit records by request identifier verifies 238 unique generations and 88 failures: 60 complete-JSON failures, six invalid citation lists, and 22 length-limit responses. All non-stop failures have the recorded finish reason `length`.

The narrative appropriately distinguishes overall parsed answer changes from changes between two valid responses. It does not claim semantic correction or a general temporal accuracy improvement from the selected diagnostic.

One reference mismatch was reported to the root immediately: `reader_results.tex` cited `tab:reader-main`, whereas `reader_main.tex` defined `tab:reader_main`. Make those identical before the final compile. No numerical or scientific correction is otherwise required for this integration.
