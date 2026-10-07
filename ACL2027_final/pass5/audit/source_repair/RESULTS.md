# Source repair results

The reconstructed adapter passed all 27 tests before full extraction.
It passed five known calendar-end checks and six known bounded-state checks.
Both complete source partitions retain every source word.
No compiler records were rejected.
All three explicit replacement pairs retain their endpoints.

| Track | Paragraphs | Claims | Explicit ends | Units | Modeled share | Pairs |
|---|---:|---:|---:|---:|---:|---:|
| Template source | 32,332 | 493 | 292 | 33,005 | 1.4937% | 3 |
| Human source | 33,493 | 464 | 238 | 34,082 | 1.3614% | 0 |

The adapter adds 16 paragraph-level calendar ends across both tracks.
Twelve occur in the template source pool.
Four occur in the human source pool.
All three cross-claim pairs remain in previously inspected calibration articles.

Comparison with pass 4 retains 882 semantic records and repairs 54 records.
It returns 600 old records to fallback and adds 21 newly grounded records.
The comparison matches paragraph identifiers, date spans, and subject spans.
It excludes metadata-only changes from the semantic change count.
These counts describe extraction changes, not accuracy.

The earlier pass-4 assessment remains unchanged at 52 accepted events among 60 examples.
The fresh assessment uses a distinct frozen sample and appears in `../source_fresh`.
The paper reports repeated QA evaluation as a post-audit revision.
