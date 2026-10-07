"""Exact support over constrained, finite integer calendar dates.

This is a separate reference oracle. It does not replace the linear compiler.
Every inequality has the form x[left] - x[right] <= bound. Index -1 denotes zero.
Feasibility uses integer difference constraints. Support uses complete branching.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

Constraint = tuple[int, int, int]


@dataclass(frozen=True)
class Model:
    bounds: tuple[tuple[int, int], ...]
    visible: tuple[int, ...]
    pairs: tuple[tuple[int, int], ...]
    constraints: tuple[Constraint, ...] = ()

    def __post_init__(self):
        n = len(self.bounds)
        if not n or any(type(v) is not int for interval in self.bounds for v in interval):
            raise ValueError("Use nonempty integer date bounds.")
        if any(lo > hi for lo, hi in self.bounds):
            raise ValueError("Date bounds must be ordered.")
        if len(set(self.visible)) != len(self.visible) or any(c < 0 or c >= n for c in self.visible):
            raise ValueError("Visible claims must name distinct events.")
        if any(d == c or min(d, c) < 0 or max(d, c) >= n for d, c in self.pairs):
            raise ValueError("Replacement pairs must name distinct events.")
        if any(min(i, j) < -1 or max(i, j) >= n or type(b) is not int
               for i, j, b in self.constraints):
            raise ValueError("Invalid difference constraint.")


class EmptyWorldFamily(ValueError):
    """The supplied dates and source constraints admit no timeline."""


class SupportOracle:
    def __init__(self, model: Model):
        self.model = model
        self.feasibility_calls = 0
        self.base = list(model.constraints)
        for c, (lo, hi) in enumerate(model.bounds):
            self.base.extend(((c, -1, hi), (-1, c, -lo)))
        self.base_world = self.feasible(())
        if self.base_world is None:
            raise EmptyWorldFamily("The feasible world family is empty.")

    def feasible(self, extra: Iterable[Constraint]) -> tuple[int, ...] | None:
        """Bellman--Ford feasibility with an explicit integer witness."""
        self.feasibility_calls += 1
        n = len(self.model.bounds)
        edges = [(n if j == -1 else j, n if i == -1 else i, b)
                 for i, j, b in (*self.base, *extra)]
        distance = [0] * (n + 1)
        for iteration in range(n + 1):
            changed = False
            for source, target, bound in edges:
                candidate = distance[source] + bound
                if candidate < distance[target]:
                    distance[target] = candidate
                    changed = True
            if not changed:
                origin = distance[n]
                return tuple(v - origin for v in distance[:n])
            if iteration == n:
                return None
        raise AssertionError("Unreachable feasibility state.")

    def _support(self, c: int, a: int, b: int, predicate: str):
        if predicate == "appointed":
            return self.feasible(((c, -1, b), (-1, c, -a)))
        threshold, start_limit = (a, b) if predicate == "overlap" else (b, a)
        incoming = tuple(sorted({d for d, target in self.model.pairs if target == c}))
        initial = ((c, -1, start_limit),)

        def search(position, chosen):
            world = self.feasible(chosen)
            if world is None:
                return None
            if position == len(incoming):
                return world
            d = incoming[position]
            # Either the replacement is no later than c, or follows the window boundary.
            for alternative in ((d, c, 0), (-1, d, -threshold - 1)):
                answer = search(position + 1, (*chosen, alternative))
                if answer is not None:
                    return answer
            return None

        return search(0, initial)

    def _exclusion(self, c: int, a: int, b: int, predicate: str):
        if predicate == "appointed":
            for branch in (((c, -1, a - 1),), ((-1, c, -b - 1),)):
                world = self.feasible(branch)
                if world is not None:
                    return world
            return None
        threshold, start_limit = (a, b) if predicate == "overlap" else (b, a)
        world = self.feasible(((-1, c, -start_limit - 1),))
        if world is not None:
            return world
        for d in sorted({d for d, target in self.model.pairs if target == c}):
            world = self.feasible(((c, d, -1), (d, -1, threshold)))
            if world is not None:
                return world
        return None

    def query(self, c: int, a: int, b: int, predicate: str = "overlap") -> dict:
        if c not in self.model.visible:
            raise ValueError("Queries must name a visible claim.")
        if type(a) is not int or type(b) is not int or a > b:
            raise ValueError("Use ordered integer query dates.")
        if predicate not in ("overlap", "throughout", "appointed"):
            raise ValueError("Unknown query predicate.")
        before = self.feasibility_calls
        support = self._support(c, a, b, predicate)
        exclusion = self._exclusion(c, a, b, predicate)
        return {
            "possible": support is not None,
            "guaranteed": exclusion is None,
            "support_world": support,
            "exclusion_world": exclusion,
            "feasibility_calls": self.feasibility_calls - before,
        }


def from_record(record: dict) -> Model:
    return Model(tuple(map(tuple, record["bounds"])), tuple(record["visible"]),
                 tuple(map(tuple, record["pairs"])), tuple(map(tuple, record["constraints"])))
