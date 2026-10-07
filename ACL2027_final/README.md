# Exact Certificates for Temporal Evidence: pass6 revision

**When Do Uncertain Dates Change Retrieval? Exact Certificates for Temporal Evidence**

This project tests whether uncertain dates can change selected evidence.
For a fixed ranking, it certifies an unchanged context or returns two feasible timelines with different contexts.
The revision adds date constraints, explicit query predicates, and a natural replacement challenge.

The structured reader experiment contains 234 completed requests and 710 scored conditions.
The unchanged parser accepts every output.
The previous pass5 release remains preserved in its original directories and document backups.

## Current manuscript and figures

The current manuscript is `pass6/paper/main.tex`.
Related Work follows the Introduction as Section 2.
Compile it with pdfLaTeX, BibTeX, and two further pdfLaTeX passes.
The final Overleaf archive places this manuscript at its root.
Vector figures and editable sources accompany the manuscript.
The release gate requires eight full main pages before the Limitations section.
The compiled paper contains eight main pages and 22 pages with references and appendices.

## Verify a completed release

Use Python 3.12 and the pinned versions in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python verify_revision.py
```

The command first runs the preserved pass5 verifier.
It then regenerates the new experiments in separate output directories.
It checks source records, constraints, exact decisions, saved reader executions, scoring rows, and tables.
It uses saved model outputs. It does not download weights or start inference.
Verification records stay under `reproduced_pass6/` and `reproduced_pass5/`.
A packaged release includes `RELEASE_VERIFICATION.json`, which binds the checks to its exact manifest.

`python verify_revision.py --full` also repeats the earlier retrieval replay.

Extract both anonymous review archives into the same parent directory.
They share the root `ACL2027_submission/` and support any extracted folder name.
The software archive contains code and documentation. The data archive contains inputs, outputs, and execution records.
The private archive preserves the complete project history.
Rebuilding release archives also requires `python -m pip install -r pass6/release/requirements.txt`.
This dependency supports PDF text and metadata checks during anonymization.

## Revised evidence

The constrained oracle supports overlap, continuous validity, and appointment predicates.
It checks the supplied bounds and difference constraints over integer dates.
The controlled study compares its results with exhaustive feasible timelines.
The independent-date compiler provides an initial screen before exact constrained checks.
A separate lazy exact baseline uses the same contexts and stopping rule.

The natural challenge contains source-grounded replacement graphs.
Its primary comparison retains the same source orders, calendar bounds, and explicit ends in both policies.
The control removes cross-claim replacement edges.
Saved records include source text, literal offsets, annotations, exclusions, queries, and feasible alternative timelines.

The new reader experiment preserves all 234 requests and 710 method conditions.
It uses schema-constrained output and a 512-token completion budget.
The model, questions, contexts, parser, and scoring rules remain fixed.
All scheduled requests completed before final scoring.
Possible and guaranteed support use identical contexts for the sixty primary questions.
Seven diagnostic questions have different contexts. Four produce changed answer sets.

The earlier retrieval study remains unchanged.
It contains 3,178 questions and ten methods under fixed context budgets.
Its guarantees concern the supplied temporal model.
Source assessments use model-assisted review.

## Files

| Location | Contents |
| --- | --- |
| `pass6/paper/` | Current manuscript, bibliography, tables, and figures |
| `pass6/modeling/` | Constraint oracle, frozen controlled cases, and exact comparisons |
| `pass6/replacement/` | Source challenge, source orders, audits, and feasible timelines |
| `pass6/reader/` | Structured requests, execution records, and complete-cohort analysis |
| `pass6/audit/` | Coverage, source, citation, and manuscript checks |
| `pass6/release/` | Verification plan, package builder, disclosure, and submission instructions |
| `pass5/` | Preserved retrieval, source adapter, reader results, and citation checks |
| `pass4/`, `pass3/`, `pass2/` | Preserved engines, earlier studies, and frozen dependencies |

`MANIFEST_pass5.json` preserves the previous release hashes.
The root `MANIFEST.json` records every private release file and its hash.
The anonymous archives use `SUBMISSION_MANIFEST.json`.

The model is Qwen2.5-3B-Instruct Q4_K_M under the Qwen Research License.
The pinned llama.cpp runtime uses MIT.
The archives exclude model weights and runtime binaries.
Asset identifiers, download instructions, hashes, and licenses remain included.
The AI assistance disclosure appears in `pass6/release/AI_ASSISTANCE.md`.
