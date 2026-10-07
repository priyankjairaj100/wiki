# Source replacement challenge

Twenty audited source paragraphs supply 45 claims and 33 directed replacement edges.
These paragraphs come from 18 articles.
Seventeen paragraphs belong to the test export; three belong to development.
Twenty-five edges are consecutive replacements.
Eight edges follow explicit ordered succession lists.
The source records preserve 51 calendar dates and 174 checked literal spans.

Two model-assisted reviewers screened a fixed panel of 384 paragraphs.
The first panel contained 128 paragraphs and yielded seven accepted graphs.
A fixed additional panel contained 256 paragraphs and yielded thirteen accepted graphs.
The expansion preceded all certificate outcomes.
All source decisions remain available, including uncertain and rejected candidates.
Known exposed examples were excluded.
Incomplete prior audit history prevents a claim that every article was unseen.

## Independent-date verification

Each successor supplies point queries at its earliest, middle, and latest date.
Duplicate dates within each record are removed.
This creates 73 queries, evaluated with two context budgets.
Source order supplies the fixed ranking.
Literal source clauses supply evidence excerpts.
The fixed fallback follows every modeled claim.
No original TimeQA question or answer enters this diagnostic.

| Budget | Queries | Possible context differs from interval control | Interval says stable; replacement says unstable | Stable with replacement |
|---|---:|---:|---:|---:|
| 1 | 73 | 30 | 42 | 24 |
| 5 | 73 | 31 | 0 | 24 |

Every context difference also changes the displayed literal excerpts.
The compiler matches all 388 support judgments from an independent exact calendar oracle.
These judgments cover 194 claim-query pairs.
The oracle searches all integer dates through complete difference-constraint branching.
The lazy selector matches all 146 decisions.
All 98 unstable decisions have two feasible worlds with different displayed contexts.
These are decisions across two budgets, rather than 98 independent source questions.

## Primary source-order comparison

Both methods retain identical calendar bounds, explicit ends, and known source orders.
The interval control removes only cross-claim replacement edges.

| Budget | Queries | Possible context differs from interval control | Interval says stable; replacement says unstable | Stable with replacement |
|---|---:|---:|---:|---:|
| 1 | 73 | 33 | 42 | 25 |
| 5 | 73 | 34 | 0 | 25 |

All 96 unstable decisions have feasible witness pairs that obey every source order.
Every witness pair changes the literal excerpts.
The comparison uses the same accepted records and the same 73 point queries.


One Levadia paragraph has overlapping 2001 start bounds.
Bondarenko starts in 2001, and Rautiainen replaces him in November 2001.
Their source order rules out Bondarenko starting after Rautiainen.
Applying that order removes three possible-support judgments for Bondarenko.
The affected dates are 30 November 2001, 1 January 2003, and 16 January 2003.
This change resolves one additional stable query at each budget.
The constrained model therefore certifies 25 of 73 queries at each budget.
This comparison measures the effect of a real source constraint.
It does not claim that the linear independent-date compiler enforces arbitrary constraints.

## Interpretation

The challenge demonstrates retrieval decisions that depend on source-derived replacement edges.
It directly separates replacement-aware support from interval overlap.
The challenge does not estimate the prevalence of these events in TimeQA.
Its queries deliberately probe successor boundaries.
Its graphs use reviewed annotations, rather than the primary automatic adapter.
The fixed ranking uses source order, rather than relevance scores.
It does not test answer accuracy or establish a broad retrieval improvement.
The separate controlled study tests the sharp need for two distinct witnesses.

## Reproduction

Run from the project root:

```bash
python pass6/replacement/run_challenge.py --out /tmp/replacement-rerun
python pass6/replacement/derive_order_view.py --out /tmp/replacement-order-rerun
python pass6/replacement/verify_saved.py --output /tmp/replacement-verification.json
```

`accepted_freeze.json` fixes accepted membership and the original runner dependencies.
`implementation_corrections.json` records a counter lookup repair and a protocol description correction.
Neither correction changes source membership, queries, certificates, or the oracle.
`verification.json` records the complete successful rerun and output hashes.
