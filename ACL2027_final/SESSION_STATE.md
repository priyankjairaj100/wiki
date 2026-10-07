# ACL 2027 pass6 release snapshot

Date: 2026-10-07.
Current manuscript: `pass6/paper/main.tex`.
Status: all scientific extensions and complete reader results are saved.
The packaged `RELEASE_VERIFICATION.json` records the final manifest-bound release check.
The PDF contains eight full main pages and 22 pages overall.
Conclusion appears on page eight. Limitations starts on page nine.
Related Work follows the Introduction as Section 2.
The main results include the saved budget-sensitivity comparison for a fixed modeled cohort.
This final layout revision changes no experiments, saved outputs, or bibliography entries.
Static checks find 27 embedded fonts and no Type 3 fonts.
The main body contains no raster figures.
The package gate also requires a completed visual review of the exact PDF.

The previous complete release remains in `pass5/`.
Its root documents and manifest have `_pass5` backups.
Do not modify the frozen pass2, pass3, pass4, or pass5 artifacts.

## Completed controlled experiments

`pass6/modeling/PROTOCOL_FREEZE.json` fixes the constrained-date study.
The study contains 140 models, including twenty empty feasible families.
The 120 feasible models contain 20,846 feasible timelines.
The oracle matches 100,800 exhaustive Boolean support checks and 30,240 fixed-ranking context checks.
It replays 68,161 concrete witnesses without disagreement.
The study evaluates overlap, continuous validity, and appointment predicates.

The two-witness grid contains 476 cases and 13,328 claim-query checks.
Both single-witness reductions fail in every selected grid case.
The full two-witness compiler remains exact.
The selection rule defines this diagnostic grid; these cases do not estimate natural prevalence.

The hybrid experiment uses 10,080 fixed contexts.
It certifies 3,001 contexts without constrained solver calls.
It certifies 312 additional contexts after exact checks.
Its outputs match the full constrained oracle and the lazy exact baseline.
The hybrid uses 62,952 feasibility calls. The lazy exact baseline uses 141,992 calls.
The full oracle uses 218,079 calls.
All methods also share 120 initial model-feasibility checks.
The lazy baseline has a separate frozen amendment after the initial hybrid run.

Reproduction commands support separate output directories:

```bash
python pass6/modeling/run_benchmark.py --output TEMP_ORACLE
python pass6/modeling/two_witness_grid.py --output TEMP_GRID
python pass6/modeling/run_hybrid.py --output TEMP_HYBRID
python pass6/modeling/run_lazy_baseline.py --output TEMP_LAZY
```

The initial result card contains runtime and environment fields.
The verifier ignores only `runtime_seconds`, `python`, and `numpy` for that card.
All other controlled results must match exactly.

The formal audit confirms the revised theorem scopes and integer-date oracle.
The frozen hybrid benchmark and API contain modeled claims only.
The paper treats fixed fallback retention as a mathematical extension of that interface.
The general context theorem allows arbitrary nonempty feasible timeline families.
The linear-time assignment construction remains restricted to independent date bounds.

## Completed source challenge

The source challenge retains 384 source judgments and its complete selection history.
Independent model-assisted review accepts twenty source records with 33 directed replacement edges.
The verifier checks 174 literal spans, 51 calendar dates, and every source export.
Two documented implementation corrections preserve the source records, graphs, and queries.

The primary source-order comparison evaluates 73 point queries at budgets one and five.
Both policies retain calendar bounds, explicit ends, and strict source orders.
The control removes only cross-claim replacement edges.

At budget one, replacement changes 33 selected contexts and 42 stability decisions.
The control certifies 67 contexts. Replacement certifies 25 contexts.
At budget five, replacement changes 34 selected contexts; both policies certify 25 contexts.
The 96 unstable decisions each have two feasible timelines with different rendered contexts.

The independent-date view remains saved as a separate comparison.
Its 98 witness pairs also replay successfully.
Use `pass6/replacement/order_runs/` for the primary natural-case table.

```bash
python pass6/replacement/run_challenge.py --out TEMP_INDEPENDENT
python pass6/replacement/derive_order_view.py --out TEMP_ORDER
python pass6/replacement/verify_saved.py --output TEMP_REPORT.json
```

The final command checks source freezes and regenerates both complete views.
It compares all eight saved output files exactly.

## Reader execution

The revised reader preserves the current 234 unique requests.
The primary cohort contains sixty questions and 600 conditions.
The diagnostic contains eleven previously selected questions and 110 conditions.
The diagnostic cohort was not selected again for this revision.

Model: Qwen2.5-3B-Instruct, official Q4_K_M.
Model revision: `7dabda4d13d513e3e842b20f0d435c732f172cbe`.
Model SHA256: `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`.
Runtime: llama.cpp b11435, commit `43fe9c64281ef735046adc025e9e7559a1f659a5`.
The new interface uses schema constraints, 512 completion tokens, and a 4,096-token context.
The temperature is zero. The seed is 1729.
A recorded scheduling amendment uses two servers with four threads each.
It preserves the original requests and separates all physical execution batches.

All 234 requests completed. The unchanged parser accepts all 234.
Every output ends normally, with a maximum completion length of 51 tokens.
All 710 method conditions remain scored.
The primary sample contains 56 single-answer questions and four two-answer questions.
Possible and guaranteed support share all sixty primary contexts and answers.
Their primary exact match is 35.00%. Strict answer-set F1 is 36.11%.
Seven of eleven diagnostic questions use different contexts, producing four changed answer sets.
Both responses are valid for every change.
Diagnostic strict F1 is 9.09% for possible support and 18.18% for guaranteed support.

Recompute the complete saved-output analysis with:

```bash
python pass6/reader/analyze.py --output TEMP_READER
```

The analyzer verifies the exact merge of all physical batches.
It checks model identity, requests, runtime settings, schemas, memberships, and all scoring denominators.
The release verifier compares its normalized result card, scoring rows, parse audits, and cardinality analysis.

## Coverage and citations

`pass6/audit/editorial/coverage_wording_audit.py` accepts `--output-dir`.
Its outputs have no volatile fields.
It reports coverage against every question and retains a heuristic wording classification.
The wording classification is not a gold annotation of temporal intent.

The revised bibliography contains 25 references.
The audit preserves the 24 previously checked entries and verifies the added Dechter reference.
The latest draft audit finds 28 citation commands, with no unknown or unused key.
The final editorial audit checks the complete reader results and both generated reader tables.
It verifies twenty metric rows against the saved result card.
The abstract contains 196 words. All checked main and reader-appendix sentences contain at most twenty words.
No em dash or unresolved editorial finding remains in that audited snapshot.

## Release workflow

Root owns `pass6/paper/` and the final figure and table checks.
The release owner maintains root documents, `verify_revision.py`, and `pass6/release/`.
`verify_submission.py` remains unchanged as the pass5 regression verifier.

1. Complete reader execution and update the manuscript from the saved results.
2. Finalize `pass6/release/VERIFICATION_PLAN.json` after checking every expected output.
3. Compile and inspect eight full main pages with the official ACL style.
4. Save the final PDF and `pass6/audit/release/PAPER_CHECKS.json`.
5. Finalize root documentation and all manuscript audits.
6. Refresh the manifest only after explicit root approval.
7. Run `python verify_revision.py` against that manifest. It includes eight revision components and exact manuscript table checks.
8. Build the five deliverables with `pass6/release/build_final_packages.py`.
9. Verify both review archives from a fresh folder with an unrelated name.
10. Save all five deliverables and return their links.

The review software and data archives must each remain below 200,000,000 bytes.
Their shared root is `ACL2027_submission/`.
The private archive retains every previous pass.
The five deliverable filenames retain the `ACL2027_final_` prefix.
The package's verification record is authoritative for final gate status and its manifest hash.
Final archive receipts also record file sizes, hashes, identity scans, and fresh-folder reproduction.
