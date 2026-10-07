# Candidate for the second pass: two-clock direct evidence

Status: theory and executable specification only.
This note reports no benchmark result.
The present benchmark bundle does not supply both clocks consistently.

## Question

Which evidence applied at event time tau, using only records available at knowledge time sigma?
An announcement and its effective date can differ.
A later report can also describe an earlier event.
One timestamp cannot represent both cases.

## Definition

Each claim c has a valid start a_c and an arrival time r_c.
Both are finite, source-attributed observations.
They need not appear in the same order.
Let G(d,c) remain a fixed direct replacement gate.
As before, the gate can be nontransitive.

The visible corpus at the two cutoffs is:

    V(tau,sigma) = {c : a_c <= tau and r_c <= sigma}.

A visible claim remains eligible when no visible claim directly replaces it:

    A_G(tau,sigma) = {c in V(tau,sigma):
        no d has a_c < a_d <= tau, r_d <= sigma, and G(d,c)}.

Equal valid starts remain unordered under this definition.
It does not resolve competing corrections with the same valid start.
That task needs an explicit revision or authority policy.

## Witness frontiers

For each c, form candidate witness points:

    P_c = {(a_d, max(r_d,r_c), d) : a_d > a_c and G(d,c)}.

The second coordinate clips arrival to the source claim's arrival.
This clipping matters for minimality.
Before r_c, the source claim is absent regardless of its witnesses.
Two witnesses arriving before r_c therefore have the same effective knowledge boundary.

A point p dominates q when both coordinates of p are at most q's coordinates.
Retain the nondominated coordinate pairs.
Keep one witness identifier for each duplicate pair.
Call this frontier F_c.

The compiled query is:

    c is eligible iff a_c <= tau, r_c <= sigma,
    and no (u,v,d) in F_c satisfies u <= tau and v <= sigma.

This is a two-dimensional dominance query.
For increasing valid starts, retained arrival coordinates strictly decrease.
Each frontier is therefore a staircase.

## Theorem 1: exactness for every cutoff pair

The frontier query equals A_G(tau,sigma) for every finite pair of cutoffs.

Proof:
When the source is absent, both decisions exclude it.
Otherwise sigma is at least r_c.
Thus r_d <= sigma exactly when max(r_d,r_c) <= sigma.
Each witness excludes the source on its upper-right coordinate rectangle.
A dominated point's rectangle lies inside its dominator's rectangle.
Removing dominated points therefore preserves their union.
Every finite point set has a nondominated point below each removed point.
The frontier preserves the complete exclusion region.

## Theorem 2: minimal witness subset

Every distinct point in F_c is necessary within subsets of the original witnesses.
Consequently, F_c has minimum cardinality among exact witness subsets.

Proof:
Consider a frontier point p = (u,v).
Query exactly at tau = u and sigma = v.
The source exists because u > a_c and v >= r_c.
Point p excludes it.
Another witness could replace p only if its effective point were coordinatewise below p.
That would contradict p's nondominance, unless the two points were equal.
Duplicate points require only one representative.
Each remaining frontier point is therefore necessary.

The result concerns subsets of witness records.
It does not establish minimum bits among arbitrary data structures.
A shared event ledger or rectangular decomposition can represent the same state function.

## Corollary: knowledge-prefix consistency

Restricting the corpus to arrivals at or before sigma gives the same answer at knowledge cutoff sigma.
Later arrivals cannot change any earlier knowledge state.
This remains true when they describe earlier valid events.
The gate must remain fixed across the compared prefixes.

## Theorem 3: local influence

Fix both clocks and the candidate ranking.
Suppose G and H differ on h valid-time-ordered pairs.
Let U contain their older valid-time endpoints.
At every cutoff pair:

    A_G(tau,sigma) symmetric_difference A_H(tau,sigma) is a subset of U.
    |R_G(tau,sigma) symmetric_difference R_H(tau,sigma)| <= 2 min(k,|U|).

Proof:
Only the older endpoint's candidate witness set changes for each altered pair.
All other frontiers remain identical.
The fixed-ranking context bound follows from one-bit replacements.

One pair edit can change many records inside its source frontier.
It still changes at most one claim's eligibility at each query.
Thus record sensitivity and decision sensitivity differ.

## Why one replacement time is insufficient

Use source c with valid start 0 and arrival 0.
Witness d has valid start 20 and arrival 1.
Witness e has valid start 10 and arrival 2.
Both gates accept replacement of c.

The frontier contains (20,1) and (10,2).
At valid cutoff 15 and knowledge cutoff 1.5, c remains eligible.
At the same valid cutoff and knowledge cutoff 2, e excludes c.
A single final replacement time of 10 loses the first answer.
A single replacement time of 20 loses the second answer.
An additional single arrival boundary cannot recover the missing staircase.

This example establishes a representation limitation.
It does not prove that every existing memory system loses this history.
Systems can retain interval versions, source events, or transaction histories.

## Storage boundary

Single-clock compilation stores one boundary per claim.
Two clocks can require many incomparable witnesses per claim.
The explicit frontier representation can therefore require Theta(n squared) witness records.

Construction:
Take m source claims with valid start zero and arrival zero.
Add m witnesses with points (j,m-j+1), for j from 1 through m.
Every witness directly replaces every source claim.
No witness dominates another.
Each source therefore needs m witness records under the subset criterion.
There are 2m claims and m squared source-witness records.

This is a worst-case bound for explicit per-source frontiers.
The example permits sharing because all source frontiers coincide.
Do not claim a universal quadratic storage lower bound for every representation.

## Construction and queries

For each source, enumerate accepted witnesses and clip their arrival coordinates.
Sort by valid start, effective arrival, and identifier.
Scan in that order and retain only strictly smaller arrival coordinates.
This constructs the nondominated frontier.

If the source has d candidate witnesses, construction costs O(d log d).
Its frontier requires O(f) witness records, where f is its frontier size.
Binary search finds the last frontier point whose valid start does not exceed tau.
Its arrival coordinate is the smallest among all preceding points.
The source is excluded exactly when that coordinate does not exceed sigma.
Query time is O(log f) per source.

The prototype scans all claim pairs for clarity.
Complete candidate indexes can reduce enumeration without changing the semantics.
Streaming insertion and deletion require further design.
Deleting a dominated witness is easy.
Deleting a frontier witness may reveal previously dominated witnesses.
The frontier alone cannot support exact arbitrary deletions.
Retain the underlying accepted pairs or a suitable dynamic index for that operation.

## Relation to prior work

Bitemporal databases already separate valid time and transaction time.
Their histories can answer what was valid and what was known.
Temporal memory systems already expose both timestamp families.
Graphiti already selects direct contradiction times for invalidation.
MemStrata already describes deterministic supersession within a bitemporal ledger.
Pareto frontiers and orthogonal dominance queries are also standard.

The candidate contribution needs a narrower claim:

- Direct text-derived gates can be noisy and nontransitive.
- One-clock certificates do not preserve every two-clock query.
- Witness frontiers give an exact minimal witness subset under these gates.
- The frontier preserves local influence without converting pair matches into entity equivalence.
- Real delayed reports could establish when this distinction changes retrieved evidence.

These observations alone do not establish sufficient research novelty.
The paper needs a prior-art comparison and a real two-clock benchmark.
It must compare against exact bitemporal snapshots or interval versioning.
It must also compare against a direct Graphiti-style implementation with retained history.
Comparing only against a mutable single interval would be weak.

## Required next evidence

Find records with both event-effective dates and publication or observation dates.
Preserve original text, source identifiers, and both timestamp extractions.
Use a public benchmark or naturally dated source archive.
Do not generate delayed arrivals and present them as benchmark evidence.
Use event-ordered and arrival-ordered slices to measure available state differences.
Evaluate both retrieval correctness and frontier size.
Measure query cost against bitemporal interval versions.
Audit ambiguous or missing dates separately.

The accompanying prototype and tests validate the specification only.
