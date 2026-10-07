# Retirement requires negative information

Status: pass 2 theory audit and executable specification.
This note distinguishes established logical facts from proposed research contributions.
It does not claim new cardinality or closed-world semantics.

## Recommendation

The research problem is deciding when a newer fact permits removal of older evidence.
Text similarity can identify a shared subject and attribute.
It does not identify whether two values can coexist.
A new positive fact alone cannot solve that second task.

Use this distinction to define the evaluation and method contract.
Retain the pass-1 compiler as an efficient implementation of supplied retirement decisions.
Do not present that compiler as a semantic retirement detector.
Do not treat the bitemporal skyline as new.

A strong system must distinguish these input types:

1. A positive observation establishes that a value applies at its stated validity time.
2. An explicit cessation establishes that a named value does not apply.
3. A complete state declaration excludes values outside its stated set.
4. A declared capacity limits the number of values that can apply simultaneously.

The method can extract these types from text.
The logical guarantees start after extraction.
An empirical study must measure extraction errors separately.
Source dates alone do not establish validity intervals or complete states.

## 1. Positive observations do not identify retirement

Let a key denote one subject and attribute.
Its state at time t is an arbitrary finite set S(t) of values.
A positive observation (t,v) states only that v belongs to S(t).
We consider values a and b, where a differs from b.
The observed history is O = {(t0,a),(t1,b)}, with t0 < t1.

**Theorem 1: retirement is not identifiable from positive observations.**
There exist two state histories consistent with O.
One makes a absent at t1.
The other keeps a present at t1.
Thus no rule using only O can always decide whether to suppress evidence for a at t1.

**Proof.**
Set S_R(t0)={a} and S_R(t1)={b} in the replacement history.
Set S_C(t0)={a} and S_C(t1)={a,b} in the coexistence history.
Both histories satisfy every observed positive statement.
Their correct decisions for a at t1 differ. QED.

The proof also permits arbitrarily many corroborating statements for b.
It permits exact subject and relation matching.
It therefore applies after a perfect matching stage.
Without additional semantics, higher matching confidence does not resolve retirement.

**Corollary 1: sharp two-world error bound.**
Suppose a randomized rule suppresses a with probability p after seeing O.
Its false-removal probability in S_C is p.
Its stale-retention probability in S_R is 1-p.
Their sum equals one, so the worst error is at least one half.
A fair random choice attains the bound.

For m independent ambiguous keys, a uniform distribution over the 2^m histories forces m/2 expected mistakes.
Therefore the minimax expected number of mistakes is at least m/2.
A deterministic rule incurs m mistakes on a suitable history.
These are decision lower bounds, not benchmark performance claims.

## 2. Exact exclusion with typed observations

Fix one query time and one key.
Let U be a finite domain of possible values.
Let P be values positively established at that time.
Let N be values explicitly excluded at that time.
Let q be a declared upper bound on simultaneous values, or infinity.
Let complete be a source assertion that P lists every current value.

The compatible states are

    W(P,N,q,complete) = {S subset U:
        P subset S,
        S intersect N = empty,
        |S| <= q,
        and (complete implies S = P)}.

Require W to be nonempty.
An inconsistent input does not justify arbitrary exclusion.
The implementation returns an explicit inconsistency error.

For a target v in U, call exclusion sound if v is absent from every compatible state.
Call it maximally permissive if it excludes every target whose absence is entailed.

**Theorem 2: maximal sound exclusion.**
Suppose the constraints are consistent.
A target v is certainly present exactly when v belongs to P.
A target v is certainly absent exactly when at least one condition holds:

- v belongs to N;
- complete is true and v does not belong to P;
- q is finite, |P|=q, and v does not belong to P.

Every other target is unresolved.

**Proof.**
Each exclusion condition directly forbids a state containing v.
Now suppose no exclusion condition holds and v does not belong to P.
The state P excludes v and satisfies all constraints.
The state P union {v} also satisfies the constraints.
It avoids N, has at most q members, and complete is false.
Thus neither presence nor absence is entailed.
For v in P, every compatible state contains v. QED.

The theorem is standard open-world model reasoning.
Its proposed role is to define a testable retirement contract for temporal retrieval.
Capacity and completeness are input assertions, not quantities inferred from the largest observed set.
A historically observed maximum cannot certify an upper bound.

## 3. Minimal support for a capacity certificate

Assume no explicit negative or complete-state assertion excludes v.
A capacity-q certificate contains q distinct positive values other than v.
It also cites the capacity declaration and their common validity time.

**Proposition 3: q positive values are necessary and sufficient.**
A capacity-q certificate proves absence of v.
Any certificate containing fewer than q distinct positive values cannot prove absence from these premises alone.

**Proof.**
The q values fill the available capacity, so including v violates the bound.
With fewer than q values, adding v respects the bound.
That state supplies a countermodel. QED.

Repeated evidence for the same value does not increase the number of occupied positions.
A pairwise retirement rule corresponds only to q=1.
For larger q, sound exclusion can require evidence from several observations.
This is an application of established maximum-cardinality reasoning.
It is not a new description-logic result.

## 4. Temporal scope is essential

The preceding rule requires observations that share a validity time.
A common publication date does not suffice.
A common calendar year does not establish simultaneity.

**Proposition 4: coarse time labels do not certify conflict.**
Consider a relation with capacity one at each instant.
Let a hold during the first part of a year.
Let b hold during the remaining part.
Both values can be valid answers to a question whose time label names that year.
Their joint appearance in the annual answer set does not violate capacity one.

The model must therefore distinguish:

- exact-time validity;
- validity at some time within a time bin;
- validity throughout a time interval;
- publication or observation time.

A capacity certificate applies only to common-time validity.
A complete benchmark answer set can define evaluation acceptance without becoming detector input.
The source semantics of TempLAMA must be checked before describing its annual multiplicity as simultaneous coexistence.

## 5. A current exclusion is not permanent retirement

Suppose S(t0)={a}, S(t1)={b}, and S(t2)={a}, with t0<t1<t2.
Absence at t1 does not imply absence at t2.
A certificate must state the time or interval it supports.
A single irreversible boundary for a value cannot represent this history.

Claim-level intervals and value-level validity have different meanings.
A later statement can end a claim's eligibility under a declared update policy.
That does not prove the claim's object never becomes valid again.
Reappearance requires a new active episode or a time-local exclusion rule.

## 6. Retrieval metrics must test preservation

Hit@k checks whether at least one accepted value is retrieved.
It does not test preservation of all accepted values.
For an answer set of size m, returning one valid value achieves Hit@1=1.
Its answer coverage equals 1/m.
Thus perfect Hit@1 can coexist with arbitrarily low complete-answer coverage.

Report these quantities separately:

- Any-answer hit: the context contains at least one accepted value.
- Answer coverage: the fraction of accepted values represented in the context.
- Stale inclusion: the fraction of retrieved values outside the accepted set.
- Harmful removal: accepted evidence removed by the temporal filter.
- Complete-set recovery: all accepted values appear, with no unaccepted values.

The final quantity requires a clearly defined finite answer set.
For incomplete annotations, label unsupported values separately from proven stale values.
A source passage can remain useful evidence even when its object no longer answers the current query.
Use the task's answer semantics when assigning stale labels.

## 7. Implemented contract

`retirement_logic.py` accepts typed time-local observations.
It returns PRESENT, ABSENT, or UNRESOLVED.
Every ABSENT decision carries a source-level certificate.
It checks explicit exclusion before a complete declaration, then capacity saturation.
The output records the certificate kind and supporting values.

The module does not inspect benchmark labels.
It does not infer closure from timestamp order.
It does not claim that text extraction is solved.
It supports a matched extraction experiment if a text extractor supplies these assertions.

`test_retirement_logic.py` enumerates finite state models.
The test checks exact agreement between the implementation and all compatible models.
It also checks duplicate handling, inconsistent assertions, witness minimality, and the two-world bound.

## Contribution assessment

The logical core is established.
A paper can contribute a new temporal retrieval evaluation, a measured failure mechanism, and an effective implementation.
That requires natural source evidence and competitive end-to-end results.
The theorem alone does not establish a strong ACL contribution.

Prior work includes OWL maximum-cardinality semantics and RDF completeness reasoning.
Modern memory systems also expose single-valued and multi-valued update policies.
The final paper must compare against those policies directly.
