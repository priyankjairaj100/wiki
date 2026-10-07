# Independent paper audit

Reviewed the active main-body sections, tables, and `appendix_pipeline.tex` against saved outputs.
This review made no manuscript edits.

## Required wording corrections

1. `sections/protocol.tex` says annotation dates enter scoring only.
   The official query renderer uses annotation dates to construct the visible question.
   Keep answer strings and spans scoring-only.
   State separately that published dates enter official query construction.

2. The context budget covers 768 whitespace-separated source-text tokens.
   Reader metadata and article titles add text outside that budget.
   Use `source-text tokens` in the budget description.

3. `sections/appendix_pipeline.tex` says every source character remains in the indexed units.
   Unit construction trims whitespace and can omit punctuation-only gaps.
   The audit verifies that all substantive source words remain.
   Use that narrower statement.

4. `sections/results.tex` describes 481 claims, including 221 explicit ends.
   There are 481 source claims and 221 additional hidden end events.
   Write: `The adapter produces 481 claims, of which 221 have explicit end dates.`

5. `sections/refinement.tex` says the exclusion witness occurs before the query starts.
   A witness exactly at the query start also excludes the target.
   Write `by the query start` to preserve the strict boundary semantics.

6. The reader appendix should state cohort overlap explicitly.
   Two diagnostic questions also occur in the primary sample.
   The executions cover 31 distinct questions and 74 actual generations.
   These totals must not imply 33 independent questions.

## Verified quantities and scopes

- Validation contains 2,348 questions from 644 articles.
- Query parsing succeeds on 2,296 questions.
- The possible context contains modeled evidence for 375 parsed questions.
- Exactly 306 of those contexts are stable: 81.60%.
- The other 69 contexts have verified differing timelines.
- All 138 constructed worlds replay successfully.
- Exclusion uses retirement in 47 cases and a late start in 22 cases.
- The frontier has one claim in 67 cases and two claims in two cases.
- All 1,921 parsed all-fallback contexts remain fixed under the stated policy.
- The table's span recall values match the scored offsets.
- Span recall and distinct annotated string recall coincide on this validation cohort.
- The quoted paired intervals match the saved article bootstrap.
- The primary reader sample has 24 questions, 21 articles, and 52 unique generations.
- Its 192 method conditions all pass the frozen parser.
- Every method has 29.17% exact answer-set accuracy and 31.94% strict F1.
- The nine-question diagnostic uses 28 prompts, including six reused primary prompts.
- Earliest versus latest completion changes four diagnostic answer sets.
- Possible versus guaranteed support also changes four diagnostic answer sets.
- Each diagnostic method has 33.33% strict F1.
- The Warburg example matches the quoted source passage.
- Its query, ranking, and timelines are explicitly described as illustrative.
- The paper correctly reports zero accepted cross-claim pairs in the main natural run.
- The paper correctly separates model extraction calibration from validation.
- The hardness statement correctly treats the context budget as an input.
- Model and runtime identifiers match the saved local provenance.

## Small additions for reproducibility

Define exact answer normalization in the appendix.
The scorer applies Unicode NFKC, case folding, and word-token normalization.
It preserves articles and compares deduplicated complete answer sets.
Strict set F1 uses the intersection of these normalized sets.
The secondary soft metric uses maximum one-to-one token matching.

State that ten excluded source-audit articles were selected through gold anchor paragraphs.
The separate 28-article succession sample used source cues only.
Both groups were excluded before validation outcomes.
The current appendix records source inspection but does not distinguish these two selection mechanisms.

## Specific redundancy cuts

The last method paragraph repeats the local-influence bound already stated in Corollary 1.
Remove its repeated `h`-pair and `2 min(k,h)` sentences.
Keep the later-dated insertion property, which adds information.

The theory section's opening date-precision sentences repeat the preceding source-interface section.
The section can start directly with occurrence dates and replacement.

The primary results and appendix both repeat every reader condition count.
Keep the main results focused on question counts, answers, and measured changes.
Keep prompt deduplication arithmetic in the appendix.

## Overall assessment

The main metrics and headline denominator are accurate.
The results support context certification and verified temporal alternatives.
They do not establish improved answer accuracy.
The current manuscript preserves that distinction.
The small wording corrections above remove remaining provenance and boundary ambiguities.
