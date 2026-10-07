"""Correctness checks for counterworlds, refinement frontiers, and hardness reduction."""
import itertools
import json
from pathlib import Path
import random
import unittest

from lifecycle import LifecycleClaim, compile_lifecycles, stable_lifecycle_context
from refinement import context_counterworlds, evaluate_world, pivot_date_assignments, refinement_frontier
from test_lifecycle import oracle


class RefinementTests(unittest.TestCase):
    def test_start_counterworld(self):
        index = compile_lifecycles([LifecycleClaim("c", "uncertain start", 0, 2)], [])
        result = context_counterworlds(index, ["c"], 1, k=1)
        self.assertEqual(result.exclusion_reason, "start_after_query")
        self.assertEqual(result.support_world.selected_context, ("c",))
        self.assertEqual(result.exclusion_world.selected_context, ())

    def test_end_counterworld(self):
        index = compile_lifecycles([LifecycleClaim("c", "uncertain end", 0, 0, 1, 3)], [])
        result = context_counterworlds(index, ["c"], 2, k=1)
        self.assertEqual(result.exclusion_reason, "retired_by_query_start")
        self.assertEqual(result.exclusion_witness, "@explicit-end:c")
        self.assertEqual(result.support_world.event_dates["@explicit-end:c"], 3)
        self.assertEqual(result.exclusion_world.event_dates["@explicit-end:c"], 2)

    def test_guaranteed_window_without_certain_point(self):
        index = compile_lifecycles([LifecycleClaim("c", "", 0, 10),
                                   LifecycleClaim("d", "", 5, 5)], [("d", "c")])
        self.assertIsNone(context_counterworlds(index, ["c", "d"], 0, 10, k=1))
        self.assertIsNotNone(context_counterworlds(index, ["c", "d"], 5, k=1))

    def test_new_frontier_can_enter(self):
        index = compile_lifecycles([LifecycleClaim("c", "", 0, 2),
                                   LifecycleClaim("d", "", 0, 2)], [])
        refined = compile_lifecycles([LifecycleClaim("c", "", 2, 2),
                                     LifecycleClaim("d", "", 0, 2)], [])
        self.assertEqual(refinement_frontier(index, ["c", "d"], 1, k=1), ("c",))
        self.assertEqual(refinement_frontier(refined, ["c", "d"], 1, k=1), ("d",))

    def test_unknown_fixed_and_fractional_world(self):
        index = compile_lifecycles([LifecycleClaim("c", "", .2, .3, .4, .8)], [])
        self.assertIsNone(context_counterworlds(index, ["u", "c"], .6, k=1, unknown_ids=["u"]))
        result = context_counterworlds(index, ["c", "u"], .6, k=1, unknown_ids=["u"])
        self.assertEqual(result.support_world.selected_context, ("c",))
        self.assertEqual(result.exclusion_world.selected_context, ("u",))
        self.assertEqual(result.exclusion_world.event_dates["@explicit-end:c"], .6)

    def test_bad_world_and_zero_budget(self):
        index = compile_lifecycles([LifecycleClaim("c", "", 0, 2)], [])
        for dates in ({}, {"c": 3}, {"c": float("nan")}, {"c": True}):
            with self.assertRaises(ValueError):
                evaluate_world(index, dates, ["c"], 1)
        self.assertIsNone(context_counterworlds(index, ["c"], 1, k=0))

    def test_assignment_only_interface_needs_no_pairs(self):
        index = compile_lifecycles([LifecycleClaim("c", "", 0, 0),
                                   LifecycleClaim("w", "", 1, 3)], [("w", "c")])
        assignments = pivot_date_assignments(index.certificates["c"], index.events, 2)
        self.assertEqual(assignments.support_dates, {"c": 0, "w": 3})
        self.assertEqual(assignments.exclusion_dates, {"c": 0, "w": 2})
        self.assertEqual(assignments.exclusion_witness, "w")
        with self.assertRaises(ValueError):
            pivot_date_assignments(index.certificates["c"], index.events, 0)


def counterworld_check():
    rng = random.Random(90212)
    counts = {"counterworld_configurations": 0, "worlds_enumerated": 0,
              "counterworld_queries": 0, "unstable_queries": 0, "constructed_worlds_checked": 0}
    for _ in range(120):
        n = rng.randint(1, 3)
        claims = []
        for j in range(n):
            lower = rng.randint(0, 2)
            upper = lower + rng.randint(0, 2)
            end_lower = upper + rng.randint(1, 2) if rng.random() < .6 else None
            end_upper = end_lower + rng.randint(0, 2) if end_lower is not None else None
            claims.append(LifecycleClaim(str(j), "source", lower, upper, end_lower, end_upper))
        pairs = [(w.cid, c.cid) for w in claims for c in claims
                 if w.cid != c.cid and rng.random() < .5]
        index = compile_lifecycles(claims, pairs)
        ranking = list(index.claims)
        rng.shuffle(ranking)
        unknown = ["unknown"] if rng.random() < .3 else []
        ranking = ranking[:1] + unknown + ranking[1:]
        ids = tuple(index.events)
        worlds = [dict(zip(ids, values)) for values in itertools.product(
            *(range(index.events[e].lower, index.events[e].upper + 1) for e in ids))]
        counts["counterworld_configurations"] += 1
        counts["worlds_enumerated"] += len(worlds)
        for a, b in ((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (0, 3), (2, 5)):
            for k in (1, 2, 3):
                contexts = {tuple(c for c in ranking if c in oracle(index, times, a, b) or c in unknown)[:k]
                            for times in worlds}
                result = context_counterworlds(index, ranking, a, b, k=k, unknown_ids=unknown)
                assert (result is None) == (len(contexts) == 1)
                counts["counterworld_queries"] += 1
                if result is None:
                    continue
                counts["unstable_queries"] += 1
                for world in (result.support_world, result.exclusion_world):
                    expected = oracle(index, world.event_dates, a, b)
                    assert set(world.supported_claims) == expected
                    expected_context = tuple(c for c in ranking if c in expected or c in unknown)[:k]
                    assert world.selected_context == expected_context
                    assert world.selected_context in contexts
                    assert all(index.events[e].lower <= t <= index.events[e].upper
                               for e, t in world.event_dates.items())
                    counts["constructed_worlds_checked"] += 1
                assert result.pivot_id in result.support_world.selected_context
                assert result.pivot_id not in result.exclusion_world.selected_context
    return counts


def refinement_check():
    intervals = [(l, u) for l in range(3) for u in range(l, 3)]
    counts = {"refinement_configurations": 0, "stable_refinements_checked": 0,
              "mandatory_pivot_checks": 0}
    for first, second in itertools.product(intervals, repeat=2):
        claims = [LifecycleClaim("c", "", *first), LifecycleClaim("d", "", *second)]
        refinements = [list((l, u) for l in range(c.lower, c.upper + 1)
                            for u in range(l, c.upper + 1)) for c in claims]
        for bits in itertools.product((False, True), repeat=2):
            pairs = [p for p, keep in zip((("c", "d"), ("d", "c")), bits) if keep]
            index = compile_lifecycles(claims, pairs)
            for a, b in ((0, 0), (1, 1), (2, 2), (0, 1), (1, 2)):
                for k in (1, 2):
                    frontier = refinement_frontier(index, ["c", "d"], a, b, k=k)
                    counts["refinement_configurations"] += 1
                    for r1, r2 in itertools.product(*refinements):
                        updated = compile_lifecycles([LifecycleClaim("c", "", *r1),
                                                      LifecycleClaim("d", "", *r2)], pairs)
                        if not stable_lifecycle_context(updated, ["c", "d"], a, b, k=k).stable:
                            continue
                        counts["stable_refinements_checked"] += 1
                        for cid in frontier:
                            cert = updated.certificates[cid]
                            assert cert.guaranteed(a, b) or not cert.possible(a, b)
                            counts["mandatory_pivot_checks"] += 1
    return counts


def set_cover_reduction_check():
    """Small exhaustive checks of the proved reduction, not a hardness proof."""
    universe = {0, 1, 2}
    possible_sets = [frozenset(i for i in universe if mask & (1 << i)) for mask in range(8)]
    counts = {"set_cover_instances": 0, "reduction_worlds_checked": 0}
    for family in itertools.product(possible_sets, repeat=3):
        for budget in (1, 2):
            cover_exists = any(set().union(*(family[j] for j in picked)) == universe
                               for size in range(budget + 1)
                               for picked in itertools.combinations(range(3), size))
            variables = [LifecycleClaim(f"v{j}", "optional replacement", 1, 3) for j in range(3)]
            targets = [LifecycleClaim(f"e{i}_{copy}", "element copy", 0, 0)
                       for i in universe for copy in range(budget + 1)]
            claims = variables + targets + [LifecycleClaim("candidate", "", 0, 0)]
            pairs = [(f"v{j}", f"e{i}_{copy}") for j, subset in enumerate(family)
                      for i in subset for copy in range(budget + 1)]
            index = compile_lifecycles(claims, pairs)
            ranking = [c.cid for c in claims]
            attainable = False
            for values in itertools.product((1, 2, 3), repeat=3):
                dates = {c.cid: c.lower for c in claims}
                dates.update(zip((v.cid for v in variables), values))
                context = tuple(cid for cid in ranking if cid in oracle(index, dates, 2, 2))[:budget + 1]
                attainable |= "candidate" in context
                counts["reduction_worlds_checked"] += 1
            assert attainable == cover_exists, (family, budget)
            counts["set_cover_instances"] += 1
    return counts


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RefinementTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    counts = {**counterworld_check(), **refinement_check(), **set_cover_reduction_check()}
    output = {"passed": True, "api_tests": result.testsRun, **counts,
              "scope": "Constructed correctness checks, not benchmark examples or independent hardness proofs."}
    Path(__file__).with_name("refinement_tests.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
