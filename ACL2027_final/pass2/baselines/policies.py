"""Matched-input temporal policies.

The Graphiti condition executes unchanged upstream policy source segments.
It supplies identical parsed candidates to every local policy. This is a
policy-kernel comparison, not a reproduction of the full Graphiti system.
"""
from __future__ import annotations

import collections
import dataclasses
import datetime as dt
import hashlib
import json
import math
import pathlib
from typing import Any, Iterable, Sequence

ROOT = pathlib.Path(__file__).resolve().parent


@dataclasses.dataclass
class _PolicyEdge:
    """Only fields read or written by the upstream policy blocks."""
    uuid: str
    valid_at: dt.datetime | None
    invalid_at: dt.datetime | None = None
    expired_at: dt.datetime | None = None


def _ensure_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc)


def _utc_now():
    # Only nullness matters in this policy. A fixed clock enables exact replay.
    return dt.datetime(2026, 10, 6, tzinfo=dt.timezone.utc)


def _load_upstream():
    manifest = json.loads((ROOT / "vendor/PROVENANCE.json").read_text())
    files = {}
    for entry in manifest["segments"]:
        path = ROOT / "vendor" / entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise RuntimeError(f"Upstream segment changed: {entry['file']}")
        files[entry["file"]] = path.read_text()
    namespace = {"EntityEdge": _PolicyEdge, "ensure_utc": _ensure_utc,
                 "utc_now": _utc_now}
    exec(compile(files["resolve_edge_contradictions.py"],
                 "graphiti:resolve_edge_contradictions", "exec"), namespace)
    forward = compile(files["resolve_extracted_edge_temporal_block.py"],
                      "graphiti:forward-temporal-block", "exec")
    return namespace, forward


_UPSTREAM, _FORWARD = _load_upstream()


def _field(item: Any, name: str):
    return item[name] if isinstance(item, dict) else getattr(item, name)


def _normalize_parsed(parsed: Sequence[Any]):
    """Accept objects or mappings exposing slot and value, with no gold fields."""
    result = []
    for item in parsed:
        slot, value = _field(item, "slot"), _field(item, "value")
        if isinstance(slot, list):
            slot = tuple(slot)
        result.append((slot, value))
    return result


def graphiti_endpoints(observations: Sequence[Any], parsed: Sequence[Any],
                       arrival_order: Iterable[int] | None = None):
    """Return matched-input official Graphiti policy endpoints and diagnostics.

    ``observations`` expose only cid, text and timestamp. ``parsed`` expose
    slot and value. Candidates share a parsed slot and differ in parsed value.
    Equal-time claims do not invalidate each other. All candidate edges enter
    the official policy, including previously expired edges.

    Default ingestion order sorts timestamp then cid. A supplied permutation
    changes ingestion only. Endpoints use the original numeric time scale.
    This adapter deliberately omits upstream semantic extraction, duplicate
    merging, candidate search, graph storage, and generative QA.
    """
    if len(observations) != len(parsed):
        raise ValueError("Observation and parsed lengths differ.")
    n = len(observations)
    features = _normalize_parsed(parsed)
    times = [_field(item, "timestamp") for item in observations]
    cids = [_field(item, "cid") for item in observations]
    if len(set(cids)) != n:
        raise ValueError("CIDs must be unique.")
    finite = [t for t in times if t is not None]
    if any(not math.isfinite(t) for t in finite):
        raise ValueError("Timestamps must be finite or None.")
    # Rank encoding preserves every comparison, including ties and missingness.
    # It avoids unsupported datetime ranges and timestamp-rounding artifacts.
    time_rank = {t: i for i, t in enumerate(sorted(set(finite)))}
    base = dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc)
    encode = {t: base + dt.timedelta(seconds=i) for t, i in time_rank.items()}
    decode = {date: number for number, date in encode.items()}
    edges = [_PolicyEdge(str(cid), encode.get(t)) for cid, t in zip(cids, times)]
    if arrival_order is None:
        order = sorted(range(n), key=lambda i: (times[i] is None,
                       times[i] if times[i] is not None else 0, str(cids[i])))
    else:
        order = list(arrival_order)
    if sorted(order) != list(range(n)):
        raise ValueError("arrival_order must be a permutation.")
    by_slot = collections.defaultdict(list)
    candidate_count = 0
    for i in order:
        slot, value = features[i]
        candidates = []
        if slot is not None and value is not None:
            candidates = [edges[j] for j in by_slot[slot]
                          if features[j][1] is not None and features[j][1] != value]
        candidate_count += len(candidates)
        local = {"resolved_edge": edges[i], "invalidation_candidates": candidates,
                 "now": _utc_now()}
        exec(_FORWARD, _UPSTREAM, local)
        _UPSTREAM["resolve_edge_contradictions"](edges[i], candidates)
        if slot is not None:
            by_slot[slot].append(i)
    endpoints = [decode[e.invalid_at] if e.invalid_at is not None else math.inf
                 for e in edges]
    return endpoints, {
        "label": "Graphiti policy kernel (matched extraction)",
        "full_system_run": False, "n_observations": n,
        "n_candidate_visits": candidate_count,
        "source_sha256": json.loads((ROOT / "vendor/PROVENANCE.json").read_text())[
            "source_sha256"],
        "tie_rule": "strict later date only",
        "time_encoding": "order-preserving ranks encoded as UTC datetimes",
        "omitted_subsystems": ["LLM extraction", "duplicate merging", "candidate search",
                               "graph storage", "reader generation"],
    }


def latest_batch_endpoints(observations: Sequence[Any], parsed: Sequence[Any]):
    """Keep every value in the newest parsed-slot date batch."""
    if len(observations) != len(parsed):
        raise ValueError("Observation and parsed lengths differ.")
    by_slot = collections.defaultdict(list)
    times = [_field(item, "timestamp") for item in observations]
    for i, (slot, _) in enumerate(_normalize_parsed(parsed)):
        if slot is not None and times[i] is not None:
            by_slot[slot].append(i)
    ends = [math.inf] * len(observations)
    for group in by_slot.values():
        dates = sorted({times[i] for i in group})
        next_date = dict(zip(dates, dates[1:]))
        for i in group:
            ends[i] = next_date.get(times[i], math.inf)
    return ends


def direct_first_endpoints(observations: Sequence[Any], parsed: Sequence[Any]):
    """Uncompiled reference: earliest strict later distinct-value witness."""
    by_slot = collections.defaultdict(list)
    times = [_field(item, "timestamp") for item in observations]
    features = _normalize_parsed(parsed)
    for i, (slot, _) in enumerate(features):
        if slot is not None and times[i] is not None:
            by_slot[slot].append(i)
    ends = [math.inf] * len(observations)
    for group in by_slot.values():
        for i in group:
            if features[i][1] is not None:
                ends[i] = min((times[j] for j in group if times[j] > times[i]
                               and features[j][1] is not None
                               and features[i][1] != features[j][1]), default=math.inf)
    return ends


def eligible_indices(observations: Sequence[Any], endpoints: Sequence[float], cutoff):
    """Return the unranked eligible set under half-open validity intervals."""
    return {i for i, item in enumerate(observations)
            if _field(item, "timestamp") is not None
            and _field(item, "timestamp") <= cutoff < endpoints[i]}


def latest_matched_batch(observations: Sequence[Any], parsed: Sequence[Any],
                         query_slot: Any, cutoff, ranking: Sequence[int]):
    """Query-local latest-date selector after exact parsed-slot matching."""
    features = _normalize_parsed(parsed)
    candidates = [i for i in ranking if features[i][0] == query_slot
                  and _field(observations[i], "timestamp") is not None
                  and _field(observations[i], "timestamp") <= cutoff]
    if not candidates:
        return []
    latest = max(_field(observations[i], "timestamp") for i in candidates)
    return [i for i in candidates if _field(observations[i], "timestamp") == latest]
