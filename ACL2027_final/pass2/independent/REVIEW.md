# Independent review of uncertain-start retrieval

Reviewed during pass 2. This review uses an independently written finite-model
oracle. It does not reuse the theory agent's compiler implementation.

## Verdict

The four proposed formulas are correct under their stated event-start model.
The distinction between guaranteed range support and a certainly active point
is real and useful. The largest empirical risk concerns timestamp semantics,
not the algebra.

Each claim c has one actual start x_c in the closed interval [l_c,u_c].
All starts vary independently. G(d,c) is a fixed directed replacement gate.
Self-pairs are excluded, equivalently G(c,c) is false.
At time T, c is active exactly when x_c <= T and no witness d satisfies
G(d,c) and x_c < x_d <= T. Witnesses need not themselves remain active.

Define

    p_c = min {u_d : G(d,c), l_d > u_c},
    r_c = min {l_d : G(d,c), u_d > l_c},

with an empty minimum equal to infinity. The exact predicates are:

| Predicate | Formula |
| --- | --- |
| Possible activity at T | l_c <= T < p_c |
| Certain activity at T | u_c <= T and (T <= l_c or T < r_c) |
| Possible support somewhere in [a,b] | l_c <= b and a < p_c |
| Support somewhere in [a,b] in every world | u_c <= b and (a <= l_c or a < r_c) |

The final row means every world contains an active point. Different worlds may
use different points. It does not require one point active in every world.

## Independent proof checks

For possible point activity, choose x_c = min(u_c,T). Each witness can be placed
before or at x_c unless its lower bound exceeds x_c. When T < u_c, such a
witness necessarily starts after T. When T >= u_c, every forced-later witness
can be placed after T exactly when T < p_c. Conversely, a forced-later witness
with u_d <= T invalidates c in every world.

For certain activity, all starts of c must precede T, giving u_c <= T. A harmful
witness exists in some world exactly when T > l_c and some witness satisfies
u_d > l_c and l_d <= T. Its absence yields the stated formula. This argument
also explains the non-strict T <= l_c term.

For possible range support, possible point activity forms [l_c,p_c). Its
intersection with the closed query range is nonempty exactly under the formula.

For guaranteed range support, u_c <= b is necessary. If a <= l_c, the realized
start itself supplies support in every world. Otherwise choose x_c=l_c. A
witness can remove all support from the query range exactly when it can start
strictly after l_c and no later than a. This occurs exactly when r_c <= a.

These proofs permit arbitrary directed gates, including cycles. They use no
transitive closure. They apply to a finite claim collection and real times.

## Exhaustive check

Run:

    python pass2/independent/exhaustive_uncertain_time.py

The independent oracle enumerates actual timestamp worlds before testing
activity. It checks zero, one, and two incoming witnesses over every closed
integer interval with endpoints from -1 through 3. Queries cover every point
from -2 through 4 and every closed range formed from those points.

The run passed:

- 3,615 interval configurations;
- 44,135 timestamp worlds;
- 50,610 point predicate comparisons;
- 202,440 range predicate comparisons.

The same cases also passed 253,050 comparisons against the actual
`compile_intervals` output. An additional 11 checks cover fractional boundaries,
singleton certainty, zero-width queries, and a supplied gate accepting self.
The implementation correctly ignores self-pairs.

The JSON run record is `exhaustive_results.json`. This is a correctness audit,
not a retrieval benchmark. Integer enumeration supplements the real-time proof.
It does not independently test every continuous realization.

## Required boundary handling

1. Strict replacement matters. Simultaneous claims never retire one another.
2. Point certainty can be a singleton. If l_c=u_c and r_c<=l_c, only T=l_c is
   certainly active. A half-open interval alone cannot represent this case.
3. Query ranges are closed. The tests a<p_c and a<r_c remain strict because
   witness arrival immediately removes the older claim.
4. Empty witness sets use infinity. The implementation must not serialize
   nonstandard JSON Infinity values as portable numeric data.
5. The model requires l_c<=u_c and a<=b. NaN timestamps need rejection.
6. One directed gate change affects only its target. One undirected matching
   decision can change both directed gates and thus two targets. Overlapping
   start intervals have no fixed older endpoint.

## Quantifier counterexample

Let c start in [0,10], and let its sole witness d start exactly at 5.
Use query range [0,10]. In every world, c is active at its own start. Therefore
the range always has support. Yet no point is active in every world. Before 10,
c may not have started. At 10, a world where c started before 5 has retired it.

## Conditions needed for an informative experiment

An uncertain-start interval bounds a single event's actual start. It is not a
fact's entire validity period. It is not automatically a publication window.
It is not automatically a calendar year containing a positive observation.

For example, a source saying a person held a role during [2010,2015] specifies
validity, not an unknown appointment date anywhere inside that interval.
Encoding that span as start uncertainty changes the proposition.

TempLAMA yearly presence labels establish accepted answers in a time bin. They
do not, without further source evidence, bound each appointment's actual start.
They therefore cannot directly validate uncertain-start reasoning. Rounding
known starts into year or month bins supports a controlled granularity study,
provided the paper identifies that transformation and retains the original
timestamps for evaluation.

The replacement gate must also be justified. Two different objects for a shared
relation need not conflict. A correct uncertainty compiler cannot repair a gate
that confuses coexistence with replacement.

The exact formulas assume a Cartesian product of time intervals. Narratives can
impose relative order. A shared source can also induce correlated date errors.
Under additional correlations, these formulas remain safe bounds for the larger
independent-world set but may cease to be exact for the intended smaller set.

Tests cannot establish natural timestamp semantics, gate accuracy, extraction
quality, end-to-end question answering gains, or literature novelty. Those
claims need separate evidence.

## Certificate terminology

The two witnesses are sufficient query summaries after complete compilation.
An unsupported decision can exhibit one mandatory later witness. However,
guaranteed retention also relies on having examined every relevant witness.
The two records alone do not prove that an omitted risky witness is absent.
Call them compiled certificates or boundary witnesses rather than independently
verifiable proofs of every retained decision.
