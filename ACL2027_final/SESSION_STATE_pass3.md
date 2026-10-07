# ACL 2027 revision: pass 3

Date: 2026-10-06. Completed sessions: 3 of at most 5.
Status: substantial research checkpoint with actual source-to-reader runs. Final submission audit remains for pass 5.

## Central story

Title: When Do Uncertain Dates Change Retrieval? Exact Certificates for Temporal Evidence.

The strongest contribution is an exact operational decision about a reader's evidence.
A fixed ranking either returns the same context under every permitted date assignment, or the compiler supplies two replayable timelines with different contexts.
The contribution is not a new earliest-invalidation rule or a demonstrated accuracy improvement.

The existing two-witness compiler remains the foundation.
For independent start bounds [l_c,u_c] and a fixed directed replacement gate:
- p_c = min u_d over accepted d with l_d > u_c.
- r_c = min l_d over accepted d with u_d > l_c.
- Possible support on [a,b]: l_c <= b and a < p_c.
- Guaranteed support: u_c <= b and (a <= l_c or a < r_c).
Guaranteed support means every timeline has some supported time within the window.
It does not require the same supporting point across all timelines.

## New theory

Files: pass3/theory/lifecycle.py, refinement.py, proofs, and test logs.

1. Explicit source ends reduce to hidden direct replacement events when end.lower > start.upper.
   Overlapping start/end bounds remain unmodeled, since their validity requires correlated constraints.
2. For P possible and H guaranteed support, all top-k contexts agree iff Top-k(P)=Top-k(H).
3. Let U = Top-k(P) minus H. Every stabilizing date refinement must make every current U claim guaranteed or impossible.
   This is necessary, not sufficient; new unresolved items can enter after earlier ones disappear.
4. From bounds and the compact certificate alone, construct two complete date assignments in O(n) time when unstable.
   Full context replay retains the accepted graph and costs O(n+m). Compact support output is O(n).
5. Arbitrary possible top-k membership is NP-hard when k is an input, even for a point query and a bipartite gate.
   Reduction from Set Cover: variables [1,3], B+1 element copies at 0, candidate at 0, query 2.
   Rank variables/copies above candidate; accepted pairs encode membership in each set.
   The candidate enters iff at most B active set variables cover all elements.
   No fixed-k=5 hardness claim.
6. First unresolved rank r in the possible order gives an exact stable budget: stable for k<r, unstable for k>=r.

Independent theory audit found no flaw in the stated model.
Independent checks: 1,300 counterworld pairs across 12,925 enumerated worlds; 1,536 reduction instances.
The implementation tests include 2,274 constructed worlds, 4,042 necessary frontier decisions, and 1,024 reduction cases.
These are constructed correctness checks, not corpus accuracy scores.

## Source protocol and frozen validation

Source corpus: 32,332 natural TimeQA paragraphs from 740 development articles.
The question pool removes the eight published dev/test article overlaps.
Initial eligible development questions: 2,651.
Pilot: 50 articles, 176 questions, selected by a fixed hash.
Validation after calibration exclusions: 644 articles, 2,348 questions.
35 extra validation articles / 127 queries were removed before outcomes.
Reasons include gold-anchor source inspection and separately source-cue-selected succession calibration.
The original split and exact exclusion records are preserved.
Rule development inspected some development source text outside the 50 pilot articles, without using QA outcomes.
Do not call this corpus wholly unseen during rule development.

Extraction reads source text/title/order only. Query parsing reads the visible question.
Official annotation dates construct the template questions; they do not enter the source extractor.
Answers and spans enter scoring only.
The common pool is complete, with no oracle article restriction.
BM25 k1=1.5,b=.75 includes article titles.
All temporal methods share the same strict ranking, units, bounds, ends, pairs, and budgets.
Latest-mentioned-year top20 is an explicitly separate ranking comparator.

Eight policies: no filter; earliest/midpoint/latest completion; outer interval control; possible; guaranteed; latest-year ranking.
Five source units, at most 768 source-text whitespace tokens. Metadata is extra prompt text.
Unparsed text stays as unknown fallback, never labeled guaranteed.
All source words survive the modeled/fallback partition. Whitespace and punctuation-only gaps need not survive.

Frozen primary adapter: pass3/extraction/source_adapter.py
SHA256: 2424a76fdcfe08330fddc45853969406f1784bb2f1aad00d90499d79d2a8d185.
Full development: 481 modeled claims; 221 have explicit ends; 32,976 units; 1.46% modeled units; zero cross-claim pairs.
Main natural run therefore exercises starts and explicit ends, not cross-claim replacement superiority.

## Completed natural results

Validation query time parses for 2,296/2,348 questions.
Parsed possible contexts containing at least one modeled unit: 375.
306/375 are stable (81.60%); 69 are unstable.
All 69 have two legal full assignments; all 138 replays produce different source contexts and replay exactly.
47 excluding worlds retire the pivot by query start; 22 start it after query end.
67 frontiers contain one claim; two contain two claims.
All-fallback parsed contexts: 1,921. Their stability is a fixed-policy fact, not temporal understanding.

Same fixed 375-query cohort, unit budgets before text truncation:
- k1: 346 stable, 92.27%.
- k3: 320, 85.33%.
- k5: 306, 81.60%.
- k10: 304, 81.07%.
- k20: 299, 79.73%.
11,480 direct equality checks agree with the first-unresolved-rank rule.

Validation span recall: no filter38.49%; earliest39.20%; midpoint39.07%; latest39.03%; interval39.07%; possible39.07%; guaranteed39.15%; latest-year53.51%.
Possible and interval masks/contexts coincide because no cross-claim pairs are accepted.
Guaranteed gain over interval0.085points, CI[-0.085,0.259].
Latest-year gain14.44points, CI[12.05,16.86].
No accuracy-superiority claim for the compiler is supported.

A deterministic reproduction correction sorts BM25 token accumulation and stops after selecting five accepted units.
All20,192 pilot+validation contexts match exactly. Original code is retained as run_matched_v1.py.

## Actual reader inference

Official Qwen/Qwen2.5-1.5B-Instruct-GGUF Q4_K_M.
Revision91cad51170dc346986eccefdc2dd33a9da36ead9.
Weight SHA2566a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e.
llama.cpp b11435, commit43fe9c64281ef735046adc025e9e7559a1f659a5.
CPU only, eight threads, temperature0, seed1729, prompt caching disabled,96max generated tokens.
No GPU or external API key was available. No paid cloud job was submitted.

Primary sample:24 fixed questions/21articles,192logical conditions,52unique actual generations.
All parse successfully. All methods29.17%exact annotated answer set and31.94%strict set F1.
Temporal completions and masks yield identical answers here.
Latest-year changes14answers but has the same aggregate strict score.

Completion-sensitive diagnostic:all9pilot questions,72conditions,28unique prompts.
Six prompts reused from primary;22additional actual generations.
Two questions overlap the primary cohort:31distinct questions and74actual reader generations overall.
Earliest vs latest changes4/9answers; possible vs guaranteed also4/9.
All methods33.33%strict set F1. This shows sensitivity, not correctness improvements.
Some changed outputs are semantically weak; do not call them corrected answers.

Strict normalization uses Unicode NFKC, case folding, word tokens, article preservation, and deduplicated answer sets.
JSON parsing was frozen before responses; no narrative substring repair or gold-aware parsing.
All raw prompts, outputs, request hashes, timing, and scoring records are preserved.

## Source succession calibration

30 paragraphs from28articles selected by source succession cues, not QA outcomes.
Separate deterministic parser: pass3/extraction/succession_rules.py.
Five dated starts, three pairs, two articles (Warburg Institute and National Council of French Women).
Model-assisted independent source review accepts those records; nine parser tests pass.
The automatic Warburg outputs reproduce stable top1 and unstable top2 for an illustrative1954--mid1955window.
The query and ranking are illustrative, not benchmark data.

Learned extraction V1 planned30, stopped after6completed:41records all omit required quotes.
Schema-constrained V2 planned30, stopped after6completed:46records,45literal grounding failures.
The remaining literal-grounded record links wrong holders/date and fails semantic review.
Zero learned claims/pairs accepted. Interrupted seventh responses were not retained.
Partial manifests, six-input replay files, raw outputs, audits, and stop reasons are included.
Do not relabel these as full30runs or held-out extraction scores.
The small all-at-once extraction interface is not viable.

## Presentation

New exact vector architecture: pass3/paper/figures/architecture.pdf and .svg.
Editable source: pass3/data/draw_architecture.py.
The paper now leads with consequential context uncertainty, then source semantics, exact support, constructive refinement, and the complexity boundary.
All main prose uses short sentences and no em dashes.
Source-only validation and real reader results replace the previous prospective integration claims.
Current limitations and failed exploratory extraction sit outside the main body.

## Remaining two sessions

Pass4: strengthen empirical source coverage and practical relevance without changing frozen validation results.
A better retrieval front end can use public question/title linking plus the strong latest-year comparator.
Apply all temporal policies to the same improved ranking, with a fresh frozen protocol.
The main improvement needed is source-grounded extraction breadth, not more exhaustive tests of the settled theory.
Try decomposed source extraction and clause-level role/date attachment rather than the failed all-at-once1.5Bprompt.
Use the audited succession parser as a minimal working interface.
A stronger local model may help but CPU inference is slow; do not launch broad runs before a source-grounding pilot.
Do not use gold histories as extractor inputs.
The published TimeQA test baselines have already been inspected; label future use confirmation, not untouched test.
TempReason was downloaded as a possible independent source, but many natural contexts omit the answer.
Keep its templated fact_context separate from natural evidence and audit source support before selecting a task.

Pass5: final independent review, novelty check against current papers, ACL2027 policy/template check, eight-page layout, anonymity, bibliography, complete source/run audit, and submission bundle.
No claim of guaranteed acceptance or final submission readiness before those gates.

## Resume

Start from pass3/paper and this state.
Read pass3/protocol/RESULTS.md, PAPER_REVIEW.md, and INDEPENDENT_THEORY_REVIEW.md.
Use pass3/pipeline/README.md and pass3/inference/RUNS.md for commands.
Prior pass2 results and original archives remain in the release.
Do not rerun valid unchanged baselines just to create activity.
Do not include inference/cache model weights in Library bundles; pinned download scripts restore them.
