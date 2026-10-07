"""Correctness tests for the candidate specification, not empirical results."""

import random
import unittest
from bitemporal import Claim, compile_frontiers, direct_scan, eligible_ids


class FrontierTests(unittest.TestCase):
    def test_two_incomparable_witnesses(self):
        claims = [Claim("c", 0, 0), Claim("d", 20, 1), Claim("e", 10, 2)]
        index = compile_frontiers(claims, lambda newer, older: older.cid == "c")
        self.assertEqual([(w.valid, w.available) for w in index["c"].witnesses], [(10, 2), (20, 1)])
        self.assertTrue(index["c"].eligible(15, 1.5))
        self.assertFalse(index["c"].eligible(15, 2))

    def test_arrival_clipping_is_needed_for_minimality(self):
        claims = [Claim("c", 0, 10), Claim("d", 1, 8), Claim("e", 2, 5)]
        index = compile_frontiers(claims, lambda newer, older: older.cid == "c")
        self.assertEqual([(w.valid, w.available) for w in index["c"].witnesses], [(1, 10)])

    def test_equal_valid_dates_do_not_replace(self):
        claims = [Claim("a", 1, 0), Claim("b", 1, 2)]
        index = compile_frontiers(claims, lambda newer, older: True)
        self.assertEqual(eligible_ids(index, 1, 2), {"a", "b"})

    def test_duplicate_points_keep_one_deterministic_witness(self):
        claims = [Claim("c", 0, 0), Claim("z", 1, 1), Claim("a", 1, 1)]
        index = compile_frontiers(claims, lambda newer, older: True)
        self.assertEqual([w.cid for w in index["c"].witnesses], ["a"])

    def test_future_arrivals_preserve_past_knowledge(self):
        claims = [Claim("c", 0, 0), Claim("d", 20, 1), Claim("e", 10, 2)]
        gate = lambda newer, older: older.cid == "c"
        full = compile_frontiers(claims, gate)
        prefix = compile_frontiers([c for c in claims if c.arrival <= 1.5], gate)
        for valid in range(25):
            self.assertEqual(eligible_ids(full, valid, 1.5), eligible_ids(prefix, valid, 1.5))

    def test_every_frontier_point_has_a_distinguishing_query(self):
        claims = [Claim("c", 0, 0)] + [Claim(str(i), i, 6-i) for i in range(1, 6)]
        index = compile_frontiers(claims, lambda newer, older: older.cid == "c")
        points = index["c"].witnesses
        self.assertEqual(len(points), 5)
        for witness in points:
            self.assertFalse(index["c"].eligible(witness.valid, witness.available))
            for other in points:
                if other != witness:
                    self.assertFalse(other.valid <= witness.valid and other.available <= witness.available)

    def test_random_gates_match_exhaustive_specification(self):
        for seed in range(30):
            rng = random.Random(seed)
            claims = [Claim(str(i), rng.randrange(5), rng.randrange(5)) for i in range(12)]
            edges = {(a.cid,b.cid) for a in claims for b in claims if rng.random() < 0.2}
            gate = lambda newer, older: (newer.cid,older.cid) in edges
            index = compile_frontiers(claims, gate)
            for valid in range(-1, 6):
                for known in range(-1, 6):
                    self.assertEqual(eligible_ids(index, valid, known), direct_scan(claims, gate, valid, known))

    def test_one_pair_changes_only_its_older_endpoint(self):
        claims = [Claim(str(i), i, 8-i) for i in range(8)]
        pairs = {(str(i+1),str(i)) for i in range(7)}
        gate = lambda newer, older: (newer.cid,older.cid) in pairs
        base = compile_frontiers(claims, gate)
        pairs.add(("7", "0"))
        changed = compile_frontiers(claims, gate)
        for valid in range(10):
            for known in range(10):
                delta = eligible_ids(base,valid,known) ^ eligible_ids(changed,valid,known)
                self.assertTrue(delta <= {"0"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
