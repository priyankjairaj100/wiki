# Local inference

This directory provides real CPU inference for the third research pass.
The model is Qwen2.5-1.5B-Instruct, using the official Q4_K_M weights.
The runtime is the official llama.cpp Ubuntu x64 CPU release, b11435.
Both artifacts have fixed revisions and checked SHA-256 hashes.

## Setup

Use Python 3.12 or later on Linux x86-64.
No Python package installation is required.

```bash
python pass3/inference/download_assets.py
```

The download requires about 1.14 GB.
Model weights and runtime binaries remain in `cache/`.
Exclude this directory from the research source bundle.
Keep the download script, manifests, prompts, responses, and licenses.

## Batch generation

```bash
python pass3/inference/run_jsonl.py INPUT.jsonl OUTPUT.jsonl --threads 8 --max-tokens 128
```

Each input row requires `id` and either `prompt` or `messages`.
Optional fields are `system`, `max_tokens`, `response_format`, `stop`, and `metadata`.
The runner does not use other fields to construct prompts.

```json
{"id":"q1","system":"Use only the passage.","prompt":"Passage: ...\nQuestion: ...","max_tokens":64}
```

The output stores each exact request and each complete server response.
It also stores the response text, timing, model identity, and request hash.
The adjacent manifest records the server command, configuration, and file hashes.
The adjacent log preserves runtime diagnostics.

The runner uses temperature zero and seed 1729.
It disables prompt caching and processes one request at a time.
This improves reproducibility on the same runtime and hardware.
Floating-point differences can still affect output across hardware.
Use `--resume` after interruption.
Resume checks each completed request against the current input.

## Python interface

```python
from pass3.inference.run_jsonl import LocalRunner

with LocalRunner(log_path="results/reader.server.log") as model:
    result = model.generate({"id": "q1", "prompt": "..."}, max_tokens=64)
```

The class starts and stops its own local server.
This also supports execution environments with isolated network namespaces.

## Smoke test

`smoke_input.jsonl` contains two constructed prompts for runtime verification.
They are not research benchmark examples.
`smoke_output.jsonl` contains the actual generated outputs.
The reading prompt returned `Mira Shah` in 0.96 seconds.
The extraction prompt returned the requested five fields in 4.41 seconds.
The extraction output used 47 tokens at 12.23 tokens per second.
These timings exclude model loading and hash verification.

## Provenance

- Model repository: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
- Model revision: `91cad51170dc346986eccefdc2dd33a9da36ead9`.
- Model license: Apache-2.0, copied in `provenance/Qwen-LICENSE`.
- Runtime release: https://github.com/ggml-org/llama.cpp/releases/tag/b11435
- Runtime commit: `43fe9c64281ef735046adc025e9e7559a1f659a5`.
- Runtime license: MIT, copied in `provenance/llama-LICENSE`.
- The release API response includes the runtime archive digest.
- The model card and server documentation are retained with the source files.

This small model enables a local pilot.
It does not establish performance for larger readers or unquantized models.

## Dataset runs

`RUNS.md` lists the frozen inputs, output paths, and reproduction commands.
The reader completed 52 primary requests and 22 mechanism requests.
Both extraction interfaces stopped after six source calibration requests.
Their partial manifests record the decisions and preserve all completed outputs.
