"""Deterministic specification checks for the bounded Graphiti comparison."""
import dataclasses
import itertools
import json
import pathlib

from policies import (direct_first_endpoints, eligible_indices,
                      graphiti_endpoints, latest_batch_endpoints,
                      latest_matched_batch)


@dataclasses.dataclass(frozen=True)
class Observation:
    cid: str
    text: str
    timestamp: int | None


@dataclasses.dataclass(frozen=True)
class Parsed:
    slot: tuple[str, str] | None
    value: str | None


def main():
    # Constructed inputs check policy semantics only. They are not benchmarks.
    checks = 0
    for n in range(1, 5):
        obs = [Observation(str(i), "", i // 2) for i in range(n)]
        for values in itertools.product("ab", repeat=n):
            parsed = [Parsed(("s", "r"), v) for v in values]
            expected = direct_first_endpoints(obs, parsed)
            for order in itertools.permutations(range(n)):
                actual, _ = graphiti_endpoints(obs, parsed, order)
                assert actual == expected, (values, order, actual, expected)
                checks += 1
    # Complete snapshots preserve concurrent values. A and B coexist at time 1.
    obs = [Observation("0", "", 0), Observation("1a", "", 1),
           Observation("1b", "", 1), Observation("2b", "", 2)]
    parsed = [Parsed(("s", "r"), v) for v in ("a", "a", "b", "b")]
    ends = latest_batch_endpoints(obs, parsed)
    assert eligible_indices(obs, ends, 1) == {1, 2}
    assert latest_matched_batch(obs, parsed, ("s", "r"), 1, [0, 2, 1, 3]) == [2, 1]
    # Positive-only updates cannot reveal coexistence or replacement. The direct
    # policy drops A here. This is expected behavior, not a factual truth check.
    partial = [Observation("a", "", 0), Observation("b", "", 1)]
    pparsed = [Parsed(("s", "r"), x) for x in "ab"]
    pends, _ = graphiti_endpoints(partial, pparsed)
    assert eligible_indices(partial, pends, 1) == {1}
    # Appending a strictly future batch preserves every prior cutoff decision.
    prefix_checks = 0
    for size in range(1, len(obs) + 1):
        prefix = obs[:size]
        for method in (latest_batch_endpoints, direct_first_endpoints):
            full_ends = method(obs, parsed)
            part_ends = method(prefix, parsed[:size])
            future = [o.timestamp for o in obs[size:]]
            if not future:
                continue
            for cutoff in [-1, 0, 0.5, 1, 1.5, 2]:
                if cutoff < min(future):
                    assert eligible_indices(obs, full_ends, cutoff) == eligible_indices(prefix, part_ends, cutoff)
                    prefix_checks += 1
    # Missing timestamps and parse failures cannot create endpoints.
    missing = [Observation("m", "", None), Observation("x", "", 1)]
    missing_parsed = [Parsed(("s", "r"), "a"), Parsed(None, None)]
    assert graphiti_endpoints(missing, missing_parsed)[0] == direct_first_endpoints(missing, missing_parsed)
    report = {"passed": True, "exhaustive_ingestion_orders": checks,
              "future_prefix_checks": prefix_checks,
              "complete_snapshot_ties_preserved": True,
              "positive_only_ambiguity_demonstrated": True,
              "constructed_checks_are_benchmarks": False}
    path = pathlib.Path(__file__).with_name("verification.json")
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
