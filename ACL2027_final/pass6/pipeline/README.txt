Paper tables and author checks

Rebuild the replacement and solver tables from their frozen result cards:
  python pass6/pipeline/build_tables.py --output /tmp/rebuilt_tables

Rebuild the structured reader tables after the complete reader result card exists:
  python pass6/reader/build_paper_tables.py --output /tmp/rebuilt_tables

The final verification plan compares these outputs with the exact manuscript tables.
The historical reader table remains separate from the structured replication.

Compile pass6/paper/main.tex with pdfLaTeX, BibTeX, and repeated pdfLaTeX passes.
The paper uses the supplied official ACL review style without margin or font-size overrides.
Author layout checks use Poppler and PyMuPDF to inspect page boundaries, fonts, and rendered pages.
The final PDF checksum and page checks are recorded in pass6/audit/release/PAPER_CHECKS.json.
All three scientific figures have editable vector sources in pass6/figures/.
