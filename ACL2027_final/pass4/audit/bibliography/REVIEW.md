# Pass 4 bibliography audit

Audit date: 6 October 2026. Scope: ten cited 2025–2026 works or source records in the sections included by `pass4/paper/main.tex`. Only primary publication pages, papers, and the official Graphiti repository support this review. Unused bibliography entries and earlier database literature were excluded. No bibliography or manuscript files were edited.

## Finding

One metadata correction was found and applied by the parent agent: the Re3 author order differs between ACL Anthology's landing-page metadata and the published PDF. The bibliography initially followed the landing page. The PDF title page, confirmed visually, orders the authors as **Jiawei Cao; Jie Ouyang; Mingyue Cheng; Zhaomeng Zhou; Yupeng Li; Zirui Liu; Chunli Liu; Shijin Wang**. The corrected entry now places Chunli Liu after Zirui Liu. ACL Anthology's own metadata guidance identifies the PDF as authoritative. The title, year, venue, pages, DOI, and cited technical description are correct. The parent's independent verification and edit are recorded in `root_correction.json`.

All other checked metadata match their primary records. All ten nearby descriptions are supported. No fabricated or mismatched reference was found.

## Finding matrix

| Citation key | Primary identity and metadata | Nearby claim checked | Assessment |
|---|---|---|---|
| `rasmussen2025zep` | Rasmussen, Paliychuk, Beauvais, Ryan, and Chalef. *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*. 2025. arXiv **2501.13956**, v1, 20 January 2025. [Record](https://arxiv.org/abs/2501.13956); [paper](https://arxiv.org/html/2501.13956v1). | Historical relationships and direct contradictory evidence can end an earlier fact. Section 2.2.3 sets the contradicted edge's invalidation time from the invalidating edge's validity time. | Metadata and claim match. This supports treating direct invalidation as prior art. |
| `graphiti2026source` | Graphiti contributors. Official `edge_operations.py`, accessed 6 October 2026. [Source](https://github.com/getzep/graphiti/blob/main/graphiti_core/utils/maintenance/edge_operations.py). No publication DOI or arXiv ID applies. | Earlier contradictory edges receive the later edge's start as their end. The code checks temporal overlap and a strictly later `valid_at`; the new-edge path searches later invalidation candidates in sorted order. | Claim matches. The bibliography labels an access-year source snapshot, not an invented publication. The URL is mutable, but the bundled snapshot and its SHA-256 provide the evaluated version. |
| `yadav2026memstrata` | Neeraj Yadav. *Temporal Validity in Retrieval Memory: Eliminating Stale-Fact Errors for AI Agents over Evolving Knowledge*. 2026. arXiv **2606.26511**, v1, 25 June 2026. [Record](https://arxiv.org/abs/2606.26511). | MemStrata applies deterministic supersession to structured keys. The abstract describes a deterministic subject–relation–object supersession rule in a bitemporal ledger. | Author, title, year, ID, and claim match. |
| `li2025erase` | Belinda Z. Li, Emmy Liu, Alexis Ross, Abbas Zeitoun, Graham Neubig, and Jacob Andreas. *Language Modeling with Editable External Knowledge*. Findings of NAACL 2025, pp. 3070–3090. Anthology **2025.findings-naacl.168**; DOI **10.18653/v1/2025.findings-naacl.168**. [Record](https://aclanthology.org/2025.findings-naacl.168/). | ERASE edits stored facts as documents arrive. Its abstract describes incrementally deleting or rewriting knowledge-base entries when adding a document. | Metadata and claim match. “Stored fact histories” is a fair summary here, without implying exact uncertainty certificates. |
| `zerhoudi2026nuggetindex` | Saber Zerhoudi, Michael Granitzer, and Jelena Mitrović. *NuggetIndex: Governed Atomic Retrieval for Maintainable RAG*. SIGIR 2026. arXiv **2604.27306**, v1; DOI **10.1145/3805712.3809687**. [Record](https://arxiv.org/abs/2604.27306); [paper](https://arxiv.org/html/2604.27306v1). | Atomic records carry source-span provenance, validity intervals, and lifecycle states. Functional and multivalued predicates receive different conflict handling. Sections 3.1–3.2 describe all four elements. | Authors including the accent, title, year, venue, DOI, and both claims match. |
| `cao2026re3` | *Re3: Relevance & Recency Retrieval for Mitigating Temporal Hallucination*. ACL 2026 long papers, pp. 25735–25760. Anthology **2026.acl-long.1180**; DOI **10.18653/v1/2026.acl-long.1180**. [Record](https://aclanthology.org/2026.acl-long.1180/); [authoritative PDF](https://aclanthology.org/2026.acl-long.1180.pdf). | Fact grouping, conflict filtering, and temporal relevance. The abstract specifies temporal encoding and conflict-aware recency filtering. Figure 1 explicitly groups extracted facts into slots before filtering obsolete versions. | **Author order corrected by parent after independent PDF verification.** Other metadata and technical claim match. |
| `chen2026defuzzrag` | Ling-Chun Chen, Hsi-Wen Chen, and Ming-Syan Chen. *DeFuzzRAG: Handling Fuzzy Time Expressions for Temporal Robustness in Retrieval-Augmented Generation*. AAAI 2026, 40(36), pp. 30252–30260. DOI **10.1609/aaai.v40i36.40276**. [Record](https://ojs.aaai.org/index.php/AAAI/article/view/40276); [paper](https://ojs.aaai.org/index.php/AAAI/article/view/40276/44237). | Adaptive temporal granularity and overlap filtering of inferred document scopes. Page 30255 explicitly describes both operations and an iterative retrieval/filtering loop. | Full metadata and the precise claim match. |
| `wang2026iarag` | Xiaoman Wang, Yaoze Zhang, Wenzhuo Fan, Hongwei Zhang, Ding Wang, Guohang Yan, Song Mao, Botian Shi, Yunshi Lan, and Pinlong Cai. *IA-RAG: Interval-Algebra-Driven Temporal Reasoning for Dynamic Knowledge Retrieval*. 2026. arXiv **2606.06044**, v1, 4 June 2026. [Record](https://arxiv.org/abs/2606.06044); [paper](https://arxiv.org/html/2606.06044v1). | Interval representations and refinement of uncertain event dates. The abstract and Section 3 introduce interval event units and subgraph time tightening. | Full author order, title, year, ID, and claim match. The abstract URL initially failed to open; primary arXiv HTML supplied verification. |
| `lau2025tarag` | Kwun Hang Lau, Ruiyuan Zhang, Weijie Shi, Xiaofang Zhou, and Xiaojun Cheng. *Reading Between the Timelines: RAG for Answering Diachronic Questions*. 2025. arXiv **2507.22917**, v1, 21 July 2025. [Record](https://arxiv.org/abs/2507.22917). | Evidence retrieval across timelines. The abstract describes a retriever balancing topic and temporal relevance to cover the requested period. | Authors, title, year, ID, and claim match. |
| `an2026fresco` | Sohyun An, Hayeon Lee, Shuibenyang Yuan, Chun-cheng Jason Chen, Cho-Jui Hsieh, Vijai Mohan, and Alexander Min. *FRESCO: Benchmarking and Optimizing Re-rankers for Evolving Semantic Conflict in Retrieval-Augmented Generation*. 2026. arXiv **2604.14227**, v1, 14 April 2026. [Record](https://arxiv.org/abs/2604.14227); [paper](https://arxiv.org/html/2604.14227v1). | Obsolete evidence versus temporally current but insufficient passages. Section 3.1 explicitly includes both candidate categories. | Authors, title, year, ID, and claim match. |

## Reproducible source note

The existing Graphiti provenance record is `pass2/baselines/vendor/PROVENANCE.json`. Its full source SHA-256 is `b773ff4489968af2a996d5074e679cab9806cc0904a7ff9f2aecc74382325abe`. A commit-pinned URL would improve the bibliography's link stability if a verified commit is later recovered. This is a provenance improvement, not a failed claim check.

## Web retrieval IDs

These identify this audit's retrievals; URLs above remain the durable references.

| Source | Retrieval IDs |
|---|---|
| Zep | `turn65view0`, `turn74view0` |
| Graphiti source | `turn67view2`, `turn72view1` |
| MemStrata | `turn65view1` |
| ERASE | `turn67view1` |
| NuggetIndex | `turn65view2`, `turn69view0` |
| Re3 | `turn67view0`, `turn70view0`; visual title-page check `turn71view0` |
| DeFuzzRAG | `turn66view3`, `turn70view2`, `turn73view0`, `turn73view1` |
| IA-RAG | `turn68academia5`, `turn70view1`, `turn74view1` |
| TA-RAG | `turn66view1` |
| FRESCO | `turn66view2`, `turn68view1`, `turn69view1` |
