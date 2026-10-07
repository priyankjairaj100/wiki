# Exact context invariance from possible and guaranteed support

## Verdict and assumptions

The proposed equivalence is correct. Let the finite claim universe have a fixed
complete strict ranking. Let k be any nonnegative integer. Let the nonempty
family of allowed worlds have support masks M_x. Define P as their union and H
as their intersection. Then

    every Top_k(M_x) is the same ordered list
    iff Top_k(P) = Top_k(H)
    iff every claim in Top_k(P) belongs to H.

No independence or product-world assumption is needed for this result. Ties
must have deterministic resolution, which induces the required strict order.

## Independent proof

First suppose every claim in C=Top_k(P) belongs to H. Every world contains C and
is a subset of P. No world can contain a claim that displaces C, since such a
claim would also displace it in P. If C contains fewer than k claims, it equals
P, and H=P. Thus every world selects C. Applying the same argument to H gives
Top_k(H)=C.

Conversely, suppose C contains a claim c outside H. Because c belongs to P,
some world contains c. Since c is among the first k members of P, fewer than k
possible claims outrank it. That world therefore selects c. Because c is outside
H, another world omits c and cannot select it. Their contexts differ. This proves
necessity and supplies a concrete indicator of context dependence.

The empty-world family is excluded. Empty claim universes and k=0 are allowed.
The argument also covers k larger than the universe size.

## Executable independent check

`check_context_invariance.py` enumerates every nonempty family of masks for each
universe size from zero through four. For each family it checks every k from zero
through the universe size. It compares ordered outputs in every world against
the two-envelope criterion.

The run passed all 328,747 conditions across 65,809 mask families. A family can
contain up to 16 masks. The families include arbitrary correlations and cases
where the union mask is not itself realizable. Results are stored in
`context_invariance_results.json`.

## Scope in the temporal paper

The new compiler supplies exact P and H for its declared product-world model.
The theorem therefore gives an exact test of context invariance under that
model. It does not require enumerating date assignments.

If the real world family instead has additional correlations, independently
compiled masks can overestimate P and underestimate H. Agreement still certifies
invariance. Disagreement need not establish actual context variation under those
extra constraints.

The theorem concerns selected claim contexts. A later renderer might merge
several claims into the same paragraph, and a reader might produce the same
answer from different contexts. Therefore context variation alone does not prove
variation in rendered passages or generated answers.

## Suggested main-text passage, 166 words

Uncertain dates need not change the retrieved context. We can test this exactly
without selecting dates or enumerating timelines. Fix a complete relevance
ranking and a context budget k. Let P contain possible support and H contain
guaranteed support. The selected top-k claims are identical under every allowed
timeline exactly when Top-k(P) equals Top-k(H).

This test has a simple implementation. Retrieve the top-k possible claims and
check whether every selected claim is guaranteed. If so, unresolved dates cannot
change this context. If an unresolved claim appears, some allowed timeline
includes it and another excludes it. Whenever it is present, fewer than k
possible claims outrank it, so it enters that timeline's context. Thus the two
timelines select different claim contexts.

The result distinguishes uncertainty in the evidence pool from uncertainty that
affects the selected context. Low-ranked uncertain claims can remain unresolved
without changing retrieval. The test applies to point and period questions. It
requires the same fixed ranking across timelines and exact possible and
guaranteed masks.
