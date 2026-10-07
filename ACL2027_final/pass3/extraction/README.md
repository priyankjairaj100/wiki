# Source-only occurrence adapter

`source_adapter.py` extracts dated states from original TimeQA passages.
It never reads answer annotations or gold date ranges.
It uses source text, source article titles, and opaque passage IDs.

## Run the frozen development pilot

```bash
python pass3/extraction/source_adapter.py \
  --article-manifest pass3/protocol/split_manifest.json \
  --out-dir pass3/extraction/pilot_results
```

The manifest selects 50 articles before evaluation.
The pilot contains 2,174 source paragraphs.
The adapter returns 29 records across 25 paragraphs and 19 articles.
Twenty records have explicit tenure endpoints.
Nine records describe an occurrence start.
Twenty-three start dates have year precision.
Three have month precision. Three have day precision.
These counts describe extraction coverage, not extraction accuracy.

The early `results/` directory is a superseded calibration run.
Do not use it for evaluation or the final audit.
The final audit uses `pilot_results/blind_audit_records.jsonl`.
Its order uses a fixed hash. It contains no gold answers or method outcomes.
An independent model reviewer can label those source records.
Those labels must be called a model audit, not human annotations.

## API

```python
from pass3.extraction.source_adapter import add_source_context, extract_passage
passages = add_source_context(passages)
claims = [claim for passage in passages for claim in extract_passage(passage)]
```

`add_source_context` inspects the first three source paragraphs for personal birth evidence.
The adapter resolves person pronouns only after that source check.
It preserves the resolution rule in each record.
This rule remains a heuristic. The audit checks its errors.

Each record contains these fields:

| Field | Meaning |
|---|---|
| `claim_id` | Stable identifier for this occurrence |
| `passage_id`, `article_path` | Original source identity |
| `source_span` | Complete source sentence for audit |
| `atomic_span` | Exact excerpt assigned to this claim |
| `coverage_scope` | Always `atomic_clause_only` |
| `subject` | Source surface, title resolution, and canonical identity |
| `slot`, `value`, `value_span` | One extracted relation and its literal value |
| `start` | Occurrence start bounds and their exact source span |
| `end` | Distinct tenure end bounds, or null |
| `temporal_kind` | `occurrence_start` or `validity_duration` |
| `compiler_eligible` | Whether rectangular endpoint bounds meet the lifecycle API |
| `exclusion_assertion` | Explicit source succession evidence, or null |

Every source offset counts Python Unicode characters.
An end offset is exclusive.
Every numeric date is a Gregorian day ordinal.
A year maps to January 1 through December 31.
A month maps to its first and last days.
An exact day maps to a singleton.

The compiler uses half-open realized support, `[start, end)`.
An end date denotes the day when the state ceases.
Year and month expressions preserve uncertainty about that day.
The adapter leaves `through` constructions unmodeled.
That construction requires a separate inclusive-boundary rule before compilation.
Unclear constructions stay outside the compiler.

## Evidence unit contract

Use `atomic_span.text` as reader evidence.
Keep all unmatched source text as unmodeled fallback evidence.
Never remove a complete paragraph because one extracted state expired.
Never credit a selected excerpt for gold spans outside that excerpt.
Source sentence spans support audit only. They are not retrieval units.

The adapter supports simple date-led events, date-suffix events, and explicit tenures.
It rejects dates attached to a later clause.
It does not treat election dates as office start dates.
It does not invent a width for approximate or relative dates.
It does not use annual positive observations as occurrence starts.
It leaves loans, contracts, and relative durations unmodeled.
Planned expiry dates do not establish observed departures.
Repeated values retain distinct occurrence IDs.

## Replacement policy

`build_pairs` accepts only explicit source succession assertions.
Ordinary joins and appointments establish no pair.
The deterministic pilot supplies zero directed replacement pairs.
Its tenure endpoints can provide private end sentinels through the lifecycle API.
No result from this pilot can establish gains from replacement-pair detection.

Model-assisted records may supply explicit succession assertions.
`MODEL_EXTRACTION_PROMPT.txt` defines that contract.
`model_schema.json` defines the structural schema.
The validator checks literal spans, date bounds, IDs, and endpoint types.
It does not prove semantic entailment.
A model audit must check any accepted exclusion phrase and role scope.

## Verification

Run `python -m unittest pass3.extraction.test_source_adapter`.
Tests check date boundaries, separate endpoints, source spans, and conservative exclusions.
They are constructed software checks, not benchmark evidence.

## Freeze record

The final adapter hash is `2424a76fdcfe08330fddc45853969406f1784bb2f1aad00d90499d79d2a8d185`.
Eleven correctness tests pass.
Initial rule development inspected source text across the separated development corpus.
Final source checks used the frozen pilot articles.
No answer labels, gold intervals, or method outcomes informed these rules.
The remaining development sources are not claimed as completely unseen source text.
Their answer labels remain separate from extraction.

`model_adapter.py` normalizes optional model output through literal source validation.
No model-generated extraction result enters the deterministic pilot.

## Separate succession calibration

`succession_rules.py` provides a narrow, separate source interface.
It processes 30 source-cue-selected development paragraphs.
It yields five dated starts and three directed pairs across two articles.
Independent source review approves those records.
Nine constructed parser checks pass.
The automatic output reproduces the natural Warburg counterworld case.
These are calibration counts, not benchmark scores.

The primary adapter hash remains unchanged.
See `learned/FINDINGS.md` for the unsuccessful small-model extraction runs.
Both model runs retain their rejected outputs and partial execution manifests.
