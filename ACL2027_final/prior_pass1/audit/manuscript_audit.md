# Manuscript audit and eight-page plan

Audit date: 6 October 2026.

## Recommended central story

**A relevant statement can describe the wrong state of an entity.**

The paper should study evidence selection when an entity attribute changes over time.
The central operation should resolve replacement within an attribute before the context budget is applied.
Global recency can select recent statements about other attributes.
Relevance can select older statements about the correct attribute.
The method must preserve both attribute identity and the state that applies at the requested time.

The practical output is a compact, source-attributed evidence set for a current or historical question.
An organization-role example gives readers an immediate entry point.
A policy-threshold example can show motivation, but existing policy results are synthetic.
Do not imply that the policy example establishes deployment performance.

This story is stronger than three existing framings:

- A regex detector beating one small prompted model on clean pairs.
- A generic graph system whose graph machinery is not necessary for the main result.
- Correctness under perfect parsing, which follows almost directly from the task definition.

Suggested working title: **Selecting Evidence That Still Applies: State-Consistent Retrieval for Temporal Question Answering**.
Another option is **Resolve Before You Retrieve: State-Consistent Evidence for Temporal Question Answering**.
Any new method name should reflect the implemented selection operation.

The strongest required competitor preserves relevance and selects the latest applicable statement within each inferred attribute.
If this simple competitor matches the method, retrieval filtering alone cannot support the new novelty claim.
A stronger method needs a measured advance in grouping, applicability, conflict handling, or evidence coverage.

## Authoritative-source order

1. The released code and result cards define what was run.
2. The uploaded PDF contains newer corrections than the Overleaf source archive.
3. Every bundled `tables/*.tex` is stale relative to the current PDF and result cards.
4. The two files called `review_1.txt` and `review_2.txt` are not referee reviews.
   The first is a reproducibility checklist.
   The second is the submitted supplement.

The new manuscript must not inherit the ZIP source's theoretical or numerical errors.
The submitted PDF fixes several errors, but it still overstates some task boundaries.

## Material PDF-source differences

| Topic | Stale source | Newer PDF | Required action |
|---|---|---|---|
| Selection | Demotes stale claims | Removes them before top-k | Describe the actual hard mask |
| Exactness | Requires exact key matching only | Requires key, value, and time conditions | Preserve all conditions |
| Error source | All errors belong to the matcher | Key, value, and time errors are possible | Remove matcher-only conclusions |
| As-of intervals | Supersession edges directly give boundaries | Components give groups; sorting gives boundaries | Separate grouping from interval construction |
| Date ceiling | Claimed against date reordering generally | Restricted to fixed-context interventions | Do not extend it to full-pool scoring |
| RAG-Time | Fixed half-life 730 days | Development-selected half-life 1,825 days | Use current result cards |
| Wikidata split | Implies a held-out result | Nine development keys remain in 33-key aggregate | Identify aggregate and test-only results |
| Historical gain | Large gains against weak RAG-Time | Smaller gains against tuned RAG-Time | Do not reuse obsolete headline margins |
| Data origin | Six broadly described datasets | Rendered and genuine prose separated | State source form precisely |

### Stale table files

`table1_detection.tex` lists Wikidata as 44 cases and Real-Wikipedia F1 as 0.613.
Current cards contain 73 Wikidata cases and Real-Wikipedia F1 0.880.

`table2_llm_baseline.tex` claims a genuine-prose LLM comparison absent from the current released cards.
Current LLM cards contain clean Wikidata pairs only.

`table3_ablation.tex` has different ablation results and an unsupported claim that every signal is necessary.
Removing the value gate improves TempLAMA F1 from 0.9764 to 0.9855 in the current card.

`table4_retrieval.tex` has obsolete active-evidence precision values.

`table6_money.tex` contains closed-model and paraphrase rows that do not match the current study.
It reports 264 Wikidata questions and 600 TempLAMA questions.
Current canonical cards report 33 and 300 questions per reader.

Regenerate all manuscript tables from one checked results manifest.

## Claims that need correction

### 1. Benchmark labels do not prove general factual replacement

`wikigraphrag/data/templama.py::_answer_name` selects `row['answer'][0]`.
The builder then converts changes in that selected answer into supersession labels.
Several TempLAMA relations permit concurrent values.
These include positions, teams, employers, owners, and party membership.
The current result therefore measures selected-answer transitions in rendered benchmark records.
It does not establish that each older statement became false.

Preserve the existing result as a transition benchmark.
For a broader replacement claim, retain all source answers or verify exclusive validity intervals.
An essential task assumption belongs in the main method description.
This need not become a caveat paragraph.

### 2. The extractive reader is an annotated value lookup

`wikigraphrag/readers/base.py::ExtractiveReader.answer` returns `contexts[0].value`.
That value comes from benchmark metadata.
This is a top-ranked-value diagnostic, not an end-to-end extraction method.
It can remain useful with the correct label.
The Qwen rows are the genuine language-model reader results.

### 3. Historical evaluation uses an oracle query anchor

`experiments/run_asof.py` selects the inferred component containing `gold[key][0].cid`.
This supplies the component anchor from the requested gold key.
The historical result measures timeline reconstruction conditional on this anchor.
It does not measure unrestricted natural-language query routing.

`wikigraphrag/lifecycle/intervals.py` also reads `Claim.value` to define value changes.
The same module returns that annotated value as its prediction.
Do not claim that every historical decision reads only span text and time.
A corrected implementation can use source spans and parsed values, then rerun these cheap experiments.

### 4. The principal data renders known records into claims

Wikidata and TempLAMA give structured records, rendered into present-tense statements.
Wikidata-prose rewrites the same records.
Real-world also renders curated changes.
Only RealWiki and RealProse use genuine Wikipedia prose.
RealWiki is the CEO subset of RealProse, not an independent broad validation.
RealProse timestamps are curated tenure starts, not the dates when Wikipedia pages were published.

### 5. Existing baselines leave a major simple competitor untested

Global newest-first ranking can discard relevant evidence.
TempRALM loses requested-key coverage in the released audit.
This makes its low score understandable without proving the proposed architecture necessary.
Test date selection within inferred keys, after relevance-preserving candidate selection.
Use the same base semantic score when the goal is to isolate temporal selection.

The old lifecycle rows use hybrid retrieval.
The temporal baseline rows use raw dense similarities.
Those choices are methods, but they do not isolate the temporal operation alone.

### 6. The date theorem and some date experiments differ

The corrected PDF theorem concerns reordering a fixed selected context.
`experiments/run_qa.py` applies `date_rerank` to the full ranked corpus before taking five claims.
The history experiments separately reorder within supplied histories.
Keep these experimental conditions distinct.

### 7. Exact-match terminology is inaccurate

`wikigraphrag/eval/qa.py::exact_match` checks normalized substring inclusion.
It is not normalized whole-answer equality.
The strict variant also rejects known stale answer strings.
Report answer containment and strict answer containment, or add exact normalized equality.
Avoid silently changing the metric behind reused results.

### 8. Historical significance does not use chronology clusters

The generic paired bootstrap resamples individual probes.
Historical probes from one chronology are dependent.
The paper says cluster bootstraps over cases, which does not describe every paired test.
Use chronology-cluster intervals for repeated-time experiments.
The 35-question RealProse gain is 0.1429, with reported p=0.076.
Do not describe that specific language-model gain as significant.

### 9. Graph and multi-hop claims need restraint

`multihop_full.json` reports typed-PPR below flat retrieval on all three included datasets.
Macro scores are 0.1467 and 0.2933.
The main method should not claim a broad graph-retrieval advantage.

The real temporal multi-hop card contains ten queries.
Both inferred and exact-key intervals score 1.000.
The current-only graph scores 0.200, but it cannot represent the historical task.
This is a useful functional demonstration, not a competitive multi-hop benchmark result.
The synthetic 40-query card has the same exact-key tie.

### 10. No-cost language is inaccurate

The detector avoids model calls, but it still uses computation.
Use "without model calls" or state measured indexing and query costs.
Remove "for free", "at no added cost", and broad cost-free claims.

## Reusable evidence and proper interpretations

Paths below are relative to `inputs/supplement/wikigraphrag-code-and-data/results/`.

| Evidence | Source | Supported use |
|---|---|---|
| TempLAMA Qwen: flat .5667, date prompt .6233, tuned RAG-Time .4733, lifecycle .9367 | `qa_templama_qwen.json` | Main existing reader result on rendered selected-answer transitions |
| TempLAMA strict: flat .5633, tuned RAG-Time .4667, lifecycle .9367 | Same card | Stricter containment check |
| Wikidata Qwen: flat .4242, tuned RAG-Time .5455, lifecycle .9697 | `qa_wikidata_qwen.json` | Small corroborating result; baseline development overlap is explicit |
| RealProse Qwen: flat .7143, lifecycle .8571, gold .9143 | `qa_realprose_qwen.json` | Genuine-prose reader result; n=35 and p=.076 |
| RealProse evidence: SER .9714 to .2286; AEP .3191 to .8586 | Same card | Direct evidence-selection gain |
| TempLAMA detection F1 .9764, P .9819, R .9709 | `detection_templama.json` | Rendered transition detection |
| RealProse detection F1 .9412, P .9778, R .9072 | `detection_realprose.json` | Pooled genuine-prose grouping result |
| CEO subset F1 .8800 | `detection_realwiki.json` | Relation breakdown; not independent broad replication |
| Pooled detection F1 .9849 | `pooled_wikidata_freshrag_realworld_templama.json` | Cross-subject detection analysis |
| Long-history TempLAMA Qwen .7097 to 1.0000 | `history_templama_qwen.json` | Supplied-history mechanism test; n=31 |
| Historical TempLAMA .9732; exact-key .9329 | `asof_templama.json` | Anchored reconstruction diagnostic until corrected routing exists |
| Historical tuned RAG-Time .9105 on TempLAMA | `temporal_rag_baselines_qwen.json` | Comparison with current tuned temporal score |
| GPT-4o-mini F1 .9600; GPT-4.1-mini .9916; rule 1.000 | `judge_wikidata_gpt-4o-mini.json`, `judge_wikidata_gpt-4.1-mini.json` | Clean-pair analysis; include both models if discussed |
| Ten real temporal chains: inferred 1.000, exact-key 1.000, current-only .200 | `multihop_real.json` | Small functional demonstration |
| Blocked detector matches all-pairs edges through 6,575 claims | `scaling.json` | Implementation equivalence on this distractor construction |

All listed numbers are archived results, not new runs from this session.
The machine-readable companion file records complete cards and source paths.
Replay and provenance checks remain necessary before a new submission.

## Exact eight-page content plan

The allocation below targets eight ACL content pages before references and required end matter.
Final venue rules must be checked separately.

| Page | Purpose | Content and space allocation |
|---|---|---|
| 1 | Make the problem immediate | Title and 150–180-word abstract; practical example; relevance-versus-state failure; three concise contributions |
| 2 | Explain the operation visually | Compact vector architecture; example timeline; task inputs and output; attribute identity and applicability in plain language |
| 3 | Specify the algorithm | Formal claim representation; source-time and validity-time distinction; grouping; selection rule; concise pseudocode |
| 4 | Explain guarantees and design | One substantial theorem tied to the new algorithm; one useful corollary; complexity; failure decomposition with intuition |
| 5 | Establish empirical credibility | Source forms and task sizes; strong baseline definitions; frozen protocol; primary result table |
| 6 | Show where the method helps | Genuine-prose result; anchored versus unrestricted historical task if both exist; subgroup and history analysis |
| 7 | Identify the effective component | Ablations; grouping errors; relevance-preserving latest baseline; budget and uncertainty analysis; measured cost |
| 8 | Position and close | Focused related work; practical interpretation; short conclusion; any final main-body evidence needed for the core claim |

### Page-one content

Use one office-holder timeline with three dated states.
Ask a current question and a historical question over the same sources.
Show that the requested time changes which source applies.
Avoid a generic "RAG systems hallucinate" introduction.

The abstract should define the practical failure before naming the method.
Use at most two quantitative findings.
Name the benchmark setting accurately.
Do not include four acronym definitions, a theorem catalogue, or checksums.

Three contributions should correspond to three actual assets:

1. A problem or distinction that existing evaluation misses.
2. An implemented method with a meaningful guarantee.
3. An empirical result against the strongest direct baseline.

An archive is supporting infrastructure, not a scientific contribution.

### Method presentation

Define every object before using its symbol.
State the applicable relation class once in the task definition.
Distinguish a source publication time from a fact's effective time.
Show both fields in the diagram if the new method uses both.
If only one timestamp exists, name exactly what it represents.

Prefer one main algorithm over separate descriptions that repeat its gates.
Use equations for the selection objective and guarantee.
Move regex details, aliases, and full proof expansions to the appendix.

### Main figures and tables

- One vector architecture with a running timeline example.
- One primary table for current-answer and historical tasks, with task labels and sample counts.
- One plot for evidence budget or history length, including the strongest simple baseline.
- One compact component ablation table.
- One genuine-prose table or plot if it does not fit the primary table.

Every figure should answer a question that prose cannot answer as efficiently.
Do not fill pages with repeated detection, QA, and exactness headlines.

### Appendix allocation

Put full proofs, parser rules, data provenance, selected parameters, and all reusable legacy results in the appendix.
Include exact commands, hashes, environment information, and the distinction between replay and new execution.
Keep important task assumptions in the main task definition.
Keep limitations required by the venue in the required section.
Avoid apologetic paragraph titles such as "The honest limit" and "Baseline safeguards".

## Five-pass completion strategy

1. Reconcile sources, repair core task definitions, and test the strongest simple competitor.
2. Implement the substantive algorithm upgrade and its required experiments.
3. Freeze results, complete theory, and write the eight-page manuscript.
4. Review claims against code and tables; check readability and the vector architecture.
5. Run clean-extraction reproduction, compile Overleaf, inspect every page, and package the final source and runs.

The number of prose passes does not determine scientific readiness.
The new contribution needs measured evidence beyond the simple within-key latest baseline.

## Final claim checklist

- Every abstract number maps to a result card.
- Every main table states its task and sample count.
- Every reused run is marked as archived in the run manifest.
- The model prompt and answer scorer match their manuscript descriptions.
- Historical evaluation does not receive an undisclosed gold anchor.
- Retrieval inputs exclude evaluation-only subject, relation, and value fields.
- Multi-valued relations do not receive unjustified replacement labels.
- No theorem claims more than its assumptions establish.
- No global date baseline stands in for a relevance-preserving state baseline.
- No essential task condition appears only in the appendix.
