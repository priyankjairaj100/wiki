# ACL 2027 research revision

This package contains the first completed revision pass.
Read SESSION_STATE.md for the current contribution and remaining gates.

## Quick verification

Use Python 3.10 or later.

```bash
python reproduce.py --quick
```

This checks file hashes and compiler correctness.
It makes no network or model calls.

## Full CPU reproduction

Install the small audit dependency if needed.

```bash
python -m pip install -r requirements-cpu.txt
python reproduce.py
```

The runner verifies the original release.
It recreates detection, retrieval, source audits, and stability results.
It uses the bundled original TempLAMA source.
It does not rerun archived language models.

## Contents

- `original/`: unchanged original code, data, caches, and result cards.
- `engine/`: the new direct-witness compiler and tests.
- `experiments/`: new CPU experiments, predictions, and result cards.
- `theory/`: proofs and the separate two-clock candidate.
- `external/`: recovered source data, source snapshots, and attribution.
- `paper/`: Overleaf sources and vector figures.
- `audit/`: literature, evidence, source, and independent reviews.
- `scripts/`: figure and table generators.

The new primary results use complete official TempLAMA answer sets.
Original single-answer results remain in their own directory.

## Build the paper

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Overleaf can compile the same directory with pdfLaTeX.

## Attribution

Original code retains its supplied MIT license.
New code uses the same license.
Dataset and paper rights remain with their original owners.
A code license does not automatically license a dataset.
Source URLs and downloaded-file hashes appear in external/sources.json.
Graphiti source retains its Apache license.
