# Matched-input temporal policies

This package executes the temporal invalidation policy from Graphiti's official source.
It also provides exact latest-batch and earliest-direct-witness reference policies.

## Scope

The displayed label must be **Graphiti policy kernel (matched extraction)**.
Do not describe this condition as a Graphiti full-system reproduction.

All policies receive the same observations and parsed features.
Observations contain only `cid`, `text`, and `timestamp`.
Parsed features contain only `slot` and `value`.
The evaluator must prevent benchmark keys and answer identifiers from entering these fields.

The adapter supplies all prior candidates with the same parsed slot and a different value.
It keeps previously expired candidates available.
Graphiti's unchanged temporal blocks then update validity endpoints.
The adapter omits semantic extraction, duplicate merging, search, graph storage, and answer generation.
Different values do not always contradict each other.
The full system's semantic resolver can therefore supply a different candidate list.
This experiment measures consequences of the supplied policy inputs.
It cannot establish the full system's factual error rate.

The adapter creates fresh records and does not mutate input observations.
It encodes timestamps through an order-preserving map into UTC datetimes.
This map preserves comparisons and ties without date-range limitations.
The expiration clock is fixed because the selected blocks only test whether it exists.

## Source preservation

`vendor/PROVENANCE.json` records the official URL, retrieval date, hash, and source lines.
The two source files contain exact source substrings with no edited source lines.
The loader verifies both hashes before execution.
`vendor/graphiti_LICENSE` preserves the upstream Apache 2.0 license.

The adapter supplies minimal records with the fields these source blocks access.
This arrangement tests the actual policy code under controlled candidates.
It does not substitute test results for the upstream complete system.

## API

```python
from policies import graphiti_endpoints
ends, diagnostics = graphiti_endpoints(observations, parsed)
```

Each endpoint uses the original timestamp scale.
An infinite endpoint indicates that no supplied candidate closed the interval.
The active test is `timestamp <= cutoff < endpoint`.
The default arrival order sorts by timestamp, then CID.
The optional `arrival_order` argument accepts a complete index permutation.

`latest_batch_endpoints` retains all values at the newest parsed-slot date.
`latest_matched_batch` implements its query-local equivalent.
Neither function resolves date ties through input order.

`direct_first_endpoints` gives the earliest distinct-value witness reference.
It does not assume that a changed value logically contradicts the previous value.
That interpretation requires an external update contract.

## Verification

```bash
python pass2/baselines/verify_policies.py
```

The constructed checks test code semantics only.
They do not form a benchmark and support no empirical accuracy claim.
The script verifies 442 ingestion cases and 22 future-prefix conditions.
It also checks concurrent values, missing dates, and missing parsed slots.

## Decisive comparison

Exact latest-batch selection is essential when a source exposes complete snapshots.
It preserves every concurrent value in the newest snapshot.
Its accuracy can reach one by construction under lossless parsing.
This result establishes the required baseline strength.
It cannot support a novel learned retrieval claim.

Positive observations alone do not establish whether an omitted value ceased to hold.
Therefore, compare snapshot-based methods only under an explicit completeness contract.
Do not use complete gold states to certify completeness at inference.

The earliest direct witness and the selected Graphiti policy share their core invalidation rule.
Their agreement is an implementation comparison, not an empirical win over Graphiti.
