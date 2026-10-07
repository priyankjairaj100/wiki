# Direct temporal witnesses

## Recommended central contribution

Compile pairwise temporal decisions into a sparse index that preserves every query cutoff.
Each claim stores its earliest direct replacement witness.
The index does not merge claims through connected components.
This choice preserves past evidence when future records arrive.
It also prevents one matching error from spreading through a timeline.

This is an evidence-management contribution.
It is not a truth-verification guarantee.
Keep this distinction in the problem definition.
The main result concerns arbitrary pair predicates, including noisy, nontransitive predicates.
Sorting exact entity keys remains an essential baseline.

## Inputs and semantics

Let C contain n source-attributed claims.
Each dated claim c has an identifier, text x_c, and finite timestamp t_c.
No gold key or value enters the compiler.
Let G(d,c) be a fixed predicate computed from the two claim texts.
It means that d concerns the same attribute and gives a replacement value.
The supplied detector implements G through its subject, relation, and changed-value gates.
G need not define an equivalence relation.

A claim is eligible at cutoff tau when it has arrived and has no direct replacement by tau:

    A_G(tau) = {c : t_c <= tau and no d satisfies t_c < t_d <= tau and G(d,c)}.

Equal timestamps do not establish replacement order.
Claims with unknown timestamps receive no historical certificate.
The current-answer path can retain them as unresolved evidence, matching the existing implementation.
Current equality claims must state this policy explicitly.

The evidence cutoff uses the supplied timestamp semantics.
A document date cannot establish an unobserved real-world validity date.
The existing corpora mix source dates and recorded change dates.
Report the timestamp type in each dataset description.

## Certificate definition

Define the first replacement time:

    b_G(c) = min {t_d : t_d > t_c and G(d,c)}, with min(empty set) = infinity.

Store one witness attaining this minimum.
Use the smallest claim identifier when several witnesses share that time.
The certificate is I_G(c) = [t_c, b_G(c)).
Witness identity supplies provenance.
Witness time determines eligibility.

## Theorem 1: all-cutoff compilation

For every finite cutoff tau:

    c belongs to A_G(tau) if and only if tau belongs to I_G(c).

Proof:
If t_c exceeds tau, both statements are false.
Otherwise, a direct replacement exists by tau exactly when b_G(c) <= tau.
Taking the complement gives the result.

Consequently, one witness per claim preserves every temporal eligibility decision.
The representation uses at most n witnesses.
It needs no claim partition, transitive closure, or gold tuple.

The original newest-witness detector gives the same final current mask.
Both methods mark c exactly when at least one qualifying later claim exists.
The earliest witness adds the boundary needed for historical queries.
This permits reuse of cached current answers after exact mask equality checks.
It does not permit reuse of cached historical retrieval scores.

## Corollary 1: prefix consistency

Let C_tau contain the claims with timestamps at most tau.
Compile the full corpus and query at tau.
The result equals the final current mask obtained from C_tau.

Proof:
Both procedures test the same pairs with t_c < t_d <= tau.
Claims after tau cannot enter either decision.

Appending claims after T therefore cannot change any earlier evidence state.
This result holds even when G contains matching errors.
Feature extraction must depend only on each claim, or each fixed claim pair.
Corpus-dependent feature updates require a separate analysis.

## Theorem 2: local influence of matching errors

Fix claim timestamps and identifiers.
Let G and H disagree on h temporally ordered claim pairs.
Let U contain the older endpoint of each changed pair.
Then, for every cutoff tau:

    A_G(tau) symmetric_difference A_H(tau) is a subset of U.
    |A_G(tau) symmetric_difference A_H(tau)| <= |U| <= h.

Proof:
Each boundary b(c) depends only on pairs whose older endpoint is c.
No such pair changes when c is outside U.
Its boundary and membership therefore remain unchanged.

This result bounds propagation, not matcher accuracy.
A changed timestamp can alter many ordered pairs.
A changed parser feature can also alter many gates.
Do not extend the h-pair bound to one arbitrary document edit.

## Corollary 2: context stability

Fix one complete candidate ranking and deterministic tie handling.
Filter this ranking by eligibility, then take at most k claims.
Let R_G(tau) and R_H(tau) denote the resulting contexts.
Then:

    |R_G(tau) symmetric_difference R_H(tau)| <= 2 min(k, |U|).

Proof:
Change one eligibility bit at a time.
Each change adds or removes at most one selected claim and one replacement.
The triangle inequality gives 2|U|.
Two contexts containing at most k claims differ in at most 2k positions.

The ranking must remain fixed across the compared compilers.
The theorem does not bound downstream answer changes.
One changed context item can still change the reader's answer.

## Exact time-local disagreement

For a claim c, two compilers disagree only between their replacement boundaries:

    c belongs to A_G(tau) symmetric_difference A_H(tau)
    iff min(b_G(c), b_H(c)) <= tau < max(b_G(c), b_H(c)).

For any query-time distribution mu, the expected mask difference equals:

    sum_c mu([min(b_G(c), b_H(c)), max(b_G(c), b_H(c)))).

The expected context difference is at most twice this quantity.
This gives an exact temporal footprint for each changed replacement decision.

## Proposition 3: closure can amplify one pair error

Use two independent keys and an integer m >= 2.
Key A contains value a at times 0, 1, ..., m-1.
It changes to b at time 2m.
Key B contains z at time m and changes to w at time 2m+1.
The four values a, b, z, and w differ.
All within-key gates are correct.

Now add exactly one false gate: w at 2m+1 replaces b at 2m.
This creates a bridge between the two component histories.
Consider the earlier cutoff tau = m + 1/2.

Direct compilation changes no eligibility decision at tau.
Only b's boundary changes, and b has not arrived yet.
Component compilation closes every earlier a claim at time m.
It therefore removes m eligible claims at this earlier cutoff.

Proof:
Correct replacement links connect all a claims to the later b claim.
They also connect z to w.
The false bridge joins those two components.
Within the merged component, z becomes each a claim's next distinct value.
All a intervals therefore end at m, rather than 2m.

This construction proves unbounded mask amplification from one pair error.
It also violates prefix consistency.
The prefix at tau contains neither bridge endpoint.
Adding k independent filler claims can produce a context difference of 2k for any k <= m.
Rank the a claims first and the filler claims next.
The direct context retains k a claims.
The component context replaces them with other claims.

Use this construction as a correctness test, not a benchmark performance claim.

## Minimal standalone representation

The linear witness count is optimal for arbitrary pair gates, up to word size.
Consider m older claims at time zero and m later claims at distinct times.
For each older claim, independently choose one later claim as its sole witness.
There are m^m different all-cutoff masks.
Any standalone representation distinguishing them needs at least m log2(m) bits.
Here n = 2m, giving an Omega(n log n) bit lower bound.
One boundary index per claim uses O(n log n) bits.

This lower bound excludes access to the original gates during queries.
Do not claim universal storage optimality when queries can recompute the entire detector.
The practical main text can omit this result.

## Streaming algorithm

1. Extract fixed text features for each dated claim.
2. Sort claims by timestamp and identifier.
3. Keep unresolved older claims in an inverted index.
4. Process all claims sharing a timestamp as one batch.
5. For each new claim, collect unresolved candidate claims from complete posting lists.
6. Evaluate G only for those candidates.
7. On a positive gate, record the current timestamp and witness identifier.
8. Remove the older claim from every posting list.
9. Insert the new batch only after all comparisons finish.
10. Give unresolved claims an infinite boundary.

Removal is safe because the scan has already found the earliest witness.
Batch insertion prevents tied claims from replacing each other.
Sorting identifiers makes witness selection deterministic.

For the supplied positive frame threshold, matching nonempty frames share a frame token.
All empty frames use one shared posting key.
These posting lists preserve every possible default-gate match.
Custom gates need a proved complete index or a full unresolved-claim scan.

Let L count posting entries and V count posting visits during compilation.
Let P count unique pair tests and g bound one gate evaluation.
Compilation costs O(n log n + L + V + Pg), excluding feature extraction.
Memory costs O(n + L + maximum candidate set size).
The certificate output costs O(n) words.
The worst case remains quadratic for uninformative blocks or long repeated-value runs.
Report observed pair tests and posting visits alongside wall time.
Do not call blocking unconditionally near-linear.

## Multi-hop support

For a path with certificates [s_i, e_i), simultaneous support is their interval intersection.
Its boundaries are max_i s_i and min_i e_i.
The path supports cutoff tau exactly when every edge supports tau.
Entity joins remain a separate requirement.
This composition rule is useful but standard.
It should not carry the novelty claim.

## Original theorem audit

The original conditional-exactness proposition is almost a restatement of the detector.
It needs exact value gates and correct temporal order, beyond exact key matching.
The uploaded PDF states these assumptions more accurately than the supplied TeX.

The original which-value lemma requires actual filtering, not demotion alone.
Demotion still includes stale evidence whenever the requested budget exceeds active claims.
The released implementation filters, so update the prose to match it.

The historical scorer uses a gold first claim to select the inferred component.
It also returns the stored gold value from that component.
Those cached scores measure component-conditioned history recovery.
They cannot support full-pool historical question-answering claims.

The interval implementation forms connected components from replacement edges.
It then uses stored gold values to distinguish values.
This differs from a fully text-derived historical compiler.
The direct compiler needs no value annotation after applying G.

Latest replacement edges do not identify first replacement times.
Sorting a valid component can recover them when component membership is correct.
That assumption creates the amplification and prefix-consistency failure above.

## Required evidence

- Verify current-mask equality on every available corpus.
- Compare all cutoffs with an exhaustive direct-pair oracle.
- Test repeated values, equal timestamps, undated claims, and shuffled inputs.
- Measure full-pool historical retrieval with text-only ranking and certificate filtering.
- Compare against exact extracted-key temporal filtering.
- Report natural full-versus-prefix violations for component compilation.
- Test one false bridge as a labeled correctness diagnostic.
- Report retained evidence and reader performance separately.
- Keep source-prose and benchmark-rendered text results separate.

Current status: theory is complete; empirical advantage still needs measurement.
