# Primary-source citation audit

Checked all 24 references against primary records on 7 October 2026.
No invented references or unsupported method attributions remain.
Full third-party papers stay outside the release package.

| Reference key | Primary source | Locator and result |
|---|---|---|
| `lewis2020rag` | [Primary source](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html) | Abstract, author list, and paper Section 2. Completed all 12 authors. The source supports retrieval before generation. It does not establish historical filtering. |
| `robertson1995bm25` | [Primary source](https://pages.nist.gov/trec-browser/trec3/proceedings/) | Okapi at TREC-3 entry; original paper pp. 109–126. Retained NIST SP 500-225 and 1995. The older TREC HTML incorrectly says 500-226. NIST assigns paper DOI 10.6028/NIST.SP.500-225.routing-city. Our BM25 parameters are implementation choices. |
| `dhingra2022templama` | [Primary source](https://aclanthology.org/2022.tacl-1.15/) | Publisher record and paper Section 2.1, pp. 258–259. Added DOI 10.1162/tacl_a_00459 and URL. TempLAMA uses annual temporal contexts. It does not directly label exact occurrence bounds. |
| `vu2024freshllms` | [Primary source](https://aclanthology.org/2024.findings-acl.813/) | Publisher metadata and abstract. Added full Findings venue, publisher, pages 13697–13720, DOI and URL. FreshQA and FreshPrompt support the changing-information-access claim. |
| `chen2021timeqa` | [Primary source](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/1f0e3dad99908345f7439f8ffabdffc4-Abstract-round2.html) | Original PDF title page and dataset construction section. Completed proceedings title and volume. The HTML record duplicates William Yang Wang. The original PDF correctly lists three authors. Passage examples also require the bundled source paragraphs. |
| `liska2022streamingqa` | [Primary source](https://proceedings.mlr.press/v162/liska22a.html) | Publisher metadata and abstract. Completed PMLR series, volume 162, pages 13604–13622 and URL. Fourteen authors verified. The benchmark studies adaptation to dated news. |
| `lau2025tarag` | [Primary source](https://arxiv.org/abs/2507.22917) | Version 1, Section 4 and Figure 1. Added arXiv DOI and URL. Five authors verified. TA-RAG uses normalized temporal intervals, time filtering and temporal context structuring. |
| `an2026fresco` | [Primary source](https://arxiv.org/abs/2604.14227) | Version 1, Section 3, Problem Formulation. Added arXiv DOI and URL. Seven named authors verified. Candidate pools include obsolete informative passages and current insufficient passages. |
| `wang2026iarag` | [Primary source](https://arxiv.org/abs/2606.06044) | Version 1, abstract and Sub-graph Time Tightening method. Added arXiv DOI and URL. Ten named authors verified. The method uses interval events, Allen relations and boundary tightening. |
| `rasmussen2025zep` | [Primary source](https://arxiv.org/abs/2501.13956) | Version 1, Section 2.2.3. Added arXiv DOI. Five authors verified. New contradictory edges can close existing validity intervals while preserving histories. |
| `yadav2026memstrata` | [Primary source](https://arxiv.org/abs/2606.26511) | Version 1, Sections 4.1–4.2. Added arXiv DOI. Single author Neeraj Yadav verified. Deterministic supersession uses normalized subject-relation keys. |
| `cao2026re3` | [Primary source](https://aclanthology.org/2026.acl-long.1180.pdf) | Published PDF title page, Figure 1 and conflict-aware filter section. Kept published PDF author order. The HTML record gives a different order. Pages 25735–25760 and DOI match. Figure 1 supports grouping, conflict filtering and temporal relevance. |
| `graphiti2026source` | [Primary source](https://github.com/getzep/graphiti/blob/7514b4467d1f20f87bcf463fdb35e9f61086d263/graphiti_core/utils/maintenance/edge_operations.py) | resolve_edge_contradictions, lines 538–573; resolve_extracted_edge, lines 754–847. Pinned the cited source to an immutable commit. Downloaded 36,703 bytes. SHA256 b773ff4489968af2a996d5074e679cab9806cc0904a7ff9f2aecc74382325abe. Direct contradictory edges trigger temporal invalidation. |
| `chen2026defuzzrag` | [Primary source](https://ojs.aaai.org/index.php/AAAI/article/view/40276/44237) | Published PDF p. 30255, temporal intent extraction and alignment filtering. Publisher metadata confirms three authors, volume 40(36), pages 30252–30260 and DOI. The method adapts granularity and checks overlap with inferred document intervals. |
| `zerhoudi2026nuggetindex` | [Primary source](https://arxiv.org/html/2604.27306v1) | Sections 3.1–3.2.2, Algorithms 1–2; author repository citation block. Added published pages 2286–2296 and ACM publisher. Changed URL to the published DOI landing page. Source supports provenance, intervals, lifecycle states and relation cardinality. |
| `anselma2013indeterminacy` | [Primary source](https://iris.unito.it/handle/2318/143137) | Institutional author repository and original author manuscript abstract. Title, three authors, volume 25(12), pages 2880–2894, 2013 and DOI verified. A separate author list contains volume/page typos. The manuscript studies valid-time uncertainty and compact representations. |
| `fan2012currency` | [Primary source](https://www.research.ed.ac.uk/en/publications/determining-the-currency-of-data-2/) | Institutional publication record and abstract. Added pages 25:1–25:46. Three authors, volume 37(4), article 25, 46 pages and DOI verified. The 2011 PODS paper is a different version. |
| `amarilli2017order` | [Primary source](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.TIME.2017.4) | Published PDF Definition 7, p. 4:6; introduction pp. 4:1–4:2. Added publisher. Definition 7 defines possibility and certainty for an entire ordered output. Do not use Definition 8 as its locator. Four authors and volume 90 verified. |
| `li2025erase` | [Primary source](https://aclanthology.org/2025.findings-naacl.168/) | Publisher abstract and author list. Six authors, pages 3070–3090, Findings NAACL 2025 and DOI verified. ERASE deletes or rewrites stored entries when new documents arrive. |
| `hua2008ranking` | [Primary source](https://www.cse.unsw.edu.au/~lxue/sigmod08.pdf) | Original paper title page and abstract; author institution record https://scholars.duke.edu/publication/1530940. Four authors, pages 673–686, SIGMOD 2008 and DOI verified. The method computes records with threshold probability of top-k membership. |
| `amarilli2017topk` | [Primary source](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICDT.2017.5) | Publisher metadata and abstract. Added LIPIcs volume 68, publisher and URL. The method studies unknown numerical values subject to order constraints. It estimates rankings under a possible-world distribution. |
| `karp1972reducibility` | [Primary source](https://link.springer.com/chapter/10.1007/978-1-4684-2001-2_9) | Original chapter p. 94, Main Theorem and Set Covering problem 6; original book front matter at https://link.springer.com/content/pdf/bfm:978-1-4684-2001-2/1. Author, title, year, pages 85–103 and DOI verified. Original front matter names Miller and Thatcher as editors. Bohlinger is associate editor. Plenum Press is the original publisher. |
| `qwen2024model` | [Primary source](https://qwenlm.github.io/blog/qwen2.5/) | Official September 19, 2024 announcement and exact GGUF artifact license. Model family, 3B variant and release year verified. The pinned 3B artifact uses the Qwen Research License, not Apache 2.0. Execution settings come from this project. |
| `feng2023ranking` | [Primary source](https://www.vldb.org/pvldb/vol16/p1346-feng.pdf) | Published PDF title page, abstract and uncertainty model. Three authors, PVLDB 16(6), pages 1346–1358, 2023 and DOI verified. The paper bounds results of ranking, top-k and SQL window queries. |

The second audit uses a separate reviewer and report.
Run `python pass5/audit/citations/first/build_inventory.py` after final manuscript edits.
The inventory checks missing keys, uncited entries, duplicate keys and audit coverage.

NIST's publication record confirms the April 1995 date and report number 500-225.
Source: https://www.nist.gov/publications/overview-third-text-retrieval-conference-trec-3

Evidence correction: A search snippet wrongly associated `T-SB.pdf` with front matter.
The second auditor opened that PDF and found a separate statistical analysis paper.
We removed that locator. The bibliography remains unchanged.
