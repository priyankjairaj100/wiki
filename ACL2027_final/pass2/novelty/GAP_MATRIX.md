# Pass 2: settled novelty assessment

Access date: 2026-10-06.

## Recommended contribution

Use **exact temporal support under uncertain dates** as the main algorithmic upgrade.

Each claim has a date range, rather than an invented exact date.
A fixed pairwise predicate defines replacement relationships.
The executor preserves every date assignment consistent with those ranges.
It answers possible support and guaranteed support for the query's time range.
The guarantee must distinguish these quantifiers:

- Possible support: there exists a date assignment and a query time with active support.
- Guaranteed range support: every date assignment has some query time with active support.
- Guaranteed point support: there exists one query time with active support under every date assignment.

The second and third properties differ.
The proposed two-boundary compiler could make this difference operational without enumerating all assignments.
Combine exactness with sparse certificates and bounded effects from pair-decision errors.
This is a specific proposed contribution, not a verified claim of global priority.

## Close-prior matrix

| Work | Verified overlap | Remaining distinction to establish |
|---|---|---|
| DeFuzzRAG, AAAI 2026 | Infers query granularity and document time scopes. Keeps overlapping intervals. Retrieves more candidates when filtering removes too many. | Its inspected method commits to inferred scopes. It does not provide the proposed exact possible/guaranteed replacement masks across every admissible date assignment. |
| IA-RAG, arXiv 2026 | Uses interval event units, fuzzy flags, Allen relations, and interval traversal. An LLM narrows uncertain intervals from neighboring evidence. | Exact symbolic date-assignment semantics and range-support certificates differ from inferred interval tightening. |
| NuggetIndex, SIGIR 2026 | Uses validity intervals, source spans, lifecycle states, and functional or multi-valued schemas. It closes earlier validity through newer supported facts. | The proposed executor does not select one date assignment. Its exact range support and error-locality guarantees require direct comparison. |
| Graphiti / Zep, 2025 | Direct contradiction witnesses close earlier validity intervals. This already overlaps the pass-1 mechanism. | Interval-censored occurrence times and all-assignment range guarantees exceed the inspected direct endpoint operation. |
| TimelyRAG, September 2026 | Uses semantic and temporal ranking for evolving documents. Models query granularity and document validity. | Ranking by temporal distance does not establish all-assignment support guarantees. Full-text theorem inspection was not completed. |
| Anselma et al., TKDE 2013 | Models valid-time indeterminacy through possible temporal scenarios. Proves compact representations correct. | This is a foundational overlap. Novelty must concern the particular replacement semantics, sparse compiler, and NLP consequences. |
| Fan et al., TODS 2012 | Studies data currency without reliable timestamps. Uses partial currency orders and certain-current query answers. | This is a foundational overlap. Do not claim the first certain-current semantics. Compare specific model assumptions and algorithm costs. |
| Amarilli et al., TIME 2017 | Studies possible and certain queries over partially ordered data. Establishes complexity and tractable cases. | The proposed fixed replacement predicate need not define a partial order. Its independent date ranges define a restricted tractable model. |

## Primary evidence

1. **DeFuzzRAG**: https://ojs.aaai.org/index.php/AAAI/article/view/40276
   - PDF: https://ojs.aaai.org/index.php/AAAI/article/download/40276/44237
   - DOI: 10.1609/aaai.v40i36.40276.
   - Primary search extraction supplied the method subsection, including the overlap rule.
   - Direct PDF download failed with HTTP 502 in this environment.
   - The paper contains a theorem. Its exact statement was not recovered.
   - Therefore, do not state that DeFuzzRAG contains no theory.
2. **IA-RAG**: https://arxiv.org/abs/2606.06044
   - Local full text: `work/audit/IA_RAG_pdf.txt`.
   - Section 3.3, equation 5 defines interval tightening through an LLM operator.
   - Figure 7 defines year, month, and fuzzy-date expansion.
   - Figure 9 defines the LLM tightening prompt.
3. **NuggetIndex**: https://arxiv.org/html/2604.27306v1
   - SIGIR DOI: 10.1145/3805712.3809687.
   - Sections 3.2 and 3.3 provide validity inference and conflict handling.
   - Release: https://github.com/searchsim-org/sigir26-nuggetindex
4. **TimelyRAG**: https://arxiv.org/abs/2609.11572
5. **Valid-time indeterminacy**: https://experts.arizona.edu/en/publications/valid-time-indeterminacy-in-temporal-relational-databases-semanti/
   - DOI: 10.1109/TKDE.2012.199.
6. **Determining the Currency of Data**: https://www.research.ed.ac.uk/en/publications/determining-the-currency-of-data-2/
   - Author PDF: https://www.pure.ed.ac.uk/ws/portalfiles/portal/17894133/Fan_Geerts_ET_AL_2012_Determining_the_currency_of_data.pdf
   - DOI: 10.1145/2389241.2389244.
7. **Order-incomplete data**: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.TIME.2017.4

## Decisive real-data experiment

Use the original TimeQA documents and questions.
Derive date ranges from source precision through a fixed parser.
Use exact days as points, months as calendar intervals, and years as calendar intervals.
Keep the original source text and source offsets for every parsed range.
Do not use answer labels to extract claim dates or choose replacement edges.

Freeze one retrieval ranking and one replacement predicate for all executor comparisons.
Compare these executors:

1. Earliest-day date completion.
2. Midpoint date completion.
3. Latest-day date completion.
4. Simple source-interval overlap.
5. Exact possible-support certificates.
6. Exact guaranteed-range certificates.

Call the first four **executor baselines**.
Do not label them full DeFuzzRAG, IA-RAG, or NuggetIndex reproductions.
Include their full systems only when their official code runs with matched inputs.

Measure complete answer coverage, valid evidence removed, stale evidence retained, and context size.
Report query-level paired confidence intervals.
Separate year, month, and exact-date questions.
Also separate source ambiguity from query ambiguity.
Use equal token budgets and include ranking without any temporal removal.

The result is decisive if certificates recover valid support removed by date completion under the same ranking.
The result needs an independent evidence audit because TimeQA answers alone do not label every retrieved fact.
Raw overlap may recover equally much evidence; the comparison must also measure retained stale evidence and budget costs.

## Rejected main-story candidates

**Multi-valued retention alone.** Aether and NuggetIndex already distinguish functional and multi-valued relations.
**Minimal support selection alone.** Coverage-aware retrieval and set-cover objectives already have substantial prior work.
**Capacity-q absence alone.** It is standard cardinality reasoning.
**Closed-list absence alone.** Completeness statements already support sound negation in knowledge graphs.

A q-witness certificate can still support an architectural result.
For q greater than one, pairwise compatibility does not imply joint compatibility.
However, experiments need trusted cardinality bounds and simultaneous witnesses.
The maximum observed answer count is not a certified bound.

## TempLAMA interpretation

TempLAMA uses yearly buckets.
Its multiple answers can result from sequential facts within one year.
They do not necessarily establish simultaneous coexistence.
Use “multiple valid answers at the benchmark's temporal granularity.”

The original source explicitly accepts overlapping answer intervals:
https://aclanthology.org/2022.tacl-1.15/

Preserve its complete answer arrays.
Distinguish an any-answer score from complete answer coverage.

## Additional essential related work

- ERASE, NAACL Findings 2025, updates fact histories through deletion or rewriting.
  https://aclanthology.org/2025.findings-naacl.168/
- PaTeCon, AAAI 2023, mines temporal conflict constraints.
  https://ojs.aaai.org/index.php/AAAI/article/view/25533
- MATQA, PeerJ Computer Science 2023, predicts sets for multi-answer temporal questions.
  https://peerj.com/articles/cs-1725/
- Darari et al., Semantic Web 2020, proves sound negation using completeness statements.
  https://journals.sagepub.com/doi/10.3233/SW-190344

