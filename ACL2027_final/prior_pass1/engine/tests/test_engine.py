"""Constructed correctness tests. These cases are not benchmark observations."""

import json
import math
import random
import unittest
from dataclasses import replace

from engine import EvidenceClaim as C, SupersessionGate, compile_certificates


def full_pair_oracle(claims, gate):
    """Independent exhaustive enumeration, with no blocking or early termination."""
    boundaries = {}
    accepted = {}
    for older in claims:
        witnesses = []
        if older.timestamp is not None:
            for newer in claims:
                if newer.timestamp is not None and newer.timestamp > older.timestamp:
                    if gate(newer, older):
                        witnesses.append((newer.timestamp, newer.cid))
        accepted[older.cid] = witnesses
        boundaries[older.cid] = min(witnesses) if witnesses else (math.inf, None)
    return boundaries, accepted


def event_cutoffs(claims):
    times = sorted({c.timestamp for c in claims if c.timestamp is not None})
    if not times:
        return [0.0]
    return [times[0] - 1, times[-1] + 1] + times + [
        (left + right) / 2 for left, right in zip(times, times[1:])]


def oracle_ids(claims, accepted, cutoff):
    # This definition checks every accepted direct pair independently of endpoints.
    return {c.cid for c in claims if c.timestamp is not None and c.timestamp <= cutoff
            and not any(time <= cutoff for time, _ in accepted[c.cid])}


class CertificateTests(unittest.TestCase):
    def assert_oracle(self, claims, gate, **options):
        index = compile_certificates(claims, gate, **options)
        boundaries, accepted = full_pair_oracle(claims, gate)
        for cid, (end, witness) in boundaries.items():
            self.assertEqual(index.certificates[cid].end, end)
            self.assertEqual(index.certificates[cid].witness_cid, witness)
        for cutoff in event_cutoffs(claims):
            self.assertEqual(index.eligible_ids(cutoff), oracle_ids(claims, accepted, cutoff))
        self.assertEqual(index.current_ids(), {cid for cid, (end, _) in boundaries.items()
                                               if end == math.inf})
        return index

    def test_nontransitive_triad_has_no_component_contamination(self):
        claims = [C("a", "alpha", 0), C("b", "beta", 1), C("c", "gamma", 2)]
        pairs = {("b", "a"), ("c", "b")}
        gate = lambda newer, older: (newer.cid, older.cid) in pairs
        index = self.assert_oracle(claims, gate)
        self.assertEqual(index.certificates["a"].witness_cid, "b")
        self.assertEqual(index.certificates["b"].witness_cid, "c")
        # A bridge claim arrives last. Connected components would end a at b's time.
        bridge = [C("a", "alpha", 0), C("b", "beta", 1), C("c", "gamma", 2)]
        gate = lambda newer, older: newer.cid == "c" and older.cid in {"a", "b"}
        index = self.assert_oracle(bridge, gate)
        self.assertEqual(index.eligible_ids(1), {"a", "b"})
        self.assertEqual(index.certificates["a"].end, 2)

    def test_a_b_a_return_does_not_resurrect_old_claim(self):
        claims = [C("a0", "A", 0), C("b1", "B", 1), C("a2", "A", 2)]
        index = self.assert_oracle(claims, lambda n, o: n.text != o.text)
        self.assertEqual(index.eligible_ids(2), {"a2"})
        self.assertEqual(index.certificates["a0"].end, 1)

    def test_same_value_repeat_retains_both_spans(self):
        claims = [C("a0", "A", 0), C("a1", "A", 1), C("b2", "B", 2)]
        index = self.assert_oracle(claims, lambda n, o: n.text != o.text)
        self.assertEqual(index.eligible_ids(1), {"a0", "a1"})
        self.assertEqual(index.eligible_ids(2), {"b2"})

    def test_simultaneous_conflicts_and_deterministic_witness_tie(self):
        claims = [C("old", "A", 0), C("z", "B", 1), C("a", "C", 1)]
        index = self.assert_oracle(claims, lambda n, o: n.text != o.text)
        self.assertEqual(index.certificates["old"].witness_cid, "a")
        self.assertEqual(index.eligible_ids(1), {"a", "z"})

    def test_missing_time_excluded_asof_retained_current(self):
        claims = [C("dated", "A", 0), C("unknown", "B", None)]
        index = self.assert_oracle(claims, lambda n, o: True)
        self.assertEqual(index.current_ids(), {"dated", "unknown"})
        self.assertEqual(index.eligible_ids(9), {"dated"})

    def test_gold_properties_are_never_read(self):
        class GoldTrap:
            cid, text, timestamp, doc_id = "x", "Only input text.", 1, "doc"

            @property
            def subject(self):
                raise AssertionError("Gold subject was accessed")

            @property
            def relation(self):
                raise AssertionError("Gold relation was accessed")

            @property
            def value(self):
                raise AssertionError("Gold value was accessed")

        index = compile_certificates([GoldTrap()], lambda n, o: False)
        self.assertEqual(index.current_ids(), {"x"})

    def test_input_order_invariance_and_all_random_event_intervals(self):
        for seed in range(100):
            rng = random.Random(seed)
            claims = [C(f"c{i:02}", f"text {i}", rng.choice([None] + list(range(-4, 7))))
                      for i in range(rng.randint(8, 40))]
            pairs = {(n.cid, o.cid) for n in claims for o in claims
                     if n.cid != o.cid and rng.random() < 0.23}
            gate = lambda n, o: (n.cid, o.cid) in pairs
            index = self.assert_oracle(claims, gate)
            for _ in range(3):
                rng.shuffle(claims)
                shuffled = compile_certificates(claims, gate)
                self.assertEqual(index.to_dict(), shuffled.to_dict())

    def test_filter_before_topk_and_unknown_id(self):
        claims = [C("old", "A", 0), C("new", "B", 1), C("other", "B", 0)]
        index = compile_certificates(claims, lambda n, o: n.text != o.text)
        self.assertEqual(index.filter_ranked(["old", "other", "new"], as_of=1, k=2),
                         ["other", "new"])
        self.assertEqual(index.filter_ranked(["old", "other", "new"], k=1), ["other"])
        self.assertEqual(index.filter_ranked(["old"], k=0), [])
        with self.assertRaises(KeyError):
            index.filter_ranked(["absent"])

    def test_empty_input(self):
        index = self.assert_oracle([], lambda n, o: False)
        self.assertEqual(index.filter_ranked([], as_of=0), [])

    def test_duplicate_and_invalid_inputs_fail(self):
        for claims in ([C("x", "A", 0), C("x", "B", 1)],
                       [C("x", "A", math.nan)], [C("x", "A", math.inf)],
                       [C("x", "A", "2000")], [C("x", "A", True)]):
            with self.assertRaises(ValueError):
                compile_certificates(claims, lambda n, o: False)
        index = compile_certificates([C("x", "A", 0)], lambda n, o: False)
        for cutoff in [math.inf, math.nan, "year"]:
            with self.assertRaises(ValueError):
                index.eligible_ids(cutoff)

    def test_json_has_portable_null_infinite_boundaries(self):
        index = compile_certificates([C("x", "A", 0)], lambda n, o: False)
        encoded = json.dumps(index.to_dict(), allow_nan=False)
        self.assertIsNone(json.loads(encoded)["certificates"][0]["end"])

    def test_original_gate_blocking_and_ablation_equivalence(self):
        from wikigraphrag.detect.supersession import SupersessionDetector
        claims = [
            C("a", "The CEO of Acme is Alice Smith.", 1),
            C("b", "The CEO of Acme is Bob Jones.", 2),
            C("c", "The CEO of Beta is Claire White.", 3),
            C("d", "ALPHA.", 0), C("e", "BETA.", 1),
            C("f", "The value is 25.", 0), C("g", "The value is 30.", 1),
        ]
        for threshold in [0.0, 0.5, 1.0]:
            for use_subject in [True, False]:
                for use_value in [True, False]:
                    detector = SupersessionDetector(frame_threshold=threshold,
                                                    use_subject=use_subject, use_value=use_value)
                    gate = SupersessionGate(claims, detector)
                    blocked = self.assert_oracle(claims, gate)
                    full = self.assert_oracle(claims, gate, blocked=False)
                    self.assertEqual(blocked.certificates, full.certificates)
                    original_stale = {edge.older for edge in detector.detect(claims)}
                    self.assertEqual(blocked.current_ids(), {c.cid for c in claims} - original_stale)

    def test_gate_ignores_changed_gold_annotations(self):
        from wikigraphrag.core.claim import Claim
        claims = [Claim("a", "The budget of Acme is 20 million.", 1, subject="GOLD", value="1"),
                  Claim("b", "The budget of Acme is 30 million.", 2, subject="GOLD", value="2")]
        poisoned = [replace(c, subject=f"false {i}", relation="unrelated", value="identical")
                    for i, c in enumerate(claims)]
        self.assertEqual(compile_certificates(claims).to_dict(),
                         compile_certificates(poisoned).to_dict())


if __name__ == "__main__":
    unittest.main()
