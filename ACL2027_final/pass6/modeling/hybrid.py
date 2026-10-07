"""Screen independent certificates, then solve only unresolved selected claims.

The supplied constrained family must be nonempty. Construction verifies this once.
The current hybrid API implements the active-somewhere predicate only.
"""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pass2.theory.uncertain_time import IntervalClaim, compile_from_pairs
from pass6.modeling.constraint_oracle import Model, SupportOracle


class HybridIndex:
    def __init__(self, model: Model):
        self.model = model
        self.oracle = SupportOracle(model)
        claims = [IntervalClaim(str(i), "", lo, hi) for i, (lo, hi) in enumerate(model.bounds)]
        self.product = compile_from_pairs(claims, ((str(d), str(c)) for d, c in model.pairs))

    def select(self, ranking, a: int, b: int, k: int) -> dict:
        ranking = tuple(ranking)
        if len(set(ranking)) != len(ranking) or set(ranking) != set(self.model.visible):
            raise ValueError("Ranking must contain every visible claim once.")
        if type(k) is not int or k < 0:
            raise ValueError("Use a nonnegative context budget.")
        if type(a) is not int or type(b) is not int or a > b:
            raise ValueError("Use ordered integer query dates.")
        possible = {c: self.product[str(c)].possible(a, b) for c in ranking}
        guaranteed = {c: self.product[str(c)].guaranteed(a, b) for c in ranking}
        possible_top = tuple(c for c in ranking if possible[c])[:k]
        guaranteed_top = tuple(c for c in ranking if guaranteed[c])[:k]
        if possible_top == guaranteed_top:
            return {"stable": True, "possible_top": possible_top, "frontier": (),
                    "screened": True, "oracle_claim_queries": 0, "feasibility_calls": 0,
                    "support_world": None, "exclusion_world": None, "pivot": None}
        chosen, frontier = [], []
        exact_queries = 0
        before = self.oracle.feasibility_calls
        first_pivot = None
        support_world = exclusion_world = None
        for c in ranking:
            if not possible[c]:
                continue
            if guaranteed[c]:
                chosen.append(c)
            else:
                exact = self.oracle.query(c, a, b, "overlap")
                exact_queries += 1
                if not exact["possible"]:
                    continue
                chosen.append(c)
                if not exact["guaranteed"]:
                    frontier.append(c)
                    if first_pivot is None:
                        first_pivot = c
                        support_world, exclusion_world = exact["support_world"], exact["exclusion_world"]
            if len(chosen) == k:
                break
        return {"stable": not frontier, "possible_top": tuple(chosen), "frontier": tuple(frontier),
                "screened": False, "oracle_claim_queries": exact_queries,
                "feasibility_calls": self.oracle.feasibility_calls - before,
                "support_world": support_world, "exclusion_world": exclusion_world, "pivot": first_pivot}
