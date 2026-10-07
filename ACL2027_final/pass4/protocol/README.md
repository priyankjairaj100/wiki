# Pass 4: evidence and reader confirmation

This protocol tests the complete source-to-context interface.
It separates front-end retrieval gains from temporal policy effects.
The exact certificate remains a distinct outcome.

## Data and development choices

The source is the official TimeQA snapshot from the pass-3 manifest.
The development pool contains 32,332 passages from 740 articles.
The test pool contains 33,493 passages from 749 articles.
Every retrieval run searches its complete declared source pool.
No question receives an oracle article restriction.

Pilot tuning uses 176 questions from 50 articles.
Additional calibration uses 127 questions from 35 articles.
Choices may use their labels and source text.
The calibration articles stay outside development confirmation.
The 2,348 development questions and 830 human questions provide confirmation.
Earlier passes inspected results for both tracks.
Neither track is described as untouched test data.

The primary reader sample contains 60 human questions from 55 articles.
Selection uses a fixed identifier hash before pass-4 outcomes.
It does not condition on gold answers, extracted claims, or retrieved support.
All selected questions remain in the denominator.
Unparsed questions, empty contexts, and malformed responses receive no exclusions.

The separate reader diagnostic uses context differences only.
Select up to 24 human questions with different possible and guaranteed rendered contexts.
Use the primary sample seed plus `-diagnostic` to order identifiers.
Freeze this membership before generating any diagnostic answers.
Report its overlap with the primary sample.
This diagnostic measures sensitivity and cannot estimate population answer accuracy.

## Feature separation

Inference queries contain only `question_id` and `question`.
Identifiers remain uninterpreted join keys.
Their embedded article and relation names are prohibited features.
Source article titles are valid public source features.
A linker may match visible question words against the complete source title inventory.
It may not use the query's original article metadata.

Source extraction reads passage text, public titles, source order, and opaque passage identifiers.
It does not read questions, answer strings, annotations, labels, or benchmark histories.
Visible question text supplies query dates and retrieval terms.
Published annotation dates previously constructed the official template questions.
They do not separately enter inference.
Evaluation grouping sidecars and label files enter scoring only.

## Shared evidence and controls

All temporal methods share the same source units, bounds, ends, and directed pairs.
All methods share one strict relevance order for each query.
The latest-year comparator is the declared ranking exception.
Every condition receives five source units and at most 768 source-text whitespace tokens.
Titles, source-derived subjects, relations, and date metadata add text outside that source budget.
No extracted answer value is added.
Every reader condition uses the same prompt format and model settings.

The eight temporal conditions are:

1. No temporal filter.
2. Earliest date completion.
3. Midpoint date completion.
4. Latest date completion.
5. Outer interval control, including explicit ends and excluding cross-claim pairs.
6. Exact possible support.
7. Exact guaranteed support.
8. Latest-mentioned-year reranking within the common top 20 source units.

The original BM25 front end and its latest-year comparator provide two further reader controls.
These controls use the new common units and identical reader budgets.
They isolate ranking gains from extraction or context-budget changes.
Do not use pass-3 scores on different source units for this attribution.

The front-end comparison evaluates BM25, the selected new ranking, and both latest-year variants.
Each comparison uses identical new source units and the same no-filter policy.
The selected front end is fixed after calibration.
Retain all tried calibration variants and the selection criterion.
Choose the variant by calibration source-span recall.
Break equal recall by simpler features, then a fixed lexical variant name.
Do not tune title weights or ranking rules after confirmation scores appear.

Unknown source text remains available through a fixed fallback policy.
It is never labeled guaranteed.
A modeled excerpt may be rejected without deleting other text from its paragraph.
All substantive source words remain in disjoint indexed excerpts.

## Temporal semantics and source audit

Year, month, and day mentions define occurrence bounds at their stated precision.
A tenure range describes separate start and retirement events.
It never becomes one uncertain start interval.
Source ends use the declared half-open lifecycle convention.
Approximate or unbounded dates remain unknown unless the adapter states a valid semantic rule.
Planned contract or loan expiry does not establish an observed departure.
Different values alone do not establish replacement.

Audit extraction before comparative confirmation outcomes.
Choose at most 60 modeled records by seeded identifier hashes per source pool.
Also audit every accepted pair, or a fixed hash sample of 60 if more exist.
Stratify the claim audit by adapter rule when feasible.
Record literal grounding and semantic attachment separately.
Check holder, relation, date role, and retirement interpretation.
A date quote match alone does not establish correctness.
Report model-assisted review as such.
Keep unsupported and unclear decisions separate.

The certificate covers the supplied date model and fixed fallback policy.
It does not verify extraction correctness or reader answers.
Report modeled coverage beside the certificate rate.
Use all parsed contexts as the broad denominator.
Also report the subset containing modeled evidence.
Report all-fallback contexts separately.

## Outcomes and statistics

The primary retrieval outcome is exact annotated source-span recall at five units.
Credit requires the shown offsets to contain the complete annotated span.
A parent passage identifier alone gives no primary credit.
Secondary outcomes include annotated string recall and parent passage hits.
Annotations measure the supplied anchors, not newly verified entailment.

Reader outcomes use complete deduplicated answer lists.
Primary metrics are exact annotated answer-set equality and strict set F1.
Normalization uses Unicode NFKC, case folding, and word tokens.
It preserves articles.
Soft token F1 is secondary.
The frozen parser accepts one whole JSON object, optionally inside one code fence.
Malformed or truncated generations become empty answer lists with failure flags.
No gold-aware repair is permitted.

Use paired article-cluster bootstrap intervals with 2,000 resamples and seed 20261006.
Resample articles and retain every question within sampled articles.
Report percentage-point deltas and 95 percent percentile intervals.
The primary compiler contrast is possible support versus outer interval control.
The second compiler contrast is guaranteed support versus outer interval control.
Compare the selected ranking against original BM25 on identical units.
Also compare against the strongest prespecified latest-year ranking.
Report all prespecified contrasts, including negative or zero differences.
Treat additional comparisons as descriptive.

Report extraction counts, date parse rate, accepted pairs, and fallback fraction.
Report unit context differences and rendered source differences separately.
Report stable contexts at budgets 1, 3, 5, 10, and 20 on one fixed cohort.
Replay both constructed worlds for every reported unstable modeled context.
Report legal assignment checks and exact replay agreement.
Record answer changes separately from answer accuracy gains.

## Freeze and provenance

The reader membership is already frozen in `reader_sample_manifest.json`.
The algorithm freeze occurs after calibration and before confirmation inference.
Use `freeze_configuration.py` with every source, ranking, query parser, renderer, and model configuration file.
The freeze records exact code and input hashes.
The source and query files must remain unchanged during execution.
Any later change creates an explicit amendment and a new run identifier.
Never overwrite the original freeze or claim an amended run was preregistered.

Save all tried calibration results, final configurations, and exact commands.
Save reader requests, outputs, hashes, model revision, quantization, and runtime revision.
Deduplicate only byte-identical model requests.
Keep every logical question-method membership when a request is reused.
Preserve temperature, seed, token limit, and failure status.
Do not count reused prompts as new model generations.
