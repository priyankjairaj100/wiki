# Final text audit

Status: source, retrieval, and reader text passed.

This read-only audit checked the reconstructed final manuscript on 2026-10-07.
It did not change manuscript files or source rules.
The final extension checks `sections/reader_results.tex` and the appendix's complete reader outcomes.
It also checks both regenerated reader tables against the completed scorer outputs.
PDF layout and citation verification have separate audit records.

## Source checks

The abstract reports 245 stable modeled contexts among 309 contexts.
The remaining 64 contexts have 128 checked date assignments.
These totals match the current source and retrieval records.

| Statement | Template | Human | Evidence |
|---|---:|---:|---|
| Source paragraphs | 32,332 | 33,493 | Extraction summaries |
| Source claims | 493 | 464 | Frozen claim records |
| Explicit ends | 292 | 238 | Frozen claim records |
| Source units | 33,005 | 34,082 | Partition audits |
| Modeled share | 1.49% | 1.36% | Partition audits |
| Succession starts | 6 | 2 | Extraction rule counts |
| Directed pairs | 3 | 0 | Frozen pair records |

The sixteen added paragraph-level ends match twelve development links and four test links.
The 27 source tests passed before full extraction and evaluation.
The five calendar-end checks and six bounded-state checks match their saved calibration report.
All three directed pairs occur in registered calibration articles.
The source adapter and all frozen dependencies still match their hashes.

The recorded source audit accepts 54 events, rejects four, and leaves two uncertain.
It covers 60 claims from 55 articles, with twenty development claims and forty test claims.
All 408 literal spans match their source offsets.
Twenty-six supplied ends pass; one fails.
Eight accepted events omit explicit paragraph-level ends.
Five further accepted events have uncertain endpoint applicability.
The manuscript preserves the earlier 52/60 result as a separate audit.
It correctly avoids a paired improvement claim.
The exposure registry contains 277 excluded articles.
The appendix correctly states the remaining uncertainty from the lost audit membership.

## Retrieval checks

| Statement | Template | Human |
|---|---:|---:|
| Questions | 2,348 | 830 |
| Parsed questions | 2,296 | 813 |
| Modeled contexts | 243 | 66 |
| Stable modeled contexts | 189 | 56 |
| Unstable modeled contexts | 54 | 10 |
| Stable share | 77.78% | 84.85% |
| Parsed all-fallback contexts | 2,053 | 747 |
| Mean examined candidates | 5.21 | 5.11 |
| Mean temporal tests | 2.63 | 2.44 |

The budget table matches all five saved budget settings.
At twenty excerpts, both fixed cohorts remain more than three quarters stable.
All 3,109 parsed queries match the complete-mask selections.
The manuscript correctly limits operation counts to selection after ranking.

The replay records contain 128 valid assignments and 64 changed rendered contexts.
Forty-one exclusions use retirement; twenty-three use a late start.
Sixty frontiers contain one claim, and four contain two claims.
These totals match the manuscript.

The ten-row recall table matches the current scorer output.
The title-aware ranking reaches 67.61% and 58.11% span recall.
Its gains over original BM25 with recency are 14.34 and 5.00 percentage points.
Their intervals match [11.86, 16.77] and [0.69, 9.10].
The human recency control reaches 64.26%.
Its 11.14-point gain has interval [7.58, 15.06].
The table and prose assign these gains to retrieval, not the temporal certificate.
Possible support and the interval control select identical excerpts on both tracks.

Every secondary ranking row matches its saved variant summary.
The strongest human retrieval control has 102 stable modeled contexts among 120 contexts.
Mean human temporal tests range from 2.34 to 2.44 across all six variants.
The prose retains the selected main ranking and identifies the secondary analysis.

## Examples and scope

The current Helen Clark claim retains its August 1987 start and January 1989 end.
Its saved question covers January through August 1989.
The current counterworld record uses this claim as its changing pivot.
The January 1 and January 31 departure examples therefore match the current model.

The current Warburg records recover starts in 1949, 1955, and 1959.
They retain two directed succession links.
The main text attributes these dates to the selected paragraph.
The appendix records the separate 1954 date in another paragraph.
The illustrative query and ranking are clearly identified.

The main theorem text keeps independent bounds and fixed directed pairs explicit.
It distinguishes period support from a common guaranteed time point.
It limits the hardness claim to a context budget supplied as input.
It separates compact certificate construction from complete context replay.

No stale lost-pass-5 numerical claims were found in the audited source or retrieval text.
No em dash was found in the audited text.

## Completed reader check

The final reader text matches `pass5/protocol/READER_RESULTS.md` and both completed scorer summaries.
All twenty table rows match the current exact-match and strict-F1 values.
The check retains all 710 conditions and both fixed cohorts.

| Reader record | Primary | Diagnostic |
|---|---:|---:|
| Questions | 60 | 11 |
| Articles | 55 | 9 |
| Conditions | 600 | 110 |
| Distinct current requests | 194 | 40 |
| Reused responses | 146 | 20 |
| New executions | 48 | 20 |
| Parser failures | 69 | 11 |

The cohorts share four articles, zero questions, and zero requests.
Seven diagnostic questions retain different possible and guaranteed contexts.
The manuscript correctly preserves all eleven diagnostic questions.

The selected ranking reaches 21.67% primary strict F1.
Original BM25 with recency reaches 18.33%.
Their exact difference is 3.3333 percentage points.
The article-cluster interval rounds to [-4.84, 11.67] points.
The text does not claim a statistically established improvement.

Possible and guaranteed support share every primary answer set.
Their 37 jointly parsed pairs also have no answer changes.
Earliest and latest completion have the same primary result.

Possible and guaranteed support change four diagnostic answer sets.
Three changes occur among seven jointly parsed pairs.
One change involves a parser failure.
Earliest and latest completion have identical change counts and changed question identifiers.
The guaranteed-minus-possible diagnostic gain is 9.09 points, with interval [0.00, 30.00].

The three jointly parsed changes concern Maher, Atlético Madrid, and Helen Clark.
Maher's strict F1 changes from zero to one.
The other two questions retain zero strict F1 under both policies.
The manuscript's qualitative claims therefore match the scored records.
Both cohorts retain all 45 paired method contrasts.

The primary ranking comparison changes twenty answer sets against original BM25 with recency.
Five changes occur among 24 jointly parsed pairs.
Fifteen changes involve a parser failure.
These values match the complete change audit.

Deduplicating the parser records by request gives eighty failures among 234 current requests.
The failures comprise 58 JSON-format errors, four invalid citation lists, and eighteen length-limit responses.
The eighteen length-limit responses all have the recorded finish reason `length`.
The paper keeps these failures in the scoring denominators.

The preserved pass-4 outputs contain 193 primary executions and 45 diagnostic executions.
The new delta contains 68 executions.
Their total is 306 archived executions.
The manuscript correctly distinguishes this execution history from its 234 current requests.

No numerical correction remains from this text audit.
PDF layout, final hashes, and package verification remain separate release gates.
