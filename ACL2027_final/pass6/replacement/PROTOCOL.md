# Source-derived replacement challenge

This diagnostic tests directed replacement on source-derived records.
It does not estimate corpus prevalence, extraction accuracy, or QA accuracy.

## Freeze before outcome evaluation

Use only the saved development and test paragraph exports from TimeQA.
Do not read question text, answer labels, reader outputs, or retrieval scores.
Exclude all articles in the existing exposure registry and the latest source audit.
Previous lost audit membership is incomplete, so unseen status is not claimed.
Select every remaining paragraph with an explicit succession cue and two distinct calendar years.
The cue vocabulary is succeeded, successor, replaced, replacing, replacement, took over, and handed over.
Retain every candidate and record every acceptance or rejection.
A paragraph qualifies only if source text establishes two dated holders of one exclusive position.
The replacement relation must be explicit or be an explicitly ordered succession list.
Do not infer replacement from role equality alone.
Do not invent an old holder's start date.
Preserve the full paragraph, literal offsets, date precision, and the directed edge provenance.
Manual source annotation can resolve local pronouns and grammar.
Records remain a separate audited diagnostic, not output from the primary adapter.

## Evaluation

Freeze accepted records before certificate outcome evaluation.
Each dated start uses its literal calendar precision as a closed date interval.
Retain all directed pairs from accepted paragraphs.
Use source order as the fixed rank and evaluate k=1 and k=5.
For each successor, form three point queries at its earliest date, interval midpoint, and latest date.
Deduplicate identical queries within each record.
Use a fixed fallback record below all modeled claims so context changes remain visible.
Compare possible and guaranteed support with the existing implementation.
The interval control removes replacement edges but retains all other records and dates.
Enumerate critical boundary worlds from lower and upper dates, query boundaries, and adjacent days inside each date interval.
For small cases enumerate the full Cartesian grid of these critical dates.
Independently replay active intervals and compare existential and universal masks.
Save each world, query, rank, context, certificate, and disagreement.
Report all accepted records, all rejected candidates, and all query outcomes.

Natural two-successor examples are reported only when source text supplies two directed incoming edges.
Controlled interventions, if needed, are reported separately and never called source facts.
