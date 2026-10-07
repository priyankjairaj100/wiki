# Independent review of the updated pass-4 manuscript

This review checks the updated abstract, results, protocol, limitations, and pipeline appendix.
It also checks the compiled manuscript at `/tmp/acl-pass4-complete/main.pdf`.
Reader results were still pending, so their three-sentence placeholder was excluded from outcome review.
No manuscript file was edited by this reviewer.

## Verified claims

The main numerical claims agree with the saved run artifacts.

| Claim | Independent check |
|---|---|
| Questions | 2,348 template plus 830 human equals 3,178. |
| Parsed questions | 2,296 plus 813 equals 3,109. |
| Parsed contexts with modeled evidence | 417 plus 90 equals 507. |
| Stable modeled contexts | 313 plus 79 equals 392. |
| Unstable modeled contexts | 104 plus 11 equals 115. |
| Replayed assignments | 208 plus 22 equals 230. |
| Different rendered contexts | All 115 counterworld pairs change rendered source excerpts. |
| Retirement exclusions | 66 plus nine equals 75. |
| Late-start exclusions | 38 plus two equals 40. |
| Frontier sizes | Direct JSONL counting gives 100 singletons, 14 pairs, and one triple. |
| Template stability | 313/417 equals 75.06 percent. |
| Human stability | 79/90 equals 87.78 percent. |
| Template ranking gain | 13.3234 points; interval [10.7997, 15.8021]. |
| Human ranking gain | 5.0000 points; interval [0.5938, 9.2121]. |
| Human title-aware recency gain | 11.2048 points; interval [7.5237, 15.1937]. |
| Strongest human control certificate | 146 of 166 modeled contexts remain stable. |

The retrieval percentages in the matched table also agree with `paper_results.json`.
The stability-budget table agrees with both independent confirmation audits.
The operation counts agree with the modeled-context slices in the lazy-selector summaries.

Checked sources:

- `pass4/pipeline/paper_results.json`
- `pass4/pipeline/validation/counterworlds.jsonl`
- `pass4/pipeline/human/counterworlds.jsonl`
- `pass4/retrieval/lazy_validation/summary.json`
- `pass4/retrieval/lazy_human/summary.json`
- `pass4/retrieval/secondary_validation/summary.json`
- `pass4/retrieval/secondary_human/summary.json`
- `pass4/extraction/RESULTS.md`
- `pass4/audit/source/RESULTS.md`
- `pass4/protocol/FEATURE_AUDIT.md`

## Precise corrections

### Use the measured operation name in the abstract

Current:

> A lazy selector tests fewer than three certificates per modeled context on average.

The saved metric counts possible-support and guaranteed-support predicate calls.
The same claim's certificate can supply both tests.

Replacement:

> A lazy selector performs fewer than three temporal tests per modeled context on average.

The main results already use the correct terminology.

### Round the secondary operation range consistently

The lowest mean is 2.5483870967741935.
The highest mean is 3.0024691358024693.
At two decimal places, the range is 2.55 to 3.00.

Replace the main text's `3.01` with `3.00`.
The portability table already rounds the maximum to 3.00.

### Preserve the Helen Clark question's wording

The literal question is:

> What governmental role did Helen Elizabeth Clark assume from 1989 to Aug 1989?

The source and frozen event record support the January departure example.
However, the verb "assume" can ask about an appointment, rather than any role held within the period.
The current paraphrase broadens that question to "governmental roles" during the period.

Replace its first sentence with:

> A human question specifies the period 1989 through August 1989.

The remaining sentences then describe the declared eligibility predicate without changing the question's semantics.
The new limitations paragraph correctly distinguishes appointment questions from the supported somewhere-within predicate.

### State the parsed restriction in the certificate cohort

The 507 denominator contains parsed questions with modeled evidence in their possible context.
The table establishes the parsed denominator in its preceding row.
For complete standalone clarity, its caption can say:

> The modeled group contains parsed questions with at least one modeled excerpt in their possible context.

The abstract could also split the count into two short sentences:

> Among parsed queries, 507 contexts contain modeled evidence.
> The compiler certifies 392 as stable and verifies alternative contexts for the remaining 115.

This is an optional clarity improvement, not a numerical correction.

## Scope and attribution

The new results keep ranking gains separate from certificate outcomes.
They do not claim that the compiler improves answer accuracy.
The comparisons use identical units and budgets.
The selected ranking remains frozen, while recency is identified as a separate ranking control.

The source audit is represented accurately.
The main body reports modeled coverage and the absence of confirmation succession pairs.
The appendix distinguishes event grounding from lifecycle completeness.
The limitations retain all 11 omitted terminations among accepted sampled starts.

The fallback path remains a fixed operational policy.
Unknown excerpts do not receive guaranteed-support labels.
The figure routes fallback text into ranked selection.
Its illustrative guaranteed set contains modeled claims, so it does not conflate those statuses.

The main text's operation counts avoid implying an end-to-end timing improvement.
The appendix identifies the excluded pipeline stages and concurrent CPU effects.

The protocol calls the reused tracks confirmation.
It does not describe them as untouched test sets.
The secondary ranking analysis is explicitly identified as post-confirmation.

## Citation and build check

The current LaTeX log has no unresolved citations, undefined references, or overfull boxes.
The cited model, TimeQA, and BM25 entries correspond to their stated roles.
The source-pipeline appendix identifies the 3B model's Qwen Research License.
This avoids carrying over the earlier 1.5B model's Apache license.

The compiled file contains 17 total pages.
Limitations starts on page nine, so the main body currently occupies eight pages.
The log still requests another line-number pass.
That routine final compilation should occur after the reader table is inserted.

## Space for the pending reader results

Page eight's right column currently ends near vertical coordinate 523.
This leaves approximately 19 ordinary text lines before the normal bottom margin.
The current placeholder contributes about eight additional lines that can be replaced.
A 200-word result plus a small table may still require a modest cut elsewhere.

Use these cuts in order:

1. Reduce the main portability paragraph to two sentences; its existing appendix retains all details.
2. Remove the budget subsection's first sentence; Method already establishes the first-unresolved-rank rule.
3. Shorten the introduction's prior-work paragraph while retaining its detailed comparison in Related Work.

Suggested short portability paragraph:

> The certificate also supports all six ranking variants considered during calibration.
> Under the strongest human retrieval control, 146 of 166 modeled contexts remain stable.
> Appendix G reports variant-specific coverage and fixed-cohort comparisons.

Replace the appendix letter with the actual cross-reference.
The first two sentences preserve the substantive portability result.

The full hardness proof, the support distinction, and the source-grounded example should remain priorities.
They contribute more than another restatement of the certificate's general purpose.

## Style check

A fresh prose and caption scan found no sentences above 20 words in the reviewed TeX files.
The complete paper sources contain no em dashes.
The new prose uses the established terms consistently.
No additional caveat paragraph is needed in the main body.

## Remaining verification

The pending reader section must use completed generations and all 600 primary method conditions.
Its diagnostic must remain separate from population accuracy claims.
Exact set accuracy, strict set F1, parse failures, and paired uncertainty should use their saved scorer outputs.
Recheck the final page count after inserting those results.
