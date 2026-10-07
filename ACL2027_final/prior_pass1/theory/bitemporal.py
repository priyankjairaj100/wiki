"""A standard-library specification for two-clock witness frontiers.

This module is a candidate extension. It contains no benchmark result.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from math import isfinite
from typing import Callable, Iterable, Mapping


@dataclass(frozen=True)
class Claim:
    cid: str
    valid: float
    arrival: float
    text: str = ""


@dataclass(frozen=True)
class Witness:
    valid: float
    available: float
    cid: str


@dataclass(frozen=True)
class Frontier:
    source: Claim
    witnesses: tuple[Witness, ...]
    valid_starts: tuple[float, ...]

    def eligible(self, valid_cutoff: float, knowledge_cutoff: float) -> bool:
        if self.source.valid > valid_cutoff or self.source.arrival > knowledge_cutoff:
            return False
        position = bisect_right(self.valid_starts, valid_cutoff) - 1
        return position < 0 or self.witnesses[position].available > knowledge_cutoff


def compile_frontiers(
    claims: Iterable[Claim], gate: Callable[[Claim, Claim], bool]
) -> dict[str, Frontier]:
    """Compile exact per-source skylines under a fixed direct pair gate."""
    items = list(claims)
    if len({claim.cid for claim in items}) != len(items):
        raise ValueError("Claim IDs must be unique.")
    for claim in items:
        if not isfinite(claim.valid) or not isfinite(claim.arrival):
            raise ValueError("Both clocks must be finite.")
    result = {}
    for source in items:
        candidates = [
            Witness(other.valid, max(other.arrival, source.arrival), other.cid)
            for other in items
            if other.valid > source.valid and gate(other, source)
        ]
        candidates.sort(key=lambda witness: (witness.valid, witness.available, witness.cid))
        frontier = []
        best_arrival = float("inf")
        for witness in candidates:
            if witness.available < best_arrival:
                frontier.append(witness)
                best_arrival = witness.available
        result[source.cid] = Frontier(
            source, tuple(frontier), tuple(witness.valid for witness in frontier)
        )
    return result


def eligible_ids(
    index: Mapping[str, Frontier], valid_cutoff: float, knowledge_cutoff: float
) -> set[str]:
    return {
        cid for cid, frontier in index.items()
        if frontier.eligible(valid_cutoff, knowledge_cutoff)
    }


def direct_scan(
    claims: Iterable[Claim], gate: Callable[[Claim, Claim], bool],
    valid_cutoff: float, knowledge_cutoff: float,
) -> set[str]:
    items = list(claims)
    return {
        source.cid for source in items
        if source.valid <= valid_cutoff and source.arrival <= knowledge_cutoff
        and not any(
            source.valid < other.valid <= valid_cutoff
            and other.arrival <= knowledge_cutoff and gate(other, source)
            for other in items
        )
    }
