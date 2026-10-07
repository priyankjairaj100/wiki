# Formal and empirical scope audit

This audit reads the current `pass6/paper` sources.
Replacement and reader results were still being integrated during review.
The audit does not modify paper sources.

## Integration findings and recheck

1. **Scope the constructive theorem to independent dates.**
   The general context theorem now permits arbitrary feasible timeline families.
   Its following constructive theorem still claims an `O(n)` assignment construction.
   That construction requires the independent product and its compact certificates.
   The constrained oracle can require exponential branching.
   Rechecking confirms the theorem now states the independent-date condition.

2. **Distinguish claim selection from rendering.**
   General instability guarantees different selected claims.
   Word truncation or shared text can conceal a selection difference.
   The abstract should promise different selected claims.
   The 64 automatic cases can separately claim verified rendered differences.
   Rechecking confirms the abstract now promises different selected claims.

3. **Update the limitation scope.**
   The earlier limitation text describes every guarantee as independent and every query as overlap.
   These statements must describe the fast compiler and automatic track.
   The constrained extension handles dependent dates and three explicit predicates.
   Strictly separated lifetime bounds must also describe the automatic adapter.
   Rechecking confirms the main limitation and lifetime statements now have the correct scope.

4. **Remove the duplicate hardness proof.**
   The first Set Cover reduction appeared in two appendix sections.
   Keep both reduction variants together under the hardness section.
   Point every hardness reference to that section.
   Rechecking confirms both reductions now appear once, together in the hardness section.

5. **Retain fallback eligibility in the hybrid interface.**
   The operational masks are `P union F` and `H union F`.
   The controlled hybrid benchmark contains no fallback items.
   A general implementation must accept fallback items without a solver call.
   Rechecking confirms the paper now includes the union with fallback items.
   The frozen `HybridIndex` API still accepts only modeled claims.
   Describe fallback retention as a mathematical extension unless another implementation supplies that API.

6. **Use the correct constraint appendix label.**
   The inserted appendix uses `app:constrained-dates`.
   An earlier main-text reference used `app:constraints`.
   Rechecking confirms the main reference now uses the correct label.

## Verified formal content

The point and window formulas are correct under independent closed date bounds.
The strict replacement convention handles equal dates correctly.
The two direct witnesses have distinct necessary roles.
The stated minimality concerns witness subsets, not arbitrary encodings.

The context criterion holds for every nonempty feasible family under a fixed complete ranking.
Its proof requires exact support unions and intersections.
The stable-prefix result follows under the same assumptions.
The refinement requirement is necessary, rather than sufficient.

The difference-constraint oracle is complete for integer dates.
Bounds, query endpoints, and constraint constants must be integers.
Integer edge weights produce integer feasible assignments.
No rounding step is needed.
The real-valued independent product remains a valid outer relaxation of the constrained integer family.

The overlap, throughout, and appointment formulas are correct.
Throughout excludes retirement at the query endpoint.
Appointment describes the start event independently of later replacement.
An empty feasible family must be rejected before support evaluation.

The hybrid screening inclusions are correct.
Its returned possible context and stability decision are exact.
Its unresolved pivot supplies two valid context witnesses.
The shared model feasibility check must remain separate from query-level solver counts.

Both hardness reductions are correct.
Their context budget grows with the Set Cover budget.
They do not establish hardness for the fixed budget of five.
The revised theorem states this scope directly.

## Empirical interpretation

The fair lazy baseline isolates product screening from budget stopping.
The reported reductions of 59.79% and 55.67% match the archived counts.
These values concern claim queries and feasibility calls.
They do not establish an end-to-end speedup.

The two-witness grid deliberately samples configurations with different supplying witnesses.
Its universal ablation failures demonstrate mechanism necessity within that grid.
They do not estimate how frequently natural sources require both witnesses.
Keep the source challenge and controlled grid as separate evidence.

The automatic stability rate should retain its 309-context denominator.
The revised coverage figure and prose make that denominator visible.
The title-aware retrieval gains remain correctly attributed to ranking.
The reader subsection requires its pending protocol update before final verification.

Query type must remain an explicit input.
The extension does not automatically infer the intended predicate from each TimeQA question.
The controlled benchmark measures all three predicates.
It does not establish automatic semantic routing accuracy.

## Useful appendix counts

The dynamic ranker sorts claims by descending realized start.
The original fixed ranking breaks ties.
Among 8,627 fixed-ranking stable contexts, selected sets change in 3,640 cases.
Ordered contexts change in 4,808 cases.
These comparisons combine all three predicates.

| Budget | Fixed stable contexts | Changed sets | Changed ordered contexts |
| --- | ---: | ---: | ---: |
| 1 | 4,604 | 2,683 | 2,683 |
| 3 | 2,197 | 957 | 1,242 |
| 5 | 1,826 | 0 | 883 |

Five visible claims explain the absence of set changes at budget five.
The simple two-claim counterexample establishes the structural issue independently of these frequencies.

Each predicate comparison contains 16,800 claim-window decisions.
Throughout changes 5,840 possible decisions relative to overlap.
Appointment changes 2,989 possible decisions relative to overlap.
These counts can document the effect of choosing a query predicate.

## Strongest central story

The strongest claim concerns decisions about evidence under uncertain dates.
The system identifies when further date resolution can affect a selected context.
It returns a certificate when resolution is unnecessary.
Otherwise, it returns concrete timelines and the selected support decisions that need attention.

The two-witness compiler supplies the compact algorithmic result.
The general context theorem separates eligibility uncertainty from relevance ranking.
The hybrid extends this interface to constrained dates with measured savings against lazy exact selection.
The source challenge tests replacement in real passages.
The automatic track measures extraction coverage and operational reach.

This story supports a useful retrieval component.
It does not require a claim of superior answer accuracy.
The manuscript should give the mechanism, hybrid result, and source challenge priority over the original reader scores.
