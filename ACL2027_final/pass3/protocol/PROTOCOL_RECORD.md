# Protocol record

The split was selected before pass-3 comparative retrieval results.
The configuration fixes eight controls, shared source excerpts, and common context budgets.

The first source-only pilot produced 39 extracted claims across 35 passages.
The pilot contained 2,174 passages from 50 articles.
Twenty claims described explicit durations.
Nineteen claims described occurrence starts.
The adapter accepted zero directed replacement pairs.
These counts describe the initial adapter, not its accuracy.

This coverage limits which contribution the pilot can test.
The pilot can test start uncertainty and explicit end handling.
It cannot test cross-claim replacement compression without accepted replacement pairs.
Later extraction revisions must retain their version and source-only audit.

The protocol treats context certification as a separate outcome.
The certificate covers modeled dates and fixed fallback eligibility.
It does not certify unresolved source text or reader answers.

Six focused scoring checks passed.
They cover source truncation, repeated passages, whole answer sets, duplicate predictions, overlap, and missing questions.
These checks use constructed examples and are not benchmark results.
