"""Finite-world verification of the explicit-end source adapter.

The oracle evaluates realized lifetimes directly. It never uses certificates.
These constructed cases test correctness, not empirical retrieval performance.
"""
import itertools
import json
from pathlib import Path
import random
import unittest

from lifecycle import (LifecycleClaim, compile_lifecycles, completion_certificates,
                       select_context, stable_lifecycle_context)


def oracle(index, times, a, b):
    supported = set()
    for cid in index.claims:
        start = times[cid]
        stop = min((times[w] for w, target in index.event_pairs
                    if target == cid and times[w] > start), default=float("inf"))
        if start <= b and a < stop:
            supported.add(cid)
    return supported


class LifecycleTests(unittest.TestCase):
    def test_explicit_end_and_hidden_sentinel(self):
        index = compile_lifecycles([LifecycleClaim("c", "from start through end", 0, 1, 3, 4)], [])
        self.assertEqual(set(index.certificates), {"c"})
        cert = index.certificates["c"]
        self.assertTrue(cert.guaranteed(1, 2))
        self.assertFalse(cert.guaranteed(3))
        self.assertTrue(cert.possible(3))
        self.assertFalse(cert.possible(4))
        self.assertEqual(cert.possible_end, 4)
        self.assertEqual(cert.potential_witness_lower, 3)
        self.assertTrue(cert.possible_end_witness.startswith("@explicit-end:"))

    def test_overlap_requires_separate_scope(self):
        for lower, upper in ((0, 2), (1, 3), (2, 3)):
            with self.assertRaises(ValueError):
                LifecycleClaim("c", "", 0, 2, lower, upper)
        with self.assertRaises(ValueError):
            LifecycleClaim("c", "", 0, 1, 4, None)

    def test_coexistence_and_recurrence(self):
        # Matching values do not identify lifetimes. Distinct occurrences retain IDs.
        claims = [LifecycleClaim("a1", "A", 0, 0, 1, 1),
                  LifecycleClaim("b", "B", 1, 1, 3, 3),
                  LifecycleClaim("a2", "A", 3, 3)]
        index = compile_lifecycles(claims, [])
        self.assertFalse(index.certificates["a1"].possible(4))
        self.assertTrue(index.certificates["a2"].guaranteed(4))
        coexisting = compile_lifecycles([LifecycleClaim("x", "X", 0, 0),
                                        LifecycleClaim("y", "Y", 1, 1)], [])
        self.assertTrue(all(c.guaranteed(5) for c in coexisting.certificates.values()))

    def test_shared_completions_and_boundary(self):
        index = compile_lifecycles([LifecycleClaim("c", "", 0, 2, 4, 6)], [])
        for mode, start, end in (("earliest", 0, 4), ("midpoint", 1, 5), ("latest", 2, 6)):
            cert = completion_certificates(index, mode)["c"]
            self.assertEqual(cert.lower, start)
            self.assertEqual(cert.possible_end, end)
            self.assertTrue(cert.possible(start))
            self.assertFalse(cert.possible(end))
        self.assertEqual(select_context(index, ["c"], 6, policy="interval"), ())

    def test_unknown_fixed_policy_not_guaranteed_support(self):
        index = compile_lifecycles([LifecycleClaim("c", "", 0, 4)], [])
        for mode in ("possible", "guaranteed", "earliest", "midpoint", "latest", "interval", "no_filter"):
            chosen = select_context(index, ["u", "c"], 2, k=1, policy=mode, unknown_ids=["u"])
            self.assertEqual([(i.cid, i.status) for i in chosen], [("u", "unknown")])
        stability = stable_lifecycle_context(index, ["u", "c"], 2, k=1, unknown_ids=["u"])
        self.assertTrue(stability.stable)
        self.assertIn("fixed unknown fallback", stability.scope)
        self.assertFalse(stable_lifecycle_context(index, ["c", "u"], 2, k=1, unknown_ids=["u"]).stable)

    def test_rejected_unknown_gate_endpoint(self):
        c = LifecycleClaim("c", "", 0, 0)
        with self.assertRaises(ValueError):
            compile_lifecycles([c], [("unmodeled", "c")])
        with self.assertRaises(ValueError):
            compile_lifecycles([c], [("c", "unmodeled")])
        with self.assertRaises(ValueError):
            select_context(compile_lifecycles([c], []), ["c"], 1, unknown_ids=["c"])

    def test_source_record(self):
        record = {"claim_id": "c", "source_span": {"text": "served from 2000 to 2003"},
                  "temporal_kind": "validity_duration", "start": {"lower": 0, "upper": 1},
                  "end": {"lower": 3, "upper": 4}}
        self.assertEqual(LifecycleClaim.from_record(record), LifecycleClaim("c", record["source_span"]["text"], 0, 1, 3, 4))
        record["end"] = None
        with self.assertRaises(ValueError):
            LifecycleClaim.from_record(record)


def finite_world_check():
    rng = random.Random(763291)
    counts = {"configurations": 0, "worlds": 0, "support_predicates": 0, "stability_conditions": 0}
    query_points = (-1, 0, 1, 2, 3, 4, 5, 6, 7, 8)
    queries = tuple((a, b) for a in query_points for b in query_points if a <= b)
    for _ in range(180):
        claims = []
        n = rng.randint(1, 3)
        for j in range(n):
            lower = rng.randint(0, 3)
            upper = lower + rng.randint(0, 2)
            end_lower = upper + rng.randint(1, 2) if rng.random() < .7 else None
            end_upper = end_lower + rng.randint(0, 2) if end_lower is not None else None
            claims.append(LifecycleClaim(str(j), "source assertion", lower, upper, end_lower, end_upper))
        pairs = [(w.cid, c.cid) for w in claims for c in claims
                 if w.cid != c.cid and rng.random() < .55]
        index = compile_lifecycles(claims, pairs)
        event_ids = tuple(index.events)
        worlds = [dict(zip(event_ids, dates)) for dates in itertools.product(
            *(range(index.events[e].lower, index.events[e].upper + 1) for e in event_ids))]
        counts["configurations"] += 1
        counts["worlds"] += len(worlds)
        ranking = list(index.claims)
        rng.shuffle(ranking)
        for a, b in queries:
            masks = [oracle(index, times, a, b) for times in worlds]
            union, intersection = set.union(*masks), set.intersection(*masks)
            for cid, cert in index.certificates.items():
                assert cert.possible(a, b) == (cid in union), (claims, pairs, cid, a, b, "possible")
                assert cert.guaranteed(a, b) == (cid in intersection), (claims, pairs, cid, a, b, "guaranteed")
                counts["support_predicates"] += 2
            for k in range(n + 1):
                actual_contexts = {tuple(cid for cid in ranking if cid in mask)[:k] for mask in masks}
                decision = stable_lifecycle_context(index, ranking, a, b, k=k)
                assert decision.stable == (len(actual_contexts) == 1)
                if decision.stable:
                    assert decision.common_context == next(iter(actual_contexts))
                counts["stability_conditions"] += 1
    return counts


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LifecycleTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    counts = finite_world_check()
    output = {"passed": True, "api_tests": result.testsRun, **counts,
              "scope": "Constructed finite-world correctness checks, not benchmark examples."}
    Path(__file__).with_name("lifecycle_tests.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
