# Structured reader replication

This directory preserves a second reader study on unchanged questions and contexts.
The study uses all 234 distinct prompts from the final pass-5 reader cohort.
These prompts cover 600 primary conditions and 110 diagnostic conditions.

The model remains Qwen2.5-3B-Instruct, with the original Q4_K_M weights.
The runtime remains llama.cpp b11435.
Each request uses greedy decoding, seed 1729, and no prompt cache.
A JSON schema constrains answers to nonempty strings and evidence to valid excerpt numbers.
The completion budget increases from 96 to 512 tokens.
The context limit increases to 4,096 tokens.
The question text and source excerpts remain unchanged.

`protocol.json` records the protocol before execution.
`pilot_result.json` records the six deterministic pilot requests.
The pilot tests output validity and truncation. It does not select settings from answer scores.
`scheduling_amendment.json` records the later use of two independent servers.
Each server retains four threads and one request slot.
The first 22 completed responses remain intact.
The remaining requests follow the frozen queue, with alternate assignment to the two servers.

The initial run was interrupted during one pending request.
That request had no completed output. The request remained in the frozen queue.
The final merge requires exactly one completed response for every request.
The merge also checks every exact request against its frozen input.

## Offline verification and scoring

Run this command from the project root:

```bash
PYTHONDONTWRITEBYTECODE=1 python pass6/reader/analyze.py --output /tmp/structured_reader_check
```

The command uses saved responses. It does not load model weights or generate new answers.
It requires all 234 completed responses and the final execution manifest.
It checks each prompt, schema, decoder setting, and runtime record.
It uses the unchanged parser and answer scores from the previous study.
It scores every question and method condition.

Compare `result_card.json` between the saved analysis and a fresh analysis.
This file excludes path-dependent provenance fields.
The full summary preserves those fields separately.
The command also produces request validity, answer changes, and answer cardinality results.

`dependencies.json` lists the saved source files needed for analysis.
The Python modules also use their existing project imports.
SciPy supports the token-based secondary answer score.
The primary exact match and strict set F1 retain their previous definitions.

## Raw records

- `reader_input.jsonl`: all frozen requests.
- `initial_output.jsonl`: completed responses before the scheduling change.
- `worker_0_output.jsonl` and `worker_1_output.jsonl`: later physical execution records.
- `reader_output.jsonl`: the checked merge in the original request order.
- `server_*.json` and `server_*.log`: server settings and execution logs.
- `execution_manifest.json`: hashes and records for the completed study.
- `human/` and `human_diagnostic/`: fixed memberships and complete scoring results.

The diagnostic keeps its original eleven questions.
Its selection used earlier context differences. It is not a random test sample.
The schema checks response format. It does not prove that cited excerpts support an answer.
