"""Exhaustively check context invariance for arbitrary possible mask families.

This test enumerates all nonempty families, without independence assumptions.
The universe order is the complete strict ranking; renaming covers any such
ranking. Outputs are ordered tuples, not only membership sets.
"""
from pathlib import Path
import json


def topk(mask, n, k):
    return tuple(i for i in range(n) if mask & (1 << i))[:k]


def main():
    families_checked = 0
    conditions_checked = 0
    largest_family = 0
    for n in range(5):
        masks = tuple(range(1 << n))
        ranked = {(mask, k): topk(mask, n, k)
                  for mask in masks for k in range(n + 1)}
        for family_bits in range(1, 1 << len(masks)):
            family = tuple(mask for mask in masks if family_bits & (1 << mask))
            families_checked += 1
            largest_family = max(largest_family, len(family))
            possible, guaranteed = 0, (1 << n) - 1
            for mask in family:
                possible |= mask
                guaranteed &= mask
            for k in range(n + 1):
                oracle = len({ranked[mask, k] for mask in family}) == 1
                condition = ranked[possible, k] == ranked[guaranteed, k]
                assert oracle == condition, (n, family, k, possible, guaranteed)
                conditions_checked += 1
    # Marginal masks can differ while the actual selected context stays fixed.
    assert topk(0b001, 3, 1) == topk(0b111, 3, 1)
    # Correlations can forbid the union mask from appearing in any world.
    assert 0b111 not in (0b011, 0b101)
    assert topk(0b011, 3, 1) == topk(0b101, 3, 1)
    result = {"status": "passed", "families_checked": families_checked,
              "conditions_checked": conditions_checked,
              "universe_sizes": [0, 1, 2, 3, 4],
              "maximum_world_masks_per_family": largest_family,
              "all_k_from_zero_to_n": True,
              "world_families": "arbitrary, including correlated and nonproduct families",
              "ranking": "fixed complete strict order"}
    Path(__file__).with_name("context_invariance_results.json").write_text(
        json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
