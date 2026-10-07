# Human diagnostic example review

Retain Helen Clark with explicit retrieval-window framing.
No alternative among the eleven cases combines a clean state question with a relevant, correctly grounded pivot.

This review inspected source paragraphs, extracted claims, selected contexts, and replayed date assignments.
It did not read answer labels, reader generations, reader scores, or generated-answer outcomes.
No adapter, frozen output, query, or benchmark record changed.

## Recommended presentation

Use the actual query identifier `/wiki/Helen_Clark#P39#annotation0` when reporting the observed run.
Its exact wording is:

> What governmental role did Helen Elizabeth Clark assume from 1989 to Aug 1989?

The verb *assume* can ask when a role began.
The source instead describes a tenure that began in August 1987.
Therefore, this case should illustrate evidence selection, without claiming the pivot answers the question.

Suggested main-body wording:

> A human query gives a January–August 1989 window for Helen Clark.
> The source dates her Conservation tenure from August 1987 until January 1989.
> An end on January 31 retains this excerpt; an end on January 1 removes it.
> Both assignments satisfy the extracted month bounds and produce different retrieved contexts.

If a figure needs a short query label, use “Helen Clark, January–August 1989 retrieval window.”
Do not replace the benchmark query with an invented state question.
An illustrative state question must be labeled as an illustration, separate from the recorded benchmark run.

## Exact evidence

- Source article: `/wiki/Helen_Clark`.
- Passage: `c63cbf6eea11fd4272979e95`.
- Pivot claim: `c8f2adbf96cb7f443ce4bc48`.
- Atomic clause offsets: `[167, 241)`.
- Query bounds: `[1989-01-01, 1989-08-31]`.
- Start bounds: `[1987-08-01, 1987-08-31]`.
- End bounds: `[1989-01-01, 1989-01-31]`.

Literal atomic clause:

> She served as Minister of Conservation from August 1987 until January 1989

The source paragraph names Clark before the pronoun.
The subsequent sentence states her appointment as Health Minister in January 1989.
No extraction step equates those two events.
The direct end event alone controls the Conservation pivot.

The support world uses start `1987-08-31` and end `1989-01-31`.
The exclusion world uses start `1987-08-01` and end `1989-01-01`.
Under the half-open lifetime model, the latter has no support inside the query window.
Both complete assignments replay to different selected contexts.
The entering unit is Clark's preceding Cabinet-minister paragraph fragment, at offsets `[0, 166)` in the same passage.
This is a context-change example, not an answer-correction example.

## All eleven candidates

| Question | Query semantics | Pivot and source assessment | Decision |
|---|---|---|---|
| `/wiki/Walter_Veltroni#P102#annotation1` | Natural membership question. | Different person: Giovanni Spadolini. Correctly grounded government role, but unrelated holder and relation. | Reject as main example. |
| `/wiki/Helen_Clark#P39#annotation3` | Election-event wording. | Different person: Annette King. Correctly grounded government roles, but wrong holder. | Reject as main example. |
| `/wiki/Atlético_Madrid#P286#annotation5` | Natural coaching-state question. | Different team and coach: Steve Guppy at Colorado Rapids. The paragraph contradicts its own 2012 endpoint with departure in November 2011. | Reject as main example. |
| `/wiki/Attaphol_Buspakom#P54#annotation4` | Natural team-membership question. | Different person and relation: Steele Hall in federal parliament. Correctly grounded political membership. It does not answer the sports question. | Reject as main example. |
| `/wiki/Mbaye-Jacques_Diop#P102#annotation1` | Natural party-membership question. | Same person, different relation: commission presidency. Correct role and 1996–2000 duration. The pivot does not establish political-party membership. | Reject as main example. |
| `/wiki/Katherine_Maher#P108#annotation3` | Natural workplace-state question. | Same person and broadly relevant employment. The extracted workplace is truncated to Washington. The full source says Washington, D.C.-based Access Now. | Reject as main example. |
| `/wiki/Zambia#P35#annotation1` | Natural leadership-state question. | Same country, different relation: one-party political regime. Correct state and dates. The selected pivot omits the named leaders from the surrounding paragraph. | Reject as main example. |
| `/wiki/Helen_Clark#P39#annotation0` | The verb assume suggests a role-start event. | Same person and governmental role. Correctly grounded Conservation tenure. The January 1989 endpoint creates an intelligible context boundary. | Retain with retrieval-window framing. |
| `/wiki/Louis_Francis_Salzman#P551#annotation0` | Natural residence-state question. | Same person, different relation: teaching at a school. Teaching in Harpenden does not establish residence there. The source separately dates a move to Cambridge. | Reject as main example. |
| `/wiki/Walter_Veltroni#P102#annotation3` | Natural party-membership question. | Same person, different relation: government office. Correctly grounded cabinet roles. Those roles do not directly establish party membership. | Reject as main example. |
| `/wiki/Campaign_Against_Homophobia#P488#annotation2` | Chairing-state question with a source typo. | Different organization and person: Kem Sokha and the Human Rights Party. Correctly grounded party leadership. It concerns neither the Polish organization nor its chair. | Reject as main example. |

## Reproducible evidence record

`selection_records.jsonl` retains each question, exact source paragraph, claim spans, two compact world records, and the review.
`selected_helen_clark.json` contains the recommended case.
The full assignments remain in `pass4/pipeline/human/counterworlds.jsonl`.
All eleven pivots occur in their supporting context and disappear from their excluding context.
The selection review did not use reader outcomes.
