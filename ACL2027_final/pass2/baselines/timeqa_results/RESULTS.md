# Natural TimeQA paragraph retrieval

All numbers measure annotated-span coverage, not generated-answer accuracy.

| Track | Method | N | Passage Hit@1 | Passage Hit@5 | Span recall@5 | All spans@5 |
|---|---|---:|---:|---:|---:|---:|
| official_templates | bm25 | 2613 | 13.28 | 32.49 | 31.75 | 31.00 |
| official_templates | latest_mentioned_year_top20 | 2613 | 26.98 | 51.86 | 50.89 | 49.90 |
| official_templates | year_envelope_filter | 2613 | 13.85 | 34.44 | 33.67 | 32.87 |
| official_templates | explicit_range_filter | 2613 | 13.20 | 32.11 | 31.39 | 30.65 |
| official_templates | range_support_top20 | 2613 | 20.93 | 38.50 | 37.63 | 36.74 |
| human_questions | bm25 | 830 | 20.72 | 45.66 | 45.04 | 44.34 |
| human_questions | latest_mentioned_year_top20 | 830 | 31.45 | 54.70 | 54.02 | 53.25 |
| human_questions | year_envelope_filter | 830 | 23.01 | 49.16 | 48.33 | 47.47 |
| human_questions | explicit_range_filter | 830 | 20.24 | 44.10 | 43.53 | 42.89 |
| human_questions | range_support_top20 | 830 | 23.25 | 44.58 | 44.00 | 43.37 |

Human questions overlap the official templated track's source records.
No parameter was fitted on either track.
