# Focused theory novelty audit

Date: 2026-10-06. Scope: five close primary scholarly sources. This review changes no manuscript or experiment files.

## Assessment

The strongest specific contribution is the **exact two-witness compilation for direct temporal replacement**, followed by constructive differing timelines and the stability-versus-membership complexity separation. The reviewed sources do not state these two boundary formulas or their tight direct-witness bound.

The equality `Top_k(P) = Top_k(H)` is a general fixed-order eligibility fact. It does not require independent dates, a temporal interpretation, or the replacement gate. For any nonempty family of eligibility sets, let `P` be their union and `H` their intersection. The manuscript's proof establishes the equivalence unchanged. It should remain a clear theorem supporting the system, without carrying the novelty claim alone.

Certainty of an entire ranked answer is established prior terminology. Possible/certain ranked answers and compact lower/upper uncertainty representations are also established. Current narrow claims about direct replacement are well chosen. No exact duplicate of the combined contribution was identified within this focused audit; this is not an exhaustive priority determination.

## Five nearest sources

### 1. Feng, Glavic, and Kennedy. PVLDB 2023

**Efficient Approximation of Certain and Possible Answers for Ranking and Window Queries over Uncertain Data.** Volume 16(6), 1346–1358. DOI: `10.14778/3583140.3583151`.

Primary PDF: https://www.vldb.org/pvldb/vol16/p1346-feng.pdf

Tool references for root to reopen: `turn57view0`, `turn60view1`, `turn59view2`.

Relevant locations: Sections 4.2 and 5; Figure 4; Theorem 1. This work bounds uncertain tuple multiplicities and ranking attributes. Top-k is sorting followed by a position filter. Its rank bounds count certainly preceding and possibly preceding tuples. The algorithms preserve bounds on query results, including SQL window aggregates. Their windows are rank-based or value-range SQL windows, not a historical support interval.

**Overlap:** lower/upper uncertainty representations, uncertain membership, top-k bounds, and one-pass algorithms. Fixed deterministic rank is a special case. Merely comparing certainty bounds for ranked retrieval is therefore weak novelty positioning.

**Specific contrast:** our marginal support bounds are exact for a direct replacement model, retain source witnesses, and construct actual complete dates when the selected context varies. The paper's top-k operator gives bounds for a broader database representation. It does not supply the two temporal witness formulas.

Suggested paraphrase: “Feng et al. bound possible and certain results for ranking and SQL window queries.”

### 2. Amarilli, Ba, Deutch, and Senellart. TIME 2017

**Possible and Certain Answers for Queries over Order-Incomplete Data.** LIPIcs 90, 4:1–4:19. DOI: `10.4230/LIPIcs.TIME.2017.4`.

Primary PDF: https://drops.dagstuhl.de/storage/00lipics/lipics-vol090-time2017/LIPIcs.TIME.2017.4/LIPIcs.TIME.2017.4.pdf

Tool references: `turn60view2`, `turn61view1`, `turn62view0`.

Relevant locations: Definition 7, Example 9, footnote 1 on page 4:7, Theorems 12–14. CERT asks whether an entire ordered result is the unique possible result. Example 9 explicitly represents top-k using order-aware accumulation. Their model varies order while tuple existence stays fixed. They also separate tractable certainty from hard possibility for some query classes.

**Overlap:** the question “does every possible world yield the same ranked answer?” and the general possibility/certainty complexity distinction have clear antecedents. Neither broad idea should be introduced as new.

**Specific contrast:** our fixed ranking is filtered by eligibility coupled through temporal replacement. Our formulas compile that eligibility and produce event-date assignments. Their partial-order representation and results do not directly prove our gate-specific witness bound or Set Cover construction.

Suggested paraphrase: “Amarilli et al. study certainty of complete ordered answers, including top-k queries over order-incomplete data.”

### 3. Anselma, Terenziani, and Snodgrass. TKDE 2013

**Valid-Time Indeterminacy in Temporal Relational Databases: Semantics and Representations.** 25(12), 2880–2894. DOI: `10.1109/TKDE.2012.199`.

Primary author PDF: https://www2.cs.arizona.edu/~rts/pubs/LucaTKDE12.pdf

Tool references: `turn62view1`, `turn63view1`, `turn63view3`, `turn63view4`. Published metadata: `turn59search3`.

Relevant locations: Sections 2–4; especially Sections 3.3–3.6. The paper defines explicit temporal scenarios and compact representations with definite/indeterminate chronons, dependencies, and duration constraints. Thus compact temporal uncertainty representations are established. Their scope is valid-time relational semantics, rather than events whose strict later occurrence retires another event's claim.

**Specific contrast:** the present paper compiles a direct replacement neighborhood into at most two supplying events. The guaranteed window condition quantifies support somewhere within each timeline. It should not be equated with finding one chronon that is definite across all scenarios. The source's general dependency machinery reinforces why this distinction matters; it does not present the manuscript's two-witness certificate.

Suggested paraphrase: “Valid-time indeterminacy has established scenario semantics and compact representations; we compile direct replacement into exact support witnesses.”

### 4. Hua, Pei, Zhang, and Lin. SIGMOD 2008

**Ranking Queries on Uncertain Data: A Probabilistic Threshold Approach.** 673–686. DOI: `10.1145/1376616.1376685`.

Primary author PDF: https://www.cse.unsw.edu.au/~lxue/sigmod08.pdf

Tool references: `turn55search8`, `turn59search9`; author institutional metadata `turn55search0`. The PDF is indexed with substantial source text, but direct open failed in this session.

Relevant scope: probabilistic threshold top-k. Tuples have fixed ranking attributes but uncertain existence, with generation rules including mutual exclusion. Results select tuples whose probability of appearing in top-k reaches a threshold. Possible/certain membership is thus close established groundwork.

**Specific contrast:** the manuscript has no prior distribution, derives dependent eligibility from occurrence bounds, and certifies the entire selected context. The current related-work sentence accurately describes this source. Do not imply that fixed scoring with uncertain membership itself is new.

### 5. Amarilli, Amsterdamer, Milo, and Senellart. ICDT 2017

**Top-k Querying of Unknown Values under Order Constraints.** LIPIcs 68, 5:1–5:18. DOI: `10.4230/LIPIcs.ICDT.2017.5`.

Primary PDF: https://drops.dagstuhl.de/storage/00lipics/lipics-vol068-icdt2017/LIPIcs.ICDT.2017.5/LIPIcs.ICDT.2017.5.pdf

Tool references: `turn57view2`, `turn61view2`.

Relevant locations: Sections 2.2–2.4, Theorem 9, Section 6. The main task ranks expected unknown numerical values under a uniform distribution over assignments satisfying order constraints. Its hardness concerns these expected values, including top-1. It also discusses alternative probabilistic top-k semantics.

**Specific contrast:** the manuscript fixes relevance rank and changes eligibility. Its NP-hardness concerns possible inclusion for an input budget, not expected-value ranking. The current citation provides useful context but should not be used as the proof or a direct equivalent of the new reduction.

## Two precise framing improvements

1. Keep the main contribution sequence as **two direct witnesses → exact context decision → complete alternative timelines → necessary refinement decisions**. Name the gate-specific compilation and its query-independent witness bound explicitly. The current introduction already substantially does this. There is no need for “first” language.

2. State the useful structural reason for the complexity separation: **“Stability depends only on each claim's support bounds, even though shared events couple claim eligibility.”** This is a consequence of the manuscript's proof. It explains why a cheap exact decision coexists with hard possible membership. The generic prefix criterion can be presented as the bridge from exact temporal support to the practical decision.

An optional related-work tightening is to describe TIME 2017 as certainty of *ordered answers*, rather than only possible/certain answers generally. This acknowledges the closest conceptual predecessor while sharpening the fixed-rank eligibility distinction.

## Search limits and evidence handling

The focused search inspected primary publisher, author, and institutional sources. It targeted uncertain tuple membership, certain top-k answers, complete-answer certainty, valid-time indeterminacy, and compact temporal representations. No new empirical claims or experiments were introduced. Source summaries above stay below 200 words each; no source text is quoted verbatim beyond titles and technical terms.
