"""Frozen amendment: compare hybrid screening against lazy exact selection."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from constraint_oracle import SupportOracle, from_record
from run_benchmark import exhaustive_worlds, direct_activity, mask_for, top

HERE = Path(__file__).resolve().parent


def freeze():
    destination = HERE / "LAZY_BASELINE_FREEZE.json"
    if destination.exists():
        raise SystemExit("The lazy baseline is already frozen.")
    protocol = {
        "amendment": "Added after hybrid results to separate budget stopping from product screening",
        "freeze_timing": "before any lazy-baseline execution",
        "scope": "all 10,080 overlap contexts in the existing hybrid benchmark",
        "cases_added_or_removed": 0,
        "algorithm": "scan the fixed ranking; query exact possible and guaranteed support; stop after k possible claims",
        "oracle": "same SupportOracle.query API used by the hybrid",
        "cache": "no support cache across queries or budgets",
        "queries": [[a, b] for a in range(7) for b in range(a, 7)], "budgets": [1, 3, 5],
        "model_feasibility": "one initial check per model, excluded from query counts",
        "reference": "exhaustive direct activity and exact possible and guaranteed sets",
        "outcomes": ["selection_agreement", "stability_agreement", "claim_queries", "feasibility_calls"],
        "files": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                  for name in ("cases.jsonl", "constraint_oracle.py", "run_benchmark.py", "run_lazy_baseline.py",
                               "hybrid_decisions.jsonl", "hybrid_results.json")}}
    destination.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    print("Lazy baseline frozen before execution.")


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((HERE / "LAZY_BASELINE_FREEZE.json").read_text())
    for name, expected in protocol["files"].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected, name
    hybrid = {}
    for line in (HERE / "hybrid_decisions.jsonl").read_text().splitlines():
        row = json.loads(line)
        hybrid[row["case_id"], tuple(row["query"]), row["k"]] = row
    counts = Counter()
    budgets = defaultdict(Counter)
    with (output / "lazy_baseline_decisions.jsonl").open("w") as destination:
        for line in (HERE / "cases.jsonl").read_text().splitlines():
            record = json.loads(line)
            if not record["expected_nonempty"]:
                continue
            oracle = SupportOracle(from_record(record))
            counts["model_feasibility_calls"] += oracle.feasibility_calls
            counts["models"] += 1
            worlds = exhaustive_worlds(record)
            activity = direct_activity(record, worlds)
            for a, b in protocol["queries"]:
                masks = mask_for(record, worlds, activity, a, b, "overlap")
                p, h = masks.any(axis=0), masks.all(axis=0)
                for k in protocol["budgets"]:
                    before = oracle.feasibility_calls
                    queries = 0
                    selected, frontier = [], []
                    for c in record["ranking"]:
                        result = oracle.query(c, a, b, "overlap")
                        queries += 1
                        if not result["possible"]:
                            continue
                        selected.append(c)
                        if not result["guaranteed"]:
                            frontier.append(c)
                        if len(selected) == k:
                            break
                    solver_calls = oracle.feasibility_calls - before
                    expected_top = top(p, record["ranking"], k)
                    expected_stable = expected_top == top(h, record["ranking"], k)
                    assert tuple(selected) == expected_top
                    assert (not frontier) == expected_stable
                    previous = hybrid[record["case_id"], (a, b), k]
                    assert selected == previous["possible_top"] and (not frontier) == previous["stable"]
                    for counter in (counts, budgets[str(k)]):
                        counter["contexts"] += 1
                        counter["stable"] += int(expected_stable)
                        counter["full_oracle_claim_queries"] += len(record["visible"])
                        counter["lazy_oracle_claim_queries"] += queries
                        counter["hybrid_oracle_claim_queries"] += previous["oracle_claim_queries"]
                        counter["full_oracle_feasibility_calls"] += previous["full_oracle_feasibility_calls"]
                        counter["lazy_feasibility_calls"] += solver_calls
                        counter["hybrid_feasibility_calls"] += previous["feasibility_calls"]
                        counter["mismatches"] += 0
                    destination.write(json.dumps({"case_id": record["case_id"], "query": [a, b], "k": k,
                        "possible_top": selected, "frontier": frontier, "stable": not frontier,
                        "lazy_oracle_claim_queries": queries, "lazy_feasibility_calls": solver_calls,
                        "hybrid_oracle_claim_queries": previous["oracle_claim_queries"],
                        "hybrid_feasibility_calls": previous["feasibility_calls"]}, sort_keys=True) + "\n")
    results = {"status": "passed", "counts": dict(counts), "by_budget": {k: dict(v) for k, v in budgets.items()},
               "protocol_sha256": hashlib.sha256((HERE / "LAZY_BASELINE_FREEZE.json").read_bytes()).hexdigest()}
    (output / "lazy_baseline_results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    freeze() if args.freeze else run(args.output)
