# Third-pass inference runs

All dataset runs use the pinned model and runtime in `provenance/assets.json`.
No evaluation labels enter the inference requests.

## Primary reader pilot

The source jobs contain 52 distinct prompts.
Each prompt comes from `pass3/pipeline/pilot_final/reader_jobs.jsonl`.
The adaptation copies `job_id` to `id` and preserves each prompt exactly.
It retains all remaining job fields in `metadata`.
Each request uses at most 96 output tokens.
The decoder uses temperature zero, seed 1729, and no JSON grammar.

```bash
python pass3/inference/run_jsonl.py \
  pass3/inference/pilot_reader/reader_input.jsonl \
  pass3/inference/pilot_reader/reader_output.jsonl \
  --threads 8 --max-tokens 96 --resume
```

## Completion-sensitive mechanism diagnostic

This batch contains 22 additional distinct prompts.
It covers nine questions selected for differences between date completion rules.
This declared diagnostic cohort is separate from the primary reader pilot.
The pipeline membership file also refers to six primary reader outputs.
The adaptation and decoder match the primary run.

```bash
python pass3/inference/run_jsonl.py \
  pass3/inference/mechanism_reader/reader_input.jsonl \
  pass3/inference/mechanism_reader/reader_output.jsonl \
  --threads 8 --max-tokens 96 --resume
```

## Source-only extraction calibration

The extraction agent froze 30 jobs before inference.
Textual succession cues selected the passages from development sources.
Selection did not inspect questions or answer labels.
The jobs and selection manifests record the complete protocol.
The initial interface required JSON syntax but did not enforce the field schema.
The first six outputs omitted the required quote fields.
The team stopped that development run and retained its six outputs.
`raw_outputs.partial_manifest.json` records the stop and its reason.
The second interface planned to enforce the schema on the same 30 passages.
The team stopped it after six completed outputs because source grounding still failed.
Both partial manifests retain the planned and completed counts.
The six completed inputs from each interface have separate replay files.
Neither calibration result is a benchmark result.
This interface correction did not use benchmark answers or performance.
The decoder retains each job's fixed token limit.
The extractor preserves literal quotes for deterministic source validation.

```bash
python pass3/inference/run_jsonl.py \
  pass3/extraction/learned/jobs_schema_v2_completed_six.jsonl \
  pass3/extraction/learned/raw_outputs_schema_v2.jsonl \
  --threads 8 --max-tokens 1400 --resume
```

Run these batches sequentially on the shared CPU environment.
Each output has an adjacent manifest and runtime log.
`--resume` skips completed requests after checking their exact settings.

## Completed run counts

- Primary reader: 52 of 52 requests, with 52 normal stops.
- Mechanism reader: 22 of 22 requests, with 22 normal stops.
- Extraction V1: six completed requests from 30 planned passages.
- Extraction V2: six completed requests from the same 30 planned passages.
- The two extraction runs each stopped during the seventh request.
- Interrupted extraction responses were not included in the result files.
