# Exact decisions under source constraints

Let each event date be an integer within its inclusive bounds.
Let `G(d,c)` identify accepted direct replacement pairs.
Let `C` contain source inequalities of the form `x_i - x_j <= b`.
The feasible family contains all bounded assignments that satisfy `C`.
The algorithm first verifies that this family is nonempty.

A known order `x_i < x_j` becomes `x_i - x_j <= -1`.
An explicit end `z_c` requires `x_c - z_c <= -1`.
Add the replacement pair `z_c -> c`.
This representation permits overlapping start and end bounds.
The constraint removes invalid lifetimes from the feasible family.

## Exact support oracle

Let the query window be `[a,b]`.
Let `D(c)` contain the accepted replacements of claim `c`.
The following formulas characterize support in one feasible assignment.

**Overlap:**

\[
 S^{\mathrm{overlap}}_x(c,[a,b])
 \iff x_c\le b\ \land\!
 \bigwedge_{d\in D(c)}(x_d\le x_c\ \lor\ x_d\ge a+1).
\]

If `x_c > b`, no query date follows the claim's start.
Otherwise, the first possible supporting date is `max(a,x_c)`.
An accepted replacement removes support precisely when `x_c < x_d <= a`.
Its negation gives the displayed disjunction.

**Throughout:**

\[
 S^{\mathrm{throughout}}_x(c,[a,b])
 \iff x_c\le a\ \land\!
 \bigwedge_{d\in D(c)}(x_d\le x_c\ \lor\ x_d\ge b+1).
\]

The claim must start by the first query date.
Any later replacement by `b` breaks support at that date.
Replacement at `b` therefore invalidates throughout support.

**Appointment:**

\[
 S^{\mathrm{appointed}}_x(c,[a,b])\iff a\le x_c\le b.
\]

Appointment support describes the start event.
It does not require continued activity after that event.

For possible support, the oracle asks whether one feasible assignment satisfies the selected formula.
Each disjunction has two difference-constraint alternatives.
The oracle explores every alternative unless its current conjunction is infeasible.
Each successful branch returns a concrete assignment.

Guaranteed support holds exactly when no feasible assignment satisfies the formula's negation.
For overlap, the negation is

\[
 x_c\ge b+1\quad\lor\quad
 \bigvee_{d\in D(c)}(x_c+1\le x_d\le a).
\]

For throughout, replace the first threshold by `a+1` and the last threshold by `b`.
For appointment, test `x_c <= a-1` and `x_c >= b+1`.
Every branch is a conjunction of difference constraints.

A difference constraint becomes one weighted graph edge.
Bounds use an additional zero node.
The feasibility algorithm initializes every distance to zero.
It repeatedly relaxes every edge.
A negative cycle proves infeasibility.
Without a negative cycle, final distances satisfy every inequality.
Subtracting the zero-node distance makes that node zero without changing any date difference.
All weights are integers, so the returned dates are integers.

These observations prove exact possible and guaranteed support.
They also prove the validity of each returned assignment.
Let `d` be the target's incoming degree.
Possible support can require exponentially many branches in `d`.
Guaranteed support needs at most `d+1` feasibility checks for overlap or throughout.
The implementation makes no constant-time claim for constrained support.

## Stability over an arbitrary feasible family

Let `Omega` be any nonempty family of allowed timelines.
The family can contain dependent event dates.
Let `S_x` be any timeline's support set under one fixed query predicate.
Define

\[
 P=\bigcup_{x\in\Omega}S_x,
 \qquad H=\bigcap_{x\in\Omega}S_x.
\]

Fix a complete strict relevance ranking and a nonnegative budget `k`.
Then every timeline selects the same ordered context exactly when

\[
 \operatorname{Top}_k(P)=\operatorname{Top}_k(H).
\]

**Proof.**
Let `T = Top_k(P)`.
If `T` is contained in `H`, every timeline retains every item in `T`.
No other possible item ranks before this context.
Thus every timeline selects `T`.

Otherwise, choose `c` in `T` but outside `H`.
One timeline supports `c`, and another does not.
At most `k-1` possible claims outrank `c`.
Every timeline supporting `c` therefore selects it.
The two timelines have different contexts.
For `k=0`, every context is empty.

The proof uses no independence assumption.
It also permits fixed fallback items in every operational support set.
The support oracle must use the same query predicate for every timeline.

## Hybrid screening and selective exact queries

Let `Omega_0` be the independent product of all date bounds.
Let the nonempty constrained family `Omega` be a subset of `Omega_0`.
For the overlap predicate, the original compiler gives exact product sets `P_0` and `H_0`.
Set inclusion gives

\[
 H_0\subseteq H\subseteq P\subseteq P_0.
\]

If `Top_k(P_0)=Top_k(H_0)`, that context is stable in the constrained family.
No support solver call is necessary after the model's initial feasibility check.

Otherwise, scan the fixed ranking.
Skip each claim outside `P_0`.
Accept each claim in `H_0` as guaranteed.
For every other relevant candidate, obtain exact constrained support from the oracle.
Stop when `k` possible claims have entered the context.
Report stability precisely when every selected claim has guaranteed support.

Each skipped claim is impossible in the constrained family.
Each accepted product-guaranteed claim remains guaranteed in that family.
The exact oracle resolves every remaining candidate used by the scan.
The selected context is therefore exactly `Top_k(P)`.
The preceding theorem proves the reported stability decision.

For instability, choose the first selected claim without guaranteed support.
The oracle supplies a supporting assignment and an excluding assignment.
Fewer than `k` possible claims outrank that pivot.
The supporting assignment therefore selects it.
The excluding assignment cannot select it.
Thus the returned contexts differ.

The hybrid benchmark counts each context request independently.
It does not reuse support answers across queries or budgets.
The full-oracle baseline queries every visible claim for each context request.
The added lazy baseline scans the ranking and stops after selecting the requested number of possible claims.
It uses the same exact query API as the hybrid.
The hybrid uses the same exact oracle for unresolved claims.
Measured savings therefore count avoided oracle work, with unchanged query semantics.
The hybrid uses 13,343 claim queries, compared with 33,180 for lazy exact selection.
The corresponding feasibility counts are 62,952 and 141,992.
All 10,080 contexts and stability decisions match the exhaustive reference.

## A failure under date-dependent ranking

Take two claims with independent starts in `[0,1]` and no replacement pairs.
Use point query `1` and budget `1`.
Both claims have guaranteed support.
Any fixed ranking therefore gives a stable context.

Now rank by descending realized start date.
The assignment `(1,0)` selects the first claim.
The assignment `(0,1)` selects the second claim.
The support sets remain identical while the context changes.
This example identifies the exact role of the fixed-ranking assumption.

## Scope of the hardness result

The existing reduction varies the context budget with the Set Cover input.
It proves hardness when that budget forms part of the input.
It does not prove hardness for budget five.
The useful separation concerns the tasks themselves.
Exact stability can avoid constructing the complete attainable context envelope.
