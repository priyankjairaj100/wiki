FIGURE SOURCES
==============

Run: python pass6/figures/draw_figures.py

The script writes PDF, SVG, and 300 dpi PNG files.
It also writes 144 dpi previews at the intended physical dimensions.
The script copies publication assets into pass6/paper/figures/.
PDF and SVG are vector formats. SVG text remains editable.
PDF fonts are embedded. No raster illustration appears inside either PDF.

Architecture: 7.00 x 2.35 inches.
Two witnesses: 3.35 x 2.65 inches.
Question coverage: 3.35 x 1.80 inches.

The teal, blue, and orange colors also have distinct labels.
Solid dots include an endpoint. Open dots exclude an endpoint.
All event ranges include their endpoints.

ARCHITECTURE CAPTION
====================

An illustrative office succession connects source evidence to a context certificate.
B's unknown start date lies within 2015.
January and December starts give different evidence for the June query.
The overview has fixed fallback eligibility.
The fixed ranking always selects it at budget one.
At budget two, the selected tenure changes between A and B.

COVERAGE CAPTION
================

Question coverage separates fixed fallback contexts from modeled contexts.
The left bars include every question in each track.
The right bars expand only the modeled subset.
Their labels give stable and unstable counts.
Unparsed questions remain a separate category.

TWO-WITNESS CAPTION
===================

Two different witnesses are necessary.
The accepted pairs are d -> c and e -> c.
For c=[0,2], d=[1,4] supplies r_c=1, while e=[3,5] supplies p_c=5.
The lower strips show support for windows [a,6].
Open endpoints exclude equality.
With only d, point 5 wrongly has possible support.
With only e, point 2 wrongly has guaranteed support.

EXACT MATHEMATICAL CHECK
=======================

G(d,c)=G(e,c)=1.
d supplies r because l_d=1 and u_d=4 > l_c=0.
e cannot improve r because l_e=3 > 1.
d cannot supply p because l_d=1 is not greater than u_c=2.
e supplies p because l_e=3 > u_c=2, with u_e=5.

For Q=[a,6], 0 <= a <= 6:
P_Q(c) iff a < 5.
H_Q(c) iff a < 1.

At point 5, the full gate gives P=false.
With only d, choose (x_c,x_d)=(2,1). Then P=true.
At point 2, the full gate gives H=false.
With only e, every c starts by 2 and every e starts after 2. Then H=true.

ARCHITECTURE CHECK
==================

A starts during 2010. B starts during 2015. The accepted pair is B -> A.
The point query asks about June 1, 2015.
A January 1 start of B makes B eligible and A ineligible.
A December 1 start of B makes A eligible and B ineligible.
Both assignments satisfy the supplied year bounds.
The fixed rank order is overview, A, B.
The overview has fixed fallback eligibility.
At k=1 both assignments select [overview].
At k=2 the assignments select [overview,B] and [overview,A].
Timeline positions use exact day indices within the non-leap year 2015.
January 1=0, June 1=151, December 1=334, December 31=364.
The source, question, and ranking are illustrative.

COVERAGE COUNTS
===============

Template: 2348 = 2053 all-fallback + 189 stable + 54 unstable + 52 unparsed.
Human:     830 =  747 all-fallback +  56 stable + 10 unstable + 17 unparsed.
The modeled subsets contain 243 and 66 questions.
The figure reports question coverage, not the proportion of modeled source units.
The script checks both total-count identities before rendering.

VISUAL QA
=========

All 144 dpi previews were inspected at the intended physical dimensions.
Additional previews use the actual ACL text width of 16 cm.
Single-column previews use the actual ACL column width of 7.7 cm.
These previews use filenames ending in _acl_size.png.
The smallest type remains approximately 6.5 points after ACL scaling.
All figure text is readable. No labels overlap or clip.
The support strips show the exact strict cutoffs at 1 and 5.
All PDFs embed DejaVu Sans as CID TrueType fonts.
Bold and oblique variants are embedded where used.
No Type 3 fonts occur.
