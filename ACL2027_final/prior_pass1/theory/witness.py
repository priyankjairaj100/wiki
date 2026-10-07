"""Compile direct temporal witnesses without connected-component closure.

The compiler reads claim IDs, text, and timestamps. It never reads gold fields.
It preserves the original detector's predicates and all temporal cutoffs.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import groupby
from math import inf, isfinite
from typing import Callable, Iterable, Mapping

from wikigraphrag.core.claim import Claim
from wikigraphrag.detect.features import ClaimFeatures, extract_features
from wikigraphrag.detect.signals import changed_value, same_subject_relation


@dataclass(frozen=True)
class Witness:
    """One claim's lifetime and its first direct contradiction."""

    cid: str
    start: float
    end: float
    witness: str | None

    def contains(self, cutoff: float) -> bool:
        return self.start <= cutoff < self.end


@dataclass(frozen=True)
class CompileStats:
    dated_claims: int
    undated_claims: int
    posting_visits: int
    pair_tests: int
    witnesses: int


class WitnessIndex:
    def __init__(self, records: Mapping[str, Witness], undated: Iterable[str], stats: CompileStats):
        self.records = dict(records)
        self.undated = frozenset(undated)
        self.stats = stats

    def eligible(self, cid: str, cutoff: float) -> bool:
        record = self.records.get(cid)
        return record is not None and record.contains(cutoff)

    def filter(self, ranked_cids: Iterable[str], cutoff: float, k: int | None = None) -> list[str]:
        """Filter before truncation while preserving the supplied ranking."""
        out = []
        if k is not None and k <= 0:
            return out
        for cid in ranked_cids:
            if self.eligible(cid, cutoff):
                out.append(cid)
                if k is not None and len(out) >= k:
                    break
        return out

    def current(self) -> set[str]:
        """Return dated claims without a contradiction in the supplied corpus."""
        return {cid for cid, record in self.records.items() if record.end == inf}


def _tokens(feature: ClaimFeatures) -> frozenset[tuple[str, str]]:
    """A complete candidate filter for the detector's default positive threshold.

    Matching nonempty frames share a frame token. Empty frames use one bucket.
    The bucket also covers cases where subject matching uses fallback features.
    """
    if feature.frame:
        return frozenset(("frame", token) for token in feature.frame)
    return frozenset({("empty_frame", "")})


def compile_witnesses(
    claims: Iterable[Claim],
    *,
    match: Callable[[ClaimFeatures, ClaimFeatures], bool] = same_subject_relation,
    differs: Callable[[ClaimFeatures, ClaimFeatures], bool] = changed_value,
    features: Callable[[Claim], ClaimFeatures] = extract_features,
    blocked: bool = True,
) -> WitnessIndex:
    """Compile one earliest direct witness per dated claim.

    Use ``blocked=False`` for custom matchers without the default frame gate.
    Time ties enter the index together after all comparisons with older claims.
    Undated claims receive no temporal certificate and remain in a separate set.
    """
    claim_list = list(claims)
    cids = [claim.cid for claim in claim_list]
    if len(set(cids)) != len(cids):
        raise ValueError("Claim IDs must be unique.")
    dated = []
    undated = []
    for claim in claim_list:
        if claim.timestamp is None:
            undated.append(claim.cid)
        else:
            if not isfinite(claim.timestamp):
                raise ValueError("Claim timestamps must be finite.")
            dated.append(claim)
    dated.sort(key=lambda claim: (claim.timestamp, claim.cid))
    feats = {claim.cid: features(claim) for claim in dated}
    tokens = {claim.cid: _tokens(feats[claim.cid]) for claim in dated}
    postings: dict[tuple[str, str], set[str]] = defaultdict(set)
    unresolved: set[str] = set()
    records = {
        claim.cid: Witness(claim.cid, float(claim.timestamp), inf, None)
        for claim in dated
    }
    posting_visits = pair_tests = 0

    for timestamp, iterator in groupby(dated, key=lambda claim: claim.timestamp):
        batch = list(iterator)
        for newer in batch:
            if blocked:
                candidates = set()
                for token in tokens[newer.cid]:
                    posting = postings.get(token, ())
                    posting_visits += len(posting)
                    candidates.update(posting)
            else:
                candidates = set(unresolved)
                posting_visits += len(candidates)
            for older_id in sorted(candidates):
                pair_tests += 1
                if not match(feats[newer.cid], feats[older_id]):
                    continue
                if not differs(feats[newer.cid], feats[older_id]):
                    continue
                old = records[older_id]
                records[older_id] = Witness(older_id, old.start, float(timestamp), newer.cid)
                unresolved.remove(older_id)
                for token in tokens[older_id]:
                    postings[token].remove(older_id)
        # Claims at this time cannot terminate one another.
        for claim in batch:
            unresolved.add(claim.cid)
            for token in tokens[claim.cid]:
                postings[token].add(claim.cid)

    stats = CompileStats(
        dated_claims=len(dated),
        undated_claims=len(undated),
        posting_visits=posting_visits,
        pair_tests=pair_tests,
        witnesses=sum(record.witness is not None for record in records.values()),
    )
    return WitnessIndex(records, undated, stats)
