# Exact certificates for temporal evidence: ACL 2027, pass 4

**When Do Uncertain Dates Change Retrieval? Exact Certificates for Temporal Evidence**

This project turns uncertain historical dates into a decision about retrieved evidence.
For a fixed relevance ranking, the system either certifies an unchanged context or returns two legal timelines with different contexts.
Its compact representation stores at most two temporal witnesses per modeled claim.

## Paper

The current manuscript is `pass4/paper/main.tex`.
The separate Overleaf ZIP places this file at its root.
Compile with pdfLaTeX, BibTeX, and two further pdfLaTeX passes.
Editable architecture sources are `pass4/pipeline/draw_architecture.py` and `pass4/paper/figures/architecture.svg`.
The PDF figure is a vector graphic.

The paper develops exact support, context stability, constructive alternative timelines, necessary refinement decisions, and a hardness boundary.
Its experimental story separates retrieval quality from sensitivity to uncertain dates.
`SESSION_STATE.md` records the current checkpoint and remaining final review.

## Main evidence

- Two confirmation tracks: **2,348 template questions and 830 human questions**.
- Matched evidence: ten methods share source units and context budgets.
- Broader source extraction: **792 development claims and 744 test claims**, with exact source offsets.
- Stronger ranking: **13.32 and 5.00 points** higher shown-span recall than original BM25 with recency.
- Exact certificates: **392 of 507** contexts with modeled evidence are stable across all permitted timelines.
- Constructive explanations: **230 complete assignments** reproduce both contexts for all 115 unstable cases.
- Lazy selection: **2.70–2.92 temporal tests** per modeled context on average; all 3,109 parsed queries match full masks.
- Completed reader study: **238 generations**, covering 60 primary questions and eleven separate diagnostic questions.
- Primary reader gain: **6.67 strict F1 points** over original BM25 with recency, with paired interval **[1.59, 13.56]**.
- Diagnostic sensitivity: three answer changes between possible and guaranteed contexts when both responses parse successfully.

Source interpretation and certificate correctness are audited separately.
All recovered cross-claim succession pairs belong to calibration articles.
The confirmation experiment primarily exercises uncertain starts and explicit ends.
The source semantic audit and prior experiment history remain available in the supplement and run files.

## Query the compiled evidence

From this project folder:

```bash
python pass4/retrieval/query.py \
  --units pass4/pipeline/human/units.jsonl \
  --claims pass4/pipeline/human/claims.jsonl \
  --question 'What governmental role did Helen Elizabeth Clark assume from 1989 to Aug 1989?' \
  --ranking title_residual --k 5 --explain
```

The command returns original excerpts, a stability decision, unresolved support decisions, and alternative timelines.
It needs no answer annotations or model inference.

## Verify the saved release

Use Python 3.12 and install `requirements.txt` when needed.

```bash
python reproduce.py
python reproduce.py --full
```

The default command verifies release hashes, all frozen inputs, source tests, retrieval scores, complete reader runs, and generated tables.
It independently rescores the saved reader outputs.
The full option additionally replays every retrieved context and alternative timeline.
Neither command downloads weights or starts inference.
The extracted project folder may have any name.
Results go to a new directory under `reproduced_pass4/`.

`pass4/audit/release/README.md` describes each verification step.
Historical verification entry points remain as `verify_pass3.py` and `verify_pass2.py`.
Their original manifests are retained for provenance.

## Reproduce inference

`pass4/inference/README.md` records exact runtime commands and resource history.
`pass4/protocol/FINAL_CHECKS.md` records complete scoring and execution-audit commands.
The reader uses Qwen2.5-3B-Instruct Q4_K_M, four CPU threads, temperature zero, and a pinned llama.cpp runtime.
The model uses the Qwen Research License; llama.cpp uses MIT.

Weights and runtime binaries are excluded from this archive.
`pass4/inference/download_assets.py` restores the pinned official assets into a separate cache.
Prompts, raw responses, timing, decoding settings, hashes, model metadata, and licenses are included.

## Navigate the sources

| Directory | Contents |
| --- | --- |
| `pass4/paper` | Current LaTeX manuscript, bibliography, generated tables, vector figures |
| `pass4/extraction` | Frozen source adapter, calibration, extracted claims, partition checks |
| `pass4/retrieval` | Ranker, lazy selector, query interface, independent metrics, six-ranking analysis |
| `pass4/pipeline` | Complete context predictions, source units, counterworlds, reader jobs, table generators |
| `pass4/protocol` | Input freezes, independent replay, reader parsing and scoring, result summaries |
| `pass4/inference` | Actual reader outputs, runtime logs, provenance, asset downloader |
| `pass4/audit` | Independent source, manuscript, novelty, and portable-release reviews |
| `pass3/theory` | Reused lifecycle and refinement engines, proofs, constructed correctness checks |
| `pass3`, `pass2`, `prior_pass1`, `inputs`, `work` | Preserved earlier experiments and original supplied project |

`MANIFEST.json` records SHA256 hashes for every packaged file except itself.
Original corpus attribution and licenses remain with their source artifacts.
