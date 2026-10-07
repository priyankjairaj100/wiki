# Central story

The strongest story is **when uncertain dates can change a reader's evidence**.
It turns date uncertainty into an exact operational decision.
A system either certifies its ranked context or returns two timelines that change that context.
This is stronger than another date filter or a latest-value retrieval policy.

The compiler supplies the mathematical foundation.
Two source witnesses per claim answer every point and period query.
The ranking test then identifies which unresolved dates actually matter.
Lower-ranked uncertainty can remain unresolved without changing the reader's context.
This creates a practical use for the theorem beyond classifying every claim.

The paper should lead with this use case:

> Sources often give years instead of exact dates. A reader still needs a short evidence context.
> The system identifies when that uncertainty changes the selected evidence.
> If it does, the system exposes two concrete timelines and their different contexts.

The exact source bounds and fixed replacement policy define the guarantee.
Place these assumptions in the mathematical setting.
They are part of the problem definition, rather than defensive prose.

# Concrete rewrite priorities

1. Put context stability before the compact witness theorem in the introduction.
2. Use the natural Warburg example below to explain the decision.
3. Introduce possible and guaranteed evidence with that example before symbols.
4. Present two outputs: an unchanged-context certificate or two replayable timelines.
5. Keep the witness theorem as the efficient engine behind those outputs.
6. Separate source extraction from temporal execution in the architecture and method.
7. Include explicit ends through the lifecycle adapter as an operational extension.
8. Keep unparsed source text available to the reader.
9. Report extraction coverage, extraction errors, and compiler behavior as separate measurements.
10. Move the extensive annual-answer audit to the appendix.

The current introduction spends too much space on multiple valid answers.
That issue motivates correct replacement inputs but does not explain the new theorem.
The TempLAMA latest-value comparison therefore should not lead the abstract.
A latest-batch baseline already resolves the annual coverage issue.

The current method repeats the support interpretation and locality result several times.
Merge those repetitions into one definition and one corollary.
Use the recovered space for the constructive certificate and its cost.

The current results mostly evaluate baseline policies outside the new compiler.
The revised results should first answer four direct questions:

- Does compiled selection match exhaustive execution?
- How often does date uncertainty reach a retained context?
- Can the system replay both contexts when certification fails?
- Which source events does the adapter cover without manual labels?

Report ranking and reader quality after those checks.
The latest-year baseline is useful and should remain prominent.
Its advantage means the compiler should act on a supplied relevance ranking.
The paper should not imply that exact temporal execution improves semantic ranking automatically.

The first three questions need real source cases and mechanical verification.
Constructed exhaustive tests can prove implementation agreement on finite instances.
They cannot establish extraction quality or benchmark gains.
The manuscript can state both facts briefly through clear experiment labels.

# Natural calibration case

`natural_context_case.json` contains exact source text, offsets, source dates, and executable results.
`build_natural_case.py` reproduces the case with the pass-2 compiler.

The source is the TimeQA development paragraph for the Warburg Institute.
Its passage ID is `72daf9756d91f4ce98b12937`.
The source states three successive directors:

| Director | Stated start | Source relation |
|---|---|---|
| Henri Frankfort | 1949 | Succeeded Saxl |
| Gertrud Bing | 1955 | Succeeded Frankfort |
| Ernst Gombrich | 1959 | Succeeded Bing |

The paragraph also says Bing joined the organization in 1922.
That date must not become her start as director.
This gives a useful source extraction check.

Use the illustrative query period **1 January 1954 to 30 June 1955**.
Frankfort has support under every allowed assignment.
Bing has support only when her appointment falls within the first half of 1955.
Gombrich has no support within the period.

The compiler therefore gives:

- Possible: Frankfort and Bing.
- Guaranteed: Frankfort.

Fix the illustrative ranking as Frankfort, Bing, then Gombrich.
A one-item context always contains Frankfort.
A two-item context depends on Bing's start date.

Two allowed timelines show the difference:

| Timeline | Frankfort starts | Bing starts | Gombrich starts | Two-item context |
|---|---|---|---|---|
| 1 | 1 June 1949 | 1 January 1955 | 1 June 1959 | Frankfort, Bing |
| 2 | 1 June 1949 | 31 December 1955 | 1 June 1959 | Frankfort |

All dates remain within the source's stated years.
Changing the ranking to Bing first also makes the one-item context unstable.
The possible evidence pool remains unchanged.
Thus uncertainty alone does not determine context stability.
The ranking and budget determine whether that uncertainty reaches the reader.

This is explicitly a **calibration case study**.
The source text is natural.
The query period, ranking, and timelines are chosen to explain the theorem.
They are not benchmark questions, learned rankings, or measured performance results.

# Architecture figure

The vector figure is `pass3/paper/figures/architecture.pdf`.
Its editable counterpart is `architecture.svg`.
The source is `pass3/data/draw_architecture.py`.

The upper flow preserves source spans, date bounds, direct succession, and unparsed evidence.
The lower inset shows the same possible pool under two budgets.
It uses an illustrative claim ranking and is separate from the natural calibration case.

Suggested caption:

> The lifecycle adapter preserves source dates and explicit succession.
> Two witnesses per claim determine possible and guaranteed support.
> Their ranked prefixes certify an unchanged context or expose two different contexts.
> Unparsed source text stays available to the reader.
> The illustrative inset shows uncertainty below the first context position but inside a two-item context.

# Claims to avoid

- Do not call the ten model-reviewed pilot clauses human annotations.
- Do not treat zero strict pairs as evidence that replacement detection succeeds.
- Do not report selected source histories as an independent QA benchmark.
- Do not label a planned contract end as an observed termination.
- Do not count proof tests as natural-data accuracy.
- Do not present the theory as a semantic guarantee for a learned extractor.

The central claims remain strong without those shortcuts.
They concern exact execution, compact certificates, and useful uncertainty decisions.
