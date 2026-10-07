# Full TempLAMA evaluation

This evaluation uses every row from the original TempLAMA test source.
It includes every answer in each source row.
It does not treat a changed first answer as a retirement.

## Reproduce

Run these commands from the project root:

```bash
python pass2/evaluation/freeze_split.py
python pass2/evaluation/run_full_benchmark.py
python pass2/evaluation/audit_ambiguity.py
python pass2/evaluation/audit_intervals.py
python pass2/evaluation/audit_quality.py
python pass2/evaluation/verify_matched_policies.py
python pass2/evaluation/summarize.py
```

The recorded run uses Python 3.12, NumPy 2.3.5, and SciPy 1.17.0.
The requirements file pins these library versions.
The original project supplies the unchanged lexical predicate.
The baseline package supplies the official Graphiti policy code.

## Split

The source contains 34,963 rows and 4,057 source keys.
Rendering all answers produces 45,866 positive observations.
The 300 previously selected keys remain development data.
A fixed SHA-256 rule partitions the other keys before evaluation.
Development contains 764 keys and 6,534 rows.
Test contains 2,993 keys and 25,752 rows.
No method chooses the test keys from its results.
The split manifest records every assignment.

## Inference input

An observation contains only an opaque identifier, text, and answer year.
The answer year comes from the benchmark query.
It is not a document publication time or an arrival time.
The parser uses the nine public benchmark templates.
It extracts a textual subject, a relation template, and a textual value.
It does not receive source keys, relation IDs, or answer IDs.
Questions contain the original template with its answer blank removed.
Evaluation uses each actual source year.
It does not create targets after the last source observation.
Every method sees the same full observation pool.

## Methods

- BM25 ranks all observations available by the question year.
- BM25 recent tie ranks equal scores by recent source year.
- Date top-five reorders the first five BM25 observations.
- Date full-pool orders all available observations by source year.
- Age policies multiply BM25 scores by exponential age weights.
- The age grid contains half-lives of 0.5, 1, 2, 5, 10, and infinity.
- Development selects the age policy using mean key-level Hit@1.
- The original earliest predicate uses the unchanged source matcher.
- The original latest-witness policy uses the last matched witness.
- The Graphiti policy executes verified upstream temporal code.
- Graphiti receives the same text-parsed slots and values.
- This condition tests a policy kernel, not the complete Graphiti system.
- Exact latest-batch retains every observation in each slot's latest year.
- Query latest-batch first matches the textual slot and retains all latest-year ties.
- Query latest-single retains only the highest-ranked observation from that batch.
- Query history-union keeps all earlier observations for the matched slot.
- Query history-distinct keeps one recent observation per textual value.
- The development quota keeps recent distinct values using a relation-specific quota.

The quota equals the largest source answer count observed during development.
An observed maximum does not establish a real-world capacity constraint.
This quota condition is a retrieval heuristic.

## Metrics

Hit@1 and Hit@5 require the correct source key and an accepted answer ID.
Value recall measures distinct accepted answers represented in five retrieved observations.
Candidate recall uses the complete retained candidate set.
Valid-value suppression measures accepted answers missing from that candidate set.
Stale-value exposure requires a target-key value absent from the current source label.
Wrong-key Hit@1 errors remain separate from stale-value exposure.
These metrics assess evidence selection.
They do not assess generated answers.

A separate diagnostic checks unsupported values for other retrieved keys.
That diagnostic uses each key's most recent observed source label.
It does not establish real-world invalidity between source observations.

## Source semantics

The source gives positive annual answers and benchmark labels.
Multiple annual answers can reflect succession within one year.
They do not necessarily describe simultaneous facts.
It does not give explicit retirement events.
A missing answer therefore creates no inference event.
Latest-batch is a strong snapshot retrieval policy.
Its success does not prove semantic invalidation from positive observations.

The source audit calls differences between label sets additions and removals.
Those names describe benchmark labels only.
The audit separately measures retained values and recurring values.

The parser merges six textual slots across thirteen source keys.
These source entities have identical question text.
The ambiguity audit preserves these records and lists their source identifiers.
The main evaluation does not remove these difficult cases.

## Outputs

`predictions.jsonl` contains each evaluated query and its retrieved identifiers.
`observations.jsonl` contains only inference-visible observations and parsed text.
`evaluation_labels.jsonl` stores scoring labels separately.
`cluster_intervals.json` contains confidence intervals from 5,000 key-cluster resamples.
`source_audit.json` records coexistence, label changes, and recurrence counts.
`run_manifest.json` records file hashes.
