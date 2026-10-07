# Independent manuscript review, pass 2

Reviewed the abstract, introduction, sources, theory, method, related work,
limitations, protocol, results, conclusion, and proof appendix. No main-paper
files were changed by this reviewer.

## Correctness verdict

The mathematical core is correct under fixed directed replacement gates and
independent closed occurrence bounds. Self-pairs are now explicitly excluded.
The two-witness necessity example is valid. Its qualification to direct witness
subsets avoids an unsupported general compression lower bound.

The refactored `compile_from_pairs` implementation passed the independent suite:
253,050 compiler comparisons and 11 fractional or boundary assertions. The
earlier finite-model counts remain unchanged. Those counts are correctly
described as finite correctness checks, not corpus performance measurements.

The future-prefix claim is correct when every newly added claim has lower bound
strictly greater than the query end, while existing bounds and gates stay fixed.
Proof: every new start is after the entire window, so no new claim contributes
support or retires an existing claim within that window. Extending a world with
these new dates leaves every original support predicate unchanged. The
existential and universal predicates therefore remain unchanged as well.

An additional independent run passed 7,000 comparisons over 500 randomized
configurations. It also checks a counterexample at equality: an event starting
exactly at the query end can change support. The executable and results are
`check_future_prefix.py` and `future_prefix_results.json`.

The smallest possible-support pool claim is correct. It concerns preserving
every individually admissible claim before the context budget. It does not
assert minimum context size, relevance, or joint support in one timeline. The
appendix already makes this distinction.

## Wording fixes recommended

1. **Introduction, unresolved status.** “The remaining evidence has an
   unresolved temporal status” can label unsupported evidence as unresolved.
   Use: “Claims with possible but unguaranteed support have unresolved status.”
   In Sources, “some, but not all, timelines” also makes the distinction exact.

2. **Method, exclusion provenance.** “An exclusion can be traced to a specific
   directed decision” is too broad. A claim can be excluded because its earliest
   start is after the window. Guaranteed-only selection can also exclude a claim
   whose latest start exceeds the window, without any replacement decision.
   Suggested wording: “A retirement-based exclusion traces to its replacement
   witness. A date-based exclusion traces to the target bounds.”

3. **Method, prefix conditions.** State explicitly that existing bounds and pair
   decisions remain fixed. Use “every new lower bound exceeds the query end.”
   The mathematical claim then has no ambiguity about ingestion or gate edits.

4. **Introduction, witness intuition.** The second witness does not always give
   the literal first instant when replacement is possible. Its lower bound may
   precede the target, and the strict comparison matters. “A second records the
   earliest lower bound among potential replacements” is more exact. The formal
   section already treats this boundary correctly.

## Contribution and evidence alignment

The draft does not misattribute corpus gains to the new compiler. The protocol
and results clearly separate finite executor verification, annual snapshot
baselines, and source-only TimeQA retrieval. The reported all-source audit count
of 1,980 retained first answers among 5,456 changes matches the saved source
audit. Its use differs legitimately from the held-out counts in the table.

The central remaining scientific need is a natural-source experiment that runs
the new compiler with justified occurrence bounds and replacement decisions.
The current corpus results establish the problem and competitive baselines.
They do not yet demonstrate the proposed compiler's practical advantage. This
is a next-pass research priority, not a request to add more caveats to the main
body.

The prior-work discussion appropriately attributes direct invalidation and
possible/certain semantics to existing work. This review checks claim alignment,
not independent bibliographic coverage of every cited source.

## Presentation and packaging

The [0,10] versus time-5 example appears fully in both the introduction and
theory. Keep the accessible explanation in the introduction. The formal section
can refer to that example when explaining the quantifier order. The opening
sentences of Sources and Theory also repeat the same year-versus-point lesson.

`sections/discussion.tex` is an unused pass-1 leftover. It still discusses old
RealProse gains and a prefix theorem not presented in that form here. It is not
included by `main.tex`, so it creates no current PDF error. Remove it from the
clean Overleaf bundle or place it only in a clearly marked historical archive.

The user requested a full eight-page content body. Page count and final rendered
layout require the root agent's compilation check; this review does not certify
the current PDF pagination.
