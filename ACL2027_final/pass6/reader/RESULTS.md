# Structured reader replication

All 234 fixed requests completed. The unchanged parser accepted 234. These requests cover 710 method conditions.

The study preserves all question text and source excerpts. It changes the output interface and completion budget.
The same 3B model uses schema constraints and a 512-token budget. Valid citation numbers are part of each schema.
The schema cannot establish whether an answer follows from its cited excerpt.

| Method | Primary EM | Primary strict F1 | Diagnostic EM | Diagnostic strict F1 |
|---|---:|---:|---:|---:|
| Original BM25 | 23.33 | 24.44 | 9.09 | 9.09 |
| Original + year | 25.00 | 25.00 | 18.18 | 18.18 |
| Title-aware | 35.00 | 36.11 | 9.09 | 9.09 |
| Earliest completion | 35.00 | 36.11 | 18.18 | 18.18 |
| Midpoint completion | 35.00 | 36.11 | 9.09 | 9.09 |
| Latest completion | 35.00 | 36.11 | 9.09 | 9.09 |
| Interval control | 35.00 | 36.11 | 9.09 | 9.09 |
| Possible support | 35.00 | 36.11 | 9.09 | 9.09 |
| Guaranteed support | 35.00 | 36.11 | 18.18 | 18.18 |
| Title-aware + year | 33.33 | 33.33 | 18.18 | 24.24 |

The primary cohort has 60 questions. The diagnostic has eleven questions selected before this replication.
The diagnostic selection used earlier context differences. It is not a random test sample.

## Primary cohort

Parser failures: 0/194 unique requests.
Target answer cardinality: `{"1": 56, "2": 4}`.
Possible and guaranteed support use different requests for 0/60 questions.
These policies change 0/60 answer sets.
All changed answers with valid outputs: 0.

## Diagnostic cohort

Parser failures: 0/40 unique requests.
Target answer cardinality: `{"1": 11}`.
Possible and guaranteed support use different requests for 7/11 questions.
These policies change 4/11 answer sets.
All changed answers with valid outputs: 4.

