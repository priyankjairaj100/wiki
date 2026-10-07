"""Constructive context ambiguity and necessary date-refinement decisions.

This module leaves the existing lifecycle API unchanged. It produces actual
date assignments, not hypothetical independent choices of support masks.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping

try:
    from .lifecycle import IntervalClaim, LifecycleIndex, TwoCertificate, _ranking, stable_lifecycle_context
except ImportError:
    from lifecycle import IntervalClaim, LifecycleIndex, TwoCertificate, _ranking, stable_lifecycle_context


@dataclass(frozen=True)
class DateWorld:
    event_dates: Mapping[str, float]
    supported_claims: tuple[str, ...]
    selected_context: tuple[str, ...]


@dataclass(frozen=True)
class ContextCounterworlds:
    pivot_id: str
    support_world: DateWorld
    exclusion_world: DateWorld
    exclusion_reason: str
    exclusion_witness: str | None
    scope: str = "modeled independent event dates with fixed unknown fallback"


@dataclass(frozen=True)
class PivotDateAssignments:
    pivot_id: str
    support_dates: Mapping[str, float]
    exclusion_dates: Mapping[str, float]
    exclusion_reason: str
    exclusion_witness: str | None


def pivot_date_assignments(
    certificate: TwoCertificate,
    events: Mapping[str, IntervalClaim],
    a: float,
    b: float | None = None,
) -> PivotDateAssignments:
    """Construct a support world and an exclusion world from a compact certificate.

    The certificate must come from complete compilation over these event bounds.
    The pivot must have unresolved support. No accepted pair list is needed.
    Both assignments use O(n) time and space. For a frontier pivot, they imply
    different contexts before any optional replay of the full graph.
    """
    b = a if b is None else b
    TwoCertificate._query(a, b)
    if not isinstance(certificate, TwoCertificate):
        raise TypeError("A compiled two-witness certificate is required.")
    if any(not isinstance(event, IntervalClaim) or eid != event.cid for eid, event in events.items()):
        raise ValueError("Event keys must match their interval identifiers.")
    pivot = certificate.cid
    if pivot not in events:
        raise ValueError("The pivot must have an event record.")
    target = events[pivot]
    if (target.lower, target.upper) != (certificate.lower, certificate.upper):
        raise ValueError("The pivot bounds differ from the compiled certificate.")
    if certificate.guaranteed(a, b) or not certificate.possible(a, b):
        raise ValueError("The pivot must have unresolved query support.")

    time = max(a, target.lower)
    pivot_date = min(target.upper, time)
    # Apply the same safe assignment to all nonpivot events. This includes every
    # incoming witness without needing to retain or scan the pair list.
    support_dates = {eid: event.lower if event.lower <= pivot_date else event.upper
                     for eid, event in events.items()}
    support_dates[pivot] = pivot_date

    exclusion_dates = {eid: event.lower for eid, event in events.items()}
    if target.upper > b:
        exclusion_dates[pivot] = target.upper
        reason, witness = "start_after_query", None
    else:
        exclusion_dates[pivot] = target.lower
        witness = certificate.potential_witness
        if witness is None or witness not in events:
            raise ValueError("The retirement certificate needs its witness event.")
        exclusion_dates[witness] = min(events[witness].upper, a)
        if not target.lower < exclusion_dates[witness] <= a:
            raise ValueError("The supplied retirement certificate is inconsistent.")
        reason = "retired_by_query_start"
    return PivotDateAssignments(pivot, support_dates, exclusion_dates, reason, witness)


def evaluate_world(
    index: LifecycleIndex,
    event_dates: Mapping[str, float],
    ranked_ids: Iterable[str],
    a: float,
    b: float | None = None,
    *,
    k: int = 5,
    unknown_ids: Iterable[str] = (),
) -> DateWorld:
    """Evaluate one realized timeline in O(n+m) time, including fixed fallback in n."""
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError("The context budget must be a nonnegative integer.")
    b = a if b is None else b
    TwoCertificate._query(a, b)
    ranking, unknown = _ranking(index, ranked_ids, unknown_ids)
    if set(event_dates) != set(index.events):
        raise ValueError("A world must assign every modeled event exactly once.")
    for eid, event in index.events.items():
        value = event_dates[eid]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("World dates must be finite numbers.")
        if not event.lower <= value <= event.upper:
            raise ValueError("A world date lies outside its source bounds.")
    stops = dict.fromkeys(index.claims, math.inf)
    for witness, target in index.event_pairs:
        if event_dates[witness] > event_dates[target]:
            stops[target] = min(stops[target], event_dates[witness])
    supported = tuple(cid for cid in index.claims
                      if event_dates[cid] <= b and a < stops[cid])
    mask = set(supported).union(unknown)
    context = tuple(cid for cid in ranking if cid in mask)[:k]
    return DateWorld(dict(event_dates), supported, context)


def refinement_frontier(
    index: LifecycleIndex,
    ranked_ids: Iterable[str],
    a: float,
    b: float | None = None,
    *,
    k: int = 5,
    unknown_ids: Iterable[str] = (),
) -> tuple[str, ...]:
    """Return unresolved claims whose support status any stabilizing refinement must settle.

    Every returned claim must become guaranteed or impossible after refinement.
    Resolving this frontier is necessary, but new frontier claims can then enter.
    This is not a minimum set of dates to request from a user or extractor.
    """
    decision = stable_lifecycle_context(index, ranked_ids, a, b, k=k, unknown_ids=unknown_ids)
    guaranteed_ids = set(decision.guaranteed_top)
    return tuple(cid for cid in decision.possible_top if cid not in guaranteed_ids)


def context_counterworlds(
    index: LifecycleIndex,
    ranked_ids: Iterable[str],
    a: float,
    b: float | None = None,
    *,
    k: int = 5,
    unknown_ids: Iterable[str] = (),
) -> ContextCounterworlds | None:
    """Construct two legal timelines with different top-k contexts, or return None.

    The first unresolved possible context item supplies the pivot.
    Every world supporting that pivot selects it, since fewer than k possible
    items outrank it. The second world removes support from the query window.
    Here n includes modeled events and fixed fallback items. The method uses
    O(n+m) time and O(n) output space. Direct replay retains the O(m) pair list.
    """
    b = a if b is None else b
    TwoCertificate._query(a, b)
    ranking, unknown = _ranking(index, ranked_ids, unknown_ids)
    frontier = refinement_frontier(index, ranking, a, b, k=k, unknown_ids=unknown)
    if not frontier:
        return None
    pivot = frontier[0]
    cert = index.certificates[pivot]
    assignments = pivot_date_assignments(cert, index.events, a, b)
    support_world = evaluate_world(index, assignments.support_dates, ranking, a, b, k=k, unknown_ids=unknown)
    assert pivot in support_world.selected_context
    exclusion_world = evaluate_world(index, assignments.exclusion_dates, ranking, a, b, k=k, unknown_ids=unknown)
    assert pivot not in exclusion_world.selected_context
    assert support_world.selected_context != exclusion_world.selected_context
    return ContextCounterworlds(pivot, support_world, exclusion_world,
                               assignments.exclusion_reason, assignments.exclusion_witness)
