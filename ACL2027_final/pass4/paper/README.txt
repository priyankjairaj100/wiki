ACL 2027 revision, pass 4

Upload this folder to Overleaf and select main.tex as the main document.
Use pdfLaTeX. The bibliography uses BibTeX and acl_natbib.bst.
The paper uses the included ACL review style and anonymous author block.

Local compilation:
  pdflatex main.tex
  bibtex main
  pdflatex main.tex
  pdflatex main.tex
  pdflatex main.tex

The architecture figure is a vector PDF. Its editable SVG is also included.
The source-and-runs bundle contains the Python figure generator.
All reported experiments have saved inputs, predictions, and provenance.
The full source bundle contains the experiment code and download instructions.
