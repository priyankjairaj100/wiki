"""Source-event adapter for the pass-2 two-witness compiler.

Times use one consistent real-valued axis. Gregorian day ordinals are suitable.
An end is a termination event, so realized activity is [start, end).
The adapter never infers replacement from a matching slot or a different value.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable, Mapping

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from pass2.theory.uncertain_time import (  # noqa: E402
    IntervalClaim, TwoCertificate, compile_from_pairs,
)

_END_PREFIX = "@explicit-end:"


@dataclass(frozen=True)
class LifecycleClaim:
    """One source assertion with an uncertain start and optional uncertain end.

    The end bounds must be strictly later than every allowed start.
    This preserves independent date choices and prevents empty lifetimes.
    A full validity duration must not be placed in the two start fields.
    """
    cid: str
    text: str
    lower: float
    upper: float
    end_lower: float | None = None
    end_upper: float | None = None

    def __post_init__(self):
        IntervalClaim(self.cid, self.text, self.lower, self.upper)
        if self.cid.startswith(_END_PREFIX):
            raise ValueError("Claim identifiers cannot use the reserved end prefix.")
        if not isinstance(self.text, str):
            raise ValueError("Claim text must be a string.")
        if (self.end_lower is None) != (self.end_upper is None):
            raise ValueError("An explicit end needs both date bounds.")
        if self.end_lower is not None:
            IntervalClaim(_END_PREFIX + self.cid, "", self.end_lower, self.end_upper)
            if self.end_lower <= self.upper:
                raise ValueError("Every explicit end must follow every allowed start.")

    @classmethod
    def from_record(cls, record: Mapping) -> "LifecycleClaim":
        """Read the source-only extractor schema, without consulting gold labels.

        The extractor must already assign start and end their stated meanings.
        Overlapping start/end bounds raise an error for explicit fallback routing.
        """
        kind = record.get("temporal_kind")
        if kind not in ("occurrence_start", "validity_duration"):
            raise ValueError("Only an occurrence start or explicit duration is supported.")
        start, end = record["start"], record.get("end")
        span = record.get("source_span", {})
        text = span.get("text", record.get("text", ""))
        if kind == "validity_duration" and end is None:
            raise ValueError("A validity duration needs a separate explicit end.")
        return cls(record["claim_id"], text, start["lower"], start["upper"],
                   None if end is None else end["lower"],
                   None if end is None else end["upper"])


@dataclass(frozen=True)
class LifecycleIndex:
    claims: Mapping[str, LifecycleClaim]
    certificates: Mapping[str, TwoCertificate]
    events: Mapping[str, IntervalClaim]
    event_pairs: tuple[tuple[str, str], ...]
    explicit_end_ids: Mapping[str, str]


def compile_lifecycles(
    claims: Iterable[LifecycleClaim],
    accepted_directed_pairs: Iterable[tuple[str, str]],
) -> LifecycleIndex:
    """Compile source claims and hidden termination events.

    Caller pairs must use source claim IDs only. Both endpoints must be modeled.
    An unknown witness cannot be discarded silently while retaining guarantees.
    No rule deduplicates recurrent values or creates a slot exclusion gate.
    """
    by_id: dict[str, LifecycleClaim] = {}
    for claim in claims:
        if not isinstance(claim, LifecycleClaim):
            raise TypeError("Inputs must be LifecycleClaim objects.")
        if claim.cid in by_id:
            raise ValueError("Claim identifiers must be unique.")
        by_id[claim.cid] = claim
    pairs: list[tuple[str, str]] = []
    for pair in accepted_directed_pairs:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("Each pair must contain witness and target identifiers.")
        witness, target = pair
        if not isinstance(witness, str) or not isinstance(target, str):
            raise ValueError("Pair identifiers must be strings.")
        if witness not in by_id or target not in by_id:
            raise ValueError("Every pair endpoint must name a modeled source claim.")
        if witness != target:
            pairs.append((witness, target))
    events = {cid: IntervalClaim(cid, c.text, c.lower, c.upper)
              for cid, c in by_id.items()}
    end_ids = {}
    for cid, claim in by_id.items():
        if claim.end_lower is not None:
            end_id = _END_PREFIX + cid
            events[end_id] = IntervalClaim(end_id, "Explicit termination of " + cid,
                                           claim.end_lower, claim.end_upper)
            end_ids[cid] = end_id
            pairs.append((end_id, cid))
    # Normalization makes repeated pair input harmless and keeps audit output stable.
    event_pairs = tuple(sorted(set(pairs)))
    all_certificates = compile_from_pairs(events.values(), event_pairs)
    certificates = {cid: all_certificates[cid] for cid in by_id}
    return LifecycleIndex(by_id, certificates, events, event_pairs, end_ids)


def completion_certificates(index: LifecycleIndex, completion: str) -> dict[str, TwoCertificate]:
    """Complete all starts and ends by the same predeclared endpoint rule."""
    if completion not in ("earliest", "midpoint", "latest"):
        raise ValueError("Completion must be earliest, midpoint, or latest.")
    completed = []
    for event in index.events.values():
        if completion == "earliest":
            date = event.lower
        elif completion == "latest":
            date = event.upper
        else:
            date = event.lower + (event.upper - event.lower) / 2
        completed.append(IntervalClaim(event.cid, event.text, date, date))
    certificates = compile_from_pairs(completed, index.event_pairs)
    return {cid: certificates[cid] for cid in index.claims}


@dataclass(frozen=True)
class ContextItem:
    cid: str
    status: str


def _ranking(index: LifecycleIndex, ranked_ids: Iterable[str], unknown_ids: Iterable[str]) -> tuple[tuple[str, ...], frozenset[str]]:
    unknown = tuple(unknown_ids)
    if any(not isinstance(cid, str) or not cid for cid in unknown):
        raise ValueError("Unknown fallback identifiers must be nonempty strings.")
    if len(unknown) != len(set(unknown)):
        raise ValueError("Unknown fallback identifiers must be unique.")
    unknown_set = frozenset(unknown)
    if unknown_set.intersection(index.claims):
        raise ValueError("A claim cannot be both modeled and unknown.")
    ranking = tuple(ranked_ids)
    if any(not isinstance(cid, str) for cid in ranking):
        raise ValueError("Ranking entries must be claim identifiers.")
    if len(ranking) != len(set(ranking)):
        raise ValueError("Ranking entries must be unique.")
    if set(ranking) != set(index.claims).union(unknown_set):
        raise ValueError("The fixed ranking must contain every source claim once.")
    return ranking, unknown_set


def select_context(
    index: LifecycleIndex,
    ranked_ids: Iterable[str],
    a: float,
    b: float | None = None,
    *,
    k: int = 5,
    policy: str = "possible",
    unknown_ids: Iterable[str] = (),
) -> tuple[ContextItem, ...]:
    """Select a fixed-ranked context and preserve every item's support status.

    Unknown claims remain available under every policy. Their tag stays unknown.
    Completion controls share claims, gates, ends, ranking, and context budget.
    `interval` ignores replacement gates and checks outer lifespan overlap.
    This control uses strict termination, just like every other policy here.
    """
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError("The context budget must be a nonnegative integer.")
    b = a if b is None else b
    TwoCertificate._query(a, b)
    ranking, unknown = _ranking(index, ranked_ids, unknown_ids)
    if policy not in ("possible", "guaranteed", "earliest", "midpoint", "latest", "no_filter", "interval"):
        raise ValueError("Unknown context policy.")
    exact = completion_certificates(index, policy) if policy in ("earliest", "midpoint", "latest") else None
    retained = []
    for cid in ranking:
        if cid in unknown:
            keep, status = True, "unknown"
        else:
            cert = index.certificates[cid]
            status = cert.status(a, b)
            claim = index.claims[cid]
            if policy == "possible":
                keep = cert.possible(a, b)
            elif policy == "guaranteed":
                keep = cert.guaranteed(a, b)
            elif exact is not None:
                keep = exact[cid].possible(a, b)
            elif policy == "interval":
                keep = claim.lower <= b and (claim.end_upper is None or a < claim.end_upper)
            else:
                keep = True
        if keep:
            retained.append(ContextItem(cid, status))
    return tuple(retained[:k])


@dataclass(frozen=True)
class LifecycleStability:
    stable: bool
    possible_top: tuple[str, ...]
    guaranteed_top: tuple[str, ...]
    common_context: tuple[str, ...] | None
    scope: str = "modeled event dates with fixed unknown fallback"


def stable_lifecycle_context(
    index: LifecycleIndex,
    ranked_ids: Iterable[str],
    a: float,
    b: float | None = None,
    *,
    k: int = 5,
    unknown_ids: Iterable[str] = (),
) -> LifecycleStability:
    """Test exact context stability across the modeled independent event dates.

    Unknown fallback is fixed in all operational masks. It is not certified valid.
    Hidden end events cannot occupy a context position.
    """
    ranking, unknown = _ranking(index, ranked_ids, unknown_ids)
    possible = tuple(x.cid for x in select_context(index, ranking, a, b, k=k,
                     policy="possible", unknown_ids=unknown))
    guaranteed = tuple(x.cid for x in select_context(index, ranking, a, b, k=k,
                       policy="guaranteed", unknown_ids=unknown))
    stable = possible == guaranteed
    return LifecycleStability(stable, possible, guaranteed, possible if stable else None)
