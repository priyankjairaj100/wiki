# Recorded source audit

`PROTOCOL.md` states the selection and review rules.
`select_sample.py` selects 20 development claims and 40 test claims after extraction freezes.
`freeze.json` records the sample and all source hashes before paragraph review.
`sample.jsonl` preserves each claim and its complete source paragraph.
`exposure_registry.json` records excluded articles and the supporting history.
`check_literal.py` checks all recorded spans against source offsets.
`review_*.jsonl` contains the individual model-assisted decisions.
`finalize_review.py` combines decisions without changing the sample.
`summary.json` reports separate event, endpoint, and lifecycle counts.
`judgments_freeze.json` protects the final judgments and their inputs.

Run literal verification with:

```sh
python pass5/audit/source_fresh/check_literal.py
```

The full membership of the lost prior audit is unavailable.
The sample excludes all documented prior exposure and identifiable lost-audit articles.
It is a new recorded audit, not a guaranteed previously unseen sample.
No prior lost results enter these records.
