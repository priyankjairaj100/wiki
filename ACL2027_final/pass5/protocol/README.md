# Source revision and verification

This revision uses the same query cohorts, ranking rules, and evidence budgets as pass 4.
The source adapter changed after a source audit.
Earlier benchmark outcomes were available during this revision.
The revised study therefore does not claim an untouched test set.

The adapter reads public source text, titles, paragraph order, and opaque identifiers.
It does not read questions, labels, or answer strings.
Its source freeze precedes full extraction and the fresh source audit.
The algorithm freeze records 35 files before revised retrieval starts.
No hash exceptions are allowed.

The template track retains 2,348 questions.
The human track retains 830 questions.
Every method searches the complete declared source pool.
The ten methods share the revised source units and evidence budgets.
Each context contains at most five excerpts and 768 source words.
Source metadata appears outside the source-word budget.
Unmodeled text remains in fixed fallback excerpts.

`run_revision.py` provides the recorded execution phases.

```bash
python pass5/pipeline/run_revision.py --phase human
python pass5/pipeline/run_revision.py --phase validation
python pass5/pipeline/run_revision.py --phase checks
```

These commands write experiment outputs.
Use an isolated project copy when rerunning them.
The release verifier reads the saved study without changing its files.

The independent replay scans incoming events directly.
It does not call the certificate compiler or counterworld constructor.
It checks every selected unit, rendered excerpt, budget comparison, and saved timeline.
The independent scorer separately recomputes five retrieval metrics for every method and question.
The lazy selector must match full-mask selection for every parsed query.

The reader retains the same 60 primary questions and 11 diagnostic questions.
A complete request and execution identity governs historical reuse.
No partial cohort is scored.
The unchanged parser retains all failures in the scored denominator.
`reader_join_verification.json` records exact lineage checks.
The two `reader_*_change_audit.json` files separate valid answer changes from parser failures.

The secondary analysis retains all six previously declared ranking variants.
It reads no answer labels or model responses.
Each variant is checked against direct full-mask selection.
Its declaration and code hashes appear in `pass5/retrieval/SECONDARY_RANKING_PROTOCOL.json`.
