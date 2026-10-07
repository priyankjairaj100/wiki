"""Check exact context invariance against enumerated event-date assignments."""
import itertools
import json
import unittest
from pathlib import Path

from uncertain_time import IntervalClaim, compile_from_pairs, stable_context


class ContextTests(unittest.TestCase):
    comparisons = 0

    def test_uncertainty_below_budget(self):
        claims = [IntervalClaim("a", "fixed", 0, 0),
                  IntervalClaim("b", "uncertain", 0, 4)]
        certificates = compile_from_pairs(claims, [])
        one = stable_context(certificates, ("a", "b"), 2, k=1)
        self.assertTrue(one.stable)
        self.assertEqual(one.common_context, ("a",))
        two = stable_context(certificates, ("a", "b"), 2, k=2)
        self.assertFalse(two.stable)
        self.assertIsNone(two.common_context)
        self.assertEqual(two.possible_top, ("a", "b"))
        self.assertEqual(two.guaranteed_top, ("a",))

    def test_range_quantifiers(self):
        claims = [IntervalClaim("c", "uncertain", 0, 10),
                  IntervalClaim("d", "replacement", 5, 5)]
        certificates = compile_from_pairs(claims, [("d", "c")])
        result = stable_context(certificates, ("c", "d"), 0, 10, k=1)
        self.assertTrue(result.stable)
        self.assertEqual(result.common_context, ("c",))

    def test_zero_budget_and_empty_index(self):
        claims = [IntervalClaim("a", "uncertain", 0, 4)]
        result = stable_context(compile_from_pairs(claims, []), ("a",), 2, k=0)
        self.assertTrue(result.stable)
        self.assertEqual(result.common_context, ())
        result = stable_context({}, (), 0, 1, k=3)
        self.assertTrue(result.stable)
        self.assertEqual(result.common_context, ())

    def test_validation(self):
        certificates = compile_from_pairs([IntervalClaim("a", "", 0, 1)], [])
        for ranking in ((), ("a", "a"), ("a", "missing"), (None,)):
            with self.assertRaises(ValueError):
                stable_context(certificates, ranking, 0)
        for budget in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                stable_context(certificates, ("a",), 0, k=budget)
        with self.assertRaises(ValueError):
            stable_context(certificates, ("a",), 1, 0)
        with self.assertRaises(ValueError):
            stable_context({"b": certificates["a"]}, ("b",), 0)

    def test_against_worlds(self):
        bounds = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
        windows = [(a, b) for a in range(3) for b in range(a, 3)]
        for left, right in itertools.product(bounds, repeat=2):
            claims = [IntervalClaim("a", "", *left), IntervalClaim("b", "", *right)]
            worlds = list(itertools.product(range(left[0], left[1]+1),
                                            range(right[0], right[1]+1)))
            for edge_bits in itertools.product((False, True), repeat=2):
                pairs = [pair for pair, keep in zip((("a", "b"), ("b", "a")), edge_bits) if keep]
                certificates = compile_from_pairs(claims, pairs)
                for window in windows:
                    for ranking in (("a", "b"), ("b", "a")):
                        for budget in range(4):
                            contexts = set()
                            for world in worlds:
                                dates = dict(zip(("a", "b"), world))
                                mask = set()
                                for cid in dates:
                                    for time in range(window[0], window[1]+1):
                                        active = (dates[cid] <= time and not any(
                                            target == cid and dates[cid] < dates[witness] <= time
                                            for witness, target in pairs))
                                        if active:
                                            mask.add(cid)
                                            break
                                contexts.add(tuple(cid for cid in ranking if cid in mask)[:budget])
                            result = stable_context(certificates, ranking, *window, k=budget)
                            self.assertEqual(result.stable, len(contexts) == 1)
                            if result.stable:
                                self.assertEqual(result.common_context, next(iter(contexts)))
                            type(self).comparisons += 1


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ContextTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    Path(__file__).with_name("context_stability_tests.json").write_text(json.dumps({
        "passed": result.wasSuccessful(), "tests": result.testsRun,
        "world_context_comparisons": ContextTests.comparisons,
        "scope": "exact context invariance over finite event-date assignments",
    }, indent=2) + "\n")
    raise SystemExit(not result.wasSuccessful())
