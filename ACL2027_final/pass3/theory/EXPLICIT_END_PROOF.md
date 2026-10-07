# Explicit ends preserve the compiler

Let claim `c` start at `x_c` within `[l_c,u_c]`.
Let its explicit termination occur at `z_c` within `[v_c,w_c]`.
Assume `u_c < v_c`.
Let starts and ends vary independently within their bounds.

In each world, define source activity by three conditions:

1. The start has occurred: `x_c <= T`.
2. The explicit end has not occurred: `T < z_c`.
3. No accepted direct replacement occurs strictly after `x_c` and by `T`.

Introduce a hidden event `e_c` with occurrence bounds `[v_c,w_c]`.
Add only the direct pair `e_c -> c` for this explicit end.
The strict separation gives `x_c < z_c` in every world.
The hidden event therefore retires `c` exactly when `z_c <= T`.
Its direct retirement condition is equivalent to explicit termination.
All original replacement conditions remain unchanged.
Thus the augmented compiler has exactly the same activity in every world.

Let `p_c` and `r_c` be the original compiler boundaries.
The explicit end updates them to:

    p'_c = min(p_c, w_c)
    r'_c = min(r_c, v_c)

The pass-2 possible and guaranteed formulas apply with these updated boundaries.
Each output still needs at most two witness records.
An explicit end can supply either or both records.

When all bounds are exact, each claim occupies a half-open realized interval.
Its stop is the earliest explicit end or strictly later replacement.
The interval query reduces to direct overlap with this realized interval.

This extension is a reduction to the existing theorem.
It is not a separate novelty claim.

## Why the separation check is necessary

Take start bounds `[0,2]` and end bounds `[1,3]`.
The independent rectangle includes start `2` and end `1`.
An explicit lifecycle must exclude that assignment.
The original direct compiler instead ignores the earlier end as a replacement.
It can then retain the claim after its supposed termination.
The hidden-event reduction is therefore invalid without separation or richer constraints.

The implementation rejects overlapping bounds.
It preserves these source items through the fixed fallback policy.
It does not report exact temporal support for those items.

## Fixed fallback items

Let `M_x` contain modeled claims supported in world `x`.
Let `F` contain unknown items preserved under every policy.
The operational mask is `M_x union F`.
Its union across worlds is `P union F`.
Its intersection across worlds is `H union F`.
Here, `P` and `H` are the exact modeled possible and guaranteed sets.

The existing context theorem therefore gives:

    invariant context iff Top_k(P union F) = Top_k(H union F).

Membership in `F` states a fixed policy choice.
It does not establish guaranteed source support.
The implementation preserves that distinction in its item tags and returned scope.

## Source constraints beyond the rectangle

Suppose source constraints restrict the date rectangle to a nonempty smaller set.
The compiled possible mask remains an outer bound on its support union.
The compiled guaranteed mask remains an inner bound on its support intersection.
Equal endpoint contexts still imply invariant context within that smaller set.
Unequal contexts need not imply actual instability under those constraints.
