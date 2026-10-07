"""Freeze or run the full two-distinct-witness stress grid."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from pass2.theory.uncertain_time import IntervalClaim, compile_from_pairs


def inputs():
    cases = []
    # c=[0,u], d can follow c, and e must follow c. The grid fixes this structure.
    for u in (1, 2, 3):
        for dl in range(u + 1):
            for du in range(max(1, dl), 7):
                for el in range(u + 1, 7):
                    for eu in range(el, 7):
                        cases.append({"case_id": f"grid_{len(cases):04}",
                                      "bounds": [[0, u], [dl, du], [el, eu]],
                                      "pairs": [[1, 0], [2, 0]], "visible": [0]})
    return cases


def freeze():
    destination = HERE / "TWO_WITNESS_FREEZE.json"
    if destination.exists():
        raise SystemExit("The grid is already frozen.")
    rows = inputs()
    data = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    (HERE / "two_witness_cases.jsonl").write_text(data)
    protocol = {"design": "complete parameter grid; no outcome-based exclusions",
                "target": "[0,u], u in {1,2,3}",
                "near_witness": "[dl,du], dl in [0,u], du in [max(1,dl),6]",
                "late_witness": "[el,eu], el in [u+1,6], eu in [el,6]",
                "dates": "integer calendar units", "cases": len(rows),
                "queries": [[a, b] for a in range(7) for b in range(a, 7)],
                "modes": {"full": [[1, 0], [2, 0]], "keep_near": [[1, 0]], "keep_late": [[2, 0]]},
                "reference": "enumerate every date tuple and test active somewhere at each query date",
                "selection_scope": "direct witness subsets; no claim about all possible encodings",
                "files": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                          for name in ("two_witness_cases.jsonl", "two_witness_grid.py")}}
    destination.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"frozen_cases": len(rows)}))


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((HERE / "TWO_WITNESS_FREEZE.json").read_text())
    for name, expected in protocol["files"].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected
    counts = Counter()
    modes = {mode: Counter() for mode in protocol["modes"]}
    with (output / "two_witness_decisions.jsonl").open("w") as destination:
        for line in (HERE / "two_witness_cases.jsonl").read_text().splitlines():
            record = json.loads(line)
            worlds = np.asarray(list(itertools.product(*(range(lo, hi + 1) for lo, hi in record["bounds"]))))
            counts["cases"] += 1
            counts["worlds"] += len(worlds)
            raw_activity = (worlds[:, 0, None] <= np.arange(7)[None, :])
            for d, c in record["pairs"]:
                raw_activity &= ~((worlds[:, c, None] < worlds[:, d, None]) &
                                  (worlds[:, d, None] <= np.arange(7)[None, :]))
            claims = [IntervalClaim(str(i), "", lo, hi) for i, (lo, hi) in enumerate(record["bounds"])]
            compilers = {mode: compile_from_pairs(claims, ((str(d), str(c)) for d, c in pairs))["0"]
                         for mode, pairs in protocol["modes"].items()}
            full = compilers["full"]
            assert full.possible_end_witness == "2" and full.potential_witness == "1"
            errors = {mode: False for mode in modes}
            for a, b in protocol["queries"]:
                values = raw_activity[:, a:b + 1].any(axis=1)
                p, h = bool(values.any()), bool(values.all())
                counts["claim_query_checks"] += 1
                for mode, compiler in compilers.items():
                    cp, ch = compiler.possible(a, b), compiler.guaranteed(a, b)
                    different = cp != p or ch != h
                    if mode == "full":
                        assert not different
                    errors[mode] |= different
                    modes[mode]["query_checks"] += 1
                    modes[mode]["possible_mismatches"] += int(cp != p)
                    modes[mode]["guaranteed_mismatches"] += int(ch != h)
                    modes[mode]["incorrect_possible_inclusion"] += int(cp and not p)
                    modes[mode]["incorrect_guaranteed_inclusion"] += int(ch and not h)
                    destination.write(json.dumps({"case_id": record["case_id"], "query": [a, b], "mode": mode,
                        "possible": cp, "guaranteed": ch, "reference_possible": p,
                        "reference_guaranteed": h, "different": different}, sort_keys=True) + "\n")
            for mode in modes:
                modes[mode]["cases_with_error"] += int(errors[mode])
            counts["cases_where_both_single_witness_subsets_fail"] += int(errors["keep_near"] and errors["keep_late"])
    result = {"status": "passed", "counts": dict(counts), "modes": {k: dict(v) for k, v in modes.items()},
              "protocol_sha256": hashlib.sha256((HERE / "TWO_WITNESS_FREEZE.json").read_bytes()).hexdigest()}
    (output / "two_witness_results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    freeze() if args.freeze else run(args.output)
