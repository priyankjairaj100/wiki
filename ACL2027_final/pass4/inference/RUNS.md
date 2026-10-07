# Fourth-pass completed reader runs

All 238 planned reader generations completed.
They cover 71 questions across 60 articles.
The frozen memberships define 710 logical method conditions.
Identical prompts share one deterministic model response.

| Cohort | Questions | Articles | Conditions | Generations | Parsed responses |
|---|---:|---:|---:|---:|---:|
| Primary human sample | 60 | 55 | 600 | 193 | 118 |
| Context-disagreement diagnostic | 11 | 9 | 110 | 45 | 32 |

The cohorts share four articles and no questions.
The diagnostic selects context disagreements without answer labels or reader outputs.
Its selection record is `human_diagnostic/original_freeze.json`.

## Fixed reader

The model is the official Qwen2.5-3B-Instruct Q4_K_M artifact.
Its revision is `7dabda4d13d513e3e842b20f0d435c732f172cbe`.
Its SHA256 is `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`.
The runtime is llama.cpp b11435.
The model uses the Qwen Research License, dated September 19, 2024.
The runtime uses the MIT License.
The source bundle includes both licenses and excludes model weights.

All final requests use temperature zero, seed 1729, and 96 output tokens.
They use no prompt cache or JSON grammar.
The server uses four CPU threads and a 2,048-token context.
Both prompt batch sizes equal 512 tokens.
CPU polling is disabled.
`provenance/primary_reader_freeze_final.json` fixes these settings.

The instruction text matches the third pass.
Source subjects and relations were added before fourth-pass QA inference.
The fields describe source-derived claims and exclude extracted answers.
Every temporal method receives the same metadata schema.
The input adaptation preserves each frozen prompt exactly.

The tokenizer checked all 238 prompts before generation.
The largest input contains 1,311 tokens.
The largest reservation contains 1,423 tokens, including output and a 16-token margin.
No input requires context truncation.

## Completed execution

The primary batch takes 4866.59 seconds of summed request time.
Its median request takes 22.77 seconds.
The diagnostic batch takes 989.92 seconds.
Its median request takes 19.41 seconds.
These timings come from a shared CPU environment.
They exclude asset downloads, setup, generic smoke tests, and interrupted infrastructure attempts.

Every output row includes the exact request, complete response, timing, and pinned model identity.
The runner flushes each completed output to disk.
Both output manifests pass independent file-hash checks.
The local summarizer verifies all 238 request hashes without answer labels.

```bash
python pass4/inference/download_assets.py
python pass4/inference/run_jsonl_final.py \
  pass4/inference/human/reader_input.jsonl \
  reproduced_primary.jsonl \
  --threads 4 --context 2048 --batch 512 --ubatch 512 --max-tokens 96
python pass4/inference/run_jsonl_final.py \
  pass4/inference/human_diagnostic/reader_input.jsonl \
  reproduced_diagnostic.jsonl \
  --threads 4 --context 2048 --batch 512 --ubatch 512 --max-tokens 96
```

The primary outputs have SHA256 `2ae23748fc863e8d1a66f6ca5ba5a816a9cdd6cc0008a606a80b4d05b2ef58ab`.
The diagnostic outputs have SHA256 `433a8d5b455fe295d92de054816624ad2af8d53ad553efb031337bd912ff0088`.
`provenance/completed_runs.json` records the final counts and checks.

## Parsing

The parser remains `pass3/protocol/parse_reader.py`.
It accepts a complete JSON object or one complete JSON code fence.
It rejects narrative prefixes, invalid types, invalid evidence indices, and unfinished generations.

The primary batch has 55 invalid JSON responses and six invalid evidence lists.
Fourteen primary responses reach the output limit.
The diagnostic batch has five invalid JSON responses and eight unfinished responses.
All failures produce empty predicted answers and remain in their method denominators.
No response is repaired or excluded.

These parser counts refer to distinct generations.
The scoring reports expand them through the frozen method memberships.
A separate descriptive audit distinguishes changes between valid answers from changes involving parser failures.

## Preserved setup history

The generic smoke files use constructed examples without benchmark labels.
Two initial QA attempts completed no responses during resource contention.
Their logs and interruption records remain in `human/interrupted_*`.
Constructed prompts selected the final resource settings.
All benchmark generations use the same final configuration.
The original runners and successive freeze records remain available for audit.
