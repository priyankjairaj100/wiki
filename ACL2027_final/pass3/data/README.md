# Source evidence audit

TimeQA remains the best primary dataset for this pass.
It supplies original Wikipedia paragraphs and human questions.
It preserves year and month expressions in its annotations.
Extract dates from the source text, not from those annotations.

## Pass-3 files

| File | Purpose |
|---|---|
| `STORY_AND_CASES.md` | Central story and concrete manuscript changes |
| `dev_succession_candidates.jsonl` | Thirty paragraphs selected only through source cues |
| `dev_succession_selection.json` | Selection recipe and calibration article paths |
| `dev_succession_cases.json` | Nine qualitative histories with dated direct succession |
| `natural_context_case.json` | Executable Warburg calibration case with exact source spans |
| `natural_context_counterworlds.json` | Actual constructive algorithm applied to that case |
| `natural_context_case_from_adapter.json` | Same case from automatic source-only parser outputs |
| `pilot_extraction_audit.json` | Model-assisted review of ten frozen pilot clauses |
| `pilot_extraction_audit_pre_freeze.json` | Earlier calibration review that identified a value-boundary error |
| `learned_v2_semantic_audit.json` | Independent review of all grounded outputs from six learned extraction jobs |
| `succession_rule_semantic_audit.json` | Independent review of the separate deterministic succession parser |
| `draw_architecture.py` | Editable vector architecture figure generator |

The succession files contain no query labels or method outcomes.
Remove their articles from validation before using them for calibration.
`select_succession.py` reproduces their source-only selection.
`build_natural_case.py` verifies the illustrative context decisions.
`replay_adapter_case.py` repeats them using actual automatic parser outputs.

## TimeQA development audit

`dev_source_audit.json` contains ten manually inspected development examples.
`build_source_audit.py` reproduces the deterministic selection.
The examples use eight dated event starts and two completion-only descriptions.
One of those starts supplies only an upper bound.
Thus, seven examples support a bounded start for some source event.
This count is descriptive and is not an extraction accuracy score.

The source supports useful coarse dates:

- Gibson served in Parliament from 1997 to 2009.
- Hirschfeld held a London fellowship from 1978 to 1989.
- Court won election to Nedlands in March 1982.
- Sekula-Gibbs served on the Houston council from 2002 to 2006.

The source also shows important event attachment cases:

- Hoyer's 1966 degree date does not supply his enrollment start.
- Gardner's 1954 degree date does not supply her enrollment start.
- Guggenberger entered the navy **by** 1934. The source permits an earlier year.
- Dundas's source gives 1775. The gold question gives May 1775.
- A biography can date several roles, birth, and death within one paragraph.

The audit does not create replacement labels from temporal adjacency.
No selected paragraph explicitly replaces the value for its annotated relation.
Aguirre's paragraph contains an explicit party transition, but its question concerns an office.

## Independent option: TempReason

The official repository points to the author's public Hugging Face release.
We retrieved its L2 test set and recorded the revision and hash.
The author marks this release as CC BY-SA 3.0.
Preserve attribution when sharing the natural source text.

- Paper: https://aclanthology.org/2023.acl-long.828/
- Code: https://github.com/DAMO-NLP-SG/TempReason
- Data: https://huggingface.co/datasets/tonytan48/TempReason
- Revision: `1646dea364ac667dd6098646da7d6638de00cc71`

The set has 5,397 questions and 999 distinct natural contexts.
Use the `context` field for source extraction.
The `fact_context` field contains rendered knowledge-base facts.
It must not enter an experiment labeled as natural-source extraction.

Only 1,608 questions have an answer string inside their natural context after simple normalization.
This is a surface count, not a measure of temporal support.
An answer mention can describe another relation.
For example, Pelikan's biography mentions Concordia Seminary as his place of study.
One question asks about his employer during 1950.
The mention alone does not support that employment claim.

The source metadata gives sampled day-level dates.
The written questions usually ask about a month.
The pipeline must use the written query's date scope.

`prepare_tempreason.py` verifies the raw hash and creates two separate files:

- `tempreason_contexts.jsonl`: natural context and source identity.
- `tempreason_questions.jsonl`: published questions, answer labels, and date metadata.

The raw file has a `.json` extension but contains JSONL.
It occupies 67.5 MB because questions repeat full articles.
The deduplicated context file occupies 8.1 MB.

We did not select a performance subset using the answer containment count.
No TempReason method result is claimed in this pass.
It is a useful independent benchmark after source-support checks.

## Alternative checked

SituatedQA offers natural questions and temporal answer labels.
Its public task files do not provide matched source passages.
Its authors used a 2021 Wikipedia dump for retrieval.
The preprocessed corpus is available on request, according to the official repository.
It therefore adds more acquisition work than TimeQA or TempReason.

Source: https://github.com/mikejqzhang/SituatedQA

## Reproduce

```bash
python pass3/data/build_source_audit.py
python pass3/data/prepare_tempreason.py
```

The TimeQA audit uses the verified normalization from pass 2.
TempReason normalization needs Python's standard library only.
