# Independent TimeQA protocol review

Reviewed `pass2/baselines/run_timeqa.py` before reading its results.

The implementation separates inference inputs from scoring labels.
It builds the paragraph index from published text and visible article titles.
The temporal parser reads paragraph text only.
It does not read answer spans, gold dates, or source keys.

Official question rendering uses the benchmark template and its published time constraint.
The completed question then supplies every method with the same input.
Human questions use their published question text.
The benchmark relation identifier selects a template only during question construction.
It does not enter retrieval.

The scoring function measures coverage of annotated answer spans.
It does not measure whether the retrieved paragraph entails the requested temporal answer.
The experiment therefore supports an annotated-span retrieval claim.
It does not support an end-to-end answering claim.

Zero-length and blank answer placeholders do not define positive retrieval targets.
Their pre-result exclusion is appropriate.
The protocol records the exclusion and its counts.

Year mentions do not establish document publication dates.
A paragraph can contain years for several unrelated events.
The temporal conditions must retain their labels as lexical policies.
The policies do not certify temporal truth.

Confidence intervals resample complete articles.
This preserves the dependence between questions from the same article.
The human questions reuse the same underlying source articles.
They form a query variant, not an independent corpus.

No blocking implementation error was found during this code review.
