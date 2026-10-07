# Independent review of the direct witness revision

Review date: 6 October 2026.

## Verdict

The direct witness compiler implements its stated semantics correctly.
The mathematical results hold under their stated assumptions.
The new experiments remove the old historical scorer's gold anchor.
Several reporting choices still determine whether the paper makes supportable claims.

This review inspected the theory, compiler, tests, evaluation scripts, source audit, and result cards.
It also inspected the original detector and historical interval code.
No manuscript sections existed when the initial review finished.

## Release requirements

| Priority | Finding | Required treatment |
|---|---|---|
| High | TempLAMA first-answer changes do not always retire the old answer. | Use complete source answer sets for primary TempLAMA relevance scores. |
| High | The source-set result card retains a condition named `oracle`. | Call it the first-answer mask, or omit it from source-set tables. |
| High | Historical gains against strong simple controls are small. | Do not claim consistent superiority over exact grouping or Text-CC. |
| High | Prefix accuracy counts still use first-answer labels. | Report mask differences, or rescore the retrieved claims against complete answer sets. |
| High | Earliest direct invalidation already appears in Graphiti. | Locate novelty in guarantees, compiler behavior, and measured closure failures. |
| Medium | TempLAMA `false_pairs` uses old single-value annotations. | Use verified cross-key pairs for error-specific claims. |
| Medium | The component baseline differs from the original implementation. | Name it Text-CC and describe its text-derived value comparator. |
| Medium | BM25 statistics use the full corpus at historical cutoffs. | State that prefix consistency concerns eligibility masks under a fixed ranking. |

## Mathematical assessment

### All-cutoff compilation

The interval identity is correct.
The earliest qualifying timestamp is sufficient for every finite cutoff.
Equal timestamps remain unordered.
Missing timestamps require the stated separate policy.

This identity is elementary once eligibility is defined through direct replacement.
It should support the method rather than carry the main novelty claim.

### Prefix consistency

The result is correct for fixed claim features and fixed pair predicates.
Claims with timestamps beyond the query cutoff cannot enter a qualifying pair.
Corpus-dependent feature updates can invalidate the argument.

The result concerns source timestamps, not data arrival order.
An arriving claim with an earlier timestamp can change an earlier evidence state.
Do not claim unconditional stability under late corrections or backdated records.

The retrieval ranking must remain fixed when comparing complete contexts.
Recomputing BM25 on a smaller corpus can change scores without changing any eligibility bit.

### Bounded influence

The older-endpoint bound is correct for changed ordered pair decisions.
The context bound is correct for one fixed ranking with deterministic tie handling.
A single parser edit can change many pair decisions.
A single timestamp edit can also change many pair decisions.
The theorem does not bound either edit by one affected claim.

The expected disagreement identity is also correct.
Its time interval excludes the larger boundary and includes the smaller boundary.
Queries must use the same timestamp axis in both compilers.

### Closure construction

The bridge construction correctly gives unbounded historical amplification.
It applies to component sorting over the specified replacement graph.
It does not establish failure for every temporal graph system.
It also does not establish average empirical accuracy superiority.

### Complexity

The stated cost includes posting visits and pair tests.
The worst case remains quadratic.
The linear output claim is correct.
Complete candidate blocking is required for equivalence.

## Compiler assessment

The compiler copies only claim ID, text, timestamp, and document ID.
It cannot access the supplied gold subject, relation, or value fields.
It processes timestamp batches before inserting that batch into the candidate index.
This prevents equal-time invalidation.

The first accepted timestamp closes each older claim.
Claims sharing that timestamp use lexicographic witness IDs.
Removing a closed claim from the index is safe for a fixed pair predicate.
The implementation retains current undated claims and excludes them from historical retrieval.

The default blocking rule is complete for the supplied gate.
Positive frame thresholds require a shared frame token for nonempty frames.
Empty frames share a separate candidate bucket.
Nonpositive thresholds use exhaustive candidate scanning.

No material compiler bug was found.
The public cutoff validator accepts Boolean values as numbers.
This is a minor interface inconsistency, not an experimental issue.

## Independent test execution

The certificate runner was executed again during this review.
All 13 constructed tests passed.
The runner checked 100 random predicate graphs and input permutations.
All ten packaged datasets matched the exhaustive direct oracle.
All ten datasets preserved the original current mask exactly.

The independent output is `work/audit/independent_certificate_tests.json`.
These tests establish implementation correctness under the stated semantics.
They are not benchmark observations.

## Experimental assessment

### Retrieval inputs and scoring

The new retrieval loop supplies only visible text and timestamps to inference.
Gold fields create questions and evaluate the returned evidence.
All conditions share the same BM25 ranking before their temporal operation.
This supports comparison of the temporal operations within this evaluation.

The primary outcomes are evidence-selection scores.
They are not generated-answer scores.
The source-set scorer correctly accepts every answer QID in the latest observed source state.
It preserves all frozen rankings and retrieved claim IDs.

The source states persist between observations and beyond the final observation within this evaluation.
That policy needs one clear description.
Historical probes come from the released first-answer transition dates.
They do not cover every original source state change.

### TempLAMA findings

The source audit exactly rebuilds all 747 released claims.
It finds 153 transitions where the old first-listed answer remains valid.
There are 447 released first-answer transitions altogether.
These counts invalidate a general retirement interpretation of those transition labels.

With complete answer sets, direct historical hit@1 is 98.21%.
Text-CC reaches 97.54%, and exact grouping reaches 98.43%.
The paired interval against Text-CC includes zero.
The paired interval against exact grouping also includes zero.

Direct current hit@1 is 94.67%.
Exact grouping reaches 88.33%.
The difference is 6.33 points, with a 95% interval from 3.33 to 9.33 points.
These intervals resample whole key clusters.

The strongest supported historical distinction is stability, not universal accuracy superiority.
The strongest current distinction is better selection than exact extracted-key grouping in this pool.

### Component comparison

The new component baseline forms components from the newest accepted direct edges.
It then finds the next distinct parsed value within each component.
The original interval implementation uses annotated values when they exist.
The original implementation also handles same-time values differently.

Therefore, the new baseline is a controlled text-only component implementation.
It is not an exact replay of the old historical method.
Its definition is reasonable for isolating closure effects.

### Prefix and sensitivity experiments

The prefix experiment holds BM25 fixed and compares eligibility masks.
Its mask differences do not depend on first-answer truth labels.
Those results remain valid after the source audit.

The stored prefix hit counts do depend on old labels.
Those counts need rescoring before source-set accuracy claims.

The sensitivity experiment deletes one observed accepted pair at a time.
It rebuilds the newest edge when another accepted witness exists.
This treatment correctly avoids deleting an entire claim or an entire detector rule.

The observed maximum amplification and average change counts answer different questions.
Direct compilation can have more total changes than closure in some datasets.
Do not claim uniformly fewer changes across all interventions.

Cross-key pair labels remain useful after the TempLAMA source audit.
The broader `false_pairs` category does not identify all false retirements.

### Reused reader results

The original lifecycle retriever filters only by the stale-ID set.
The new compiler reproduces that set exactly on the packaged corpora.
Therefore, archived current contexts remain unchanged when their base ranking remains unchanged.
This supports reuse of archived current reader results with explicit provenance.

The equality does not support reuse of archived historical reader claims.
It also does not repair first-answer labels in archived TempLAMA answer scores.
Those reader results need their original transition-task label or complete-answer rescoring.

## Useful strengths

- The historical retrieval path removes gold component selection.
- The compiler gives exact masks for arbitrary fixed pair predicates.
- Its error influence remains local to changed older endpoints.
- The engine preserves equal-time evidence and records a concrete replacement witness.
- The current mask equality supports efficient reuse of existing reader runs.
- The source audit detects a consequential mismatch between answer changes and retirement labels.
- The evaluation includes a strong exact-group temporal baseline.
- The archived inputs and new predictions support independent checking.

## Remaining scientific limits

The experiments use small released pools and development evaluations.
The central historical accuracy gain over strong controls is not established.
The proof alone does not establish a new temporal memory primitive.
The paper can still present a clear contribution through fixed-predicate stability and measured closure failures.
It should state that contribution directly and keep empirical claims specific.

## Final manuscript review

The completed sections were reviewed after the first report.
The manuscript addresses the major source-set and comparison issues identified above.
Its numerical claims match the checked result cards.

Two precise corrections remain important:

- Replace the context-slot claim with at most one removal and one insertion.
- Rename the dataset table's `Keys` column to `Query keys`.

The first correction matters because one inserted record can shift several ordered positions.
The theorem bounds set membership, not the number of changed positions.
The second correction distinguishes Wikidata's 33 query keys from its 73 corpus keys.

The historical single-answer subset was independently rescored using complete source sets.
Its reported scores remain unchanged.
Direct selection returns 55 correct first results among 57 probes.
Text-CC returns 54, while exact grouping returns 57.
Their stale-context counts are one, one, and eleven, respectively.

The current subset has one unpublished scoring difference.
Exact-group stale contexts decrease from 19 to 16 under source-set scoring.
The manuscript does not report this current subset count.

Minor wording corrections improve source precision:

- Distinguish national heads of government from heads of state when listing five RealProse families.
- Remove the claim that the dataset table supplies timestamps.
- Specify that source states persist after their final observation within the snapshot evaluation.
- Say the audit rebuilds texts and answer identifiers, since its comparison does not check claim identifiers.

The final review found no additional material mathematical or implementation error.
