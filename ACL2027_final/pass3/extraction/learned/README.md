# Exploratory model extraction of source succession

This batch tests a learned source adapter on 30 development paragraphs.
The source selection uses succession words and date counts.
It does not use questions, answer labels, or method results.
The batch is a calibration study. It is not a benchmark test split.

The model receives the article title and source paragraph only.
`prompt.txt` and `jobs.jsonl` were frozen before inference.
`manifest.json` records source, prompt, job, and validator hashes.
The primary deterministic adapter remains unchanged.

## Run

```bash
python pass3/extraction/learned/prepare_batch.py
python pass3/inference/run_jsonl.py \
  pass3/extraction/learned/jobs.jsonl \
  pass3/extraction/learned/raw_outputs.jsonl
python pass3/extraction/learned/validate_outputs.py
```

The model returns states and explicit successions.
A slot consists of an organization and a role.
A holder supplies the value for that slot.
A tenure preserves separate start and end dates.
A succession starts the new holder. It does not invent the previous holder's start.
A source gap remains a gap.
Planned expiry dates do not establish observed departures.

## Validation

The validator checks literal source quotes, names, organizations, roles, and dates.
It rejects year fragments taken from seasons.
It rejects approximate and unbounded dates.
It preserves unknown dates as unknown.
It does not fill missing fields through outside knowledge.
It does not use answer labels.

The output separates these records:

| File | Contents |
|---|---|
| `grounded_states.jsonl` | States passing literal source checks |
| `grounded_successions.jsonl` | Successions passing literal source checks |
| `grounding_failures.jsonl` | Rejected outputs and explicit reasons |
| `compiler_candidates.jsonl` | Records with usable endpoint bounds |
| `pair_candidates.jsonl` | Unique predecessor and successor matches |
| `pair_failures.jsonl` | Missing dates or ambiguous occurrence matches |

Literal checks do not establish semantic entailment.
Every compiler candidate and replacement pair requires a separate source audit.
The audit checks event attachment, role scope, coreference, gaps, and actual end dates.
Record this as a model-assisted source audit, not human annotation.

The compiler can run after semantic acceptance.
Its conclusions apply to the supplied occurrence bounds and replacement decisions.
This exploratory batch alone supports no end-to-end QA accuracy claim.

Run six constructed validation checks with:

```bash
python -m unittest pass3.extraction.learned.test_validation
```
