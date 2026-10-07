"""Enumerate possible states to verify maximal sound exclusion."""
import itertools
import json
import unittest
from pathlib import Path

from retirement_logic import Status, TimeLocalEvidence


def powerset(items):
    return [frozenset(part) for size in range(len(items)+1)
            for part in itertools.combinations(items, size)]


class RetirementTests(unittest.TestCase):
    model_cases = 0
    target_cases = 0

    def test_all_models(self):
        for size in range(1, 6):
            universe = tuple(str(index) for index in range(size))
            sets = powerset(universe)
            for positive in sets:
                for negative in sets:
                    if positive & negative:
                        continue
                    for capacity in [None, *range(size+1)]:
                        for complete in (False, True):
                            models = [state for state in sets
                                      if positive <= state and not state & negative
                                      and (capacity is None or len(state) <= capacity)
                                      and (not complete or state == positive)]
                            evidence = TimeLocalEvidence(
                                tuple((v, f"positive:{v}") for v in positive),
                                tuple((v, f"negative:{v}") for v in negative),
                                capacity, "capacity" if capacity is not None else None,
                                "complete" if complete else None)
                            type(self).model_cases += 1
                            if not models:
                                with self.assertRaises(ValueError):
                                    evidence.decide(universe[0])
                                continue
                            for target in universe:
                                expected = (Status.PRESENT if all(target in state for state in models)
                                            else Status.ABSENT if all(target not in state for state in models)
                                            else Status.UNRESOLVED)
                                actual = evidence.decide(target)
                                self.assertEqual(actual.status, expected)
                                self.assertEqual(actual.certificate is None, expected == Status.UNRESOLVED)
                                type(self).target_cases += 1

    def test_duplicates_do_not_fill_capacity(self):
        evidence = TimeLocalEvidence((("a", "s1"), ("a", "s2")), capacity=2,
                                     capacity_source="capacity")
        self.assertEqual(evidence.decide("b").status, Status.UNRESOLVED)

    def test_capacity_certificate_minimal(self):
        for capacity in range(1, 8):
            values = tuple((str(i), f"source:{i}") for i in range(capacity))
            evidence = TimeLocalEvidence(values, capacity=capacity, capacity_source="capacity")
            decision = evidence.decide("target")
            self.assertEqual(decision.status, Status.ABSENT)
            self.assertEqual(len(decision.certificate.positive_values), capacity)
            for removed in range(capacity):
                subset = values[:removed] + values[removed+1:]
                less = TimeLocalEvidence(subset, capacity=capacity, capacity_source="capacity")
                self.assertEqual(less.decide("target").status, Status.UNRESOLVED)

    def test_positive_only_ambiguity(self):
        evidence = TimeLocalEvidence((("b", "new observation"),))
        self.assertEqual(evidence.decide("a").status, Status.UNRESOLVED)
        for probability in (0, .1, .5, .8, 1):
            coexistence_error = probability
            replacement_error = 1 - probability
            self.assertEqual(coexistence_error + replacement_error, 1)
            self.assertGreaterEqual(max(coexistence_error, replacement_error), .5)

    def test_explicit_sources_required(self):
        with self.assertRaises(ValueError):
            TimeLocalEvidence((("a", "s"),), capacity=1).decide("b")
        with self.assertRaises(ValueError):
            TimeLocalEvidence((("a", "s"),), complete_source="").decide("b")

    def test_explicit_negative_and_complete_state(self):
        negative = TimeLocalEvidence((("b", "s1"),), (("a", "s2"),))
        self.assertEqual(negative.decide("a").certificate.kind, "explicit_negative")
        complete = TimeLocalEvidence((("b", "s1"),), complete_source="s2")
        self.assertEqual(complete.decide("a").certificate.kind, "complete_state")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RetirementTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "passed": result.wasSuccessful(), "tests": result.testsRun,
        "constraint_cases": RetirementTests.model_cases,
        "target_model_comparisons": RetirementTests.target_cases,
        "scope": "finite-model correctness checks; no benchmark performance claim",
    }
    Path(__file__).with_name("retirement_logic_tests.json").write_text(json.dumps(report, indent=2)+"\n")
    raise SystemExit(not result.wasSuccessful())
