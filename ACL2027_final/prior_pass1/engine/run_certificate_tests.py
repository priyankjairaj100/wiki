"""Run constructed tests and exhaustive equivalence checks on packaged claims."""

import argparse
import hashlib
import json
import sys
import time
import unittest
from pathlib import Path

from engine import SupersessionGate, compile_certificates, load_visible_claims


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.package_root.resolve()))
    sys.path.insert(0, str(Path(__file__).parent / "tests"))
    from test_engine import event_cutoffs, full_pair_oracle, oracle_ids
    from wikigraphrag.detect.supersession import SupersessionDetector

    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent / "tests"))
    started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    engine_root = Path(__file__).parent
    report = {"provenance": {
                  "python": sys.version,
                  "source_sha256": {str(path.relative_to(engine_root)):
                      hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in (engine_root / "engine.py", Path(__file__),
                                   engine_root / "tests" / "test_engine.py")}},
              "constructed_tests": {"tests_run": result.testsRun,
                                    "failures": len(result.failures), "errors": len(result.errors),
                                    "random_seeds": 100,
                                    "label": "Correctness tests, not benchmark observations"},
              "packaged_data_equivalence": []}
    if not result.wasSuccessful():
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(1)
    root = args.data_root or args.package_root / "data"
    for path in sorted(root.glob("*/claims.jsonl")):
        claims = load_visible_claims(path)
        detector = SupersessionDetector()
        gate = SupersessionGate(claims, detector)
        index = compile_certificates(claims, gate)
        boundaries, accepted = full_pair_oracle(claims, gate)
        cutoffs = event_cutoffs(claims)
        mismatches = []
        for cid, (end, witness) in boundaries.items():
            if (index.certificates[cid].end, index.certificates[cid].witness_cid) != (end, witness):
                mismatches.append({"cid": cid, "kind": "boundary_or_witness"})
        for cutoff in cutoffs:
            if index.eligible_ids(cutoff) != oracle_ids(claims, accepted, cutoff):
                mismatches.append({"cutoff": cutoff, "kind": "eligible_set"})
        original_current = {c.cid for c in claims} - {e.older for e in detector.detect(claims)}
        current_difference = len(original_current ^ index.current_ids())
        report["packaged_data_equivalence"].append({
            "dataset": path.parent.name, "claims": len(claims), "cutoffs": len(cutoffs),
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "endpoint_witness_cutoff_mismatches": mismatches,
            "original_current_mask_difference": current_difference,
            "compiler_stats": index.stats,
        })
        print(f"{path.parent.name}: {len(claims)} claims; {len(cutoffs)} cutoffs; "
              f"{len(mismatches)} mismatches; current difference {current_difference}")
    report["elapsed_seconds"] = time.perf_counter() - started
    report["passed"] = all(not d["endpoint_witness_cutoff_mismatches"] and
                           d["original_current_mask_difference"] == 0
                           for d in report["packaged_data_equivalence"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
