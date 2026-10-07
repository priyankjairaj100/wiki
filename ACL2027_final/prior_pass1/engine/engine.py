"""Compile earliest direct witnesses for temporal evidence eligibility.

Only the Python standard library is required. The default gate adapter imports
the unchanged WikiGraphRAG detector package supplied with this project.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from itertools import groupby
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional


@dataclass(frozen=True)
class EvidenceClaim:
    """Detector-visible fields. No gold annotation enters the compiler."""

    cid: str
    text: str
    timestamp: Optional[float]
    doc_id: str = "doc"


@dataclass(frozen=True)
class Certificate:
    cid: str
    start: Optional[float]
    end: float
    witness_cid: Optional[str]
    doc_id: str

    def contains(self, cutoff: float) -> bool:
        return self.start is not None and self.start <= cutoff < self.end


class SupersessionGate:
    """Use the original feature parser and pair predicates without modification.

    Positive frame thresholds permit complete frame-token candidate blocking.
    Other thresholds use a shared bucket, which performs an exhaustive scan.
    """

    def __init__(self, claims: Iterable[EvidenceClaim], detector=None):
        from wikigraphrag.detect.features import extract_features
        from wikigraphrag.detect.signals import changed_value, same_subject_relation
        from wikigraphrag.detect.supersession import SupersessionDetector

        self.detector = detector or SupersessionDetector()
        if self.detector.randomize_time:
            raise ValueError("Freeze timestamp perturbations before compilation.")
        self.features = {
            c.cid: extract_features(c, positional=self.detector.positional,
                                    role_aware=self.detector.role_aware)
            for c in claims
        }
        self._match = same_subject_relation
        self._changed = changed_value
        self.source_functions = (extract_features, same_subject_relation, changed_value)

    def __call__(self, newer: EvidenceClaim, older: EvidenceClaim) -> bool:
        a, b = self.features[newer.cid], self.features[older.cid]
        matched = self._match(
            a, b, frame_threshold=self.detector.frame_threshold,
            token_threshold=self.detector.token_threshold,
            require_subject=self.detector.use_subject,
        )
        return matched and (not self.detector.use_value or self._changed(a, b))

    def candidate_keys(self, claim: EvidenceClaim) -> frozenset:
        if self.detector.frame_threshold <= 0:
            return frozenset({("all", "")})
        frame = self.features[claim.cid].frame
        if frame:
            return frozenset(("frame", word) for word in frame)
        return frozenset({("empty_frame", "")})

    def provenance(self) -> dict:
        config = {name: getattr(self.detector, name) for name in (
            "frame_threshold", "token_threshold", "use_subject", "use_value",
            "positional", "role_aware",
        )}
        sources = {}
        for function in self.source_functions:
            path = Path(inspect.getfile(function))
            sources[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        # Parser changes can alter extracted features without changing features.py.
        from wikigraphrag.parse import text
        parser_path = Path(inspect.getfile(text))
        sources["parse/text.py"] = hashlib.sha256(parser_path.read_bytes()).hexdigest()
        return {"name": "SupersessionDetector unchanged pair gates",
                "config": config, "source_sha256": sources}


class CertificateIndex:
    def __init__(self, certificates: Mapping[str, Certificate], stats: dict,
                 provenance: dict):
        self.certificates = dict(certificates)
        self.records = self.certificates
        self.stats = stats
        self.provenance = provenance

    def eligible(self, cid: str, cutoff: float) -> bool:
        _validate_cutoff(cutoff)
        return self.certificates[cid].contains(cutoff)

    def eligible_ids(self, cutoff: float) -> set[str]:
        _validate_cutoff(cutoff)
        return {cid for cid, item in self.certificates.items() if item.contains(cutoff)}

    def current_ids(self) -> set[str]:
        """Undated claims remain current, matching the original stale mask."""
        return {cid for cid, item in self.certificates.items() if math.isinf(item.end)}

    def filter_ranked(self, ranked_cids: Iterable[str], as_of: Optional[float] = None,
                      k: Optional[int] = None) -> list[str]:
        """Apply eligibility before top-k while preserving the supplied ranking."""
        if k is not None and (not isinstance(k, int) or isinstance(k, bool) or k < 0):
            raise ValueError("k must be a nonnegative integer or None.")
        if as_of is not None:
            _validate_cutoff(as_of)
        if k == 0:
            return []
        output = []
        for cid in ranked_cids:
            item = self.certificates[cid]
            keep = math.isinf(item.end) if as_of is None else item.contains(as_of)
            if keep:
                output.append(cid)
                if k is not None and len(output) == k:
                    break
        return output

    def to_dict(self) -> dict:
        records = []
        for cid in sorted(self.certificates):
            item = asdict(self.certificates[cid])
            item["end"] = None if math.isinf(item["end"]) else item["end"]
            records.append(item)
        return {
            "schema": "direct-witness-certificates-v1",
            "semantics": {
                "boundary": "earliest strictly later accepted direct witness",
                "interval": "[start,end)", "null_end": "positive infinity",
                "tie_policy": "lexicographically smallest cid at earliest witness time",
                "undated_policy": "excluded as-of; retained current",
                "time_axis": "input source timestamp; no inferred event time",
                "guarantee": "eligibility relative to the supplied pair predicate",
            },
            "provenance": self.provenance,
            "stats": self.stats,
            "certificates": records,
        }


def _validate_cutoff(cutoff: float) -> None:
    if not isinstance(cutoff, (int, float)) or not math.isfinite(cutoff):
        raise ValueError("As-of cutoffs must be finite numbers.")


def _visible_claim(claim) -> EvidenceClaim:
    """Copy only permitted fields, including when inputs carry gold annotations."""
    if not isinstance(claim.cid, str) or not claim.cid:
        raise ValueError("Claim IDs must be nonempty strings.")
    if not isinstance(claim.text, str):
        raise ValueError("Claim text must be a string.")
    timestamp = claim.timestamp
    if timestamp is not None:
        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
            raise ValueError("Timestamps must be finite numbers or None.")
        if not math.isfinite(timestamp):
            raise ValueError("Timestamps must be finite numbers or None.")
        timestamp = float(timestamp)
    return EvidenceClaim(claim.cid, claim.text, timestamp, getattr(claim, "doc_id", "doc"))


def compile_certificates(claims: Iterable, gate: Optional[Callable] = None, *,
                         detector=None, blocked: bool = True) -> CertificateIndex:
    """Compile one direct witness per claim in timestamp batches.

    A custom gate receives (newer, older) EvidenceClaim objects. Custom gates use
    exhaustive unresolved candidates unless they expose candidate_keys(claim).
    Such keys MUST overlap for every accepted pair. Set blocked=False to bypass
    candidate keys. Input order cannot affect boundaries or witness selection.
    """
    claim_list = [_visible_claim(claim) for claim in claims]
    by_cid = {claim.cid: claim for claim in claim_list}
    if len(by_cid) != len(claim_list):
        raise ValueError("Claim IDs must be unique.")
    if gate is not None and detector is not None:
        raise ValueError("Supply a gate or a detector, not both.")
    if gate is None:
        gate = SupersessionGate(claim_list, detector)
    dated = sorted((c for c in claim_list if c.timestamp is not None),
                   key=lambda c: (c.timestamp, c.cid))
    certificates = {
        c.cid: Certificate(c.cid, c.timestamp, math.inf, None, c.doc_id)
        for c in sorted(claim_list, key=lambda c: c.cid)
    }
    can_block = blocked and hasattr(gate, "candidate_keys")
    keys = {c.cid: gate.candidate_keys(c) if can_block else frozenset({("all", "")})
            for c in dated}
    postings = defaultdict(set)
    posting_visits = pair_tests = 0
    for timestamp, batch_iter in groupby(dated, key=lambda c: c.timestamp):
        batch = list(batch_iter)
        # No member of this batch enters postings before all comparisons finish.
        for newer in batch:
            candidates = set()
            for key in keys[newer.cid]:
                posting = postings.get(key, ())
                posting_visits += len(posting)
                candidates.update(posting)
            # Older-claim order cannot affect a pure direct pair predicate.
            # Newer claims already have canonical timestamp/CID order.
            for older_id in candidates:
                pair_tests += 1
                if not gate(newer, by_cid[older_id]):
                    continue
                old = certificates[older_id]
                certificates[older_id] = Certificate(
                    older_id, old.start, timestamp, newer.cid, old.doc_id)
                for key in keys[older_id]:
                    postings[key].remove(older_id)
        for claim in batch:
            for key in keys[claim.cid]:
                postings[key].add(claim.cid)
    visible_records = [asdict(by_cid[cid]) for cid in sorted(by_cid)]
    canonical = json.dumps(visible_records, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    gate_provenance = (gate.provenance() if hasattr(gate, "provenance")
                       else {"name": "custom pair predicate"})
    provenance = {
        "visible_input_sha256": hashlib.sha256(canonical).hexdigest(),
        "engine_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "gate": gate_provenance,
        "blocking": "complete candidate keys" if can_block else "all unresolved claims",
    }
    stats = {
        "claims": len(claim_list), "dated_claims": len(dated),
        "undated_claims": len(claim_list) - len(dated),
        "posting_visits": posting_visits, "pair_tests": pair_tests,
        "witnesses": sum(c.witness_cid is not None for c in certificates.values()),
    }
    return CertificateIndex(certificates, stats, provenance)


def load_visible_claims(path: Path) -> list[EvidenceClaim]:
    claims = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            try:
                claims.append(EvidenceClaim(row["cid"], row["text"],
                                            row.get("timestamp"), row.get("doc_id", "doc")))
            except KeyError as error:
                raise ValueError(f"Missing field at line {line_number}: {error}") from error
    return claims


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--package-root", type=Path,
                        help="Directory containing the original wikigraphrag package")
    parser.add_argument("--no-blocking", action="store_true")
    parser.add_argument("--as-of", type=float, help="Include eligible IDs at this finite source time")
    args = parser.parse_args()
    if args.package_root:
        sys.path.insert(0, str(args.package_root.resolve()))
    index = compile_certificates(load_visible_claims(args.claims), blocked=not args.no_blocking)
    result = index.to_dict()
    result["provenance"]["input_file_sha256"] = hashlib.sha256(args.claims.read_bytes()).hexdigest()
    result["current_ids"] = sorted(index.current_ids())
    if args.as_of is not None:
        result["as_of"] = {"cutoff": args.as_of, "eligible_ids": sorted(index.eligible_ids(args.as_of))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({"output": str(args.output), "stats": index.stats}, sort_keys=True))


if __name__ == "__main__":
    main()
