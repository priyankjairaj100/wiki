"""Freeze or evaluate hybrid screening on the existing frozen model grid."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

from constraint_oracle import from_record
from hybrid import HybridIndex
from run_benchmark import exhaustive_worlds, direct_activity, mask_for, top, world_valid

HERE = Path(__file__).resolve().parent


def freeze():
    destination = HERE / "HYBRID_FREEZE.json"
    if destination.exists():
        raise SystemExit("The hybrid protocol is already frozen.")
    result = {
        "scope": "all 120 nonempty models from the previous frozen benchmark; no exclusions",
        "predicate": "overlap", "queries": [[a, b] for a in range(7) for b in range(a, 7)],
        "budgets": [1, 3, 5], "model_feasibility": "checked once per model before selection",
        "cache": "no support cache across queries or budgets",
        "comparison": "five exact support queries per context; full oracle without product screening",
        "outcomes": ["exact_support_context", "exact_stability", "all_counterworlds_replay",
                     "oracle_claim_queries", "feasibility_calls", "zero_solver_screens", "new_stable_contexts"],
        "reference": "exhaust every feasible assignment and directly evaluate activity",
        "timing_policy": "count solver calls only; no end-to-end runtime claim",
        "files": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                  for name in ("PROTOCOL_FREEZE.json", "cases.jsonl", "constraint_oracle.py", "hybrid.py", "run_hybrid.py", "run_benchmark.py")}}
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("Hybrid extension frozen before its execution.")


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((HERE / "HYBRID_FREEZE.json").read_text())
    for name, expected in protocol["files"].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected, name
    counts = Counter()
    budgets = defaultdict(Counter)
    with (output / "hybrid_decisions.jsonl").open("w") as destination:
        for line in (HERE / "cases.jsonl").read_text().splitlines():
            record = json.loads(line)
            if not record["expected_nonempty"]:
                continue
            index = HybridIndex(from_record(record))
            counts["models"] += 1
            counts["model_feasibility_calls"] += index.oracle.feasibility_calls
            worlds = exhaustive_worlds(record)
            activity = direct_activity(record, worlds)
            for a, b in protocol["queries"]:
                masks = mask_for(record, worlds, activity, a, b, "overlap")
                p, h = masks.any(axis=0), masks.all(axis=0)
                # Charge one full support query per visible claim and per context budget.
                baseline = [index.oracle.query(c, a, b, "overlap") for c in record["visible"]]
                baseline_feasibility = sum(row["feasibility_calls"] for row in baseline)
                for k in protocol["budgets"]:
                    result = index.select(record["ranking"], a, b, k)
                    expected_top = top(p, record["ranking"], k)
                    expected_stable = expected_top == top(h, record["ranking"], k)
                    assert tuple(result["possible_top"]) == expected_top
                    assert result["stable"] == expected_stable
                    reference_contexts = {top(mask, record["ranking"], k) for mask in masks}
                    assert result["stable"] == (len(reference_contexts) == 1)
                    if not result["stable"]:
                        contexts = []
                        for field, wanted in (("support_world", True), ("exclusion_world", False)):
                            world = result[field]
                            assert world_valid(record, world)
                            array = np.asarray([world])
                            mask = mask_for(record, array, direct_activity(record, array), a, b, "overlap")[0]
                            context = top(mask, record["ranking"], k)
                            assert (result["pivot"] in context) == wanted
                            contexts.append(context)
                        assert contexts[0] != contexts[1]
                        counts["counterworld_pairs_replayed"] += 1
                    for counter in (counts, budgets[str(k)]):
                        counter["contexts"] += 1
                        counter["stable"] += int(result["stable"])
                        counter["zero_solver_screens"] += int(result["screened"])
                        counter["new_stable_contexts"] += int(result["stable"] and not result["screened"])
                        counter["full_oracle_claim_queries"] += len(record["visible"])
                        counter["hybrid_oracle_claim_queries"] += result["oracle_claim_queries"]
                        counter["full_oracle_feasibility_calls"] += baseline_feasibility
                        counter["hybrid_feasibility_calls"] += result["feasibility_calls"]
                        counter["mismatches"] += 0
                    destination.write(json.dumps({"case_id": record["case_id"], "query": [a, b], "k": k,
                                                  **result, "full_oracle_feasibility_calls": baseline_feasibility}, sort_keys=True) + "\n")
    results = {"status": "passed", "counts": dict(counts), "by_budget": {k: dict(v) for k, v in budgets.items()},
               "protocol_sha256": hashlib.sha256((HERE / "HYBRID_FREEZE.json").read_bytes()).hexdigest()}
    (output / "hybrid_results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    freeze() if args.freeze else run(args.output)
