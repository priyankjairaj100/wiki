# ACL 2027 revision: pass 3

This checkpoint contains the revised eight-page manuscript, exact vector figures, theory, source adapters, actual reader runs, and complete retrieval outputs.
The main contribution now certifies when uncertain dates can change a fixed-ranked context.
It constructs two legal date assignments when the context is unstable.
Two sessions remain for the empirical strengthening and final submission audit requested by the author.

## Paper

Open `pass3/paper/main.tex` in Overleaf or compile it with pdfLaTeX and BibTeX.
`pass3/paper/main.pdf` has eight main-body pages and eight additional pages for limitations, references, and appendices.
The separate Overleaf ZIP places this paper at its root.
Editable architecture files are in `pass3/paper/figures/`; Python source is `pass3/data/draw_architecture.py`.

## What actually ran

- Frozen natural-source retrieval:176 pilot questions and2,348 validation questions; eight matched policies.
- Exact counterworld replay:69 ambiguous validation questions and138 complete date assignments.
- Fixed-cohort budget diagnostic:375 queries, five context budgets.
- Actual CPU answer generation:74 unique prompts across31 distinct questions.
- Learned extraction calibration:two six-request partial runs; no accepted learned records.
- Automatic succession calibration:five starts and three directed pairs from30 source paragraphs.
- Independent theorem, scorer, source-span, and reproduction checks.

Among375 parsed validation questions with modeled evidence in context,306 are certified stable.
The remaining69 have verified alternative contexts.
The compiler does not outperform the interval control on retrieval accuracy in this adapter.
The latest-year ranking control remains stronger.
The complete research scope and remaining work appear in `SESSION_STATE.md`.

## Verify without inference

Use Python3.12 and install `requirements.txt` if required.
Run `python reproduce.py` from this folder.
It checks saved hashes, runs the lifecycle/refinement/source/scoring checks, and rebuilds all three new paper tables.
It writes verification outputs to a separate temporary workspace under `reproduced_pass3/`.
Run `python reproduce.py --full` to additionally reproduce the frozen176-question retrieval pilot.
This flag does not download weights or run a model.
Prior-pass verification remains available as `verify_pass2.py`.

## Reproduce complete runs

`pass3/pipeline/README.md` gives complete pilot and validation retrieval commands.
`pass3/protocol/RESULTS.md` links independently scored question-level outcomes.
`pass3/inference/RUNS.md` gives exact reader and completed extraction replay commands.
Model weights and runtime binaries are excluded from this archive.
`pass3/inference/download_assets.py` restores the pinned, hash-checked public assets, about1.14GB.
Inference uses the official1.5B Qwen model on CPU. It requires no external API key.
All exact prompts, raw responses, settings, request hashes, model licenses, and runtime licenses are included.
Run the documented model batches sequentially.

## Contents

- `pass3/theory`: explicit-end reduction, constructive counterworlds, refinement theorem, hardness proof, tests.
- `pass3/extraction`: frozen primary adapter, separate succession parser, learned calibration failures, source validators.
- `pass3/protocol`: split versions, complete labels separated from inference inputs, frozen parsing, independent metrics and reviews.
- `pass3/pipeline`: exact source units, predictions, context certificates, counterworlds, and budget diagnostic.
- `pass3/inference`: pinned downloader, local runner, actual reader outputs, manifests, and licenses.
- `pass3/data`: source audits, cue-selected histories, automatic natural-case replay, figure source, exploratory TempReason provenance.
- `pass3/audit`: paper table generator and PDF validation.
- `pass2`, `prior_pass1`, `inputs`, and `work`: retained earlier valid runs and the original supplied project.

Corpus data retain their original attribution and licenses.
The study's natural source dates are distinguished from annual positive observations.
The learned calibration failures and previous selected-answer metrics remain clearly separated from the current results.
`MANIFEST.json` records SHA256 for every packaged file.
