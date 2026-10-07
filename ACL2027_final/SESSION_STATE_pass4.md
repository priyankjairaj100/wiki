# ACL 2027 revision: pass 4

Date: 2026-10-06. Current work: fourth session of at most five.
Status: both reader cohorts, retrieval, theory, source audits, and portable replay are complete.
The compiled paper has eight main pages and seventeen total pages. Limitations begin on page nine.
The release builder requires successful verification against the exact final manifest before packaging.

## Central story and current files

Title: **When Do Uncertain Dates Change Retrieval? Exact Certificates for Temporal Evidence**.
Current manuscript: `pass4/paper/main.tex`.
Do not resume from the older paper directories.
The source tree retains its prior checkpoint folder name locally; the new archive uses `ACL2027_pass4/`.

The contribution is an exact operational decision about a reader's selected evidence.
A fixed-ranked retriever either returns the same excerpts across every permitted date assignment or supplies two legal timelines with different contexts.
Two direct temporal witnesses per claim make that decision cheap and explainable.
Stable prefixes and necessary refinement decisions turn the guarantee into an actionable interface.

The title-aware ranking provides stronger evidence retrieval.
Its accuracy gains belong to the front end, not to the temporal certificate itself.
The paper's main novelty is not earliest invalidation, title linking, or generic possible/certain semantics.
Independent review found no antecedent for the exact two-witness boundaries within its focused primary-source search.
Whole ordered-answer certainty and uncertain ranking bounds are established prior work and are cited explicitly.

## Exact model and theory

Each modeled event has an independent unknown date x_c in [l_c,u_c].
The fixed directed gate G(d,c) records semantic replacement eligibility.
Replacement happens only when x_d>x_c; equal dates do not establish order.
Self-pairs are excluded, and the gate need not be transitive.

The compact boundaries are:
- p_c = min u_d over accepted d with l_d>u_c.
- r_c = min l_d over accepted d with u_d>l_c.
- Possible support on [a,b]: l_c<=b and a<p_c.
- Guaranteed support: u_c<=b and (a<=l_c or a<r_c).

Guaranteed support means every timeline supports the claim somewhere in the query window.
The supporting time may differ across timelines.
It does not require a common certainly active point.
Two records are sharp among subsets of direct witnesses.

Compilation takes O(n+m) for n modeled events, including hidden explicit ends, and m supplied pairs.
Pair discovery remains a separate source procedure.
The stored certificates use O(n) space; each support query takes O(1).
A source end reduces to a hidden replacement event when end.lower>start.upper.
This condition preserves the independent interval model.

For exact possible and guaranteed sets P,H, all fixed-ranked top-k contexts agree iff Top_k(P)=Top_k(H).
With fixed fallback set F, apply that equality to P union F and H union F.
Fallback text remains temporally unknown.
The equality is a general fixed-order eligibility fact; the temporal compiler provides its exact inputs.

If unresolved selected frontier U=Top_k(P union F) minus (H union F) is nonempty:
- Two full date assignments with different selected contexts can be constructed in O(n).
- Every stabilizing date refinement makes each current U claim guaranteed or impossible.
- This condition is necessary, not sufficient; new unresolved claims may enter later.
- It does not identify a minimum number of date fields to resolve.

Let N count all ranked excerpts, including fallback text.
Full context replay takes O(n+m+N), retaining the pair graph.
This explicit N term was corrected during the fourth-pass review.
Constructing a supporting world places accepted incoming replacements no later than the pivot or after its supporting query time.
It does not require unrelated events to satisfy that placement.

Arbitrary possible top-k membership is NP-hard when k is an input, even for a point query and bipartite gate.
The main Set Cover proof remains in the paper.
There is no fixed-k=5 hardness claim.
The first unresolved possible rank r yields a stable budget exactly for k<r.
Lazy selection checks candidates until k possible excerpts are selected, and guarantees only for selected modeled items.
Its query cost is O(j) for j examined candidates, excluding relevance ranking.

## Frozen source extraction

Adapter: `pass4/extraction/source_adapter.py`.
SHA256: e55a2981bc5e04f84e1534be37669f79860d54fe975f6df0921f0eca618cc74f.

Calibration covers 86 articles: 50 pilot articles plus 39 earlier source paths, with three overlaps.
There are 85 calibration articles with eligible development questions.
Final calibration contains 114 claims, 78 explicit ends, five succession starts, and three pairs.
Eleven source regression/integration tests pass.

Development: 32,332 paragraphs, 740 articles, 792 claims, 445 explicit ends, seven succession starts, three pairs.
Test: 33,493 paragraphs, 749 articles, 744 claims, 384 explicit ends, two succession starts, no pairs.
Development claims increase 64.7% over the previous 481.

The source partitions contain 33,433 development units and 34,480 test units.
Modeled fractions are 2.37% and 2.16%.
Every source word survives; no units overlap and no pair endpoints are rejected.
All three cross-claim pairs occur in calibration articles.
Confirmation therefore primarily exercises starts and explicit ends.

The independent semantic audit samples 60 of 678 development claims outside calibration by a frozen identifier hash.
It accepts 52 events, rejects five, and marks three uncertain.
Eleven accepted starts omit a paragraph-stated termination.
Of 29 sampled explicit-end records, 27 have accepted event grounding.
The audit is model-assisted, not human annotation or a recall estimate.
These outcomes do not change the frozen extraction.
Full records: `pass4/audit/source/`.

## Ranking and matching

Ranker: `pass4/retrieval/ranking.py`.
SHA256: bd898547382a12903b34656c4d06d518c63390efb68aec0fdbd46722066205dd.

The visible question links the longest exact title-token match from the public source inventory.
Linked article units receive priority, while every other global unit remains in the complete ranking.
The selected residual variant removes matched title-token types before BM25.
BM25 uses k1=1.5 and b=0.75 and includes source titles.
No article ID, hidden relation, answer, or span enters ranking.
Question IDs are opaque join keys.

The 176-question pilot selects title_residual among six variants.
Pilot span recall: original BM25 38.64%; original recency 54.83%; selected title_residual 67.23%.
Confirmation outcomes do not change that selection.
Ranking integrity checks cover full permutations, metadata perturbations, ID remapping, blocked label access, and repeated runs.

Runner: `pass4/pipeline/run_matched.py`.
Protocol: `pass4/protocol/config.json` and original 27-file `ALGORITHM_FREEZE.json`.
Ten conditions share the source units and budgets:
no filter; earliest, midpoint, latest completion; interval control; possible; guaranteed;
title-aware recency; original BM25; original BM25 with recency.

Each context has five excerpts and at most 768 whitespace source words.
Source titles, bounds, tags, and source-derived subject/relation metadata add prompt text.
No extracted answer value is inserted as metadata.
This metadata amendment precedes all completed fourth-pass QA generations.
All original text offsets remain auditable.
Unmodeled source text follows the same fallback policy in every condition.

## Complete retrieval results

The confirmation tracks contain 2,348 template questions from 644 articles and 830 human questions from 251 articles.
They have previously inspected outcomes and are not described as untouched tests.
The complete source pools are searched, with no gold article restriction.
Labels enter scoring only.

Shown-span recall, template / human, percentages:
- Original BM25: 37.84 / 43.90.
- Original BM25 with recency: 52.98 / 52.39.
- Selected title-aware no filter: 66.30 / 57.39.
- Earliest completion: 66.84 / 57.87.
- Midpoint completion: 66.56 / 57.75.
- Latest completion: 66.48 / 57.75.
- Interval control: 66.73 / 57.75.
- Possible support: 66.73 / 57.75.
- Guaranteed support: 66.62 / 57.87.
- Title-aware recency: 65.33 / 63.59.

Primary paired article-cluster bootstrap: 2,000 resamples, seed20261006.
Selected title-aware versus original recency: +13.32 points, CI[10.80,15.80], on template questions.
The human gain is +5.00, CI[0.59,9.21].
Title-aware recency improves human recall by +11.20, CI[7.52,15.19], over original recency.
Independent per-question scoring matches all ten primary metrics exactly.
Independent interval sampling uses a different implementation; the paper consistently reports primary intervals.

Modeled contexts are parsed possible contexts containing at least one modeled claim:
- Template: 2,296 parsed; 417 modeled; 313 stable; 104 unstable; 1,879 all-fallback.
- Human: 813 parsed; 90 modeled; 79 stable; 11 unstable; 723 all-fallback.
- Combined: 3,109 parsed; 507 modeled; 392 stable; 115 unstable.

All 230 complete assignments replay independently.
All115 counterworld pairs change the rendered source excerpts.
Exclusion mechanisms:75 retirement cases and40 late starts.
Frontiers:100 single claims,14 pairs,one triple.

Same fixed modeled cohorts, stable counts for budgets1/3/5/10/20:
- Template417:375/322/313/309/305.
- Human90:87/81/79/74/66.
All15,545 prefix-equality checks pass.

The lazy selector matches full masks on all3,109 parsed queries.
Modeled template contexts average5.26 candidates and2.92 temporal tests.
Modeled human contexts average5.17 candidates and2.70 tests.
Do not interpret these counts or microbenchmarks as end-to-end reader speedups.

A secondary six-ranking certificate analysis was declared after confirmation, before its own label-free analysis.
It preserves the main ranker and reports both variant-specific and fixed cohorts.
Title-aware recency certifies146 of166 modeled human contexts as stable.
Mean temporal tests across variants range2.55–3.00 when rounded.

## Completed reader study

Official model: Qwen/Qwen2.5-3B-Instruct-GGUF, Q4_K_M.
Revision:7dabda4d13d513e3e842b20f0d435c732f172cbe.
Weight SHA256:626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d.
License:Qwen Research License, not Apache2.
Runtime:llama.cpp b11435, commit43fe9c64281ef735046adc025e9e7559a1f659a5, MIT.

The primary cohort is fixed at60 questions/55articles,600 conditions,193 distinct requests.
The diagnostic contains all11 human possible/guaranteed context differences from9articles,110conditions,45 requests.
There is no question or request overlap.
The cohorts share four articles.
Total:71questions across60articles,710conditions,238 completed actual requests.
The diagnostic is a context-sensitivity slice, not an independently sampled accuracy benchmark.

Final settings:four threads,2,048 context tokens,batch and microbatch512,polling disabled,temp0,seed1729,max output96.
No prompt cache or JSON grammar.
All238 prompt reservations pass token preflight; largest input1,311tokens; largest reservation1,423.
Two earlier QA runtime attempts completed zero responses and remain archived.
Generic prompts selected the final resource settings before completed QA outcomes.
Original freezes remain unchanged; RESOURCE_AMENDMENT.json links the final runner and settings without hash exemptions.
A stale explanatory eight-thread sentence remains in the archived final freeze; executed numeric settings and amendment specify four.

Do not score incomplete cohorts.
The exact parser accepts a full JSON object or one code fence, with no narrative substring repair.
Invalid types, indices, and truncations yield empty answers and remain in denominators.
Normalization uses NFKC, case folding, word tokens, article preservation, and deduplicated sets.
All45 paired method contrasts are retained.

Scoring and execution commands are in `pass4/protocol/FINAL_CHECKS.md`.
Presentation generator:`pass4/pipeline/build_reader_results.py`.
Final outputs belong in `pass4/protocol/reader_primary_scored/` and `reader_diagnostic_scored/`.
Primary results: selected no-filter and selected recency reach 21.67% EM and strict F1.
All six temporal conditions reach 20.00%; original BM25 reaches 18.33%; original recency reaches 15.00%.
Selected no-filter versus original recency: +6.67 points, paired interval [1.59, 13.56].
Versus original BM25: +3.33 points, interval [-4.92, 11.86].
Primary earliest/latest and possible/guaranteed answer changes: zero of 60; zero among 38 jointly parsed pairs.

Diagnostic: earliest and guaranteed reach EM18.18%, strict F1 24.24%.
Midpoint, latest, interval, and possible reach EM0%, strict F1 6.06%.
Original BM25 reaches EM/F1 9.09%; no-filter and both recency controls reach zero.
Guaranteed-minus-possible strict F1 difference: +18.18 points, paired interval [0.00, 40.00].
Possible/guaranteed and earliest/latest each change six of eleven scored answer sets.
Three changes occur among six jointly parsed pairs; three involve parse failure.
The three valid changes are Maher (role phrase to annotated employer), Atlético (named coach to abstention), and Clark (one role to another).
Only the Maher change gains strict F1 among these valid pairs.
Do not describe all three as factual corrections.
The presentation source audit rejects Maher as a clean main example because the extracted employer name is truncated.

Primary parsing: 118 valid and 75 failures among 193 distinct generations.
Diagnostic parsing: 32 valid and 13 failures among 45 generations.
Combined failures: 60 JSON-format failures, six invalid citation lists, and 22 length-limit responses.
All 88 remain scored as empty answer sets.
Actual generation wall time is 5,856.51 seconds (97.61 minutes).
There are 160,360 prompt tokens and 11,401 completion tokens.
`pass4/inference/RUNS.md` and `provenance/completed_runs.json` record exact execution provenance.

Independent reconstruction matches every one of the 710 conditions and all 45 contrasts in each cohort.
`pass4/protocol/reader_primary_change_audit.json` and `reader_diagnostic_change_audit.json` separate parse-status changes.
`pass4/pipeline/paper_reader_results.json` contains presentation values for both complete cohorts.

## Presentation and verification

The current draft has eight main pages; limitations start on page9.
The title and abstract lead with consequential evidence uncertainty.
The Warburg source example precedes the equations.
Annual snapshot semantics and earlier controls are outside the main body.
Main prose uses short sentences, defined notation, and no em dashes.

Architecture source:`pass4/pipeline/draw_architecture.py`.
Vector outputs:`pass4/paper/figures/architecture.pdf` and`.svg`.
The fallback route correctly enters ranked selection.

Independent reviews are in `pass4/audit/manuscript`, `novelty`, `bibliography`, `source`, and`examples`.
The new uncertain-ranking reference is Feng,Glavic,Kennedy,PVLDB2023.
TIME2017 is described as certainty of entire ordered answers.
Re3 author order follows its authoritative PDF, correcting the landing metadata.

The Helen Clark example is a retrieval-window boundary, not an answer-correction claim.
Its Conservation endpoint ranges fromJanuary1toJanuary31,1989.
No diagnostic alternative combines a cleaner question predicate with a relevant, sound pivot.
The all-eleven presentation audit reads no answers or generated outcomes.

Portable full replay succeeds from a renamed folder:
31,780 method contexts,230 counterworlds,15,545 budget equalities.
Default `python reproduce.py` verifies hashes, source tests, independent scores, reader execution, and generated tables.
`--full` additionally replays complete retrieval.
Neither starts inference or downloads weights.
Final default verification must use the completed release manifest.

## Final session priorities

1. Start from this fourth-pass checkpoint and its complete reader result card.
2. Implement the bounded source repairs in `pass4/audit/source/PASS5_REPAIR_PLAN.md` as a distinct pass-5 version.
   Treat inspected audit articles as calibration and record a fresh source audit outside them.
   Reuse reader generations only for identical complete request hashes and the same model/runtime/decoder.
3. Verify current official ACL2027 submission instructions and template availability.
4. Recheck paper claims, bibliography, anonymity, limitations/ethics requirements, and exact eight-page main body.
5. Inspect the finished PDF, especially first three pages, all tables, and page8.
6. Confirm every paper number against saved results and every submitted artifact against its manifest.
7. Deliver final Overleaf, PDF, and source/run bundles. Separate a blinded submission supplement from the private historical archive if needed.

No further parameter tuning should be called held-out evaluation.
Do not rerun unchanged valid baselines or settled constructed theory tests just to create activity.
The source semantic audit identifies the remaining empirical weakness; any future extractor changes require a distinct version and fresh recorded comparison.
Keep metadata-only patches separate from frozen run dependencies.
