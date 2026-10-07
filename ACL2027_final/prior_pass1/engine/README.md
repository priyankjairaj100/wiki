# Direct witness compiler

This compiler converts the unchanged detector predicates into exact temporal eligibility certificates.
It uses claim text and source timestamps.
It does not read gold subject, relation, or value annotations.
The implementation uses the Python standard library.
The supplied original package provides the feature parser and detector predicates.

## Semantics

For claim `c`, the boundary is the earliest strictly later claim accepted by both original pair gates.
The claim is eligible at cutoff `T` exactly when `start <= T < boundary`.
A missing boundary means positive infinity.
The current mask retains claims without an accepted later witness.
Undated claims remain current, but cannot enter an as-of result.
These certificates describe the supplied predicate and source timestamps.
They do not certify factual truth or infer event dates.

The compiler never joins connected components.
An indirect path cannot terminate a claim.
Repeated values remain separate claims.
Simultaneous claims cannot terminate each other.
The lexicographically smallest claim ID resolves a tie between earliest witnesses.

## Algorithm

The compiler processes timestamp batches in ascending order.
Each batch compares newer claims against unresolved older claims.
A direct match sets the older claim's boundary.
The compiler then removes that older claim from its candidate index.
Only after all comparisons does the batch enter the candidate index.
This order preserves simultaneous claims.

Positive frame thresholds permit complete candidate blocking.
Accepted nonempty frames share a token.
Empty frames use one common bucket.
Nonpositive thresholds use one global bucket.
The compiler does not use the original detector's optional blocking heuristic.
Custom predicates use all unresolved claims unless they supply complete candidate keys.

The retained output has one certificate per claim.
The temporary index stores unresolved claims and their frame tokens.
Worst-case pair work remains quadratic.
Sparse frame overlap and early witnesses reduce practical pair work.
The output records pair tests and index visits separately.

## Compile

Run from the delivered source directory.
Replace `original` with the directory containing the original `wikigraphrag` package.

```bash
python engine/engine.py \
  --package-root original \
  --claims original/data/templama/claims.jsonl \
  --as-of 2015 \
  --output runs/templama_certificates.json
```

The JSON includes source hashes, detector settings, tie rules, and missing-time rules.
JSON `null` represents an infinite boundary.
An undated start also uses `null`.
The result keeps source document IDs for witness lookup.

## Use in retrieval

```python
from engine import compile_certificates

index = compile_certificates(claims)
context_ids = index.filter_ranked(ranked_ids, as_of=2015, k=10)
current_context_ids = index.filter_ranked(ranked_ids, k=10)
```

Filtering precedes top-k selection.
The method preserves the supplied ranking.
Call `index.eligible_ids(T)` or `index.current_ids()` to obtain complete masks.
Each `index.certificates[cid]` provides `start`, `end`, and `witness_cid`.

## Reproduce checks

```bash
python engine/run_certificate_tests.py \
  --package-root original \
  --output runs/certificate_tests.json
```

The runner checks every packaged dataset.
It compares all boundaries and witnesses against an exhaustive pair oracle.
It checks event cutoffs and every open interval between events.
It also checks the original detector's current mask.
Constructed tests cover 100 random predicate graphs and three input permutations each.
Other tests cover nontransitive matches, value returns, repeated values, simultaneous conflicts, and missing timestamps.
These constructed cases are correctness tests.
They are not benchmark observations.
