# Independent manuscript review

This review covers the stable pass-4 introduction, source interface, theory, method, refinement, related work, and protocol.
The abstract and results were awaiting their pass-4 update during the initial review.
No paper files were edited by this reviewer.

## Central story

The strongest claim is an operational guarantee:

> A system can decide whether more precise dates could change its selected evidence.
> If they can, the system returns two admissible timelines that produce different contexts.

This story connects four contributions in one causal chain:

1. Compile independent occurrence bounds into exact possible and guaranteed support.
2. Test whether those masks yield the same fixed-ranked context.
3. Construct complete alternative timelines when that context is unstable.
4. Identify support decisions that every stabilizing refinement must resolve.

The largest stable prefix makes the guarantee actionable under an evidence budget.
It answers how much context the system can select before unresolved dates affect membership.
Possible-membership hardness provides a useful boundary around this tractable decision.

The new title-aware front end supplies stronger practical retrieval.
Its improvements should remain distinct from the temporal compiler's contribution.
The compiler provides exact decisions for its extracted model.
The current corpus evidence does not support an answer-accuracy superiority claim for the compiler.

## Mathematical review

The support formulas, context theorem, refinement necessity, and Set Cover reduction are sound under the stated independent-date model.
The budget must remain an input in the hardness statement.
The context theorem operates before rendering and word truncation.
Constructed worlds require the fixed direct gate and independent bounds.
Explicit-end reduction requires the declared strict separation of start and end bounds.

I found one overbroad proof sentence, but no theorem failure.

### Required proof wording correction

File: `sections/appendix_refinement.tex`.

Current text:

> The second places d after t.

The following argument uses the possible-support boundary.
It applies only to events accepted as incoming witnesses of the pivot.
An unrelated event can take the second assignment branch while remaining before the query time.
That assignment remains valid and cannot retire the pivot.

Replacement:

> For every accepted witness, the second case places d after t.

The later sentence about events outside the incoming witness set already states their harmlessness correctly.

### Clarify fixed fallback notation in the main text

File: `sections/method.tex`, following the context theorem.

Suggested replacement for the first two fallback sentences:

> Let F contain the excerpts retained by the fixed fallback policy.
> Apply the test to P(Q) union F and H(Q) union F.

Use the corresponding LaTeX union expressions.
The same augmented sets must define the possible ranking and unresolved frontier below.
The appendix already gives this formalization.
Putting it in the main body prevents ambiguity when most selected excerpts are fallback items.

### Distinguish necessary support decisions from particular date fields

File: `sections/introduction.tex`.

Current text:

> They identify which dates need clarification.

This can imply that the algorithm identifies a unique or minimum collection of date fields.
The theorem identifies necessary support-status decisions for current pivots.
Different date refinements can resolve the same pivot.

Replacement:

> They identify selected support decisions that further date evidence must resolve.

The method's explanation of the frontier correctly states the necessary, iterative character of this result.

### Clarify compilation versus pair discovery

File: `sections/theory.tex`.

Current text:

> These compiled certificates require a complete candidate scan.
> The compiler evaluates candidate gates and updates these two minima.

This wording obscures the stated linear compilation result for supplied accepted pairs.
Pair discovery can use a complete scan or a complete index.
Boundary compilation itself scans the accepted pairs.

Replacement:

> Compilation scans every supplied replacement pair and updates these two minima.
> Discovering those pairs requires a complete source procedure.

The method already explains the quadratic reference gate scan.

## Presentation improvements

### Bring the natural example forward

Move the Warburg example from Method to the end of Sources.
Readers then see a stable and unstable context before the formal support equations.
The introduction already defines possible and guaranteed support in plain language.
The moved example therefore needs no additional mathematical notation.

Keep its last sentence identifying the illustrative query and ranking.
It is a concise provenance statement, not defensive prose.

### Use the abstract for the decision and the evidence

The abstract should prioritize three pieces:

1. The practical decision: whether date clarification can alter selected evidence.
2. The exact certificate and constructive alternative timelines.
3. The new confirmation counts and a clearly attributed retrieval result, if space permits.

Avoid using the title-aware gain as evidence that the certificate improves answers.
Avoid listing every theoretical corollary in the abstract.
The first two pages already establish the broader framework.

### Keep the generic ranking property in proportion

The equality between top-k possible and guaranteed contexts follows from a general fixed-ranking property.
The temporal contribution supplies exact masks and constructive assignments for the source model.
The full combination makes the method useful.
Do not claim that the equality criterion alone solves general uncertain ranking.

### Keep the lazy-scan result scoped to its measured operation

The saved human microbenchmark reports approximately 492 times less selection time than full mask evaluation.
It excludes extraction, compilation, ranking, rendering, and reader inference.
Sparse modeled evidence also strongly reduces the lazy scan's work.

A suitable main-text statement is:

> Lazy evaluation checks only the candidates needed to fill the context.
> On human questions, it examines 5.06 candidates on average for a five-item budget.

Any timing ratio should be labeled a query-selection microbenchmark.
Do not describe it as an end-to-end system speedup.

## Figure review

The replacement architecture figure is clean, readable, and vector-based.
It has consistent spacing, restrained colors, and no decorative generated imagery.
The fallback path correctly joins ranked selection.
The lower example demonstrates why uncertainty below the first selected item can matter at a larger budget.

Two optional wording changes would improve first-page accessibility:

- Rename "Source reader" to "Answer model".
- Define P and H in the caption if the figure remains before their formal introduction.

## Source-claim precision

The main results should report modeled coverage beside certificate counts.
The current adapter models 2.37 percent of development units and 2.16 percent of test units.
All three development cross-claim pairs occur in calibration articles.
The test source has no cross-claim pairs.
Confirmation therefore primarily exercises uncertain starts and explicit ends.

The source audit accepted 52 of 60 event records.
Eleven accepted events omitted a termination stated elsewhere in their paragraphs.
Literal source spans establish traceability, not complete lifecycle extraction.
These results belong in the source-audit appendix and a short scope statement near the natural results.

The protocol correctly treats prior-inspected tracks as confirmation.
It should retain that term instead of calling them untouched test sets.
The feature separation and matched ranking controls are clearly stated.

## Sentence and style check

A line-level scan found no prose sentences above 20 words in the stable sections reviewed.
The manuscript consistently avoids em dashes.
Core terminology is mostly consistent: possible support, guaranteed support, unknown fallback, and fixed ranking.

In the appendix, replace isolated uses of "certain support" with "guaranteed support" when they denote H.
Keep "certainly active point" only when contrasting pointwise support with guaranteed support somewhere in a window.

The two source meanings, occurrence precision and lifetime duration, are explained before the equations use them.
The formal proof correctly distinguishes universal support somewhere from one common active point.

## Final update still required

After the new results are inserted, verify all counts and cohort denominators against saved summaries.
The abstract, conclusion, limitations, and appendices still contain several pass-3 values in the reviewed snapshot.
Recheck the page count after the results and figure settle.
Eight full main pages should result from substantive analysis, not repeated contribution statements.
