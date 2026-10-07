# Final technical and story review

This review covers the current pass-4 manuscript before the pending reader results.
It proposes only changes that clarify the actual contribution or recover useful space.
No manuscript files were edited by this reviewer.

## Assessment

The manuscript now has a coherent contribution as a paper about guarantees for temporal evidence selection.
Its strongest result is the combination of exact support compilation, context stability, and constructive alternative timelines.
The refinement frontier and stable prefix turn that guarantee into practical decisions.
The hardness result explains why this useful decision remains tractable despite a harder neighboring problem.

The title-aware retrieval gains establish a stronger usable front end.
They do not carry the novelty claim for the temporal method.
The main text correctly separates those gains from certificate outcomes.

The source-grounded Warburg example now appears before the equations.
That substantially improves the entry path.
The reader first sees what a changed context means, then learns how the compiler detects it.

The paper should retain this central story through the final reader update.
The reader experiment should answer whether the changed evidence affects answers.
It should not turn the paper into an unsupported accuracy-superiority claim.

## Two technical corrections applied during this review

### Counterworld construction

Location: `sections/refinement.tex`, construction paragraph after Theorem 3.

The previous sentence incorrectly placed every other event before the pivot or after the supporting time.
Only accepted incoming replacement events require that placement.
Equality with the pivot is also allowed.

The current replacement is correct:

> We place every accepted replacement no later than c or after a supporting query time.

The appendix now makes the same restriction explicitly.

### Replay complexity with fallback evidence

Locations: `sections/method.tex`, compilation complexity paragraph;
`sections/refinement.tex`, replay paragraph;
`sections/appendix_refinement.tex`, construction complexity paragraph.

The number of modeled events differs from the number of ranked excerpts.
Fallback excerpts can greatly outnumber modeled events.
An entire ranking replay must include their scan.

The current definitions resolve this correctly:

- n counts modeled events, including hidden end events.
- N counts ranked excerpts, including fallback items.
- Assignment construction takes O(n).
- Full context replay takes O(n+m+N).

## Remaining high-value replacements

### 1. Define the fixed gate independently of its date condition

Location: `sections/theory.tex`, first paragraph.

Current:

> A fixed text gate G(d,c) accepts a direct replacement when d occurs strictly after c.

This sentence makes the fixed gate sound date-dependent.
The activity equation separately enforces the strict date condition.

Replace with:

> A fixed text gate G(d,c) records whether d can replace c.

No additional explanation is required.
The equation and following equal-date sentence already specify the temporal condition.

### 2. State independence in plain language before the product notation

Location: `sections/theory.tex`, immediately before the definition of Omega.

Current:

> The allowed assignments form the product

Replace with:

> Each timeline independently chooses one date per range:

Keep the existing product expression.
This states the exact model without introducing a caveat paragraph.

### 3. Explain the easy/hard boundary through joint eligibility

Location: `sections/refinement.tex`, opening of “A tractability boundary.”

Replace its first two sentences with:

> Possible support concerns one claim at a time.
> Possible context membership also depends on which higher-ranked claims coexist.

These sentences explain why the hardness result does not contradict the simple support formulas.
They are shorter than the current opening.
The theorem then states the decision problem precisely.

The distinction also prevents readers from treating the possible-support context as a jointly realizable timeline.
A union of individually possible claims need not occur together.
The paper need not add another warning about this fact.
The proposed two-sentence contrast expresses the substantive reason directly.

### 4. Remove annual snapshot semantics from the main entry path

Location: `sections/sources.tex`, opening paragraph and date-types table.

The current main experiment uses occurrence bounds and explicit lifetimes.
Annual snapshot observations now appear only in the archived-control appendix.
Introducing them on the first pages adds a third temporal concept before readers need it.

Replace the opening with:

> The source interface separates occurrence precision from state duration.
> An occurrence date says when a state began.
> A duration gives separate start and end dates.
> Table 1 shows their different representations.

Use the existing table cross-reference instead of a literal table number.
Move the snapshot row and annual-observation sentence to the existing annual-control appendix.
Keep both remaining rows.

This is the best remaining cut because it improves focus and recovers table space.

## Optional small cuts if the reader table needs room

These cuts remove repeated statements without weakening a result.

- `sections/sources.tex`, “All temporal policies receive identical pair decisions.”
  The matched-control protocol states this in its operational context.
- `sections/sources.tex`, final sentence of “Support tags.”
  The preceding text already defines modeled support and fixed fallback eligibility.
- `sections/method.tex`, the three opening compilation sentences.
  The theory formulas and complete pseudocode already specify initialization and pair updates.
  The subsection can open with the figure reference and deterministic tie rule.

Retain the two-witness sharpness example.
It demonstrates a claimed lower bound with almost no notation overhead.
Retain the main Set Cover proof if the reader results fit after the preceding cuts.
It makes the computational separation inspectable within the eight-page body.

## Final technical judgment

I found no further mathematical failure in the stated model.
The support proof correctly distinguishes guaranteed support somewhere from a common certainly active time.
The context theorem correctly uses the fixed complete ranking.
The refinement theorem states a necessary frontier condition, not minimum-cost date clarification.
The Set Cover reduction correctly treats the context budget as part of the input.
The explicit-end reduction correctly requires separated independent bounds.

The practical claim is now precise: uncertainty can be localized to evidence selection and explained through replayable timelines.
That claim should remain the paper's organizing principle.
