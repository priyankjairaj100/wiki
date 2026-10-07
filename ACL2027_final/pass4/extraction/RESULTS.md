# Frozen source extraction

The new adapter expands modeled source coverage while preserving every source word.
All claims use literal source spans.
No question, answer, or answer annotation enters extraction.

| Corpus | Paragraphs | Articles | Modeled claims | Explicit ends | Direct pairs | Source units |
|---|---:|---:|---:|---:|---:|---:|
| Calibration source | 4,030 | 86 | 114 | 78 | 3 | See tests |
| Full DEV source | 32,332 | 740 | 792 | 445 | 3 | 33,433 |
| Full TEST source | 33,493 | 749 | 744 | 384 | 0 | 34,480 |

DEV has 64.7% more modeled claims than the prior matched pipeline's 481 claims.
Its 445 explicit ends exceed the prior 221 ends.
Modeled units constitute 2.37% of DEV units and 2.16% of TEST units.
These counts measure coverage, not extraction accuracy.

Every record passes literal grounding and calendar-bound validation.
Both full source partitions have no overlapping or rejected modeled records.
Every direct-pair endpoint survives partitioning.
Every source word appears in one retained unit.
Eleven regression and integration tests pass.

The independent calibration audit reviewed source semantics and all three pairs.
It found clause errors during development.
General source guards now reject those patterns.
The candidate versions preserve the original errors and their corrections.
The final adapter was frozen before full extraction or new comparative QA outcomes.

All three DEV pairs occur in calibration articles.
They connect explicitly named directors or presidents in two source paragraphs.
No predecessor start date was invented.
The remaining confirmation corpus mainly exercises start bounds and explicit ends.

The separate confirmation audit estimates semantic extraction quality after freezing.
Its sample and judgments reside under `pass4/audit/source`.
Those judgments must not change the frozen extractor or selectively remove records.
