"""Build a source-grounded calibration case, with illustrative query and ranking."""
from datetime import date
from dataclasses import asdict
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pass2.theory.uncertain_time import IntervalClaim, compile_from_pairs
from pass3.theory.lifecycle import LifecycleClaim, compile_lifecycles
from pass3.theory.refinement import context_counterworlds, refinement_frontier

HERE = Path(__file__).resolve().parent


def ordinal(value):
    return date.fromisoformat(value).toordinal()


def main():
    rows = [json.loads(line) for line in (HERE / "dev_succession_candidates.jsonl").read_text().splitlines()]
    source = next(row for row in rows if row["passage_id"] == "72daf9756d91f4ce98b12937")
    text = source["text"]
    spans = []
    for expression in [
        "Henri Frankfort succeeded Saxl as director in 1949",
        "in 1955 was succeeded by Gertrud Bing",
        "Bing was succeeded by Ernst Gombrich in 1959",
    ]:
        start = text.index(expression)
        spans.append({"start": start, "end": start+len(expression), "text": expression})
    records = [
        {"id": "c", "name": "Henri Frankfort", "start_lower": "1949-01-01", "start_upper": "1949-12-31"},
        {"id": "d", "name": "Gertrud Bing", "start_lower": "1955-01-01", "start_upper": "1955-12-31"},
        {"id": "e", "name": "Ernst Gombrich", "start_lower": "1959-01-01", "start_upper": "1959-12-31"},
    ]
    claims = [IntervalClaim(row["id"], row["name"], ordinal(row["start_lower"]), ordinal(row["start_upper"])) for row in records]
    pairs = [("d", "c"), ("e", "d")]
    cert = compile_from_pairs(claims, pairs)
    a, b = ordinal("1954-01-01"), ordinal("1955-06-30")
    possible = [row.cid for row in claims if cert[row.cid].possible(a, b)]
    guaranteed = [row.cid for row in claims if cert[row.cid].guaranteed(a, b)]
    assignments = [
        {"c": "1949-06-01", "d": "1955-01-01", "e": "1959-06-01"},
        {"c": "1949-06-01", "d": "1955-12-31", "e": "1959-06-01"},
    ]
    worlds = []
    for assignment in assignments:
        x = {cid: ordinal(value) for cid, value in assignment.items()}
        support = []
        for claim in claims:
            end = min([x[w] for w, target in pairs if target == claim.cid and x[w] > x[claim.cid]] + [float("inf")])
            if x[claim.cid] <= b and max(a, x[claim.cid]) < end:
                support.append(claim.cid)
        worlds.append({"dates": assignment, "support": support})
    views = []
    for ranking, budget in [(["c", "d", "e"], 1), (["c", "d", "e"], 2), (["d", "c", "e"], 1)]:
        top_p = [cid for cid in ranking if cid in possible][:budget]
        top_h = [cid for cid in ranking if cid in guaranteed][:budget]
        contexts = [[cid for cid in ranking if cid in world["support"]][:budget] for world in worlds]
        views.append({"ranking": ranking, "budget": budget, "top_possible": top_p,
                      "top_guaranteed": top_h, "stable": top_p == top_h,
                      "two_replay_contexts": contexts})
    assert possible == ["c", "d"] and guaranteed == ["c"]
    assert [view["stable"] for view in views] == [True, False, False]
    output = {
        "scope": "Natural source, manually interpreted calibration case. Query window, relevance order, and two admissible timelines are illustrative. No benchmark result or measured ranking is claimed.",
        "source": source, "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "supporting_spans": spans, "role_key": ["Warburg Institute", "director"],
        "claims": records, "direct_pairs": pairs,
        "query_window": ["1954-01-01", "1955-06-30"],
        "possible": possible, "guaranteed": guaranteed,
        "assignments": worlds, "ranking_views": views,
        "takeaway": "The same possible evidence pool can produce a stable one-item context and an unstable larger context.",
    }
    (HERE / "natural_context_case.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    lifecycle = compile_lifecycles([
        LifecycleClaim(row["id"], row["name"], ordinal(row["start_lower"]), ordinal(row["start_upper"]))
        for row in records
    ], pairs)
    constructed = []
    for ranking, budget in [(["c", "d", "e"], 1), (["c", "d", "e"], 2), (["d", "c", "e"], 1)]:
        result = context_counterworlds(lifecycle, ranking, a, b, k=budget)
        value = None if result is None else asdict(result)
        if value is not None:
            for key in ["support_world", "exclusion_world"]:
                world = value[key]
                world["event_dates_iso"] = {cid: date.fromordinal(int(day)).isoformat()
                                           for cid, day in world["event_dates"].items()}
        constructed.append({"ranking": ranking, "budget": budget,
            "frontier": list(refinement_frontier(lifecycle, ranking, a, b, k=budget)),
            "result": value})
    assert constructed[0]["result"] is None
    assert constructed[1]["result"]["pivot_id"] == "d"
    assert constructed[2]["result"]["pivot_id"] == "d"
    (HERE / "natural_context_counterworlds.json").write_text(json.dumps({
        "scope": output["scope"], "source_case": "natural_context_case.json",
        "constructor": "pass3.theory.refinement.context_counterworlds",
        "query_window": output["query_window"], "results": constructed,
    }, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"possible": possible, "guaranteed": guaranteed, "views": views}))


if __name__ == "__main__":
    main()
