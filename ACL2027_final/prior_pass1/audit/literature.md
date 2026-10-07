# Literature and submission audit

Access date: 2026-10-06. All substantive findings use papers, official code, or official venue pages.

## Main finding

The old story has substantial prior-art overlap. Deterministic supersession, validity intervals, historical retrieval, and temporal conflict filtering already exist.

The revised contribution should concern the correctness of evidence removal under imperfect pair matching. A precise characterization can contribute beyond existing implementations. It must distinguish its guarantees from the earlier mechanisms.

This is a research assessment, not a proof of global novelty. The closest implementations require direct comparison.

## Closest work

### Zep and Graphiti

Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, and Daniel Chalef. 2025. *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*. arXiv:2501.13956.

- Paper: https://arxiv.org/abs/2501.13956
- Full text: https://arxiv.org/html/2501.13956
- Official source: https://github.com/getzep/graphiti/blob/main/graphiti_core/utils/maintenance/edge_operations.py

Section 2.2.3 uses an LLM to identify contradictions between facts. Temporal overlap permits direct edge invalidation. The replacement's valid time closes the earlier interval. The system retains source provenance and historical records.

The current source implements a particularly close operation. It sorts contradiction candidates by valid time. The first later candidate closes the new fact's interval. The backward routine updates earlier contradictory facts directly. It does not require component closure.

Thus, earliest direct witnesses are an existing implementation primitive. Novelty could concern exact compilation, minimal certificates, or error bounds for arbitrary pair matchers. Those claims need proofs and comparison with this primitive.

Cached source: `work/external/graphiti_edge_operations.py`. The inspected routines are `resolve_edge_contradictions` and `resolve_extracted_edge`. Source hash and Apache license are in `work/external/`.

### MemStrata

Neeraj Yadav. 2026. *Temporal Validity in Retrieval Memory: Eliminating Stale-Fact Errors for AI Agents over Evolving Knowledge*. arXiv:2606.26511.

- Paper: https://arxiv.org/abs/2606.26511
- Full text: https://arxiv.org/pdf/2606.26511
- Follow-up: https://arxiv.org/abs/2608.20685

MemStrata uses deterministic subject–relation–object supersession without an LLM on the structured path. It closes validity intervals and retains retired facts. Its evaluated changing facts have one mutable value. Its experiments use ingestion order as the currency signal. Historical evaluation is deferred in the first paper.

The August follow-up tests 130 clean atomic transitions from real software histories. Therefore, real-data evaluation alone does not separate the revised work.

The old manuscript's central mechanism substantially overlaps this paper. Cite it directly. Do not claim the first deterministic supersession memory.

### Re3

Jiawei Cao, Jie Ouyang, Mingyue Cheng, Zhaomeng Zhou, Chunli Liu, Yupeng Li, Zirui Liu, and Shijin Wang. 2026. *Re3: Relevance & Recency Retrieval for Mitigating Temporal Hallucination*. ACL 2026, pages 25735–25760. DOI: 10.18653/v1/2026.acl-long.1180.

- Paper: https://aclanthology.org/2026.acl-long.1180/
- Full text: https://aclanthology.org/2026.acl-long.1180.pdf
- Linked repository: https://github.com/cjwyv/Re3

Its recency filter extracts triples jointly from retrieved documents with Llama-3-8B. It groups facts by subject and relation. The latest publication selects the winning value. It removes documents that support conflicting values. A separate encoder learns temporal relevance.

This is a necessary related-work comparison for obsolete-evidence suppression. Its published limitation concerns historical questions and multiple-time aggregation. The revised work can distinguish formal all-cutoff behavior and preprocessing costs.

Re2 Bench contains generated questions and passages based on real records and perturbed tuples. It is not an untouched natural-prose benchmark. The linked repository returned HTTP 404 through GitHub API and raw access.

### Reliable post-retrieval assembly

Vikas Reddy and Sumanth Reddy Challaram. 2026. *Reliable Post-Retrieval Assembly for Agent Memory: Separating Evidence Extraction from Policy Execution*. arXiv:2606.01435v2.

- Current paper: https://arxiv.org/abs/2606.01435
- Version date: 2026-08-02.

The earlier title was *Don't Ask the LLM to Track Freshness*. Cite the current title. The revised study separates semantic candidate extraction from deterministic policy execution. Its controlled analysis attributes most improvements to extraction. Replacing the executor alone contributes two percentage points on average. This supports a matched-extraction baseline in our evaluation.

### IA-RAG

Xiaoman Wang, Yaoze Zhang, Wenzhuo Fan, Hongwei Zhang, Ding Wang, Guohang Yan, Song Mao, Botian Shi, Yunshi Lan, and Pinlong Cai. 2026. *IA-RAG: Interval-Algebra-Driven Temporal Reasoning for Dynamic Knowledge Retrieval*. arXiv:2606.06044.

- Paper: https://arxiv.org/abs/2606.06044
- Repository: https://github.com/xiaoAugenstern/IA-RAG

IA-RAG represents facts as interval event units. It includes explicit uncertainty flags and source identifiers. It builds interval relations using Allen's algebra. Its time-tightening operator uses an LLM and neighboring events to refine uncertain intervals. Its main tasks include TimeQA, TempReason, and ComplexTR.

The repository reports acceptance at EMNLP 2026 Findings. It currently says implementation release is pending. Use the verified arXiv citation until final publication metadata is available.

Cached full paper: `work/audit/IA_RAG_pdf.pdf`. The text extraction is beside it. The proposed work should distinguish inferred replacement endpoints from general interval reasoning.

### FRESCO

Sohyun An, Hayeon Lee, Shuibenyang Yuan, Chun-cheng Jason Chen, Cho-Jui Hsieh, Vijai Mohan, and Alexander Min. 2026. *FRESCO: Benchmarking and Optimizing Re-rankers for Evolving Semantic Conflict in Retrieval-Augmented Generation*. arXiv:2604.14227.

- Paper: https://arxiv.org/abs/2604.14227
- Official repository: https://github.com/facebookresearch/fresco

FRESCO aligns Wikidata validity intervals with historical Wikipedia revisions. Its candidates include obsolete passages and current but insufficient passages. It evaluates timestamp-visible reranking. Thus, it tests more than choosing the newest document.

The public tree has code and query templates, but no passage dataset. The release API returned an empty list. The README requires regeneration. The pipeline calls Wikidata and Wikipedia, then mines negatives with Qwen3 embeddings.

Do not claim FRESCO results without constructing or obtaining its actual evidence pools. Inspection records are in `work/audit/fresco_*`.

## Existing temporal baselines

### TempRALM

The 2024 preprint has two authors. A refereed 2025 version adds Hardi Trivedi.

Anoushka Gade, Jorjeta G. Jetcheva, and Hardi Trivedi. 2025. *It's About Time: Incorporating Temporality in Retrieval Augmented Language Models*. IEEE CAI, pages 75–82. DOI: 10.1109/CAI64502.2025.00019.

- Author repository: https://scholarworks.sjsu.edu/faculty_rsca/6190/
- Earlier full text: https://arxiv.org/pdf/2401.13222

The temporal score is inverse query–document time distance. The method matches its mean and variance to semantic scores. It adds both scores and excludes future documents. The paper uses Atlas, over-retrieval, and few-shot training.

The supplied implementation adapts the scoring formula to MiniLM. It is not a reproduction of the full TempRALM system. State this in the baseline definition. Use identical semantic scores and candidate pools for controlled scorer comparisons.

### Half-life scoring

Matthew Grofsky. 2025. *Freshness and the Limits of Heuristic Trend Detection in Temporal RAG*. arXiv:2509.19376. The inspected revision is v2, dated 2026-06-26.

- Full text: https://arxiv.org/html/2509.19376

Its score is alpha times cosine similarity plus a half-life recency term. Defaults are alpha 0.7 and 14 days. The revision explicitly tests corpus-specific settings. It recommends broad candidate pools. Call the local comparison a half-life scoring baseline. Its default alone is weak evidence of superiority.

### MRAG

Siyue Zhang, Yuxiang Xue, Yiming Zhang, Xiaobao Wu, Anh Tuan Luu, and Chen Zhao. 2025. *MRAG: A Modular Retrieval Framework for Time-Sensitive Question Answering*. Findings of EMNLP, pages 3080–3118. DOI: 10.18653/v1/2025.findings-emnlp.167.

- Paper: https://aclanthology.org/2025.findings-emnlp.167/
- Code: https://github.com/siyue-zhang/MRAG

MRAG separates query content from temporal constraints. It retrieves and summarizes evidence. It then combines semantic and temporal scores. It supplies the TempRAGEval benchmark. This is another substantive published temporal baseline.

### TempRetriever

Abdelrahman Abdallah, Bhawna Piryani, Jonas Wallat, Avishek Anand, and Adam Jatowt. 2026. *TempRetriever: Fusion-based Temporal Dense Passage Retrieval for Time-Sensitive Questions*. WSDM 2026, pages 5–15. DOI: 10.1145/3773966.3777938.

- Author repository: https://repository.tudelft.nl/record/uuid:d1da3322-0cf6-41a6-b837-1396d8132e00
- Preprint: https://arxiv.org/abs/2502.21024

It learns temporal representations and fuses them with semantic embeddings. It evaluates archival and NobelPrize questions. This provides context for learned temporal retrieval. It does not establish equivalence with a supersession compiler.

## Database foundation

Christian S. Jensen and Richard T. Snodgrass. 1999. *Temporal Data Management*. IEEE TKDE 11(1):36–44. DOI: 10.1109/69.755615.

- Author copy: https://www2.cs.arizona.edu/~rts/pubs/TKDEJan99.pdf

Valid time concerns the modeled world. Transaction time concerns database records. A publication date need not equal a fact's effective date. Use these established terms. Do not claim the time distinction as new.

Richard Snodgrass and Ilsoo Ahn. 1985. *A Taxonomy of Time in Databases*. SIGMOD, pages 236–246. DOI: 10.1145/318898.318921.

## Recommended contribution boundary

This assessment follows the inspected papers and source code.

1. Define the observable pairwise replacement predicate separately from real-world truth.
2. Compile its all-cutoff decisions into minimal direct witnesses.
3. Prove exactness for arbitrary nontransitive pair decisions.
4. Bound changes caused by one pair-decision error.
5. Compare component closure, direct invalidation, and exact-key latest selection with identical pair decisions.
6. Test multi-answer histories using full answer sets.

Graphiti already supplies the core earliest invalidation primitive. Strong novelty needs a result beyond renaming that primitive. An empirical failure analysis can motivate the new guarantee. A comparison only against the old code's component closure cannot establish superiority over current temporal memory systems.

## Two-clock extension

The proposed extension uses valid time and arrival time. Its candidate witnesses define upper-right regions in this plane. Keeping only nondominated boundaries is a standard skyline operation.

Stephan Börzsönyi, Donald Kossmann, and Konrad Stocker. 2001. *The Skyline Operator*. ICDE, pages 421–430. DOI: 10.1109/ICDE.2001.914855.

- Primary paper: https://cse.hkust.edu.hk/~raywong/reading/paper/skyline.pdf

Potential novelty concerns the connection to noisy pair decisions and the resulting guarantees. Neither two-clock semantics nor Pareto pruning should be presented as new. A full bitemporal database can preserve historical belief states. Compare the extension against a single mutable endpoint, rather than against all bitemporal storage.

## Full TempLAMA recovery

The official README links the preprocessed Google files. Both the official test split and the Yova mirror were downloaded.

- Official test: https://storage.googleapis.com/gresearch/templama/test.json
- Mirror: https://huggingface.co/datasets/Yova/templama/resolve/main/test_with_aliases.json
- Official README: https://raw.githubusercontent.com/google-research/language/master/language/templama/README.md

Both files contain 34,963 records. Of these, 8,723 contain multiple distinct answers. The maximum answer count is seven. Thus, taking only `answer[0]` changes the benchmark's semantics.

Files and hashes are in `work/external/sources.json`. Answer-count results are in `work/audit/templama_full_answer_audit.json`. The mirror has no README at the requested path. The Google code license is preserved separately. Do not infer a dataset-specific license from a code license.

## Submission rules

Official pages accessed on 2026-10-06:

- ACL 2027 CFP: https://2027.aclweb.org/calls/main/
- ARR CFP: https://aclrollingreview.org/cfp
- Submission checklist: https://aclrollingreview.org/authorchecklist
- Format: https://acl-org.github.io/ACLPUB/formatting.html
- Style: https://github.com/acl-org/acl-style-files

ACL 2027 lists January 4, 2027 as the final ARR deadline. The deadline uses anywhere-on-Earth time. Conference commitment details remain pending.

Long submissions permit eight content pages. Limitations, references, and appendices fall outside that limit. A dedicated Limitations section is mandatory. Put it after the conclusion and before references. Appendices follow references and normally use two columns. The paper must remain self-contained.

Use A4 paper, the official ACL template, and its review option. Do not alter template spacing. Figures and tables must remain readable. Acknowledgements are omitted from anonymous submissions. Supplementary files must also be anonymous. Disclose writing and coding assistance in the responsible-research checklist. The final paper can include the acknowledgement details.

ARR requires material needed to assess novelty and technical correctness in the main body. A limitation that changes a headline claim cannot be hidden in an appendix.

The current service policy requires a qualified designated reviewer for guaranteed review. Otherwise, the submission enters a lottery. Authors need complete OpenReview profiles. These administrative fields require author action.

Official style files were downloaded without modification into `work/acl_template/`. Its provenance file records URLs, source commit, and hashes.
