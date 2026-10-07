# Reconstructed final source adapter

`source_adapter.py` implements `source-clause-v3` from the preserved pass-4 repair plan.
Workspace maintenance removed the earlier pass-5 files.
This reconstruction has its own freeze and new outputs.
The paper must use these outputs rather than remembered counts.

The adapter reads source paragraphs and article metadata only.
It requires paragraph-local named subjects for pronouns.
Its parsing view preserves abbreviation offsets.
It checks date ownership and cuts values at specified finite predicates.
It attaches calendar ends to unique compatible occurrences.
It retains recognized unresolved bounded states as unknown fallback.
It creates replacement pairs only from explicit succession statements.

The 27 source tests passed before full extraction.
Five known calendar-end checks and six bounded-state checks also passed.
These are calibration checks, not fresh accuracy measurements.

Run from the project root:

```sh
python -m unittest pass5.extraction.test_source_adapter -v
python pass5/extraction/source_adapter.py --source pass3/protocol/dev_source_passages.jsonl --out reproduced_pass5/extraction/dev
python pass5/extraction/source_adapter.py --source pass3/protocol/test_source_passages.jsonl --out reproduced_pass5/extraction/test
python pass5/extraction/verify_partitions.py --source pass3/protocol/dev_source_passages.jsonl --claims reproduced_pass5/extraction/dev/claims.jsonl --out reproduced_pass5/extraction/dev/partition_audit.json
python pass5/extraction/verify_partitions.py --source pass3/protocol/test_source_passages.jsonl --claims reproduced_pass5/extraction/test/claims.jsonl --out reproduced_pass5/extraction/test/partition_audit.json
```

`freeze_manifest.json` binds the adapter, source helpers, tests, and calibration evidence.
`output_manifest.json` binds both extracted claim sets and partition reports.
`build_repair_audit.py` records changes from the preserved pass-4 claims.
The fresh source audit is separate in `pass5/audit/source_fresh`.
