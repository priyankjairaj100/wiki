# Source-only extraction calibration findings

The source pool contains 30 development paragraphs selected through succession cues.
Neither model prompt contains questions, gold answers, or evaluation outcomes.
Both runs preserve full requests, model outputs, and execution manifests.

## Model runs

| Variant | Completed paragraphs | Returned records | Literal-grounded records | Semantically accepted records |
|---|---:|---:|---:|---:|
| V1: JSON object | 6 | 41 | 0 | 0 |
| V2: required schema | 6 | 46 | 1 | 0 |

V1 omitted every required source quote.
The run stopped after six completed paragraphs.
Its original plan contained 30 paragraphs.

V2 required every schema field, including the source quote.
It used the same source paragraphs and unchanged validator.
The run stopped after six completed paragraphs.
Forty-five records failed literal source or date checks.
The sole grounded record assigned an unrelated succession to its quote.
An independent source audit rejected that record.

The rejected record claimed Bing to Gombrich in 1949.
Its quote instead described Saxl to Frankfort in 1949.
The source dates Bing to Gombrich to 1959.
These outcomes establish an extraction failure for this small local model.
They do not establish a compiler error or a QA accuracy result.

Validation reports:

- `validated/summary.json`
- `validated_schema_v2/summary.json`
- `../../data/learned_v2_semantic_audit.json`

## Minimal source interface

A separate deterministic adapter parses explicit succession clauses.
It runs over all 30 source paragraphs.
It extracts five dated starts and three directed pairs across two articles.
An independent source audit approves all five starts and all three pairs.
Nine constructed checks verify dates, directions, role scope, and missing starts.

The parser extracts these starts:

- Warburg Institute: Frankfort in 1949, Bing in 1955, and Gombrich in 1959.
- CNFF: Avril de Sainte-Croix in 1922 and Marguerite Pichon-Landry in 1932.

It does not invent starts for Saxl or Julie Siegfried.
It does not create an edge from an ordinary appointment.
An explicit same-event end remains linked to its successor event.

The automatic Warburg records reproduce the earlier source case exactly.
For January 1954 through June 1955, the oldest-first ranking has stable top-1 retrieval.
Top-2 retrieval changes with Bing's allowed start date.
The counterworld constructor supplies both allowed date assignments.

The parser and this case are source calibration artifacts.
The counts are not benchmark results.
The frozen primary adapter and primary evaluation remain unchanged.

Files:

- `../succession_rules.py`
- `../succession_rule_results/`
- `../test_succession_rules.py`
- `../../data/succession_rule_semantic_audit.json`
- `../../data/replay_adapter_case.py`
- `../../data/natural_context_case_from_adapter.json`
