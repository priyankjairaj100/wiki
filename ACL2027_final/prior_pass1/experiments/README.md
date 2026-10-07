# Reproduce the evidence audit

These scripts use Python 3.11 and the Python standard library.
They load parser code from the original release.
They make no model calls and require no GPU.

Run:

```sh
python experiments/run_all.py \
  --source /absolute/path/to/wikigraphrag-code-and-data \
  --templama-source /absolute/path/to/TempLAMA_test_with_aliases.json
```

Outputs appear in `experiments/results/`.
Each query has saved retrieved claim IDs.
No script changes the original release.
The frozen protocol has no parameter tuning.
These are development evaluations, not a preregistered confirmatory study.

## Conditions

All conditions use the same BM25 scores.
The implementation uses k1=1.5, b=0.75, and positive Robertson IDF.
Ties use the original claim order.
All inference objects contain only text, timestamp, and claim ID.

- `bm25`: rank all claims observed by the query cutoff.
- `date_top5`: sort the first five BM25 results by descending date.
- `date_full_pool`: sort every observed claim by descending date.
- `exact_group_latest`: group identical extracted frame and subject features; keep each group's latest date.
- `direct_first`: use the earliest direct contradiction as each claim's end time.
- `direct_last`: use the latest direct contradiction as each claim's end time.
- `component`: connect the original latest edges; end each claim at its component's next changed extracted value.
- `component_latest`: keep each component's latest observed date.
- `oracle`: use annotated first-answer keys and values to compute eligibility.

The oracle is an explicit diagnostic.
It is not a source-set oracle.
The `direct_last` condition is an edge-timing ablation.
It is not the original paper's connected-component historical method.

## Primary source evaluation

`templama_source_set_results.json` uses every valid answer in each original TempLAMA source row.
It scores the unchanged predictions from `templama_predictions.jsonl`.
At a cutoff, each key uses its last observed source answer set.
This source snapshot remains in force until another observation.
This evaluation does not establish current real-world truth.

`hit1` measures correct evidence selection at rank one.
`hit5` measures whether any of five selected claims provides correct evidence.
Neither metric measures generated answers.
`stale_exposure5` measures any selected claim outside its own key's source answer set.
That metric includes irrelevant selected keys.

`templama_single_value_results.json` restricts query keys only.
Every observed source year must have exactly one answer.
The pool still contains all 747 released claims.

## Mechanism evaluations

`prefix_summary.json` compares full-corpus intervals with intervals built from each observed prefix.
Every comparison uses actual source-event times.
`*_prefix.json` records each changed claim membership.

`sensitivity_summary.json` summarizes single-link deletion interventions.
Each deleted link came from an actual matcher decision.
The scripts rebuild replacement latest edges after each deletion.
They add no artificial claims or false links.
The `false_pairs` subset uses gold labels only to classify the intervention afterward.

## Release checks

`release_integrity.json` checks all dataset and result hashes in the original manifest.
`detection_replay.json` reruns all ten detection datasets.
`pooled_detection_replay.json` reruns both released pooled experiments.
`cache_inventory.json` inventories saved model outputs.
It does not claim to rerun model inference.

`independent_engine_validation.json` compares the independent evaluator with the production certificate engine.
The saved check covers all ten released datasets.
