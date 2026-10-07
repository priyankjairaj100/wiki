"""Independent finite-model audit of uncertain-start temporal support.

The oracle constructs every integer timestamp realization. It never uses a
compiled bound when evaluating activity. Exhaustive integer cases include all
boundary orderings for integer intervals; continuous semantics additionally
require the analytic proof documented in REVIEW.md.
"""
from itertools import product
from math import inf
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "theory"))
from uncertain_time import IntervalClaim, compile_intervals


def active(realization, witnesses, t):
    return realization[0] <= t and not any(
        realization[0] < realization[d] <= t for d in witnesses)


def compiled(intervals, witnesses):
    lower, upper = intervals[0]
    possible_end = min((intervals[d][1] for d in witnesses
                        if intervals[d][0] > upper), default=inf)
    risk_start = min((intervals[d][0] for d in witnesses
                      if intervals[d][1] > lower), default=inf)
    return lower, upper, possible_end, risk_start


def main():
    intervals = [(a, b) for a in range(-1, 4) for b in range(a, 4)]
    points = range(-2, 5)
    query_ranges = [(a, b) for a in points for b in points if a <= b]
    counts = {"interval_configurations": 0, "worlds": 0,
              "point_comparisons": 0, "range_comparisons": 0,
              "implementation_comparisons": 0}
    # All choices of incoming G are represented by zero to two witnesses.
    for n_witnesses in range(3):
        witnesses = tuple(range(1, n_witnesses + 1))
        for bounds in product(intervals, repeat=n_witnesses + 1):
            counts["interval_configurations"] += 1
            worlds = list(product(*(range(a, b + 1) for a, b in bounds)))
            counts["worlds"] += len(worlds)
            lower, upper, possible_end, risk_start = compiled(bounds, witnesses)
            claims = [IntervalClaim(f"c{i}", "", a, b)
                      for i, (a, b) in enumerate(bounds)]
            actual = compile_intervals(claims, lambda d, c: c.cid == "c0")["c0"]
            # Deliberately permit G(c,c); the implementation skips self-pairs.
            assert actual.possible_end == possible_end
            assert actual.potential_witness_lower == risk_start
            all_active = {t: [active(w, witnesses, t) for w in worlds]
                          for t in points}
            for t in points:
                possible = lower <= t < possible_end
                certain = upper <= t and (t <= lower or t < risk_start)
                assert possible == any(all_active[t]), ("possible", bounds, t)
                assert certain == all(all_active[t]), ("certain", bounds, t)
                assert actual.possible(t) == any(all_active[t])
                assert actual.guaranteed(t) == all(all_active[t])
                counts["implementation_comparisons"] += 2
                counts["point_comparisons"] += 2
            for a, b in query_ranges:
                supports = [any(active(w, witnesses, t)
                                for t in range(a, b + 1)) for w in worlds]
                possible = lower <= b and a < possible_end
                guaranteed = upper <= b and (a <= lower or a < risk_start)
                assert possible == any(supports), ("possible range", bounds, (a, b))
                assert guaranteed == all(supports), ("guaranteed range", bounds, (a, b))
                assert actual.possible(a, b) == any(supports)
                assert actual.guaranteed(a, b) == all(supports)
                counts["implementation_comparisons"] += 2
                counts["range_comparisons"] += 2

    # Explicit quantifier inversion counterexample, including interior starts.
    bounds = ((0, 10), (5, 5))
    worlds = list(product(range(11), (5,)))
    assert all(any(active(w, (1,), t) for t in range(11)) for w in worlds)
    assert not any(all(active(w, (1,), t) for w in worlds) for t in range(11))
    counts["quantifier_counterexample"] = {
        "claim": [0, 10], "witness": [5, 5], "query": [0, 10],
        "all_worlds_have_some_support": True,
        "some_point_is_active_in_all_worlds": False,
    }
    c, d = IntervalClaim("c", "", 0.0, 0.0), IntervalClaim("d", "", 0.0, 1.0)
    cert = compile_intervals([c, d], lambda d, c: True)["c"]
    assert cert.guaranteed(0.0)
    assert cert.guaranteed(0.0, 0.0)
    assert not cert.guaranteed(0.25)
    assert cert.possible(0.25)
    assert not cert.guaranteed(-0.25)
    # Nonintegral boundary and zero-width queries.
    c, d = IntervalClaim("c", "", 0.25, 0.75), IntervalClaim("d", "", 1.25, 1.75)
    cert = compile_intervals([c, d], lambda d, c: True)["c"]
    assert cert.possible(1.749) and not cert.possible(1.75)
    assert cert.guaranteed(1.249) and not cert.guaranteed(1.25)
    assert cert.guaranteed(0.75, 0.75) and not cert.guaranteed(0.749, 0.749)
    counts["continuous_boundary_assertions"] = 11
    counts["status"] = "passed"
    Path(__file__).with_name("exhaustive_results.json").write_text(
        json.dumps(counts, indent=2) + "\n")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
