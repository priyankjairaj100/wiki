# Source-only clause adapter

The frozen adapter expands exact source extraction before temporal compilation.
It reads paragraph text, public article titles, source order, and opaque identifiers.
It never reads questions, answer strings, answer spans, or annotation histories.

The adapter supports explicit date intervals, simple modifiers, named subjects, biography clauses, and adjacent coordinated roles.
Dates retain their stated precision.
An explicit duration has separate start and end bounds.
The adapter accepts an independent duration only when the end lower bound exceeds the start upper bound.
Overlapping bounds stay unmodeled.
The existing source grammar supplies explicit succession relations.
No role name creates an exclusion relation by itself.

Each record stores literal source spans and offsets.
The common retrieval partition retains every source word.
Unmodeled words remain fallback evidence.
A date filter removes only its modeled clause.
The validation script checks disjoint spans, exact text, and surviving pair endpoints.

## Freeze

`freeze_manifest.json` records code hashes before full DEV and test extraction.
The calibration source contains 4,030 paragraphs from 86 articles.
It combines 50 pilot paths with 39 prior calibration paths, with three overlaps.
One calibration source article has no eligible DEV question.
Thus the corresponding QA calibration pool contains 85 articles.

The independent audit used source text only.
It checked new clauses and all calibration succession pairs.
Its judgments are model-assisted reviews, not human annotations.
Candidate versions and correction records remain available.
The frozen confirmation sample must not drive further extractor changes.

## Run

From the project root:

```bash
python pass4/extraction/source_adapter.py \
  --source pass3/protocol/dev_source_passages.jsonl \
  --out pass4/extraction/dev_frozen
python pass4/extraction/source_adapter.py \
  --source pass3/protocol/test_source_passages.jsonl \
  --out pass4/extraction/test_frozen
python pass4/extraction/test_source_adapter.py
```

The JSONL output follows the pass-3 claim schema.
The unchanged validator and lifecycle compiler accept these records.
The unchanged `build_pairs` function reads explicit source exclusions.

## Source rendering

Some succession clauses inherit their role from a prior clause.
Each local atomic span retains the successor name and date.
The full source assertion and role span retain the original supporting words.
Resolved holder and role metadata can support reader interpretation.
A renderer must label that metadata consistently across methods.
It must not treat an inherited role as words inside the local excerpt.

The adapter deliberately leaves unsupported relative dates and durations unmodeled.
It rejects incomplete abbreviations, crossed clauses, ungrounded organizational pronouns, and projected loan endpoints.
These rules improve source attachment, rather than increasing coverage through inferred dates.
