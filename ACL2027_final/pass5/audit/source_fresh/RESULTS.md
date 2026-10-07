# Recorded source-audit results

Two language-model reviewers assessed 60 frozen claims from 55 articles.
The sample contains 20 development claims and 40 test claims.
Every review used the complete source paragraph.
No current benchmark questions, answers, retrieval results, or reader outputs entered this review.

| Check | Result |
|---|---:|
| Literal spans that match their offsets | 408 / 408 |
| Core events accepted | 54 / 60 |
| Core events rejected | 4 / 60 |
| Core events uncertain | 2 / 60 |
| Supplied ends accepted | 26 / 27 |
| Supplied ends rejected | 1 / 27 |
| Explicit omitted ends among accepted events | 8 / 54 |
| Uncertain endpoint applicability among accepted events | 5 / 54 |

Core-event review checks the subject, relation, value, and start-date attachment.
Endpoint review separately checks the source support for supplied ends.
Literal offsets alone do not establish either semantic property.

The rejected core events concern one adjacent-role date, two relation types, and one lost role phrase.
The uncertain events concern a future club joining and a coarse military affiliation label.
The rejected end belongs to the adjacent-role date error.

Eight accepted events omit an explicit paragraph-level departure.
These concern Bowers, Davis, Buttigieg, Nogan, Anning, Harkness, Holdsworth, and Ashcroft.
The source expresses some departures with relative dates or undated transitions.
The review does not convert these expressions into unsupported exact dates.

Five accepted events have uncertain endpoint applicability.
These concern Glennon, Scott, Tang-Martinez, Dunn, and Scanlon.
Their paragraphs describe loans, discharge, role sequences, or later appointments.
Those statements do not unambiguously end the same modeled relation.

The source registry excludes 277 documented or identifiable exposure articles.
The full membership of the earlier lost audit remains unavailable.
This sample is a new recorded audit, not a guaranteed previously unseen sample.
The former unsaved counts are not reused.

The adapter and sample stayed fixed throughout this audit.
`judgments.jsonl` preserves every decision and its reason.
`judgments_freeze.json` records the final hashes.
These model-assisted judgments are not human annotations or an extraction-recall estimate.
