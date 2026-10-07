"""API and certificate checks; independent exhaustive tests live separately."""
import itertools
import json
import unittest
from pathlib import Path

from uncertain_time import IntervalClaim, compile_from_pairs, compile_intervals


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.claims = [IntervalClaim("c", "old", 0, 2),
                       IntervalClaim("d", "possible replacement", 1, 4),
                       IntervalClaim("e", "forced replacement", 3, 5)]
        self.pairs = [("d", "c"), ("e", "c")]

    def test_two_witnesses_necessary(self):
        cert = compile_from_pairs(self.claims, self.pairs)["c"]
        self.assertEqual((cert.possible_end, cert.potential_witness_lower), (5, 1))
        self.assertFalse(cert.possible(5))
        self.assertFalse(cert.guaranteed(2))
        without_forced = compile_from_pairs(self.claims, [("d", "c")])["c"]
        without_potential = compile_from_pairs(self.claims, [("e", "c")])["c"]
        self.assertTrue(without_forced.possible(5))
        self.assertTrue(without_potential.guaranteed(2))

    def test_pair_and_claim_order(self):
        reference = compile_from_pairs(self.claims, self.pairs)
        for claims in itertools.permutations(self.claims):
            for pairs in itertools.permutations(self.pairs):
                self.assertEqual(compile_from_pairs(claims, pairs), reference)
                self.assertEqual(compile_from_pairs(claims, pairs + pairs), reference)

    def test_scan_and_pairs(self):
        pair_set = set(self.pairs)
        scan = compile_intervals(self.claims, lambda d, c: (d.cid, c.cid) in pair_set)
        self.assertEqual(scan, compile_from_pairs(self.claims, self.pairs))

    def test_ties(self):
        claims = [IntervalClaim("target", "", 0, 1),
                  IntervalClaim("z", "", 2, 4),
                  IntervalClaim("a", "", 2, 4)]
        pairs = [("z", "target"), ("a", "target")]
        for order in itertools.permutations(pairs):
            cert = compile_from_pairs(claims, order)["target"]
            self.assertEqual(cert.possible_end_witness, "a")
            self.assertEqual(cert.potential_witness, "a")

    def test_self_pairs_are_ignored(self):
        reference = compile_from_pairs(self.claims, self.pairs)
        pairs = self.pairs + [(claim.cid, claim.cid) for claim in self.claims]
        self.assertEqual(compile_from_pairs(self.claims, pairs), reference)
        single = compile_intervals([self.claims[0]], lambda d, c: True)["c"]
        self.assertTrue(single.guaranteed(2))

    def test_unknown_and_duplicate_ids(self):
        with self.assertRaises(ValueError):
            compile_from_pairs(self.claims, [("missing", "c")])
        with self.assertRaises(ValueError):
            compile_from_pairs(self.claims, [("c", "missing")])
        with self.assertRaises(ValueError):
            compile_from_pairs(self.claims + [self.claims[0]], [])
        with self.assertRaises(ValueError):
            compile_intervals(self.claims + [self.claims[0]], lambda d, c: False)
        for malformed in (("c",), ("c", "d", "e"), "cd", (None, "c")):
            with self.assertRaises(ValueError):
                compile_from_pairs(self.claims, [malformed])

    def test_guaranteed_window_without_certain_point(self):
        claims = [IntervalClaim("c", "", 0, 10), IntervalClaim("d", "", 5, 5)]
        cert = compile_from_pairs(claims, [("d", "c")])["c"]
        self.assertTrue(cert.guaranteed(0, 10))
        for point in (-1, 0, .5, 4.999, 5, 5.001, 10, 11):
            self.assertFalse(cert.guaranteed(point))

    def test_singleton_certain_point(self):
        claims = [IntervalClaim("c", "", 0, 0), IntervalClaim("d", "", 0, 1)]
        cert = compile_from_pairs(claims, [("d", "c")])["c"]
        self.assertTrue(cert.guaranteed(0))
        self.assertFalse(cert.guaranteed(.001))
        self.assertFalse(cert.guaranteed(-.001))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CompilerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    Path(__file__).with_name("compiler_api_tests.json").write_text(json.dumps({
        "passed": result.wasSuccessful(), "tests": result.testsRun,
        "scope": "compiler API, exact bounds, deterministic ties, and witness minimality",
    }, indent=2) + "\n")
    raise SystemExit(not result.wasSuccessful())
