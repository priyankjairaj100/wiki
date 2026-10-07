# Constrained dates and query predicates

This component extends the reference model with explicit source constraints.
It uses integer calendar dates.
It accepts known event order and overlapping start and end bounds.
It supports three query predicates.

| Predicate | Meaning |
| --- | --- |
| `overlap` | The claim is active at some date within the query window. |
| `throughout` | The claim is active at every date within the query window. |
| `appointed` | The claim starts within the query window. |

Appointment support does not depend on later replacement.
Activity uses half-open lifetimes.
Equal event dates do not establish replacement order.
The oracle rejects an empty feasible family.

The benchmark uses generated event models.
Its results measure exact decisions and solver calls.
It does not measure extraction accuracy or answer quality.
The source replacement challenge remains a separate evaluation.

## Main results

The frozen benchmark contains 120 feasible models and 20 inconsistent models.
It covers 28 windows, three predicates, and three context budgets.
The reference enumerates every integer date assignment.
It evaluates direct activity independently of the support oracle.

| Check | Result |
| --- | ---: |
| Feasible assignments | 20,846 |
| Support decisions | 100,800 / 100,800 agree |
| Fixed-ranking context decisions | 30,240 / 30,240 agree |
| Concrete assignments checked | 68,161 |
| Empty families rejected | 20 / 20 |
| Explicit lifetimes with overlapping bounds | 38 |
| Stable contexts recovered through constraints | 929 |

The hybrid procedure applies to overlap queries.
It first compares contexts from the existing independent certificates.
It calls the exact oracle only when unresolved candidates can affect selection.
Each model receives one initial feasibility check.
The following counts exclude that shared check.

| Hybrid check | Result |
| --- | ---: |
| Context decisions | 10,080 / 10,080 agree |
| Stable contexts without query solver calls | 3,001 |
| Additional stable contexts | 312 |
| Full oracle claim queries | 50,400 |
| Lazy exact claim queries | 33,180 |
| Hybrid oracle claim queries | 13,343 |
| Claim query reduction against lazy exact | 59.79% |
| Feasibility call reduction against lazy exact | 55.67% |
| Counterworld pairs replayed | 6,767 |

At budget five, the hybrid reduces claim queries by 59.23%.
It recovers 98 additional stable contexts at that budget.
These measurements count solver work.
They do not establish an end-to-end speedup.
The exact oracle can require exponential branching.

## Two-witness ablation

The separate grid contains 476 configurations and 13,328 claim-window decisions.
Each configuration has two different supplying witnesses.
All configurations and windows remain in the results.
The full compiler agrees with every exhaustive decision.
Each single-witness subset fails on at least one window in every configuration.
Keeping only the nearby witness causes 1,750 incorrect possible inclusions.
Keeping only the later witness causes 5,576 incorrect guaranteed inclusions.
This result concerns subsets of direct witnesses.
It does not establish a lower bound for arbitrary encodings.

## Run all checks

Run these commands from the project root.
Use a separate directory to preserve the original results.

```bash
python pass6/modeling/run_benchmark.py --output /tmp/modeling_check
python pass6/modeling/two_witness_grid.py --output /tmp/modeling_check
python pass6/modeling/run_hybrid.py --output /tmp/modeling_check
python pass6/modeling/run_lazy_baseline.py --output /tmp/modeling_check
```

Python and NumPy are the only dependencies.
The current reference used Python 3.12.14 and NumPy 2.3.5.
Each command verifies its frozen source hashes before execution.
All JSONL files must match exactly.
All result JSON fields must match, except `runtime_seconds`, `python`, and `numpy` in `results.json`.
The other result files have no ignored fields.

## Files

| File | Role |
| --- | --- |
| `constraint_oracle.py` | Exact integer feasibility and typed support queries |
| `hybrid.py` | Independent screening and selective exact queries |
| `cases.jsonl` | Every generated model, bound, constraint, pair, and ranking |
| `PROTOCOL_FREEZE.json` | Initial protocol and source hashes |
| `support_decisions.jsonl` | Every support decision and concrete assignment |
| `context_decisions.jsonl` | Fixed and date-dependent ranking results |
| `case_results.jsonl` | Every model outcome and feasibility count |
| `results.json` | Complete benchmark aggregates |
| `TWO_WITNESS_FREEZE.json` | Grid protocol and source hashes |
| `two_witness_cases.jsonl` | Every grid configuration |
| `two_witness_decisions.jsonl` | Every full and ablated decision |
| `two_witness_results.json` | Grid aggregates |
| `HYBRID_FREEZE.json` | Hybrid protocol and source hashes |
| `hybrid_decisions.jsonl` | Every hybrid context and returned assignments |
| `hybrid_results.json` | Hybrid aggregates |
| `LAZY_BASELINE_FREEZE.json` | Frozen amendment for a fair lazy baseline |
| `lazy_baseline_decisions.jsonl` | Every lazy baseline context and comparison |
| `lazy_baseline_results.json` | Full, lazy, and hybrid counts |
| `PROOFS.md` | Oracle and hybrid correctness arguments |

The protocols were frozen before their respective evaluations.
The hybrid protocol extends the completed benchmark without changing its models.
The later baseline amendment separates budget stopping from product screening.
It was frozen before running the added baseline.
The lazy baseline uses the same oracle and stops after selecting the requested number of possible claims.
No case was removed after evaluation.

## Oracle interface

Event indices identify dates.
An inequality `(i, j, b)` means `x[i] - x[j] <= b`.
Index `-1` denotes zero.
For integer dates, `(i, j, -1)` requires event `i` before event `j`.
An explicit end requires both a replacement pair and a strict lifetime constraint.
End events remain outside the visible claims.

```python
from pass6.modeling.constraint_oracle import Model, SupportOracle

model = Model(
    bounds=((0, 2), (1, 3)),
    visible=(0,),
    pairs=((1, 0),),
    constraints=((0, 1, -1),),
)
oracle = SupportOracle(model)
result = oracle.query(0, 1, 2, "throughout")
```

The result includes possible support, guaranteed support, and concrete supporting or excluding assignments.
The hybrid API accepts a complete fixed ranking.
It returns the possible context and its unresolved claims.
An unstable context also returns a pivot and two differing assignments.

## Ranking and query scope

Different query predicates produce different support decisions.
Throughout changes 5,840 possible decisions relative to overlap.
Appointment changes 2,989 possible decisions relative to overlap.
Each comparison contains 16,800 claim-window decisions.
The implementation therefore requires an explicit query type.

The fixed-ranking theorem does not extend to date-dependent rankings.
The benchmark separately sorts claims by realized start dates.
Under that policy, selected sets change in 3,640 contexts certified stable under fixed ranking.
The comparison contains 8,627 fixed-ranking stable contexts.
This is a controlled failure analysis, not a failure of the stated theorem.

The paper's hardness reduction treats the context budget as input.
It does not establish hardness at the evaluated budget of five.
