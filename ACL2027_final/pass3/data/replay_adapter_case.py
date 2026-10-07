"""Replay an illustrative query using actual source-only parser outputs.

The query period and ranking explain the theorem. They are not a QA benchmark.
Claims, dates, and replacement edges come from the automatic succession parser.
"""
from dataclasses import asdict
from datetime import date
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pass3.theory.lifecycle import LifecycleClaim, compile_lifecycles, stable_lifecycle_context
from pass3.theory.refinement import context_counterworlds, refinement_frontier

HERE = Path(__file__).resolve().parent
INPUT = ROOT / "pass3/extraction/succession_rule_results"


def read(name):
    return [json.loads(line) for line in (INPUT / name).read_text().splitlines()]


def main():
    claims = [row for row in read("claims.jsonl") if row["article_path"] == "/wiki/Warburg_Institute"]
    by_name = {row["holder"]: row["claim_id"] for row in claims}
    names = ["Henri Frankfort", "Gertrud Bing", "Ernst Gombrich"]
    assert set(by_name) == set(names)
    ranking = [by_name[name] for name in names]
    pairs = [(row["witness_id"], row["target_id"]) for row in read("pairs.jsonl")
             if row["witness_id"] in ranking and row["target_id"] in ranking]
    index = compile_lifecycles([LifecycleClaim.from_record(row) for row in claims], pairs)
    a, b = date(1954, 1, 1).toordinal(), date(1955, 6, 30).toordinal()
    name_by_id = {value: key for key, value in by_name.items()}
    views = []
    for budget in [1, 2]:
        stability = stable_lifecycle_context(index, ranking, a, b, k=budget)
        counterworlds = context_counterworlds(index, ranking, a, b, k=budget)
        value = None if counterworlds is None else asdict(counterworlds)
        if value is not None:
            for key in ["support_world", "exclusion_world"]:
                world = value[key]
                world["event_dates_iso"] = {name_by_id[cid]: date.fromordinal(int(t)).isoformat()
                                           for cid, t in world["event_dates"].items()}
                world["selected_context_names"] = [name_by_id[cid] for cid in world["selected_context"]]
        views.append({"budget": budget, "stability": asdict(stability),
                      "frontier_names": [name_by_id[cid] for cid in refinement_frontier(index, ranking, a, b, k=budget)],
                      "counterworlds": value})
    assert views[0]["counterworlds"] is None
    assert views[1]["frontier_names"] == ["Gertrud Bing"]
    world_a = views[1]["counterworlds"]["support_world"]["selected_context_names"]
    world_b = views[1]["counterworlds"]["exclusion_world"]["selected_context_names"]
    assert world_a == ["Henri Frankfort", "Gertrud Bing"]
    assert world_b == ["Henri Frankfort"]
    manual = json.loads((HERE / "natural_context_case.json").read_text())
    assert manual["possible"] == ["c", "d"] and manual["guaranteed"] == ["c"]
    for record, expected in zip(claims, manual["claims"]):
        assert record["holder"] == expected["name"]
        assert record["start"]["lower_iso"] == expected["start_lower"]
        assert record["start"]["upper_iso"] == expected["start_upper"]
    output = {
        "scope": "Source-only deterministic extraction followed by exact compilation. The query window and ranking are illustrative calibration choices. No QA score.",
        "input_hashes": {name: hashlib.sha256((INPUT / name).read_bytes()).hexdigest()
                         for name in ["claims.jsonl", "pairs.jsonl", "assertions.jsonl"]},
        "semantic_audit": "pass3/data/succession_rule_semantic_audit.json",
        "claims": claims, "pairs": pairs, "ranking_names": names,
        "query_window": ["1954-01-01", "1955-06-30"],
        "possible_names": [name_by_id[cid] for cid in ranking if index.certificates[cid].possible(a, b)],
        "guaranteed_names": [name_by_id[cid] for cid in ranking if index.certificates[cid].guaranteed(a, b)],
        "matches_earlier_manually_structured_case": True,
        "views": views,
    }
    (HERE / "natural_context_case_from_adapter.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"possible": output["possible_names"], "guaranteed": output["guaranteed_names"],
                      "stable_budget_1": views[0]["counterworlds"] is None,
                      "budget_2_contexts": [world_a, world_b], "manual_case_match": True}))


if __name__ == "__main__":
    main()
