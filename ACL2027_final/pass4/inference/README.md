# Fourth-pass reader runtime

The reader uses the official Qwen2.5-3B-Instruct Q4_K_M artifact.
The runtime remains llama.cpp b11435 on CPU.
`provenance/assets.json` pins the repository revision and both asset hashes.
The official model uses the Qwen Research License, dated September 19, 2024.
The license and upstream model card are included.
Weights remain outside the source bundle.

The inference interface matches the third pass.
It uses temperature zero, seed 1729, and no prompt cache.
Reader jobs retain their exact frozen prompt strings.
The instruction text matches the third pass.
The fourth pass adds source subjects and relations to modeled excerpt metadata.
These source-derived fields are shared across methods.
They do not include an extracted answer or value.
The amendment preceded all fourth-pass QA inference.
`provenance/primary_reader_freeze_v2.json` records this change.
`provenance/primary_reader_freeze_final.json` records the final resource settings.
The original freeze remains available.
The frozen reader output limit is 96 tokens.
No JSON grammar is added.
The response parser remains the pipeline's existing parser.
It accepts complete JSON or one complete JSON code fence.
It rejects narrative prefixes, invalid fields, and truncated responses.
All failures remain in the denominator.

```bash
python pass4/inference/download_assets.py
python pass4/inference/adapt_jobs.py FROZEN_JOBS.jsonl READER_INPUT.jsonl
python pass4/inference/run_jsonl_final.py READER_INPUT.jsonl READER_OUTPUT.jsonl --threads 4 --context 2048 --batch 512 --ubatch 512 --max-tokens 96
```

`ACL2027_INFERENCE_CACHE` can set an external asset directory.
The default directory is beside the project root.
The server and HTTP client run within one process tree.
Do not start concurrent model servers on the shared CPU.
Each output row stores the exact request and full response.
The runner flushes each completed row to disk.
An adjacent manifest stores file hashes, runtime properties, and decoding settings.
Resume verifies the completed requests before skipping them.

## Generic smoke

`smoke_input.jsonl` contains three constructed prompts.
None contains benchmark questions or answer labels.
The longest input uses the unchanged reader instruction with fictional museum excerpts.
The long request has 1,028 prompt tokens and finishes in 20.77 seconds.
Its response correctly identifies Nora Vale and excerpt 3.
One short source request ignores the JSON instruction and reaches its 64-token limit.
That failed response remains in the smoke output.
A separate eight-worker CPU job overlaps this failed request.
Smoke timings therefore do not estimate isolated throughput.
The JSON summary records each request's exact timings and finish reason.
These examples only verify the runtime interface.
They are not benchmark or extraction results.

## Final resource settings

The shared machine has an eight-GiB cgroup memory limit.
Two initial QA attempts completed no responses during severe resource contention.
Their logs and interruption manifests remain under `human/interrupted_*`.
Neither attempt contributes an answer or score.

Constructed generic prompts determined the final resource settings.
Two four-thread requests finished in 40.21 and 47.99 seconds.
An eight-thread comparison required 50.39 seconds for prompt processing alone.
The final runner uses four threads and disables CPU polling.
It uses a 2,048-token context and 512-token prompt batches.
The prompt batch and microbatch sizes both equal 512.
The model, prompt strings, decoder, output limit, and parser did not change.

Before generation, the runner applies the model chat template and tokenizer.
It checks every primary and diagnostic prompt against the context limit.
The largest input contains 1,311 tokens.
The largest reservation contains 1,423 tokens, including output and a safety margin.
All 238 planned prompts fit the final context without truncation.

`run_jsonl.py` preserves the original smoke runtime.
`run_jsonl_resource.py` preserves the first resource amendment.
`run_jsonl_resource_v4_candidate.py` preserves the generic resource calibration.
`run_jsonl_final.py` runs all final benchmark requests.
The candidate and final source files are byte-identical.

## Completed benchmark runs

All 238 planned generations completed.
`RUNS.md` documents both cohorts and the exact replay commands.
`provenance/completed_runs.json` records final hashes, counts, and model identity.
The primary cohort has 193 generations for 600 method conditions.
The diagnostic has 45 additional generations for 110 conditions.
The cohorts contain 71 distinct questions across 60 articles.
The fixed parser accepts 150 distinct responses.
All 88 parser failures remain in the scoring denominators.
