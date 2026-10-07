# Exact certificates for temporal evidence: pass 4

This revision improves source extraction, relevance ranking, and executable retrieval certificates.
It preserves the earlier theory and archived experiments.

## Current paper and main results

`paper/main.tex` is the current manuscript.
The paper leads with the decision of whether finer dates can change selected evidence.
It gives exact support formulas, context stability, counterworld construction, and a complexity boundary.
The architecture is an editable vector figure.

The two confirmation tracks contain 2,348 template questions and 830 human questions.
The title-aware ranking improves source-span recall by 13.32 and 5.00 points over original BM25 with recency.
Adding recency to the title-aware ranking reaches 63.59% on human questions.
Those gains belong to the retrieval front end.
The certificate identifies 392 stable contexts among 507 parsed contexts with modeled evidence.
All 115 unstable contexts have two independently replayed timelines with different rendered excerpts.

The source adapter extracts 792 development claims and 744 test claims.
Their explicit end counts are 445 and 384.
Only calibration articles contain the three recovered cross-claim pairs.
The independent semantic audit is recorded in `audit/source/RESULTS.md`.

## Run one question

From the project root:

```bash
python pass4/retrieval/query.py \
  --units pass4/pipeline/human/units.jsonl \
  --claims pass4/pipeline/human/claims.jsonl \
  --question 'What governmental role did Helen Elizabeth Clark assume from 1989 to Aug 1989?' \
  --ranking title_residual --k 5 --explain
```

This command uses no question labels or model calls.
It returns source contexts, a stability decision, unresolved support decisions, and alternative timelines.
The lazy selector matches all 3,109 parsed confirmation queries.
On modeled contexts, it performs 2.70–2.92 temporal predicate calls on average.
Those counts exclude relevance ranking and answer generation.

## Locate the evidence

- `extraction/`: frozen source rules, claims, calibration history, partition checks.
- `retrieval/`: fixed ranker, lazy selector, independent scores, six-ranking analysis, query CLI.
- `pipeline/`: all matched retrieval predictions, source units, timelines, and reader jobs.
- `protocol/`: input freezes, exact sample membership, independent replays, reader parsing and scoring.
- `inference/`: model pins, prompts, raw generations, resource history, and runtime logs.
- `audit/`: independent source and manuscript reviews.
- `paper/`: Overleaf-compatible manuscript and figures.

The code accepts source text and visible questions for inference.
Gold answers and spans enter scoring only.
The tracks are confirmation experiments because earlier outcomes had been inspected.
All new extraction and ranking choices use the declared calibration materials.

## Reader reproduction

The reader uses Qwen2.5-3B-Instruct Q4_K_M and pinned llama.cpp binaries.
The final settings use four CPU threads, 2,048 context tokens, and batches of 512.
Temperature is zero; seed is 1729; the output limit is 96 tokens.
See `inference/README.md` for exact commands and licensing.
Weights are downloaded separately and are excluded from this release.

The fixed primary cohort has 60 questions and 600 logical conditions.
Its 193 distinct prompts are separate from the eleven-question diagnostic and its 45 prompts.
Both cohorts are complete: 238 generations cover 710 method conditions.
The selected ranking reaches 21.67% strict F1 on the primary sample, against 15.00% for original BM25 with recency.
The paired difference is 6.67 points, with interval [1.59, 13.56].
The diagnostic has three possible-versus-guaranteed answer changes with two valid responses.
Its strict F1 values are 6.06% and 24.24%, respectively.
`protocol/FINAL_CHECKS.md` gives complete integrity, replay, and scoring commands.
The scorer rejects partial cohorts.
