# Revised reader execution

This study reuses the frozen question cohorts from pass 4.
The primary cohort has 60 questions and 600 method conditions.
The diagnostic cohort has 11 questions and 110 method conditions.
The diagnostic membership remains fixed after the source revision.

The revised contexts produce 234 distinct requests.
The primary cohort uses 194 requests.
The diagnostic cohort uses 40 requests.
Exact historical requests supply 166 responses.
The delta batch executes the remaining 68 requests.
These counts describe requests, not answer quality.

## Exact reuse

`reuse_manifest.json` records the request and execution identity.
`reader_lineage.jsonl` links each current request to its actual response.
A reusable request must match every serialized request field.
Its model weights, model revision, runtime commit, and execution settings must also match.
Metadata does not enter the model request.
The script retains each original response without changing its answer or failure status.

`prepare_reader.py` checks the complete historical batches before it constructs the delta.
`finalize_reader.py` checks all physical batches before it merges either current cohort.
It checks server flags, server logs, token counts, output coverage, and request hashes.
It also checks each merged record against its recorded source.
The merger does not generate answers.

## Executed model

The model is `Qwen/Qwen2.5-3B-Instruct-GGUF`.
Its revision is `7dabda4d13d513e3e842b20f0d435c732f172cbe`.
Its quantization is Q4_K_M.
The model SHA256 is `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`.
The runtime is llama.cpp b11435, commit `43fe9c64281ef735046adc025e9e7559a1f659a5`.

Each request uses temperature zero and seed 1729.
The output limit is 96 tokens.
The runtime uses four CPU threads and 2,048 context tokens.
The prompt batch and microbatch each contain 512 tokens.
The runtime uses one slot, no GPU layers, and zero polling.
It does not use a JSON grammar or prompt caching.
The tokenizer checks every delta request before generation.
The largest reservation is 1,384 tokens, including output and safety margin.

## Commands

Run these commands from the project root.
The first command obtains the immutable model and runtime assets.
Keep these large assets outside the submission package.

```bash
python pass4/inference/download_assets.py
python pass4/inference/run_jsonl_final.py pass5/inference/delta_input.jsonl NEW_OUTPUT.jsonl --threads 4 --context 2048 --batch 512 --ubatch 512 --max-tokens 96
```

Use a new output path for a new physical execution.
Do not overwrite the archived execution.
The complete saved study can be verified without model downloads.

```bash
python pass5/protocol/finalize_reader.py --verify-only --report reproduced_reader_verification.json
```

## Scoring

The parser and answer metrics remain unchanged from pass 3.
The scorer requires every question and every method.
Malformed and truncated responses become empty predictions.
They remain in the original denominator.
The diagnostic cohort measures answer sensitivity on previously selected questions.
It does not estimate population accuracy.
