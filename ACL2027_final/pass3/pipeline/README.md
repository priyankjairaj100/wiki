# Matched source retrieval

This pipeline reads natural source text from TimeQA.
It uses the complete development corpus as one retrieval pool.
A query's article identifier never restricts retrieval candidates.
Answer labels enter only the separate scoring stage.

## Frozen outputs

`pilot_final/` contains the accepted pilot run.
It contains 176 queries from 50 articles.
`validation/` contains the frozen validation retrieval run.
The protocol excludes articles inspected during source calibration.
Earlier pilot folders contain debugging runs and do not support paper claims.

The corpus contains 32,332 paragraphs from 740 articles.
Some corpus articles have no retained positive question.
The final adapter extracts 481 modeled claims and 221 explicit end events.
It accepts no directed replacement pair in this corpus.
The exact partition contains 32,976 source units.
All substantive source characters remain in that partition.
Unmatched text remains available as fallback units under every condition.

## Selection

The pipeline extracts source claims before reading answer labels.
Every claim retains exact source offsets.
Each explicit duration keeps separate start and end bounds.
An occurrence date does not become a full validity duration.
Temporary states without supported endpoints remain fallback text.
Overlapping atomic claims also become fallback text.

BM25 indexes each unit's article title and exact source text.
All temporal conditions use the same complete ranking.
They use the same source claims, date bounds, and directed pair decisions.
The latest-year control separately reorders the shared top twenty lexical units.
The protocol declares this exception.

The context budget permits five source units and 768 whitespace tokens.
The final unit uses a source prefix when the token budget ends.
Multiple disjoint units can come from one paragraph.
The scorer requires the annotated span to occur inside a shown unit.
A parent paragraph match alone does not establish span coverage.

## Reproduce retrieval

Run commands from the project root.
The pilot uses its preserved configuration.

```bash
python pass3/pipeline/run_matched.py --config pass3/protocol/config_pilot.json --output pass3/pipeline/pilot_reproduced
python pass3/pipeline/audit_run.py --folder pass3/pipeline/pilot_reproduced
python pass3/pipeline/summarize_mechanism.py --folder pass3/pipeline/pilot_reproduced
python pass3/protocol/score_predictions.py --labels pass3/protocol/dev_pilot_labels.jsonl --predictions pass3/pipeline/pilot_reproduced/predictions.jsonl --passages pass3/protocol/dev_source_passages.jsonl --config pass3/protocol/config_pilot.json --output pass3/pipeline/pilot_reproduced/scored
```

The validation run creates no reader jobs.

```bash
python pass3/pipeline/run_matched.py --queries pass3/protocol/dev_validation_queries.jsonl --output pass3/pipeline/validation_reproduced --reader-limit 0
python pass3/pipeline/audit_run.py --folder pass3/pipeline/validation_reproduced
python pass3/pipeline/summarize_mechanism.py --folder pass3/pipeline/validation_reproduced
python pass3/protocol/score_predictions.py --labels pass3/protocol/dev_validation_labels.jsonl --predictions pass3/pipeline/validation_reproduced/predictions.jsonl --passages pass3/protocol/dev_source_passages.jsonl --output pass3/pipeline/validation_reproduced/scored
```

The runner records input hashes before retrieval.
It checks those hashes again after retrieval.
Changes during a run cause an error.
The manifest also records artifact hashes and the exact command.
Each accepted run preserves its configuration in `config.json`.

A later audit sorted BM25 query tokens before score accumulation.
This removes dependence on Python hash ordering.
Selection also stops after five accepted units, avoiding unnecessary full-list scans.
`run_matched_v1.py` preserves the exact original code.
`check_rank_reproduction.py` checks every recorded selection under deterministic accumulation.
Each accepted run stores the resulting `rank_reproduction_audit.json`.
This implementation correction does not use answer labels.

## Reader jobs

The primary reader pilot selects 24 questions by a seeded hash.
This selection does not use retrieval scores or answer labels.
Identical full prompts share one model call.
The pilot produces 52 unique prompts across eight conditions.
`reader_jobs.jsonl` stores complete prompts and source provenance.
Each record maps one model call to its associated methods.

`build_mechanism_reader_jobs.py` creates a separate diagnostic cohort.
It includes all nine pilot questions with different completion contexts.
It adds 22 prompts and reuses six primary prompts.
Selection uses context differences, never answer outcomes.
The diagnostic cohort must remain separate from the primary reader pilot.

Prompts request a JSON answer list and supporting excerpt numbers.
Shared excerpts receive identical original bounds and temporal status metadata.
The reader never receives filled-in dates or answer labels.
The inference runner and scoring code live in adjacent project directories.

## Interpretation

The certificate concerns modeled dates under fixed source extraction.
It does not certify fallback text or source extraction accuracy.
`conditioned_mechanism.json` reports certificate coverage among contexts with modeled units.
It also separates contexts that contain only fallback units.

Possible support equals the outer interval control here because accepted replacement pairs are absent.
The main gain tested here concerns date completion and context stability.
This run alone does not establish better answer quality than existing retrieval methods.

## Dependencies

The retrieval runner requires Python 3.12 and NumPy.
The complete answer scorer also uses SciPy.
No GPU or external service is required for retrieval reproduction.

## Constructive ambiguity audit

`build_counterworlds.py` creates two legal timelines for each ambiguous query.
Every timeline respects the extracted source bounds.
One timeline selects an unresolved source claim.
The other timeline excludes that claim.
The output stores complete event dates, exact source excerpts, and the refinement frontier.
An independent direct evaluator replays each stored timeline.
These timelines demonstrate model ambiguity.
They are constructed audit examples, not observed historical dates.

```bash
python pass3/pipeline/build_counterworlds.py --folder pass3/pipeline/validation
```

## Stable context budget

`stable_budget.py` computes the first unresolved item in the possible-filtered ranking.
Every smaller unit budget gives a stable context.
Every budget that reaches this item gives an unstable context.
The script compares this rule with direct context equality at five budgets.

The diagnostic uses the complete fixed BM25 ranking.
It varies source units before token clipping.
Its cohort remains fixed at 375 parsed validation queries with modeled evidence in the original possible context.
The script reads no answer labels and makes no model calls.
It saves each query's exact first unresolved rank.
It also saves counts, a compact LaTeX table, and vector figures.

```bash
python pass3/pipeline/stable_budget.py
```
