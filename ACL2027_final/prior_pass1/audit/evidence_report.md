# Evidence audit and new experiments

The new method compiles each claim's earliest direct contradiction.
It preserves the original current mask.
It also preserves past eligibility when later evidence arrives.

All new experiments use fixed BM25 scores.
No experiment uses a model generation.
Inference receives only claim IDs, text, and timestamps.
Gold labels create questions and score retrieved evidence.
The protocol is a development evaluation with no parameter tuning.

## Main source-grounded results

The pool contains all 747 released TempLAMA claims.
The evaluation contains 447 historical probes and 300 current probes.
Each probe uses the last observed source answer set at its cutoff.
All source answers are valid targets.
This evaluates the supplied snapshot history.
It does not assert current real-world truth.

| Condition | Historical Hit@1 | Historical stale exposure@5 | Current Hit@1 | Current stale exposure@5 |
|---|---:|---:|---:|---:|
| BM25 | 78.08% | 70.92% | 23.33% | 100.00% |
| Date within BM25 top five | 54.36% | 70.92% | 60.67% | 100.00% |
| Global date sort | 28.41% | 0.00% | 12.67% | 0.00% |
| Exact extracted key plus date | 98.43% | 16.55% | 88.33% | 28.33% |
| Text-CC | 97.54% | 1.79% | 94.67% | 16.33% |
| Earliest direct witness | 98.21% | 1.79% | 94.67% | 16.33% |

Hit@1 measures evidence selection.
It does not measure a generated answer.
Stale exposure includes any selected claim outside its own key's source answer set.
A global date sort can achieve low stale exposure by selecting irrelevant evidence.

The current improvement over exact extracted keys is 6.33 percentage points.
Its 95% cluster bootstrap interval is [3.33, 9.33] points.
The historical difference against Text-CC is 0.67 points.
Its interval is [-0.23, 1.67] points.
The historical difference against exact extracted keys is -0.22 points.
Its interval is [-1.83, 1.53] points.
These results do not establish general accuracy superiority over Text-CC.

`Text-CC` is a text-only reconstruction of the original component design.
It derives value signatures from extracted text features.
It does not use the original interval code's gold values.
The saved method name is `component`.

Files:

- `work/experiments/results/templama_source_set_results.json`
- `work/experiments/results/templama_source_set_predictions.jsonl`
- `work/experiments/results/templama_predictions.jsonl`

## Past-state stability

Each comparison uses a real source-event cutoff.
We compare full-corpus intervals with intervals rebuilt from the observed prefix.

| Dataset | Event cutoffs | Text-CC mismatch cutoffs | Changed memberships | Maximum changes at one cutoff | Direct mismatches |
|---|---:|---:|---:|---:|---:|
| TempLAMA | 11 | 8 | 21 | 4 | 0 |
| Wikipedia leads | 42 | 27 | 50 | 4 | 0 |
| Wikidata | 27 | 0 | 0 | 0 | 0 |
| Rendered Wikidata prose | 27 | 0 | 0 | 0 | 0 |
| Wikipedia CEO subset | 19 | 0 | 0 | 0 | 0 |
| Curated real-world transitions | 41 | 0 | 0 | 0 | 0 |

TempLAMA Text-CC changes six historical top-ranked claims after future records become available.
Its correct historical selections fall from 439 to 435 under first-answer labels.
The direct method selects 439 correct claims under those labels.

Wikipedia leads change eight historical selections.
The total correct selections remain 81 of 97.
Thus equal accuracy can hide unstable past evidence.

Files:

- `work/experiments/results/prefix_summary.json`
- `work/experiments/results/*_prefix.json`

## Local effects of link errors

Each intervention deletes one observed matcher link.
No intervention adds claims or invented links.
The procedure rebuilds the latest-edge graph after deletion.
It also selects a replacement latest edge when one exists.

| Dataset | Observed links | Largest Text-CC endpoint change | Largest direct endpoint change | Cross-key links | Largest cross-key Text-CC change |
|---|---:|---:|---:|---:|---:|
| TempLAMA | 698 | 3 claims | 1 claim | 46 | 3 claims |
| Wikipedia leads | 273 | 8 claims | 1 claim | 96 | 3 claims |
| Wikidata | 452 | 4 claims | 1 claim | 0 | 0 claims |

Direct certificates localize each link change to its older claim.
This result concerns the number of affected claims.
It does not claim fewer total membership changes across all times.

The saved `false_pairs` classification uses the released first-answer labels.
Use `cross_key_pairs` or `all_pairs` for the paper's intervention table.

Files:

- `work/experiments/results/sensitivity_summary.json`
- `work/experiments/results/*_sensitivity.json`

## Original TempLAMA source audit

The released builder selects the first listed answer from each year.
It collapses consecutive repetitions of that answer.
The resulting 747 claims exactly match the supplied release.

The 300 selected keys contain 2,677 original yearly rows.
Of these, 613 rows contain multiple valid answers.
A total of 245 keys contain at least one such year.
The builder records 447 first-answer transitions.
In 153 transitions, the prior answer remains valid in the new source row.
These transitions span 130 keys.

Only 55 keys have one answer in every observed year.
Their current results are 50/55 for direct witnesses and 46/55 for exact extracted keys.
Their historical results are 55/57 and 57/57, respectively.
The full 747-claim pool remains unchanged for this slice.

The official release and alias mirror contain 34,963 matching record IDs.
Their complete answer-QID sets, query texts, and first-answer QIDs match exactly.
The source-grounded evaluation therefore uses the official benchmark's answer sets.

Files:

- `work/experiments/results/templama_source_audit.json`
- `work/experiments/results/templama_source_rows.json`
- `work/experiments/results/templama_source_transitions.json`
- `work/experiments/results/templama_official_source_validation.json`
- `work/experiments/results/templama_single_value_results.json`

## Released evidence and limits

All dataset and result hashes in the released manifest pass.
All ten detection datasets were rerun.
All seven cached detection cards match the new detection runs.
Both released pooled detection cards also match.

| Dataset | Claims | Annotated keys | Conflicting date ties | Recurrent-value keys | Replayed detection F1 |
|---|---:|---:|---:|---:|---:|
| Wikidata | 208 | 73 | 9 | 11 | 1.0000 |
| TempLAMA | 747 | 300 | 0 | 8 | 0.9764 |
| Rendered Wikidata prose | 208 | 73 | 9 | 11 | 1.0000 |
| Wikipedia leads | 132 | 35 | 0 | 2 | 0.9412 |
| Wikipedia CEO subset | 26 | 12 | 0 | 0 | 0.8800 |
| Curated real-world transitions | 56 | 20 | 0 | 2 | 1.0000 |
| Generated FreshRAG | 304 | 100 | 0 | 0 | 1.0000 |
| Synthetic multihop | 277 | 120 | 0 | 0 | 0.9544 |
| Curated real multihop | 67 | 19 | 0 | 1 | 1.0000 |
| LLM-normalized Wikidata prose | 208 | 73 | 9 | 11 | 0.3699 |

Rendered variants share source facts.
They are not independent benchmark replications.
FreshRAG and synthetic multihop are generated data.
They should not support the main benchmark claim.

The original extractive reader returns the top claim's annotated `value` field.
Its score measures top-ranked annotated value selection.
It does not measure text extraction.

The original historical script selects a component through the first gold claim.
The original interval code also reads annotated values.
Its historical result measures timeline alignment under a gold anchor.
The new full-pool evaluation uses neither input.

Some Wikipedia leads omit their annotated relation.
For example, the Bill Gates lead does not state his Microsoft CEO role.
Those labels require a support audit before they support a strong natural-prose claim.

The cache contains 4,995 Qwen outputs and 1,828 OpenAI outputs.
The cache inventory verifies file integrity and counts.
It does not rerun generation or reconstruct every historical prompt.

Files:

- `work/experiments/results/release_integrity.json`
- `work/experiments/results/detection_replay.json`
- `work/experiments/results/pooled_detection_replay.json`
- `work/experiments/results/cache_inventory.json`

## Independent implementation check

The evaluation compiler and production engine were developed separately.
Their earliest endpoints match on every claim across all ten released datasets.
The production engine strips gold fields before compilation.

The experiment compiler also checks every source-event cutoff.
Its intervals exactly equal the direct pairwise eligibility definition.
Every original current stale mask is reproduced.

File: `work/experiments/results/independent_engine_validation.json`.

## Reproduction

The scripts require Python 3.11 and the standard library.
They load the original parser from the supplied source directory.
No script changes that directory.

```sh
python work/experiments/run_all.py \
  --source inputs/supplement/wikigraphrag-code-and-data \
  --templama-source work/external/TempLAMA_test_with_aliases.json
```

Detailed condition definitions appear in `work/experiments/README.md`.
