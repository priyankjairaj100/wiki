# ACL 2027 revision: pass 1

Date: 2026-10-06.
Status: research revision checkpoint, not submission-ready.
Prompts used: 1 of at most 5 requested sessions.

## Objective

Produce a strong eight-page ACL long paper.
Deliver an Overleaf bundle, complete source, and reproducible runs.
Use simple English and a contribution-first structure.
Preserve valid old results without inventing new model runs.

## What changed

The original current-answer story overlaps Graphiti, MemStrata, and Re3.
The new draft studies temporal evidence stability under imperfect pair decisions.
Graphiti already uses earliest direct contradiction times.
The draft credits that mechanism.
Its candidate contribution concerns exact compilation, prefix consistency, and bounded influence.

The source ZIP differs from the submitted PDF.
All original table files were stale.
New tables now come from result files.
The architecture figure now uses editable vector graphics.
The document uses the official ACL review format.

## Implemented and checked

- Direct-witness compiler with one boundary and one witness per claim.
- Complete posting index for the supplied pair gates.
- Timestamp batches that preserve simultaneous claims.
- Current and historical retrieval filters.
- Exactness proofs for every cutoff.
- Prefix consistency for eligibility masks under later-dated additions.
- One-pair influence bounds for masks and fixed rankings.
- Counterexample showing unbounded component amplification.
- Full-pool BM25 comparisons with exact extracted keys and Text-CC.
- Complete-source TempLAMA scoring.
- Original detection and integrity replays.
- Independent compiler review.

All 13 compiler tests passed.
Exhaustive checks covered 2,233 packaged claims and 692 cutoffs.
These counts include archive variants and correctness fixtures.
They do not represent independent natural benchmark examples.
A separate two-clock prototype passed eight correctness tests.
It has no benchmark result and no established novelty claim.

## Critical source correction

The old TempLAMA builder selected only the first listed answer.
The original benchmark permits multiple valid answers.
The released subset contains 300 keys and 2,677 yearly source records.
Among 447 first-answer transitions, 153 retain the previous answer.
The new primary scorer accepts every official answer QID.
The official source and mirror agree on all 34,963 test records.

## Verified new results

| Method | Historical Hit@1 | Current Hit@1 | Historical Stale@5 |
| --- | ---: | ---: | ---: |
| BM25 | 78.08% | 23.33% | 70.92% |
| Exact-group latest | 98.43% | 88.33% | 16.55% |
| Text-CC | 97.54% | 94.67% | 1.79% |
| Direct certificates | 98.21% | 94.67% | 1.79% |

These are evidence selection results, not generated-answer results.
Direct certificates exceed exact grouping by 6.33 points on current queries.
The cluster bootstrap interval is [3.33, 9.33] points.
Historical accuracy does not show uniform superiority.

Text-CC changes past eligibility at 8/11 TempLAMA event cutoffs.
It changes past eligibility at 27/42 Wikipedia event cutoffs.
Direct certificates have zero mismatches.
The guarantee assumes fixed pair rules.
The retrieval bound also assumes a fixed candidate ranking.

## Archived results

The archive retains original Qwen generations and result cards.
No fresh language-model inference ran in this session.
The original current masks remain unchanged.
Old Qwen scores measure normalized target-value containment.
They do not establish complete-answer-set QA performance.
The old extractive reader accesses annotated values.
The old historical evaluator uses a gold anchor.
Those results are kept separate from the new primary evaluation.

## Remaining sessions

### Pass 2: establish the final contribution

Compare the proposed guarantees with Graphiti and bitemporal database work.
Do not rename an existing primitive as a new algorithm.
Use the two-clock candidate only if an unmet practical requirement survives this comparison.
Its skyline operation and time distinction are established ideas.
An alternative is a rigorous stability and evaluation paper.
Select the direction from evidence, not from headline wording.

### Pass 3: independent empirical test

Freeze the final method, sources, prompts, and metrics.
Add a natural evidence benchmark with actual passages.
FRESCO currently requires regeneration from its official code.
Its repository inspection found no finished passage dataset.
The linked Re3 repository returned HTTP 404 during this pass.
Run matched extraction and candidate pools for modern comparisons.
Report source correctness, relevant-evidence retention, and reader accuracy separately.
Use real data; constructed examples remain correctness tests.

### Pass 4: reader and manuscript completion

Run the selected method with a frozen capable reader.
Add sufficient and insufficient evidence cases.
Track unsupported answers and answer-set coverage.
Revise the eight-page manuscript around the final empirical result.
Keep material task assumptions in the method.
Put auxiliary failure analysis in the appendix.
Keep the mandatory Limitations section after the conclusion.

### Pass 5: release gate

Complete independent theory and empirical review.
Verify every table against saved predictions.
Compile the final anonymous Overleaf bundle.
Check all figures, references, and page boundaries.
Create final source and run archives.
Do not call the paper submission-ready before these gates pass.

## Resume instructions

Start from this state and the evidence report.
Read the current manuscript and source-set result cards.
Do not restore the original first-answer retirement labels.
Do not repeat completed CPU experiments unless a code change requires them.
Do not replace original results or claim new model runs.
