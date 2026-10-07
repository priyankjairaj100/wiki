# Natural-passage retrieval protocol

The source is TimeQA's official annotated test release.
The corpus contains original Wikipedia paragraphs.
The experiment retrieves paragraphs across the entire released test corpus.

The first track uses each relation's first published question template.
Its subject comes from the visible article title.
Its time constraint comes from the published question annotation.
The second track uses the published human questions unchanged.
These human questions overlap the first track's source records.
They are not an independent test corpus.

Every indexed paragraph includes its visible article title.
The index includes headings and short paragraphs.
No answer string, relation label, gold span, or gold interval enters paragraph features.
The temporal functions read paragraph text only.
They read query years from the final question text.

## Methods

All conditions share BM25 with `k1=1.5`, `b=0.75`, and positive log IDF.
All use the complete test corpus and the same lexical ranking.
Temporal rerankers reorder its first 20 paragraphs.
Each evaluation returns five paragraphs.
No development or test labels fit a method parameter.

| Method | Fixed rule |
|---|---|
| BM25 | Rank article-title and paragraph text by lexical relevance. |
| Latest-mentioned-year | Within the first 20, prefer the latest mentioned year before the question's last year. |
| Year-envelope filter | Remove paragraphs whose mentioned-year envelope misses the question envelope. Keep undated paragraphs. |
| Explicit-range filter | Remove paragraphs only when every recognized range misses the question envelope. Keep unresolved paragraphs. |
| Range-support reranker | Prefer overlapping ranges, then unresolved text, then disjoint ranges within the first 20. |

Temporal ties preserve lexical order.
Unresolved questions preserve the lexical ranking.
Ranges use an explicit regular expression over full years and abbreviated year endings.
The parser does not resolve semantic scope, publication dates, or effective dates.
Month constraints remain visible in the question but temporal features use years.

These methods test simple temporal filtering under identical natural evidence.
They do not reproduce learned temporal retrieval systems.
No claim should present the regex conditions as full temporal reasoning.

## Evaluation

Positive retrieval excludes empty answers and zero-length span placeholders.
This excludes 384 templated annotations and 159 human questions.
The resulting tracks contain 2,613 and 830 questions, respectively.

Every retained gold span must equal its source substring.
Annotated passage hit measures whether a retrieved paragraph contains a marked source span.
Annotated span recall measures coverage of the marked spans.
All-span coverage requires every marked span's paragraph in the first five results.

These annotations can identify headings, aliases, or weak source anchors.
Therefore, coverage is not proof of temporal entailment or generated-answer correctness.
Multiple marked strings do not necessarily represent multiple distinct facts.
The experiment reports no generated-answer result.

Paired intervals resample article groups with a fixed seed.
The script preserves per-question rankings and metrics.
Gold-derived filter diagnostics count marked spans removed from the candidate set.
These diagnostics never affect retrieval.

## Files and reproduction

Run `python pass2/baselines/run_timeqa.py` from the project root.
The script records input hashes and method parameters before ranking starts.
Outputs appear under `pass2/baselines/timeqa_results/`.

An initial pre-result execution stopped after the source audit found empty placeholders.
The corrected execution excludes them from positive scoring.
No method parameter changed after that correction.
The query renderer also handles the official pointwise `$2` placeholder.
It inserts `in DATE`, or the raw date after an existing `since`.
Every pointwise test annotation has identical start and end dates.
The renderer corrected this placeholder before any result output.
