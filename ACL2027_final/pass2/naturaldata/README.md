# Natural temporal evidence for Pass 2

TimeQA provides the primary natural-text source for this pass.
The release preserves the authors' Wikipedia paragraphs, annotations, and human questions.
It adds no generated evidence.

## Reproduce

Run these commands from the project root:

```bash
python pass2/naturaldata/download_timeqa.py
python pass2/naturaldata/build_timeqa.py
python pass2/naturaldata/finalize_audit.py
```

The downloader uses immutable URLs and verifies SHA256 hashes.
The normalizer also verifies Git blob hashes against the recorded source tree.
The scripts need Python's standard library only.

## Source

- Paper: Wenhu Chen, Xinyi Wang, and William Yang Wang. 2021. *A Dataset for Answering Time-Sensitive Questions*.
- Paper URL: https://arxiv.org/abs/2108.06314
- Official repository: https://github.com/wenhuchen/Time-Sensitive-QA
- Immutable source URLs and hashes: `source_manifest.json`.
- Author license: `raw/TimeQA_LICENSE`.

The authors release their data and code under BSD 3-Clause.
Wikipedia paragraphs remain third-party source content.
Retain the source attribution and applicable Wikipedia terms when redistributing the material.
The manifest does not imply that a code license replaces Wikipedia's terms.

## Files

| File | Use |
|---|---|
| `normalized/test_annotations.jsonl` | All 2,997 original dated test annotations |
| `normalized/test_nonempty_annotations.jsonl` | 2,613 test annotations with nonempty answer spans |
| `normalized/dev_disjoint_nonempty_annotations.jsonl` | 2,651 development annotations after source separation |
| `normalized/human_test_questions.jsonl` | All 989 verbatim human questions |
| `normalized/human_test_nonempty_questions.jsonl` | 830 human questions with nonempty answer spans |
| `normalized/test_passages.jsonl` | 33,493 distinct source paragraphs |
| `normalized/dev_passages.jsonl` | 32,678 distinct source paragraphs |
| `normalized/*_histories.jsonl` | Original history IDs, relations, articles, and paragraph order |
| `timeqa_audit.json` | Counts, empty labels, source overlap, and label scope |
| `source_grounded_examples.json` | Five inspected examples with exact source offsets |

The human questions form a subset of the test annotations.
They are not an independent test split.
All 257 human histories preserve their parent test paragraphs and answer annotations exactly.

## Question and passage schema

Each annotation contains a stable `question_id` and its original `history_id`.
`date_range` preserves both source strings and their year or month precision.
`answers` contains distinct literal answer strings after whitespace normalization.
`gold_answer_spans` records paragraph IDs and character offsets.
The end offset is exclusive.
`gold_passage_ids` lists the paragraphs containing those spans.

The complete annotated files contain no natural-language question text.
Their `question_text` field is null.
The human subset contains original human question text.
Official question templates remain in `raw/TimeQA_relations.json`.
A baseline can use these templates when it clearly identifies the resulting questions.

Each passage preserves the source text exactly.
Its ID derives from the article path, paragraph position, and text.
Repeated relation histories reuse the same passage identity.
No publication time or ingestion time appears in the source annotations.
The normalization does not invent either time.

## Evaluation scope

All 6,498 released answer spans match their source text exactly.
This count includes empty spans.
The test data contains 384 questions with only an empty answer and a zero-length span.
Development contains 347 such questions.
The human test subset contains 159 such questions.
Exclude these questions from positive retrieval metrics.
Do not treat their paragraph-zero pointer as positive evidence.

A span match establishes a benchmark anchor.
It does not establish temporal entailment.
Some anchors are headings, aliases, or mentions outside the relevant event description.
For example, one Attaphol Buspakom answer points to a later coaching paragraph.
Some questions also contain noisy answer labels.
Keep these limitations in the evaluation definition and data audit.

Multiple answer strings have several causes.
They can identify concurrent values, sequential values within a range, or aliases for one value.
The 191 test questions with multiple strings do not establish 191 cases of concurrent facts.
Likewise, adjacent annotation differences do not independently establish real retirement events.

The date ranges use year or month precision.
Some ranges have equal endpoints.
Do not convert them into half-open day intervals without an explicit modeling rule.
Preserve the original range question during benchmark evaluation.
Use dates extracted from source text only for passage features.
Keep gold spans and annotated ranges out of passage feature construction.

## Source separation

Eight article paths occur in both development and test.
One complete history ID also occurs in both splits.
The audit records every overlapping article.
`dev_disjoint_nonempty_annotations.jsonl` removes all eight articles before selecting questions with nonempty spans.
Use this development subset for parameter selection.
Do not tune on the full test or its human subset.

## Inspected examples

Chicago Stadium supplies the clearest concurrency example.
Its source gives overlapping tenancies for the Blackhawks and Bulls.
The human question asks about 1967 to 1988.
Both stated tenancies cover that range.

The News Quiz supplies range answers and a returning host.
Its answer set does not represent simultaneous hosts.
The Lubbers paragraph shows month-level dates beside a question with year-level dates.
The Arnolfini paragraph says an acquisition occurred before 1516.
The Coxie paragraph gives an approximate move date around 1713.
The last two sources do not identify numeric uncertainty widths.

## Legacy RealProse audit

Run `audit_realprose.py` against the original supplied claims.
The optional `--source` argument accepts another copy of that file.
The audit found 17 excerpts that do not state their assigned subject-role pair.
It found 33 excerpts without their assigned start year.
One excerpt conflicts with its assigned start year.
These findings concern supplied evidence, not the truth of the underlying facts.
Use RealProse as a legacy controlled detection check.
The new natural-text results should use TimeQA.

## Access probes

The `access_probes` directory records alternative source access.
The public TempRAGEval tree was accessible, but its data download returned HTTP 401.
FRESCO code was accessible, but no released passage dataset was available in the inspected tree.
A Wikipedia revision request succeeded.
No FRESCO or Wikipedia-revision benchmark result is claimed here.
