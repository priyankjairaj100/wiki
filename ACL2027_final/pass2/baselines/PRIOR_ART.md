# Added prior-art checks

Primary sources accessed on 2026-10-06.

## Existing temporal policy

Graphiti already closes a fact at the earliest later contradictory candidate.
The preserved source implements forward closure and backward invalidation.
The comparison fixes candidate extraction to isolate this policy.

Source: https://github.com/getzep/graphiti/blob/main/graphiti_core/utils/maintenance/edge_operations.py

Re3 groups extracted facts by subject and relation before selecting recent support.
The latest-batch baseline tests this common policy under identical extraction.
It is not a reproduction of Re3's trained retrieval system or extraction model.

Paper: https://aclanthology.org/2026.acl-long.1180/

MemStrata already uses deterministic structured supersession with temporal validity.
The paper studies changing single-value facts and supplies a bitemporal ledger.
No claim should present deterministic retirement or historical storage as a new primitive.

Paper: https://arxiv.org/abs/2606.26511

## Completeness and negation

The open-world distinction is established knowledge representation theory.
Positive facts do not imply that absent facts are false.
Explicit completeness information can make negative conclusions sound.

Darari, Fariz; Nutt, Werner; Pirro, Giuseppe; Razniewski, Simon. 2018.
*Completeness Management for RDF Data Sources*.
ACM Transactions on the Web 12(3), article 18, pages 1–53.
DOI: https://doi.org/10.1145/3196248

Darari, Fariz; Nutt, Werner; Razniewski, Simon; Rudolph, Sebastian. 2020.
*Completeness and soundness guarantees for conjunctive SPARQL queries over RDF data sources with completeness statements*.
Semantic Web. DOI: https://doi.org/10.3233/SW-190344

Primary publisher page: https://journals.sagepub.com/doi/10.3233/SW-190344

Razniewski, Simon; Arnaout, Hiba; Ghosh, Shrestha; Suchanek, Fabian. 2021.
*On the Limits of Machine Knowledge: Completeness, Recall and Negation in Web-scale Knowledge Bases*.
Proceedings of the VLDB Endowment 14(12):3175–3177.
DOI: https://doi.org/10.14778/3476311.3476401

Primary paper: https://www.vldb.org/pvldb/vol14/p3175-razniewski.pdf

## Cardinality constraints

OWL 2 defines minimum, maximum, and exact cardinality over distinct values.
Section 8.3 explains why distinctness must itself be established.
Cardinality-based exclusion therefore needs an explicit relation bound and distinctness evidence.
The logical inference is established prior art.

Primary standard: https://www.w3.org/TR/2012/REC-owl2-syntax-20121211/

## Assessment

A contribution can measure incorrect retirement caused by mismatched source contracts.
It can supply an inference interface that carries explicit completeness evidence.
It can quantify tradeoffs between stale retention and valid-value deletion on real sources.
Those contributions require operational evidence beyond restating open-world semantics.

Complete TempLAMA snapshots cannot alone establish superiority over exact latest-batch selection.
The comparison must preserve complete answer sets and use the same parsed evidence.
Partial observations need separate treatment because omitted values remain unidentified.
