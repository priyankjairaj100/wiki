# Constructive context uncertainty

This note uses the pass-2 independent event-date model.
The directed replacement gate and complete strict ranking remain fixed.
The query is a closed interval `Q=[a,b]`.
Each world supports a claim somewhere within that interval, as defined previously.
Explicit ends follow the proved hidden-event reduction.

Let `P` contain possibly supported claims.
Let `H` contain guaranteed claims.
Let `F` contain fixed fallback items with unknown temporal support.
The actual retrieval mask in world `x` is `M_x union F`.
The context budget is `k`.

Write `Top_k(S)` for the first `k` ranked items in `S`.
Define the refinement frontier:

    U = Top_k(P union F) \ (H union F).

These are unresolved items that appear in the possible context.
This definition does not enumerate every item that could enter some realized context.

## Theorem 1: constructive instability

If the context is unstable, two witnessing date assignments can be constructed in `O(n)` time after compilation.
Here, `n` counts modeled events and fixed fallback items.
The quantity `m` counts accepted directed pairs.
The worlds use `O(n)` output space.
One selected pivot appears in the first context and disappears from the second.
The construction never treats marginal support decisions as independent.

### Proof

The existing exact stability theorem implies `U` is nonempty.
Choose any `c` in `U`.
At most `k-1` items in `P union F` outrank `c`.
Every realized context draws from this possible mask.
Therefore, every world supporting `c` selects it.

We now construct one world supporting `c`.
Let `t=max(a,l_c)` and assign `x_c=min(u_c,t)`.
The possible-support formula gives `t<=b` and `t<p_c`.
For every nonpivot event `d`, choose its date as follows:

    if l_d <= x_c: x_d = l_d;
    otherwise:    x_d = u_d.

In the first case, `d` is not strictly later than `c`.
In the second case, `u_d>t`.
To see this, first consider `x_c=t`.
Then `u_d>=l_d>x_c=t`.
Otherwise, `x_c=u_c<t` and `l_d>u_c`.
Such a witness enters the definition of `p_c`.
Thus `u_d>=p_c>t`.
Every incoming witness occurs no later than `c`, or after `t`.
The same rule makes valid choices for all events outside the incoming witness set.
Those choices do not affect whether `c` is active.
Independence makes these assignments jointly valid.
Claim `c` is active at `t` and therefore supports the query.

Next, construct a world without support for `c`.
If `u_c>b`, assign `x_c=u_c`.
Then the claim starts after the query.
Set every other event to its lower bound.

Otherwise, guaranteed support fails with `u_c<=b`.
The guaranteed-support formula then gives `a>l_c` and `r_c<=a`.
Let `d` be the stored witness for `r_c`.
Set `x_c=l_c` and `x_d=min(u_d,a)`.
The witness conditions imply `l_d<=x_d<=u_d` and `l_c<x_d<=a`.
Thus `d` retires `c` by the query start.
The claim has no support anywhere in the query interval.
Assign all remaining dates their lower bounds.

The first world must select `c`.
The second cannot select `c`.
Their contexts therefore differ.
Constructing both assignments scans only the event bounds and the pivot certificate.
It takes `O(n)` time and needs no retained pair list.
Evaluating both contexts scans all accepted pairs and the fixed ranking.
This optional replay takes `O(n+m)` time, without sorting or world enumeration. QED.

Direct context replay reuses the accepted pair list.
That full audit state uses `O(n+m)` space.
The two-witness certificate alone stores support boundaries in `O(n)` space.
It does not store every replacement pair needed for arbitrary world evaluation.
The pivot's rank condition proves that the constructed contexts differ before this optional replay.

The returned dates are complete source-event assignments.
They are not just two incompatible combinations of marginal masks.
For finite rational input bounds, every returned date is rational.
The construction uses bounds and query endpoints only.

## Theorem 2: unavoidable frontier resolution

Refine any event bounds to nonempty subintervals.
Keep the same claims, accepted pairs, query, ranking, budget, and fallback policy.
If the refined context is stable, every current frontier claim becomes guaranteed or impossible.

### Proof

Let `P'` and `H'` denote the refined support sets.
Refinement monotonicity gives `P' subset P` and `H subset H'`.
Take a current frontier item `c`.
Suppose it remains possible after refinement.
Originally, fewer than `k` items in `P union F` outrank `c`.
The refined possible set cannot introduce additional higher-ranked items.
Therefore, `c` remains in `Top_k(P' union F)`.
Stable context requires every item in this possible context to belong to `H' union F`.
The pivot is modeled, so it does not belong to `F`.
Thus `c` must belong to `H'`.
Alternatively, it must leave `P'` and become impossible. QED.

Every current frontier item is therefore an unavoidable support decision.
The theorem does not identify a minimum set of date fields to resolve.
One date refinement may settle several frontier items.
Several date refinements may be needed for one item.

Resolving the current frontier is necessary, but not sufficient.
Removing an item can expose a new unresolved item below the budget.
For example, rank `c` before `d`, with `k=1` and query time `1`.
Give both claims start bounds `[0,2]` and no replacements.
Initially, the frontier is `{c}`.
Refine `c` to the exact start `2`.
The frontier becomes `{d}`.

## Proposition 3: the full possible context envelope is hard

Consider this decision problem:

> Can a specified claim appear in the top-k context of any allowed date world?

This problem is NP-hard under the direct replacement model when `k` is part of the input.
Hardness holds for a point query and a bipartite gate with one edge layer.
All uncertain dates can use `[1,3]`.
All other dates can be exactly `0`.
The candidate can have guaranteed temporal support.

### Reduction from Set Cover

Take a Set Cover instance with universe `E`, sets `S_1,...,S_s`, and budget `K`.
Assume `1<=K<=s`.
Create these claims:

- A variable claim `v_j` for each set, with date bounds `[1,3]`.
- `K+1` element claims for every element of `E`, all dated exactly `0`.
- The candidate claim `c`, dated exactly `0`.

Accept `v_j -> e_copy` when `e` belongs to `S_j`.
Accept no other pairs.
This gate is bipartite, with one edge layer from variables to element copies.

Rank every variable and element claim above `c`.
Use query time `2` and context budget `k=K+1`.
The candidate has no incoming gate and is always supported at this query.

At time `2`, variable `v_j` is active exactly when its date is at most `2`.
Every active variable starts strictly after its associated element copies.
It therefore retires those copies by the query time.
An inactive variable starts after the query and cannot retire any copy by that time.

Suppose a cover uses at most `K` sets.
Assign their variables date `1` and every other variable date `3`.
All element claims are retired.
At most `K` higher-ranked variables remain active.
Thus `c` enters the top `K+1` context.

Conversely, suppose some world selects `c`.
At most `K` higher-ranked claims can then be active.
Let `J` contain variables whose dates are at most `2`.
Every such variable is active, so `|J|<=K`.
If these sets miss an element, all its `K+1` copies remain active.
Those copies alone would exclude `c`.
Therefore, the sets indexed by `J` cover `E` within budget `K`.

The construction has polynomial size because `K<=s`.
It is equivalent to the original Set Cover decision.
Thus possible top-k membership is NP-hard. QED.

The reduction does not establish hardness for any fixed context budget, such as `k=5`.

### Variant with every start at or before the query

Hardness also holds when every event must occur by the query time.
This variant uses two edge layers instead of one.
Give every variable bounds `[0,2]` and every element copy exact date `1`.
Give the candidate exact date `2`.
Add a clock event at exact date `1`, ranked below the candidate.
The clock replaces every variable if it occurs strictly later.
Keep the variable-to-element pairs from the first reduction.
Use query time `2` and budget `K+1`.

A variable dated below `1` is retired by the clock.
A variable dated at least `1` remains active.
Only variables dated after `1` retire their element copies.
A cover sets its selected variables to `2` and all others to `0`.
Conversely, a selected candidate permits at most `K` active higher-ranked variables.
The variables after `1` must cover every element, or `K+1` active copies exclude the candidate.
Variables exactly at `1` add cost without covering elements and cannot invalidate this converse.
The gate is acyclic, with clock-to-variable and variable-to-element edge layers.

This result does not claim that uncertainty-aware ranking is a new problem.
It identifies a complexity boundary within the specific direct replacement model.
Exact support masks and exact context stability remain linear after pair discovery.
Enumerating every possibly selected item can require solving a harder joint problem.

The independent protocol review supplied this one-edge-layer reduction.
The code checks small reduction instances exhaustively.
Those checks supplement the proof but do not prove hardness.

## Practical use

An unstable context can return one pivot and two concrete source timelines.
The timelines show the decision that missing date precision can change.
The frontier identifies support decisions that a successful refinement must settle.
The pipeline can inspect the corresponding original source dates first.
After refinement, it recompiles the certificates and checks the frontier again.
This procedure claims no minimum clarification cost.
