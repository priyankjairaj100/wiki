# Uncertain-date compilation

`uncertain_time.py` implements the two-certificate compiler.
It uses only the Python standard library.

Each input interval describes uncertainty about one event's occurrence date.
It does not describe how long a fact remains valid.
The compiler assumes independent date assignments within these closed bounds.
The directed text gate must distinguish replacement from coexistence.

## Use the complete pair list

```python
from uncertain_time import IntervalClaim, compile_from_pairs

claims = [
    IntervalClaim("c", "Earlier claim", 0, 2),
    IntervalClaim("d", "Possible replacement", 1, 4),
    IntervalClaim("e", "Forced replacement", 3, 5),
]
# Each pair is (witness_id, target_id).
pairs = [("d", "c"), ("e", "c")]
index = compile_from_pairs(claims, pairs)

assert index["c"].possible(4)
assert not index["c"].possible(5)
assert index["c"].guaranteed(0, 2)
assert not index["c"].guaranteed(2)
```

Pair compilation costs O(n+m), for n claims and m supplied pairs.
It does not sort the inputs or store the pair stream.
The output uses O(n) records.
Duplicate pairs have no effect.
Self-pairs have no effect.
Unknown identifiers and duplicate claim identifiers cause errors.
Boundary ties select the smallest witness identifier.
Claim order controls dictionary order, but never certificate values.

The pair list must contain every accepted directed pair.
An incomplete list does not establish the guarantees.
Each query uses a closed interval.
Omit the second bound for a point query.

## Use a text gate

```python
from uncertain_time import compile_intervals

accepted = set(pairs)
index = compile_intervals(
    claims,
    lambda witness, target: (witness.cid, target.cid) in accepted,
)
```

This reference scan evaluates all n(n-1) non-self directed pairs.
A gate receives the claim text and interval bounds.
It must make one fixed decision across every allowed date assignment.
For a text-only gate, use only the text fields.

`possible(a,b)` retains a claim when one assignment supports some time in the window.
`guaranteed(a,b)` retains a claim when every assignment supports some time in the window.
The supporting time can differ between assignments.
`status(a,b)` returns `guaranteed`, `unresolved`, or `unsupported`.

These guarantees concern evidence eligibility under the supplied gate.
They do not certify the truth of text extraction or generated answers.

## Files and verification

- `UNCERTAIN_TIME_THEORY.md`: complete definitions and proofs.
- `main_theory.tex`: concise main section.
- `appendix_proofs.tex`: formal proofs and implementation scope.
- `test_uncertain_time.py`: API tests and boundary examples.
- `../independent/exhaustive_uncertain_time.py`: independent finite-world oracle.
- `../independent/REVIEW.md`: independent review.

Run the local API tests:

```bash
python pass2/theory/test_uncertain_time.py
```

The earlier `retirement_logic.py` is a separate open-world audit prototype.
It implements established completeness and cardinality semantics.
It is not the uncertain-date method or a claimed novel contribution.

## Certify an unchanged retrieved context

```python
from uncertain_time import stable_context

result = stable_context(index, ["c", "d", "e"], 0, 5, k=2)
print(result.stable)
print(result.possible_top)
print(result.guaranteed_top)
# common_context contains the invariant context when stable is true.
```

The ranking must contain every indexed identifier exactly once.
Its order must remain fixed across date assignments.
The test is exact under the compiler's date model.
Uncertain claims below the context budget can leave the selected context unchanged.
The test does not certify generated answers.

Run its tests with:

```bash
python pass2/theory/test_context_stability.py
```
