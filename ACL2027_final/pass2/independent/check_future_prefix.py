"""Check the uncertain-start prefix property independently of paper proofs."""
from pathlib import Path
import json
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "theory"))
from uncertain_time import IntervalClaim, compile_from_pairs

rng = random.Random(20261006)
comparisons = 0
for trial in range(500):
    a = rng.randint(-3, 3)
    b = rng.randint(a, 5)
    original = []
    for i in range(5):
        lo = rng.randint(-5, 7)
        original.append(IntervalClaim(f"c{i}", "", lo, rng.randint(lo, 10)))
    pairs = [(d.cid, c.cid) for c in original for d in original
             if c.cid != d.cid and rng.random() < 0.5]
    before = compile_from_pairs(original, pairs)
    additions = [IntervalClaim("new0", "", b + 0.25, b + 2.5),
                 IntervalClaim("new1", "", b + 0.5, b + 0.5)]
    complete = original + additions
    appended_pairs = pairs + [(d.cid, c.cid) for c in complete for d in complete
                              if c.cid != d.cid and
                              (c.cid.startswith("new") or d.cid.startswith("new"))]
    after = compile_from_pairs(complete, appended_pairs)
    for c in original:
        assert before[c.cid].possible(a, b) == after[c.cid].possible(a, b)
        assert before[c.cid].guaranteed(a, b) == after[c.cid].guaranteed(a, b)
        comparisons += 2
    for c in additions:
        assert not after[c.cid].possible(a, b)
        assert not after[c.cid].guaranteed(a, b)
        comparisons += 2

# Strictness is necessary: a witness exactly at the window end can matter.
c, d = IntervalClaim("c", "", 0, 0), IntervalClaim("d", "", 2, 2)
assert compile_from_pairs([c], [])["c"].guaranteed(2)
assert not compile_from_pairs([c, d], [("d", "c")])["c"].possible(2)

result = {"status": "passed", "trials": 500, "comparisons": comparisons,
          "strict_boundary_counterexample": "a new event at b can change support",
          "scope": "existing date bounds and directed gates remain fixed"}
Path(__file__).with_name("future_prefix_results.json").write_text(
    json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
