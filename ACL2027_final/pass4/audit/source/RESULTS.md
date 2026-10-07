# Source audit results

The revised adapter preserves source text, but its semantic coverage remains incomplete.

An independent model-assisted audit guided calibration before the freeze. It did not read answer labels or retrieval results.
The audit inspected all 57 inherited calibration records, 76 first-revision records, and each later addition.
The final calibration set contains 114 claims, including five succession claims and three accepted pairs.
All earlier identified failures were absent from that final set.

The frozen adapter then produced 792 claims from 32,332 development paragraphs.
Independent checks verified 5,188 literal spans and all 33,433 source units.
No units overlapped. Every source word remained in a modeled or fallback unit.

## Frozen confirmation sample

The sample contains 60 claims from 678 claims outside the 86 calibration articles.
Selection uses the fixed hash described in `PROTOCOL.md`.
The reviewer inspected each full source paragraph.
These judgments did not change the frozen adapter or evaluation records.

| Audit dimension | Result |
|---|---:|
| Event grounding accepted | 52/60 |
| Event grounding rejected | 5/60 |
| Event grounding uncertain | 3/60 |
| Accepted grounding without an omitted paragraph-level termination | 41/60 |
| Accepted start, but stated termination omitted | 11/60 |
| Explicit-end records in the sample | 29/60 |
| Explicit-end records with accepted event grounding | 27/29 |

Two rejected records assign a husband's event to the article subject.
Two rejected records truncate football club names at abbreviations.
One rejected record merges distinct predicates into its value.
Two uncertain records borrow dates from adjacent events.
One uncertain record combines two roles within a summarized duration.

Eleven otherwise grounded starts omit a termination stated elsewhere in the reviewed paragraph.
Seven omit later departures. Two omit relative durations.
One omits an expired trial. One omits the organization's dissolution.

All three development replacement pairs occur in calibration articles.
Each pair has a source-supported successor, predecessor, role, and date.
The adapter does not invent dates for unknown predecessor starts.

## Interpretation

The source audit separates literal grounding, event semantics, and lifecycle completeness.
Exact offsets do not establish correct reference resolution.
An unspecified end in the extracted model does not establish an ongoing real-world state.
The certificates remain exact for the declared extracted model.
These model-assisted judgments are not human annotations or an extraction recall estimate.

## Suggested appendix text

We audited 60 claims outside calibration using a fixed identifier hash.
An independent model-assisted reviewer inspected each full source paragraph without question labels.
The reviewer accepted 52 events, rejected five, and marked three uncertain.
Eleven accepted starts omitted a termination stated elsewhere in the paragraph.
The rejected records contain reference errors, truncated names, or merged predicates.
These judgments did not change the frozen adapter.
The audit distinguishes source interpretation from the compiler's exact guarantees for its input model.

## Files

- `confirmation/semantic_review.jsonl`: all 60 judgments and reasons.
- `confirmation/semantic_summary.json`: counts, hashes, and sample definition.
- `confirmation/confirmation_sample.jsonl`: extracted records and full source paragraphs.
- `confirmation/integrity_report.json`: independent literal and partition results.
- `calibration_v5_pair_review.jsonl`: all three accepted pair judgments.
- `check_source_integrity.py`: repeatable literal checks and deterministic sample selection.

To reproduce the source integrity check, provide a units file from the matched pipeline.
The confirmation sample does not require that optional units file.

```bash
python pass4/audit/source/check_source_integrity.py \
  --sources pass3/protocol/dev_source_passages.jsonl \
  --claims pass4/extraction/dev_frozen/claims.jsonl \
  --calibration-sources pass4/extraction/calibration_sources.jsonl \
  --out reproduced_pass4/source_audit
```
