"""Create the controlled cases and freeze the protocol before evaluation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
SEED = 20271007


def generate():
    rng = random.Random(SEED)
    cases = []
    for stratum in ("precedence", "lifetime", "joint"):
        for number in range(40):
            centers = [rng.randrange(0, 6) for _ in range(5)]
            bounds = [[max(0, x - rng.randrange(3)), min(6, x + rng.randrange(3))]
                      for x in centers]
            constraints = []
            source_constraints = []
            pairs = [[d, c] for d in range(5) for c in range(5)
                     if d != c and rng.random() < 0.3]
            if stratum in ("lifetime", "joint"):
                c = rng.randrange(5)
                centers[c] = rng.randrange(0, 4)
                bounds[c] = [max(0, centers[c] - rng.randrange(3)), min(6, centers[c] + rng.randrange(3))]
                end = rng.randrange(centers[c] + 1, 7)
                centers.append(end)
                bounds.append([max(0, end - rng.randrange(3)), min(6, end + rng.randrange(3))])
                constraints.append([c, 5, -1])
                source_constraints.append({"kind": "valid_lifetime", "start": c, "end": 5})
                pairs.append([5, c])
            if stratum in ("precedence", "joint"):
                available = [(i, j) for i in range(5) for j in range(5) if centers[i] < centers[j]]
                rng.shuffle(available)
                for i, j in available[:rng.randrange(1, 5)]:
                    constraints.append([i, j, -1])
                    source_constraints.append({"kind": "known_order", "before": i, "after": j})
            ranking = list(range(5))
            rng.shuffle(ranking)
            cases.append({"case_id": f"{stratum}_{number:03}", "stratum": stratum,
                          "bounds": bounds, "visible": list(range(5)), "pairs": sorted(pairs),
                          "constraints": constraints, "source_constraints": source_constraints,
                          "generation_witness": centers, "ranking": ranking, "expected_nonempty": True})
    for number in range(20):
        # The strict cycle cannot hold, even when the interval bounds overlap.
        cases.append({"case_id": f"empty_{number:03}", "stratum": "empty",
                      "bounds": [[0, 1 + number % 5], [0, 1 + number % 5]],
                      "visible": [0, 1], "pairs": [[1, 0]],
                      "constraints": [[0, 1, -1], [1, 0, -1]], "source_constraints": [],
                      "ranking": [0, 1], "expected_nonempty": False})
    return cases


def main():
    if (HERE / "PROTOCOL_FREEZE.json").exists():
        raise SystemExit("Protocol already frozen. Do not replace outcomes or cases.")
    cases = generate()
    data = "".join(json.dumps(row, sort_keys=True) + "\n" for row in cases)
    (HERE / "cases.jsonl").write_text(data)
    protocol = {
        "seed": SEED, "design": "controlled source-independent stress benchmark",
        "counts": {"precedence": 40, "lifetime": 40, "joint": 40, "empty": 20},
        "queries": [[a, b] for a in range(7) for b in range(a, 7)],
        "predicates": ["overlap", "throughout", "appointed"], "budgets": [1, 3, 5],
        "fixed_ranking": "one seeded complete relevance order per model",
        "date_dependent_ranking": "descending realized start, with fixed ranking as tie break",
        "end_semantics": "half-open lifetime; end follows start by at least one calendar day",
        "reference": "enumerate every integer date tuple; evaluate direct activity at each query date",
        "outcomes": ["support_oracle_agreement", "concrete_witness_validity", "fixed_rank_stability_equivalence",
                     "independent_relaxation_gap", "query_predicate_changes", "dynamic_rank_false_certification"],
        "exclude_cases": "none", "empty_family_policy": "explicit rejection before support queries",
        "timing_policy": "descriptive only; no system speedup claim", "frozen_before_run": True,
        "files": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                  for name in ("cases.jsonl", "constraint_oracle.py", "freeze_protocol.py", "run_benchmark.py")},
    }
    (HERE / "PROTOCOL_FREEZE.json").write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"cases": len(cases), "case_sha256": protocol["files"]["cases.jsonl"]}))


if __name__ == "__main__":
    main()
