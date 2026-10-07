# Editorial audit for pass 6

The central contribution is an exact decision about selected temporal evidence.
The practical output is a stable context or explicit dates that change its excerpts.
Retrieval quality and answer quality provide separate evaluations.

## Priorities

1. Exercise cross-claim replacement in a separate source-grounded challenge.
   The existing TimeQA tracks cannot measure that mechanism.
   All three recovered pairs belong to calibration articles.
   The 64 test instabilities use uncertain starts or explicit ends.
   Possible support selects the same excerpts as the interval control.
   Retain those facts when adding the challenge results.

2. Report corpus coverage before the conditional stability rate.
   The complete partition contains 3,178 questions.
   It includes 2,800 parsed all-fallback contexts, 245 modeled stable contexts, 64 modeled unstable contexts, and 69 unparsed questions.
   Thus 9.72% reach modeled contexts.
   Unstable modeled contexts represent 2.01% of all questions.
   Those percentages describe the current adapter and ranking.
   They do not estimate historical uncertainty across the corpus.

3. State the source grounding bottleneck in the main evaluation.
   Both learned variants use Qwen2.5-1.5B on the same six paragraphs.
   Their 87 returned records produce no accepted claim.
   The JSON-only variant omits 41 source quotes.
   The required-schema variant has 45 literal failures and one rejected interpretation.
   This result supports the source interface design.
   It does not establish a general limit for learned extraction.

4. Separate the ranking gain from the temporal decision.
   Title-aware ranking supplies the principal retrieval improvement.
   Temporal policies provide support masks and counterworlds under each fixed ranking.
   Avoid language implying that exact certificates cause the retrieval gain.
   The six fixed ranking variants already establish useful compatibility.

5. Give the reader a measured role.
   The existing primary temporal contrast changes no answers.
   Three diagnostic changes have valid responses under both policies.
   One of those changes improves strict F1.
   Eighty of 234 distinct requests fail the frozen parser.
   The main answer paragraph should show this denominator beside its answer-change count.
   A repaired reader must use a separate frozen run and preserve the existing outcomes.
   Grammar enforcement alone cannot correct semantic errors or prove model generality.

6. Lead the complexity section with the useful separation.
   The abstract currently omits the variable-budget condition.
   Replace its hardness sentence with these three sentences:

   > One scan certifies stability without computing every attainable context member.
   > Membership is NP-hard when the context budget varies; this result does not cover our fixed budget of five.
   > The certificate therefore avoids solving a harder neighboring problem.

   Do not claim that fixed-budget membership is polynomial for the complete model.
   The given reduction only loses its hardness implication when its cover budget becomes constant.

## Question wording screen

The frozen screen reads visible question strings only.
Its result is a wording count, not a semantic benchmark.
It flags 82 questions with start-event words.
They include 50 template questions and 32 human questions.
Seven flagged questions have modeled contexts.
Three of those contexts are unstable.
The remaining 3,096 questions lack an explicit predicate cue in this screen.
No question matches its explicit throughout or explicit overlap cues.
Words such as "from", "between", and "during" do not settle the quantifier.

The Helen Clark example uses the word "assume".
It therefore makes a poor lead example for the overlap predicate.
The Peter Beattie example provides a cleaner state question.
Its question asks which title he held in February 1998.
The selected paragraph dates his premiership to 1998 through 2007.
Saved witnesses start that event on February 1 or December 31, 1998.
These dates respectively include or exclude its excerpt.

The example file also preserves Sulzberger and Romme endpoint cases.
These examples were selected after results for explanation.
They do not form an independent evaluation sample.

## Modeling scope

Known order constraints can remove timelines from the independent product model.
A stable product-model certificate remains valid after such removal.
A product-model instability can disappear because its witnesses violate the additional order.
Measure both outcomes if adding an order-constrained check.

An appointment predicate concerns the occurrence date itself.
It differs from support at any time during the window.
A throughout predicate concerns support across the whole window.
It requires a different possible-support test.
The present wording screen does not assign either predicate automatically.

A date-dependent ranking also changes the problem.
The current theorem assumes one complete order before date filtering.
Six separately fixed rankings do not evaluate a ranking that changes with each timeline.
Use a separately named extension for any such experiment.

## Artifacts

- `WORDING_PROTOCOL.json`: rules recorded before classification.
- `coverage_wording_audit.py`: deterministic coverage and wording audit.
- `coverage_wording.json`: aggregate counts, track counts, examples, and input hashes.
- `question_wording.jsonl`: membership and matched wording for every question.
- `learned_extraction_audit.json`: independently recounted failure reasons and source hashes.
- `illustrative_unstable_examples.json`: original questions, source paragraphs, bounds, and saved contexts.

All semantic judgments in this audit are model-assisted.
No question answer, reference annotation, or reader output informs the wording screen.
The deterministic coverage audit reads saved retrieval records and mechanism flags.
