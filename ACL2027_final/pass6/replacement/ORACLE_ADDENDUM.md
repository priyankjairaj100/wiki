# Exact calendar oracle

Replace the proposed critical-boundary enumeration with an exact reference oracle.
This change precedes all certificate outcomes.
The oracle searches integer difference constraints over every day in each calendar interval.
It returns support and exclusion worlds when each exists.
The linear compiler and lazy selector are compared with this separate implementation.
Every returned world is replayed directly through active intervals.
Every unstable decision saves a pair of feasible worlds with different literal contexts.
No endpoint sample serves as ground truth.

Use the implementation in `pass6/modeling/constraint_oracle.py`.
The modeling study validates that implementation against exhaustive finite grids.
This diagnostic uses only the overlap predicate on point queries.
The runner also evaluates every recorded source order.
The expanded Levadia case has overlapping bounds, so its strict source order constrains permitted dates.
