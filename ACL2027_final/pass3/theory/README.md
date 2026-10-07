# Source-backed lifecycle adapter

`lifecycle.py` connects source extraction to the pass-2 compiler.
It preserves the original model and adds explicit termination events.
It does not infer replacement from a shared subject, slot, or changed value.

## Date meaning

Each start interval bounds one unknown occurrence date.
Each end interval bounds one unknown termination date.
A realized claim applies during `[start, end)`.
An end therefore removes support at its own timestamp.
An absent end remains open unless an accepted replacement occurs.

Use one consistent numeric time axis.
The source extractor uses Gregorian day ordinals.
A year spans January 1 through December 31.
A query interval includes both endpoints.
An explicit phrase such as “through December 31” needs a deliberate termination convention.
The adapter does not silently add one day.

Do not encode a complete validity duration as an uncertain start.
Instead, preserve separate start and end bounds.
For example, “from 2001 to 2005” provides two dates with year precision.

## Safe explicit ends

The adapter requires `end.lower > start.upper`.
Every allowed end then follows every allowed start.
It adds one hidden end event and one directed pair targeting the claim.
The existing theorem applies without modification.
End events never enter the retrieved context.

Overlapping bounds require a start-before-end constraint.
That constraint violates the independent date model.
The adapter rejects these records for explicit fallback handling.
It does not force an arbitrary order.

An exact validity interval also follows this path.
Its start and end bounds are singletons.
The result equals direct overlap with its half-open validity interval.

## Minimal interface

```python
from pass3.theory.lifecycle import (
    LifecycleClaim, compile_lifecycles, select_context,
    stable_lifecycle_context,
)

claims = [
    LifecycleClaim("c", "Original source span", 0, 2, 5, 6),
    LifecycleClaim("d", "Explicit replacement source span", 3, 4),
]
index = compile_lifecycles(claims, [("d", "c")])

# Every source claim appears once. Unknown fallback is fixed across policies.
ranking = ["c", "untimed", "d"]
context = select_context(index, ranking, 3, 5, k=2,
                         policy="possible", unknown_ids=["untimed"])
decision = stable_lifecycle_context(index, ranking, 3, 5, k=2,
                                    unknown_ids=["untimed"])
```

`LifecycleClaim.from_record` accepts the extractor schema.
It reads `claim_id`, `source_span.text`, `temporal_kind`, `start`, and optional `end`.
Date objects need `lower` and `upper` fields.
The temporal kind must be `occurrence_start` or `validity_duration`.
A validity duration needs an explicit end.

The adapter preserves source claim identifiers.
Repeated values can have separate lifetimes.
It never merges them by value.

Pairs use `(witness_id, target_id)`.
Every endpoint must name a modeled claim.
An unmodeled witness cannot silently disappear from an accepted pair.
Such omission could create a false guarantee.
The extractor must define its accepted pair scope before compilation.

## Matched controls

`select_context` supports seven policies:

| Policy | Eligibility |
| --- | --- |
| `possible` | Support exists under some allowed date assignment. |
| `guaranteed` | Support exists within the query under every allowed assignment. |
| `earliest` | Complete every start and end with its lower bound. |
| `midpoint` | Complete every start and end with its midpoint. |
| `latest` | Complete every start and end with its upper bound. |
| `interval` | Check outer lifespan overlap and ignore replacement pairs. |
| `no_filter` | Keep every source claim. |

All policies share the same source claims, accepted pairs, ranking, and budget.
All completion controls also share the same explicit end representation.
The interval control uses `start.lower <= query.end` and `query.start < end.upper`.
The second condition disappears when no end exists.
It never treats an occurrence interval as a full validity duration.

Each selected item has a support tag.
The tags are `guaranteed`, `unresolved`, `unsupported`, and `unknown`.
These tags describe source eligibility under the model.
They do not certify source truth or reader accuracy.

## Untimed fallback and stability

Unknown items stay available under every policy.
Their factual support tag remains `unknown`.
They are never assigned guaranteed temporal support.

The operational context contains modeled support plus fixed fallback items.
The stability test compares its possible and guaranteed endpoint contexts.
Equality proves that modeled date choices cannot change the selected claim identifiers.
The converse holds for the stated independent model.
The returned scope records the fixed fallback policy.

The test runs before paragraph aggregation.
A paragraph may contain several claims with different dates.
Repeated paragraph identifiers must not erase claim-level differences before this test.

## Correlations and provenance

Bounds can still hide source constraints or shared event dates.
The rectangular model treats each event date independently.
Additional constraints can reduce its allowed worlds.
Possible support then remains an outer bound.
Guaranteed support remains an inner bound.
Context equality remains sufficient for stability.
Context inequality no longer proves instability under the smaller world set.

The pipeline must retain source spans and the reason for every accepted replacement pair.
Appointment language alone does not establish exclusivity.
Coexisting affiliations remain separate when the text provides no replacement evidence.

## Cost and checks

The adapter adds at most one event per source claim.
The two-witness certificate output still uses linear space.
This evaluation wrapper also retains accepted pairs for matched completion controls.
Its full audit state therefore uses `O(n+m)` space.
This does not change the compiler's `O(n)` certificate output claim.

Run:

```bash
python pass3/theory/test_lifecycle.py
```

The tests enumerate realized lifetimes independently from the certificate formulas.
They check explicit ends, repeated values, coexistence, fallback tags, completion controls, and stability.
The JSON report records their counts.
These are constructed correctness checks, not benchmark examples.

## Constructive date refinement

`refinement.py` adds a separate interface without changing the frozen lifecycle adapter.

```python
from pass3.theory.refinement import refinement_frontier, context_counterworlds

frontier = refinement_frontier(index, ranking, 3, 5, k=2,
                               unknown_ids=["untimed"])
worlds = context_counterworlds(index, ranking, 3, 5, k=2,
                              unknown_ids=["untimed"])
```

The frontier contains unresolved claims in the possible context.
Every refinement that stabilizes this context must make each current frontier claim guaranteed or impossible.
Resolving its own start date may not resolve its support.
Replacement dates can also control that support.
New frontier claims can enter after current claims disappear.
This is not a minimum set of date fields to inspect.

`context_counterworlds` returns `None` exactly when the modeled context is stable.
Otherwise, it returns two complete event assignments and their different contexts.
It also returns the pivot claim and its exclusion mechanism.
The assignments respect all source bounds and the shared replacement gate.
They do not combine incompatible marginal support choices.

`pivot_date_assignments` constructs both complete assignments using only event bounds and the pivot certificate.
It takes linear time in the event count and needs no pair list.
The frontier rank condition proves that their contexts differ.
Actual context replay also scans the accepted pairs, ranking items, and fallback items.
That optional replay requires the retained pair list.
The compact boundary certificates alone do not represent every pair.

`REFINEMENT_THEORY.md` contains the proofs.
`main_refinement.tex` and `appendix_refinement.tex` contain manuscript text.
The appendix also proves hardness of arbitrary possible context membership when the budget is part of the input.
It makes no hardness claim for a fixed budget such as five.

Run the added correctness checks:

```bash
python pass3/theory/test_refinement.py
```

The saved results are in `refinement_tests.json`.
Independent checks and a separate world evaluator are in `../protocol/independent_refinement_checks.json`.
