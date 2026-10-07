"""Exact possible and guaranteed support under interval-valued event dates.

Each claim's date varies independently within a closed interval. Fixed gates
mean direct replacement only when the witness occurs strictly later.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class IntervalClaim:
    cid: str
    text: str
    lower: float
    upper: float

    def __post_init__(self):
        if not self.cid or not isinstance(self.cid, str):
            raise ValueError("Claim identifiers must be nonempty strings.")
        for bound in (self.lower, self.upper):
            if isinstance(bound, bool) or not isinstance(bound, (int, float)) or not math.isfinite(bound):
                raise ValueError("Date bounds must be finite numbers.")
        if self.lower > self.upper:
            raise ValueError("The lower date cannot exceed the upper date.")


@dataclass(frozen=True)
class TwoCertificate:
    cid: str
    lower: float
    upper: float
    possible_end: float
    potential_witness_lower: float
    possible_end_witness: str | None
    potential_witness: str | None

    @staticmethod
    def _query(a: float, b: float) -> None:
        if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t)
               for t in (a, b)):
            raise ValueError("Query bounds must be finite numbers.")
        if a > b:
            raise ValueError("The query start cannot exceed its end.")

    def possible(self, a: float, b: float | None = None) -> bool:
        b = a if b is None else b
        self._query(a, b)
        return self.lower <= b and a < self.possible_end

    def guaranteed(self, a: float, b: float | None = None) -> bool:
        b = a if b is None else b
        self._query(a, b)
        return self.upper <= b and (a <= self.lower or a < self.potential_witness_lower)

    def status(self, a: float, b: float | None = None) -> str:
        if self.guaranteed(a, b):
            return "guaranteed"
        if self.possible(a, b):
            return "unresolved"
        return "unsupported"


def _claim_map(claims: Iterable[IntervalClaim]) -> dict[str, IntervalClaim]:
    result: dict[str, IntervalClaim] = {}
    for claim in claims:
        if not isinstance(claim, IntervalClaim):
            raise TypeError("Inputs must be IntervalClaim objects.")
        if claim.cid in result:
            raise ValueError("Claim identifiers must be unique.")
        result[claim.cid] = claim
    return result


def compile_from_pairs(
    claims: Iterable[IntervalClaim],
    accepted_directed_pairs: Iterable[tuple[str, str]],
) -> dict[str, TwoCertificate]:
    """Compile accepted (witness_id, target_id) pairs in O(n+m) time.

    The iterable must contain every accepted directed pair. Duplicate pairs are
    harmless. Self-pairs are ignored because a claim cannot replace itself.
    Boundary ties use the smallest witness identifier, regardless of pair order.
    Unknown identifiers raise ValueError. The returned mapping preserves claim
    input order; its records do not depend on claim or pair input order.
    """
    by_id = _claim_map(claims)
    mandatory: dict[str, tuple[float, str] | None] = dict.fromkeys(by_id)
    potential: dict[str, tuple[float, str] | None] = dict.fromkeys(by_id)
    for pair in accepted_directed_pairs:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("Each directed pair must contain two claim identifiers.")
        witness_id, target_id = pair
        if not isinstance(witness_id, str) or not isinstance(target_id, str):
            raise ValueError("Pair identifiers must be strings.")
        if witness_id not in by_id or target_id not in by_id:
            raise ValueError("Every pair identifier must name an input claim.")
        if witness_id == target_id:
            continue
        witness, target = by_id[witness_id], by_id[target_id]
        if witness.lower > target.upper:
            candidate = witness.upper, witness.cid
            if mandatory[target_id] is None or candidate < mandatory[target_id]:
                mandatory[target_id] = candidate
        if witness.upper > target.lower:
            candidate = witness.lower, witness.cid
            if potential[target_id] is None or candidate < potential[target_id]:
                potential[target_id] = candidate
    result = {}
    for target in by_id.values():
        forced, permitted = mandatory[target.cid], potential[target.cid]
        result[target.cid] = TwoCertificate(
            target.cid, target.lower, target.upper,
            forced[0] if forced else math.inf,
            permitted[0] if permitted else math.inf,
            forced[1] if forced else None,
            permitted[1] if permitted else None)
    return result


def compile_intervals(
    claims: Iterable[IntervalClaim],
    gate: Callable[[IntervalClaim, IntervalClaim], bool],
) -> dict[str, TwoCertificate]:
    """Evaluate every non-self directed gate, then compile the accepted pairs.

    This reference scan uses n(n-1) gate evaluations. Use compile_from_pairs when
    a complete index or an earlier detector already supplies accepted pairs.
    """
    by_id = _claim_map(claims)
    claims = tuple(by_id.values())
    accepted = ((witness.cid, target.cid)
                for target in claims for witness in claims
                if witness.cid != target.cid and gate(witness, target))
    return compile_from_pairs(claims, accepted)


@dataclass(frozen=True)
class ContextStability:
    """Whether every allowed date assignment returns the same ranked context."""
    stable: bool
    possible_top: tuple[str, ...]
    guaranteed_top: tuple[str, ...]
    common_context: tuple[str, ...] | None


def stable_context(
    certificates: dict[str, TwoCertificate],
    ranked_cids: Iterable[str],
    a: float,
    b: float | None = None,
    *,
    k: int = 5,
) -> ContextStability:
    """Certify exact top-k invariance without enumerating date assignments.

    The ranking must list every indexed claim exactly once. It remains fixed
    across worlds. Its order resolves all score ties. The certificate masks
    must be exact unions and intersections of the world support masks.
    With conservative outer/inner masks, equality still proves stability, but
    inequality would no longer prove instability.
    """
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError("The context budget must be a nonnegative integer.")
    b = a if b is None else b
    TwoCertificate._query(a, b)
    ranking = tuple(ranked_cids)
    if any(not isinstance(cid, str) for cid in ranking):
        raise ValueError("Ranking entries must be claim identifiers.")
    if len(ranking) != len(set(ranking)):
        raise ValueError("The ranking cannot contain duplicate identifiers.")
    if set(ranking) != set(certificates):
        raise ValueError("The ranking must contain every indexed claim exactly once.")
    if any(not isinstance(item, TwoCertificate) or item.cid != cid
           for cid, item in certificates.items()):
        raise ValueError("Certificate keys must match their claim identifiers.")
    possible = tuple(cid for cid in ranking if certificates[cid].possible(a, b))[:k]
    guaranteed = tuple(cid for cid in ranking if certificates[cid].guaranteed(a, b))[:k]
    stable = possible == guaranteed
    return ContextStability(stable, possible, guaranteed, possible if stable else None)
