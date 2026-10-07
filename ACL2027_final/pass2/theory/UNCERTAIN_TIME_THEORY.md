# Two certificates for uncertain dates and interval questions

Status: derived theory with executable specification.
The theory concerns uncertainty in occurrence dates.
It does not equate occurrence uncertainty with a fact's validity duration.

## Problem

A text can date an update only to a month or year.
A question can also ask about a month or year.
Picking an arbitrary exact date changes which evidence appears stale.
Using only evidence that is certainly active at one fixed time can also discard required evidence.

The key distinction is between these questions:

- Could this evidence apply somewhere in the requested interval?
- Does this evidence apply somewhere in the interval under every allowed date assignment?

The second question need not have one common witness time across assignments.
Ordinary intersection with a certainly active interval answers a different question.

## Inputs and assumptions

Let C contain n claims.
Claim c has text, an identifier, and a closed occurrence interval [l_c,u_c].
Its unknown exact occurrence time x_c satisfies l_c <= x_c <= u_c.
Dates may use any consistent real-valued time axis.

Let G(d,c) be a fixed directed gate.
Require G(c,c)=false; every witness differs from its target.
It states that d replaces c if d occurs strictly after c.
The gate can be noisy and nontransitive.
The theorem is relative to this gate.
Text matching alone does not establish replacement semantics.
The gate cannot change with the chosen date assignment.

A possible world assigns every x_c independently within its interval.
For a given world x, c is active at time T exactly when

    x_c <= T and no d satisfies G(d,c) and x_c < x_d <= T.

Equal occurrence times do not retire each other.
This definition is the pass-1 direct policy with uncertain occurrence dates.

A closed query interval is Q=[a,b], where a<=b.
A claim supports Q in a world if it is active at some T in Q.
Point queries use a=b.

The four quantifiers are:

    possible point:     exists x: active_x(c,T)
    certain point:      for all x: active_x(c,T)
    possible interval:  exists x, exists T in Q: active_x(c,T)
    guaranteed interval: for all x, exists T in Q: active_x(c,T)

“Guaranteed interval” does not mean “active throughout the interval”.
It does not mean one time works in every world.

## Two direct certificates

Define

    p_c = min {u_d : G(d,c) and l_d > u_c},
    r_c = min {l_d : G(d,c) and u_d > l_c},

where the minimum of an empty set is positive infinity.
Store one direct witness attaining each minimum.
Ties use the smallest claim identifier.

The p witness must occur after c in every world.
The r witness can occur after c in at least one world.
The latter witness's earliest allowed time can precede c.
The comparison against l_c handles this strict-order boundary.

Each claim needs at most two witness records.
These are compiled certificates.
Their correctness requires a complete scan of accepted candidate witnesses.
The two records alone cannot verify that the compiler omitted no earlier witness.
A single witness can supply both records.
No connected component or equivalence class is required.

## Theorem 1: exact point decisions

For every finite T:

    possible(c,T) iff l_c <= T < p_c;

    certain(c,T) iff u_c <= T and (T <= l_c or T < r_c).

These conditions give exact marginal decisions under the product of date intervals.
They do not assert that every possible claim is jointly active in one world.

### Proof of the possible condition

If T<l_c, c has not occurred in any world.
Suppose T>=p_c.
A p witness has l_d>u_c and u_d<=T.
It therefore occurs strictly after c and by T in every world.
Thus c cannot be active.

Now suppose l_c<=T<p_c.
Choose x_c=min(u_c,T).
For each witness d, choose x_d<=x_c whenever its interval permits that choice.
If its interval does not permit that choice, l_d>x_c.
When x_c=T, that witness already occurs after T.
When x_c=u_c<T, the definition of p_c implies u_d>T.
Choose that witness after T.
Each witness then occurs no later than c or after T.
The independent intervals permit these choices simultaneously.
Thus c is active in this world. QED.

### Proof of the certain condition

Every world has x_c<=T exactly when u_c<=T.
Assume this condition.
A witness can retire c by T exactly when it can satisfy x_c<x_d<=T.
Choose the smallest allowed x_c=l_c.
A suitable x_d exists exactly when T>l_c, l_d<=T, and u_d>l_c.
Taking the minimum l_d over such witnesses gives T>l_c and r_c<=T.
Its complement is T<=l_c or T<r_c. QED.

The T<=l_c term is necessary.
For c=[0,0] and d=[0,1], c is certainly active at T=0.
No event can be strictly later than zero while occurring by zero.
For every T>0, some assignment lets d retire c by T.

## Theorem 2: exact interval decisions

For every closed interval Q=[a,b]:

    possible(c,Q) iff l_c <= b and a < p_c;

    guaranteed(c,Q) iff u_c <= b and (a <= l_c or a < r_c).

The result applies when the certainly active point set is empty.

### Proof of the possible condition

Theorem 1 gives the possible point set [l_c,p_c).
It intersects [a,b] exactly when l_c<=b and a<p_c.
The two existential quantifiers commute. QED.

### Proof of the guaranteed condition

In any world, c first becomes active at its own occurrence time x_c.
It remains active until the first strictly later direct witness.
If x_c lies in [a,b], it therefore supports Q at x_c.
If x_c<a, it supports Q exactly when no witness retires it by a.

If u_c>b, choose x_c>b.
That world supplies no support in Q.
Now assume u_c<=b.
A world lacks support exactly when a witness can satisfy x_c<x_d<=a.
As in Theorem 1, such a world exists exactly when a>l_c and r_c<=a.
Taking the complement proves the condition. QED.

## Why ordinary certain-interval filtering fails

Take c with occurrence interval [0,10].
Take d with exact occurrence time 5.
Let G(d,c) hold.
The certainly active point set of c is empty.
Before time 10, c might not have occurred.
From time 10 onward, c might have occurred before d and been retired.

Nevertheless, c supports Q=[0,10] in every world.
If c occurs before 5, it supports the early part.
If c occurs at or after 5, it supports the later part.
The relevant time depends on the world.

Thus

    for all x, exists T in Q: active_x(c,T)

cannot be replaced by

    exists T in Q, for all x: active_x(c,T).

The two-certificate query uses the correct order of quantifiers.

## Proposition 3: two witnesses can be necessary

The compiler uses at most two direct source witnesses per claim.
This bound is sharp among subsets of direct witness records.

Take c=[0,2], d=[1,4], and e=[3,5].
Accept precisely d->c and e->c.
The possible boundary is p_c=5, supplied by e.
The potential boundary is r_c=1, supplied by d.
Removing e changes possible support at time 5 from false to true.
Removing d changes certain support at time 2 from false to true.
Thus no single witness preserves all possible and guaranteed queries.

This is a source-witness subset result.
It is not a bit-complexity lower bound for arbitrary representations.
The current tie policy can retain two records when one tied witness would suffice.
The claimed bound is worst-case sharpness, not per-instance minimum cardinality.

## Corollary 1: sharp safe filters

The possible filter is the smallest retained set that never removes a supported claim in any allowed world.
Removing any further claim causes an error in a witnessing world.

The guaranteed filter is the largest retained set whose individual claims support Q in every allowed world.
Adding any further claim admits a claim without support in a witnessing world.

Every intermediate filter must decide which unresolved claims to retain.
The certificates expose this uncertainty without selecting an arbitrary exact date.
These are eligibility guarantees, not reader correctness guarantees.

## Corollary 2: refinement monotonicity

Suppose every date interval becomes narrower without excluding the true date.
The allowed worlds form a subset of the original worlds.
For every fixed query interval:

- the possible retained set can only shrink;
- the guaranteed retained set can only grow.

This follows directly from the existential and universal quantifiers.
It also provides a useful implementation invariant.

## Corollary 3: recovery of exact-date compilation

When l_c=u_c for every claim, possible and guaranteed decisions coincide.
Both use the earliest strictly later direct witness.
Point queries recover the pass-1 compiler exactly.
Interval queries retain a claim precisely when its direct validity interval overlaps the query.

## Corollary 4: local gate influence

Suppose gates G and H differ on h directed pairs.
Let U contain the targets c of those pairs.
For either query policy and any query interval, the changed eligibility set is a subset of U.
Its size is at most |U|<=h.

Each claim's two boundaries depend only on gates targeting that claim.
All other certificates remain unchanged.
For a fixed candidate ranking, filtering then taking k claims changes at most 2 min(k,|U|) context items.
This extends the pass-1 locality result.
A date edit can affect many directed pairs and has no analogous one-claim guarantee.

## Endpoint representation

The possible point set is [l_c,p_c).
The certain point set is

    {T: T>=u_c and (T<=l_c or T<r_c)}.

Usually it is [u_c,r_c), or empty.
When u_c=l_c and r_c<=l_c, it contains the singleton {l_c}.
An ordinary half-open interval cannot represent that singleton correctly.
Store the exact comparison rule or an explicit endpoint flag.

The interval query needs both l_c and u_c.
It also needs the two retirement boundaries.
Do not derive guaranteed interval answers by intersecting the certain point set.

## Compiler and cost

Evaluate each candidate directed gate once.
For each accepted pair d->c:

1. If l_d>u_c, update p_c with u_d.
2. If u_d>l_c, update r_c with l_d.
3. Store the smallest identifier on a boundary tie.

The reference implementation evaluates all n(n-1) directed pairs.
If m accepted pairs are supplied, boundary construction costs O(n+m).
Its output uses O(n) records.
Each claim query takes O(1) time.
A full eligibility mask takes O(n) time.
Complete text blocking can reduce gate evaluations, without changing the proofs.
The method does not imply subquadratic pair discovery.

## Necessary scope

A date interval represents uncertainty about one occurrence.
It does not mean the claim is valid throughout that interval.
A fact explicitly valid from January through March has different semantics.
Such known validity intervals should enter a separate direct overlap path.

The sharpness proofs assume independent date assignments.
If external constraints correlate dates, the product model may contain impossible worlds.
The possible filter remains safe but can retain extra claims.
The guaranteed filter remains safe but can retain fewer claims.
The exactness claim then requires the richer constraint model.

The text gate remains responsible for replacement versus coexistence.
A possible retirement certificate is not evidence that the text gate is semantically correct.
The earlier open-world impossibility still applies.

## Prior-work boundary

Possible-world semantics for uncertain temporal data already exists.
Certain-current answers under partial currency orders also exist.
The proposed contribution is narrower: two direct witnesses answer all point and interval support queries under this policy.
Its relevance depends on natural coarse dates, actual interval questions, and empirical comparisons.
The final paper must cite uncertain temporal databases and avoid claiming invention of certain/possible semantics.

## Exact context stability

Fix a complete strict ranking and a budget k.
The ranking resolves all score ties and remains fixed across worlds.
Let M_x(Q) be the support mask in world x.
Let P(Q) be the union of those masks.
Let H(Q) be their intersection.
Write Top_k(S) for the first k ranked claims in S.

**Theorem 5: exact context stability.**
For any nonempty family of worlds, every world returns the same context exactly when

    Top_k(P(Q)) = Top_k(H(Q)).

**Proof.**
Every mask lies between H and P.
Equal endpoint contexts therefore force the same context for every intermediate mask.
Conversely, suppose every world returns context C.
Every member of C then belongs to H.
If |C|<k, any possible outsider would change a world's context.
Thus P=H=C in this case.
If |C|=k, a possible outsider cannot outrank any member of C.
Such an outsider would enter in a witnessing world.
Thus Top_k(P)=C, and C subset H subset P gives Top_k(H)=C.
For k=0, both sides return the empty context. QED.

This theorem does not require independent worlds.
It requires exact union and intersection masks.
With conservative outer and inner masks, equality remains sufficient for stability.
Inequality then need not establish an unstable context.

`stable_context` implements this test without enumerating worlds.
It validates a complete ranking, unique identifiers, finite query bounds, and a nonnegative integer budget.
It returns both endpoint contexts and their common context when stable.
Uncertain claims below the retrieval budget can leave the context invariant.
The guarantee concerns retrieved evidence rather than generated answers.
