# Exact Certificates for Temporal Evidence: final ACL 2027 revision

**When Do Uncertain Dates Change Retrieval? Exact Certificates for Temporal Evidence**

This project tests whether uncertain dates can change a reader's selected evidence.
For a fixed ranking, it certifies an unchanged context or returns two valid timelines with different contexts.
At most two direct witnesses per claim support exact temporal decisions.

## Paper and editable figure

The final manuscript is `pass5/paper/main.tex`.
The Overleaf archive places this file at its root.
Compile with pdfLaTeX, BibTeX, and two further pdfLaTeX passes.
The vector architecture figure is `pass5/paper/figures/architecture.pdf`.
Its editable SVG accompanies it; `pass4/pipeline/draw_architecture.py` supplies the drawing source.

## Verify the release

Use Python 3.12 and the versions in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python verify_submission.py
python verify_submission.py --full
```

The default command verifies hashes and reconstructs saved results.
The full command also replays retrieval decisions.
Neither command downloads weights or starts model inference.
The extracted project folder can have any name.

The anonymous software and data archives share one `ACL2027_submission/` folder.
Extract both archives into the same parent folder before verification.
Upload those two archives as the respective submission supplements.
The full source-and-runs archive preserves private project history and is not the anonymous submission supplement.

## Inspect a context

```bash
python pass4/retrieval/query.py \
  --units pass5/pipeline/human/units.jsonl \
  --claims pass5/pipeline/human/claims.jsonl \
  --question 'What governmental role did Helen Elizabeth Clark assume from 1989 to Aug 1989?' \
  --ranking title_residual --k 5 --explain
```

The command returns original excerpts, support decisions, and alternative timelines when selection can change.
It needs neither answer labels nor model inference.

## Evidence and provenance

The final revision preserves the original questions, ranking, context budgets, reader, parser, and scoring rules.
The revised source adapter addresses the recorded source audits.
The current results are post-audit comparisons on previously evaluated questions.
Earlier results retain their original versions and scope.

Exact request matches reuse archived responses under the same model and execution settings.
Only unmatched requests receive new generations.
All response failures remain in the scoring denominators.
The model is Qwen2.5-3B-Instruct Q4_K_M under the Qwen Research License.
The pinned llama.cpp runtime uses MIT.
Weights and runtime binaries are excluded; their download pointers and checksums are included.

Both citation audits check the bibliography against primary sources.
The source audit separates literal grounding, event interpretation, and lifecycle completeness.
Source assessments use model-assisted review.
The certificate proofs concern the supplied temporal model.

| Location | Contents |
| --- | --- |
| `pass5/paper/` | Current manuscript, bibliography, tables, and vector figures |
| `pass5/extraction/` | Revised source adapter, tests, extracted records, and freeze |
| `pass5/pipeline/` | Complete retrieval outputs and table generators |
| `pass5/protocol/` | Independent checks, scoring, and result summaries |
| `pass5/inference/` | Requests, responses, reuse checks, and execution records |
| `pass5/retrieval/` | Secondary analysis of six ranking variants |
| `pass5/audit/` | Source, citation, venue, and release checks |
| `pass5/release/` | Package builder, disclosure, licenses, and submission instructions |
| `pass4/`, `pass3/`, `pass2/` | Preserved engines, earlier studies, and frozen dependencies |

`MANIFEST.json` records the private release hashes.
`SUBMISSION_MANIFEST.json` records the paired anonymous release hashes.
The submission disclosure appears in `pass5/release/AI_ASSISTANCE.md`.
