"""Independent exhaustive evaluation of the frozen constrained-date benchmark."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
import time
from collections import Counter, defaultdict

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from pass2.theory.uncertain_time import IntervalClaim, compile_from_pairs
from constraint_oracle import EmptyWorldFamily, SupportOracle, from_record


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def exhaustive_worlds(record, constrained=True):
    rows = []
    for values in itertools.product(*(range(lo, hi + 1) for lo, hi in record["bounds"])):
        if not constrained or all((0 if i == -1 else values[i]) - (0 if j == -1 else values[j]) <= bound
                                  for i, j, bound in record["constraints"]):
            rows.append(values)
    return np.asarray(rows, dtype=np.int64).reshape((-1, len(record["bounds"])))


def direct_activity(record, worlds):
    """Evaluate the defining predicate at every integer date, without certificates."""
    active = np.empty((len(worlds), 7, len(record["visible"])), dtype=bool)
    for t in range(7):
        for column, c in enumerate(record["visible"]):
            result = worlds[:, c] <= t
            for d, target in record["pairs"]:
                if target == c:
                    result = result & ~((worlds[:, c] < worlds[:, d]) & (worlds[:, d] <= t))
            active[:, t, column] = result
    return active


def mask_for(record, worlds, activity, a, b, predicate):
    if predicate == "overlap":
        return activity[:, a:b + 1, :].any(axis=1)
    if predicate == "throughout":
        return activity[:, a:b + 1, :].all(axis=1)
    return (worlds[:, record["visible"]] >= a) & (worlds[:, record["visible"]] <= b)


def top(mask, ranking, k):
    return tuple(c for c in ranking if mask[c])[:k]


def world_valid(record, world):
    return all(lo <= value <= hi for value, (lo, hi) in zip(world, record["bounds"])) and all(
        (0 if i == -1 else world[i]) - (0 if j == -1 else world[j]) <= bound
        for i, j, bound in record["constraints"])


def run(output: Path):
    output.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((HERE / "PROTOCOL_FREEZE.json").read_text())
    for filename, expected in protocol["files"].items():
        assert hashlib.sha256((HERE / filename).read_bytes()).hexdigest() == expected, filename
    started = time.perf_counter()
    records = [json.loads(line) for line in (HERE / "cases.jsonl").read_text().splitlines()]
    counts = Counter()
    strata = defaultdict(Counter)
    by_predicate = defaultdict(Counter)
    by_budget = defaultdict(Counter)
    examples = {}
    support_file = (output / "support_decisions.jsonl").open("w")
    context_file = (output / "context_decisions.jsonl").open("w")
    case_file = (output / "case_results.jsonl").open("w")
    for number, record in enumerate(records):
        group = record["stratum"]
        counts["cases"] += 1
        worlds = exhaustive_worlds(record)
        if not len(worlds):
            try:
                SupportOracle(from_record(record))
            except EmptyWorldFamily:
                counts["empty_families_rejected"] += 1
            else:
                raise AssertionError("Empty family accepted.")
            assert not record["expected_nonempty"]
            case_file.write(json.dumps({"case_id": record["case_id"], "worlds": 0, "status": "rejected_empty"}) + "\n")
            continue
        assert record["expected_nonempty"]
        oracle = SupportOracle(from_record(record))
        independent_worlds = exhaustive_worlds(record, False)
        activity = direct_activity(record, worlds)
        independent_activity = direct_activity(record, independent_worlds)
        counts["feasible_models"] += 1
        counts["feasible_worlds"] += len(worlds)
        counts["independent_worlds"] += len(independent_worlds)
        strata[group]["models"] += 1
        strata[group]["feasible_worlds"] += len(worlds)
        if len(worlds) < len(independent_worlds):
            counts["models_with_restrictive_constraints"] += 1
            strata[group]["models_with_restrictive_constraints"] += 1
        for constraint in record["source_constraints"]:
            if constraint["kind"] == "valid_lifetime":
                c, e = constraint["start"], constraint["end"]
                counts["explicit_lifetimes"] += 1
                if record["bounds"][c][1] >= record["bounds"][e][0]:
                    counts["overlapping_lifetime_bounds"] += 1
        intervals = [IntervalClaim(str(i), "", lo, hi) for i, (lo, hi) in enumerate(record["bounds"])]
        old = compile_from_pairs(intervals, ((str(d), str(c)) for d, c in record["pairs"]))
        ranking = record["ranking"]
        rank_position = {c: position for position, c in enumerate(ranking)}
        dynamic_rankings = [tuple(sorted(record["visible"], key=lambda c: (-int(row[c]), rank_position[c])))
                            for row in worlds]
        query_masks = {}
        for a, b in protocol["queries"]:
            for predicate in protocol["predicates"]:
                mask = mask_for(record, worlds, activity, a, b, predicate)
                p, h = mask.any(axis=0), mask.all(axis=0)
                query_masks[a, b, predicate] = (p, h)
                independent_mask = mask_for(record, independent_worlds, independent_activity, a, b, predicate)
                op, oh = independent_mask.any(axis=0), independent_mask.all(axis=0)
                for c in record["visible"]:
                    result = oracle.query(c, a, b, predicate)
                    assert result["possible"] == bool(p[c]), (record["case_id"], c, a, b, predicate, "possible")
                    assert result["guaranteed"] == bool(h[c]), (record["case_id"], c, a, b, predicate, "guaranteed")
                    counts["claim_query_decisions"] += 1
                    by_predicate[predicate]["claim_query_decisions"] += 1
                    counts["boolean_support_checks"] += 2
                    counts["support_mismatches"] += 0
                    for field, wanted in (("support_world", True), ("exclusion_world", False)):
                        witness = result[field]
                        if witness is not None:
                            assert world_valid(record, witness)
                            array = np.asarray([witness])
                            witness_activity = direct_activity(record, array)
                            actual = bool(mask_for(record, array, witness_activity, a, b, predicate)[0, c])
                            assert actual == wanted, (record["case_id"], c, field)
                            counts["concrete_witnesses_checked"] += 1
                    assert not p[c] or op[c]
                    assert not oh[c] or h[c]
                    by_predicate[predicate]["relaxed_possible_only"] += int(op[c] and not p[c])
                    by_predicate[predicate]["constrained_guaranteed_only"] += int(h[c] and not oh[c])
                    if predicate == "overlap":
                        assert old[str(c)].possible(a, b) == bool(op[c])
                        assert old[str(c)].guaranteed(a, b) == bool(oh[c])
                        counts["old_compiler_boolean_checks"] += 2
                    support_file.write(json.dumps({"case_id": record["case_id"], "claim": c,
                        "query": [a, b], "predicate": predicate, **result,
                        "independent_possible": bool(op[c]), "independent_guaranteed": bool(oh[c])}, sort_keys=True) + "\n")
                for k in protocol["budgets"]:
                    possible_top, guaranteed_top = top(p, ranking, k), top(h, ranking, k)
                    fixed_contexts = {top(row, ranking, k) for row in mask}
                    stable = possible_top == guaranteed_top
                    assert stable == (len(fixed_contexts) == 1)
                    independent_stable = top(op, ranking, k) == top(oh, ranking, k)
                    assert not independent_stable or stable
                    dynamic_contexts = {top(row, order, k) for row, order in zip(mask, dynamic_rankings)}
                    dynamic_sets = {tuple(sorted(context)) for context in dynamic_contexts}
                    dynamic_stable = len(dynamic_contexts) == 1
                    dynamic_set_stable = len(dynamic_sets) == 1
                    counts["fixed_rank_context_checks"] += 1
                    counts["fixed_rank_stability_mismatches"] += 0
                    for counter in (by_predicate[predicate], by_budget[str(k)], strata[group]):
                        counter["context_checks"] += 1
                        counter["constrained_stable"] += int(stable)
                        counter["independent_stable"] += int(independent_stable)
                        counter["relaxation_false_alarm"] += int(stable and not independent_stable)
                        counter["fixed_stable_dynamic_order_changes"] += int(stable and not dynamic_stable)
                        counter["fixed_stable_dynamic_set_changes"] += int(stable and not dynamic_set_stable)
                    row = {"case_id": record["case_id"], "query": [a, b], "predicate": predicate, "k": k,
                           "possible_top": possible_top, "guaranteed_top": guaranteed_top,
                           "constrained_stable": stable, "independent_stable": independent_stable,
                           "fixed_context_count": len(fixed_contexts), "dynamic_context_count": len(dynamic_contexts),
                           "dynamic_set_count": len(dynamic_sets)}
                    context_file.write(json.dumps(row, sort_keys=True) + "\n")
                    if stable and not independent_stable and "relaxation_false_alarm" not in examples:
                        examples["relaxation_false_alarm"] = {**row, "model": record}
                    if stable and not dynamic_set_stable and "dynamic_set_failure" not in examples:
                        examples["dynamic_set_failure"] = {**row, "model": record}
            overlap_p, overlap_h = query_masks[a, b, "overlap"]
            for predicate in ("throughout", "appointed"):
                other_p, other_h = query_masks[a, b, predicate]
                by_predicate[predicate]["possible_differs_from_overlap"] += int(np.count_nonzero(other_p != overlap_p))
                by_predicate[predicate]["guaranteed_differs_from_overlap"] += int(np.count_nonzero(other_h != overlap_h))
                for k in protocol["budgets"]:
                    by_predicate[predicate]["possible_context_differs_from_overlap"] += int(top(other_p, ranking, k) != top(overlap_p, ranking, k))
                    by_predicate[predicate]["guaranteed_context_differs_from_overlap"] += int(top(other_h, ranking, k) != top(overlap_h, ranking, k))
        counts["feasibility_calls"] += oracle.feasibility_calls
        case_file.write(json.dumps({"case_id": record["case_id"], "worlds": len(worlds),
                        "independent_worlds": len(independent_worlds), "feasibility_calls": oracle.feasibility_calls,
                        "status": "all_checks_passed"}, sort_keys=True) + "\n")
        if (number + 1) % 20 == 0:
            print(f"Validated {number + 1} models", flush=True)
    support_file.close()
    context_file.close()
    case_file.close()
    results = {"status": "passed", "counts": dict(counts), "by_predicate": dict(by_predicate),
               "by_budget": dict(by_budget), "by_stratum": dict(strata), "examples": examples,
               "runtime_seconds": time.perf_counter() - started, "python": platform.python_version(),
               "numpy": np.__version__, "protocol_sha256": hashlib.sha256((HERE / "PROTOCOL_FREEZE.json").read_bytes()).hexdigest()}
    dump(output / "results.json", results)
    print(json.dumps({"status": results["status"], "counts": dict(counts)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE)
    run(parser.parse_args().output)
