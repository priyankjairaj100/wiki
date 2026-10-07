# Fourth-pass revision notes

The central contribution is an exact decision about selected evidence under uncertain historical dates.
A stable context needs no finer dates within the supplied model.
An unstable context receives two legal timelines and the current support decisions that further evidence must resolve.

## What changed

| Component | Previous checkpoint | Current checkpoint |
| --- | --- | --- |
| Development source extraction | 481 modeled claims; 221 explicit ends | 792 claims; 445 explicit ends |
| Matched retrieval confirmation | 2,348 template questions | 2,348 template plus 830 human questions |
| Common ranking | Original BM25 | Pilot-selected title-aware residual BM25 |
| Ranking controls | Original lexical and recency controls | Ten matched conditions, including both original controls and title-aware recency |
| Context mechanism | 375 modeled template contexts | 417 modeled template contexts plus 90 human contexts |
| Alternative timelines | 69 context pairs; 138 assignments | 115 pairs; 230 assignments |
| Query execution | Full support masks | Lazy selection matching every parsed confirmation query |
| Reader | Qwen2.5-1.5B | Qwen2.5-3B with official pinned quantization |
| Primary reader cohort | 24 questions | 60 fixed questions across 55 articles |
| Separate diagnostic | Nine questions; two overlap the primary cohort | Eleven questions; no primary overlap |
| Research interface | Experiment runners | Reusable query command returning evidence, certificate, and alternative timelines |
| Release verification | Earlier-pass checks | Portable rescoring, table reconstruction, full context replay, and final execution audits |

These rows describe different checkpoints, not paired causal comparisons.
The current matched ranking contrasts use the same new source units and budgets.

## Current evidence

The selected ranking improves shown-span recall over original BM25 with recency by 13.32 points on template questions.
The corresponding human gain is 5.00 points.
Their paired 95% intervals are [10.80, 15.80] and [0.59, 9.21] points.
Title-aware recency reaches 63.59% recall on human questions.
It remains a reported comparator; confirmation results do not change the selected ranking.

Of 507 parsed contexts containing modeled evidence, 392 are stable.
All 115 remaining contexts have independently verified alternatives.
Lazy selection uses 2.92 and 2.70 temporal tests per modeled context on the two tracks.
The counts exclude relevance ranking and answer generation.
Six-ranking secondary analysis checks that the same certificate interface works across ranking variants.

The source audit and corpus-wide partition checks are separate.
Partition checks preserve every source word and every accepted pair endpoint.
The independent semantic audit accepts 52 of 60 sampled events.
Eleven accepted starts omit a termination stated elsewhere in their paragraphs.
Those judgments remain visible and do not alter the frozen experiments.

## Completed reader study

All 238 generations are complete, covering 710 method conditions across 71 distinct questions.
The primary selected ranking reaches 21.67% strict F1.
Original BM25 and original BM25 with recency reach 18.33% and 15.00%.
The prespecified recency comparison gains 6.67 points, with paired interval [1.59, 13.56].
All six temporal conditions reach 20.00% on this primary sample.

The separate eleven-question diagnostic selects contexts with possible/guaranteed disagreement.
Guaranteed and possible support reach 24.24% and 6.06% strict F1, respectively.
Their difference has interval [0.00, 40.00].
Six scored answer sets change; three changes have two valid responses.
The other three involve a response-format failure.
The release retains all raw responses and unchanged scoring.

## Theory and presentation

The paper now introduces a natural succession example before the equations.
The main proof explains why individual support remains easy while joint context membership can be hard.
Independent review corrected the construction wording for tied event dates.
Replay complexity now explicitly counts fallback excerpts.
A focused novelty review added the closest uncertain-ranking database work.
It keeps the novelty claim centered on exact temporal compilation and constructive certificates.

The architecture is a clean vector figure with editable SVG and Python sources.
Its fallback route joins ranked selection explicitly.
The diagram connects the system pipeline to stable and unstable context budgets.
The main prose uses short sentences, defined notation, and no em dashes.
Repeated explanations were removed to preserve space for results.

## Final pass

The last pass will repair the bounded source issues identified in `audit/source/PASS5_REPAIR_PLAN.md`.
It will preserve this frozen version and use a separate version for any revised extraction.
It will then complete the submission audit: venue instructions, bibliography, anonymity, final PDF, and release consistency.
The 2027 venue-specific requirements must be checked against the official instructions available at that time.
The current checkpoint retains all previous data, runs, and protocol history.
