# Final ACL 2027 release

Date: 2026-10-07.
Current manuscript: `pass5/paper/main.tex`.
Current paper: **When Do Uncertain Dates Change Retrieval? Exact Certificates for Temporal Evidence**.

## Contribution

The paper asks when more precise dates can change selected evidence.
The compiler stores at most two direct witnesses per modeled claim.
It answers exact possible and guaranteed support queries.
A fixed ranking then yields a stable context or two complete timelines with different selections.
The paper also proves necessary refinement decisions and a hardness boundary for possible context membership.
The hardness result treats the context budget as an input.
The lazy selector stops when the selected context is full.

The source model uses independent occurrence bounds and fixed directed replacement decisions.
The guarantees apply to that supplied model.
Unknown fallback excerpts remain available through a fixed policy.
The title-aware ranking provides the retrieval gains.
The certificate provides the uncertainty decisions.

## Recovery and frozen revision

Workspace maintenance removed the first temporary pass-5 work after an execution outage.
The final release reconstructs the adapter from the saved repair plan.
It regenerates all affected outputs and uses only the new saved records.
It does not substitute remembered numerical outcomes for missing runs.
The complete pass-4 archive remains unchanged under its original version.

Final adapter SHA256:
`217a493c0ec3f2f831c4e3ae9824a50a3289a8ff4f0fcc7adff40c8a9ce767f5`.

The final adapter passes 27 source tests and all eleven known repair checks.
It adds sixteen paragraph-level calendar ends.
Both source partitions preserve every source word and every supplied pair endpoint.

| Track | Claims | Ends | Units | Modeled share | Directed pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Template | 493 | 292 | 33,005 | 1.4937% | 3 |
| Human | 464 | 238 | 34,082 | 1.3614% | 0 |

All three pairs occur in inspected calibration articles.
The evaluation primarily exercises starts and explicit ends.

The new recorded source audit reviews sixty claims from fifty-five articles.
It accepts 54 core events, rejects four, and marks two uncertain.
All 408 literal spans match.
It accepts 26 of 27 supplied ends.
Eight accepted events omit explicit paragraph-level ends; five further endpoints have uncertain applicability.
The sample excludes 277 documented or identifiable exposure articles.
The lost audit's complete membership remains unavailable, so unseen status is not guaranteed.
These are model-assisted judgments.
No source rule changes after the recorded audit.

## Verified retrieval

The fixed tracks contain 2,348 template questions and 830 human questions.
Ten methods use the same evidence units and budgets.
All 31,780 contexts, 15,545 budget comparisons, and 128 alternative timelines pass independent replay.
All 158,900 independently calculated retrieval values agree.
All 3,109 parsed questions match lazy and full-mask selection.

The compiler certifies 189/243 modeled template contexts and 56/66 modeled human contexts.
Their combined result is 245/309 stable contexts.
The remaining 64 cases all change rendered evidence across their two timelines.
Exclusions comprise 41 retirements and 23 late starts.
Sixty refinement frontiers contain one claim; four contain two.

Title-aware recall reaches 67.61% and 58.11% on the two tracks.
Its gains over original BM25 with recency are 14.34 and 5.00 percentage points.
The corresponding intervals are [11.86,16.77] and [0.69,9.10].
Title-aware recency reaches 64.26% human recall.
Its gain over original recency is 11.14 points, with interval [7.58,15.06].
These are retrieval gains, not gains caused by certification.

The lazy selector averages 5.21 candidates and 2.63 temporal tests on modeled template contexts.
The human averages are 5.11 candidates and 2.44 tests.
These counts exclude relevance ranking and model inference.
The secondary study checks all six prespecified rankings.
All 18,654 query/variant decisions match full masks.

## Verified reader study

The current requests total 234: 166 exact archived matches and 68 new executions.
The primary cohort has 60 questions, 600 conditions, and 194 distinct requests.
The diagnostic retains eleven earlier selected questions, yielding 110 conditions and forty requests.
Seven diagnostic context pairs still differ after source revision.
The cohorts share four articles but no question or request.
The release retains all 238 earlier executions and 68 new executions.

Model: Qwen2.5-3B-Instruct, official Q4_K_M.
Model revision: `7dabda4d13d513e3e842b20f0d435c732f172cbe`.
Weights SHA256: `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`.
Runtime: llama.cpp b11435, commit `43fe9c64281ef735046adc025e9e7559a1f659a5`.
Settings: four threads, 2,048 context tokens, batch and microbatch 512, temperature zero, seed 1729, maximum output 96.
No JSON grammar or response repair is used.
The Qwen Research License and runtime MIT license remain recorded.

Primary strict F1: title-aware 21.67%; original BM25 with recency 18.33%.
Their difference is 3.33 points, with interval [-4.84,11.67].
All primary temporal methods score 20.00% and share identical answer sets.
The diagnostic guaranteed-minus-possible difference is 9.09 points, with interval [0,30].
Four diagnostic answer sets change; three changes have valid responses on both sides.
Only the Maher change improves strict F1.
The other valid changes concern Atlético Madrid and Helen Clark.

Eighty of 234 current responses fail the frozen parser.
These include 58 JSON failures, four invalid citation lists, and eighteen length-limit responses.
All failures remain in the scoring denominators.
All 710 conditions and 45 paired contrasts per cohort remain available.

## Presentation, citations, and delivery

The main paper fills eight pages.
Limitations begin naturally on page nine.
The architecture is a vector diagram with editable source files.
The first pages explain the practical problem before the formal model.
The paper uses the official ACL template and standard font sizes.
The release contains a full AI-assistance disclosure and submission-form guidance.

Two independent audits check all 24 references and 28 citation commands against primary sources.
No fabricated reference, unknown key, unsupported method attribution, or duplicate key remains.
The bibliography SHA256 is `b53ec72bf39ac7ed88d93b039011fc68fc417ee71ffdc37237f40e2e0a7c56c7`.

`verify_submission.py` checks the final manifest, frozen dependencies, source tests, saved scores, reader lineage, and generated tables.
The package builder requires a passing verification report bound to the exact release manifest.
It also requires PDF checks proving eight main pages and the correct PDF hash.
The review archives receive a separate check after extraction into an unrelated folder.

The final deliverables are the paper PDF, Overleaf archive, full private source/run archive, anonymous software archive, and anonymous data archive.
The software and data archives each stay below 200 MB.
No external submission or repository push is performed.
