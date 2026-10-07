# Independent review of constructive refinement

The reviewed model fixes replacement decisions and the relevance ranking.
Event dates vary independently inside closed bounds.
Query support requires activity somewhere inside the closed query window.

## Constructive instability

The construction is sound.
A frontier claim has fewer than `k` possible items above it.
Every world supporting that claim therefore selects it.

The support construction treats two boundary cases correctly.
If the selected start equals the supporting query time, each later witness starts after that time.
Otherwise, the claim starts at its upper bound.
The stored possible-support boundary then places every forced later witness after the supporting time.

The exclusion construction also preserves valid source bounds.
A claim can start after the query when its upper bound exceeds the query end.
Otherwise, the stored potential witness can retire it by the query start.
The strict inequality between claim start and witness date remains necessary.
Equal dates cannot create retirement.

The two date assignments share all fixed input constraints.
They do not combine independently chosen marginal support masks.
This distinction matters when several claims depend on the same event.

## Necessary refinement

The frontier theorem is sound.
Interval narrowing cannot add a new possibly supported claim.
A frontier claim that remains possible therefore keeps its place within the possible top `k`.
A stable result must make that claim guaranteed.
Otherwise, refinement must make it impossible.

The theorem concerns support status, not the claim's own date field.
Refining another event can settle the claim's status.
The frontier is necessary, but it need not be sufficient.
Removing one frontier claim can expose another claim below it.

## Hardness boundary

The bipartite Set Cover reduction is sound.
Each chosen set contributes one active variable claim.
Each uncovered element contributes `K+1` active copies.
The target enters the top `K+1` exactly when at most `K` selected sets cover every element.
Its own temporal support can remain guaranteed throughout.

The reduction has polynomial size after the standard restriction `K<=number_of_sets`.
The ranking budget `k` forms part of the input.
This result does not establish hardness for a fixed budget such as five.
It does not make marginal support compilation hard.
The full attainable context envelope is a different object from the possible-support top `k`.

The older clock construction also remains valid.
It places every start at or before the query.
That variant uses two gate layers instead of one.

## Corrections and implementation scope

The initial runtime statement omitted fixed fallback items.
The revised definition counts those items in `n`.
The revised runtime statement is therefore valid.

The current replay function retains the accepted pair graph.
It uses that graph to compute both complete realized contexts.
That replay storage differs from the compiler's linear certificate output.
The revised documentation separates these costs.

The final implementation removes graph access from assignment construction.
It applies the support-date rule to every event, including events outside the pivot's incoming set.
This gives two assignments from bounds and certificates alone in `O(n)` time.
Full context replay remains a separate `O(n+m)` audit step.
The independent checks also passed after this final implementation change.

## Independent checks

The separate checker implements direct world semantics without the theory module's world evaluator.
It passed 3,556 context checks across 120 configurations.
It verified 1,300 returned counterworld pairs.
It enumerated 12,925 legal date worlds.
Cases include fractional queries, strict ties, explicit end events, fallback items, and zero budgets.

The Set Cover reduction passed 1,536 independent finite instances.
Those checks evaluated 12,288 date worlds.
Finite checks support implementation correctness.
They do not replace the hardness proof or provide benchmark evidence.

Reproduce with `python pass3/protocol/review_refinement.py`.
The results appear in `independent_refinement_checks.json`.
