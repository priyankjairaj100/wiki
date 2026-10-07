# Anonymous review supplement

Extract both ZIP files into the same directory. They share the root `ACL2027_submission/`.
The software archive contains code and documentation. The data archive contains saved inputs, predictions, and run records.
Each archive stays below 200,000,000 bytes.

Install Python 3.12. Install the pinned dependencies with `python -m pip install -r requirements.txt`.
Run `python verify_revision.py` from the extracted root.
The check reconstructs the previous results, then checks the revised experiments.
It uses saved model outputs. It needs no model download or new inference.
Use `python verify_revision.py --full` to replay every saved retrieval context and alternative timeline.
Verification outputs stay under `reproduced_pass6/`.

Open `pass6/paper/main.tex` in Overleaf or compile it with pdfLaTeX and BibTeX.
The paper uses the bundled official ACL style. Its architecture figure includes editable SVG and vector PDF files.

The full private archive preserves previous revisions. Submit only the anonymous paper, software ZIP, and data ZIP.
The author must supply author profiles, service details, prior submission details, and final submission form responses.
`AI_ASSISTANCE.md` gives the recorded scope of model assistance for the E1 response.
`THIRD_PARTY_NOTICES.md` lists the source assets and their terms.
The project license appears in `prior_pass1/LICENSE`.
