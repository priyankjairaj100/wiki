# Final pass-4 checks

Run these commands from the project root.
They never start model inference.
Reader commands require completed output manifests.
Do not score a partial batch.

## Frozen inputs and resource history

```bash
python pass4/protocol/verify_freeze.py --output pass4/protocol/freeze_verification.json
```

Every original code and input hash remains mandatory.
The checker permits zero exceptions to the original 27-file freeze.
It separately verifies files linked by the final resource amendment.
The final runner is an additional file, not a replacement for a frozen retrieval dependency.
`audit_confirmation.py` therefore retains its strict input checks.
No resource exception is needed for its retrieval replay.

The previous resource linkage remains in `RESOURCE_AMENDMENT_v3.json`.
The final linkage is `RESOURCE_AMENDMENT.json`.
Both interrupted QA attempts produced zero completed responses.
The final runtime uses four threads, 2,048 context tokens, and batches of 512 tokens.
Both polling settings are zero.

## Independent retrieval and counterworld replay

These optional full reproductions repeat all saved context checks.
Their support oracle scans direct incoming events.
It does not call compiler or counterworld functions.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python pass4/protocol/audit_confirmation.py --folder pass4/pipeline/human --passages pass3/protocol/test_source_passages.jsonl --queries pass4/protocol/human_test_confirmation_queries.jsonl --output pass4/protocol/human_confirmation_audit.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python pass4/protocol/audit_confirmation.py --folder pass4/pipeline/validation --passages pass3/protocol/dev_source_passages.jsonl --queries pass4/protocol/dev_validation_queries.jsonl --output pass4/protocol/validation_confirmation_audit.json
```

## Actual reader execution

The audit checks complete job coverage, model identity, decoder settings, and executed server arguments.
It also checks runtime logs for four threads and 2,048 context tokens.
Every prompt must pass the recorded tokenizer check without truncation.

```bash
python pass4/protocol/audit_reader_run.py --outputs pass4/inference/human/reader_output.jsonl --jobs pass4/pipeline/human/reader_jobs.jsonl --output pass4/protocol/human_reader_execution_audit.json
python pass4/protocol/audit_reader_run.py --outputs pass4/inference/human_diagnostic/reader_output.jsonl --jobs pass4/pipeline/human_diagnostic/reader_jobs.jsonl --output pass4/protocol/diagnostic_reader_execution_audit.json
```

## Reader scoring

The primary scorer verifies the original 60-question sample hash.
The diagnostic scorer verifies all declared cohort memberships.
Both reuse the unchanged pass-3 parser and answer metrics.
No new inference is required.

```bash
python pass4/protocol/score_reader.py --jobs pass4/pipeline/human/reader_jobs.jsonl --outputs pass4/inference/human/reader_output.jsonl --membership pass4/pipeline/human/reader_memberships.jsonl --predictions pass4/pipeline/human/predictions.jsonl --labels pass3/protocol/human_test_confirmation_labels.jsonl --passages pass3/protocol/test_source_passages.jsonl --config pass4/protocol/config.json --output pass4/protocol/reader_primary_scored --track human_confirmation
python pass4/protocol/score_reader.py --jobs pass4/pipeline/human_diagnostic/reader_jobs.jsonl --outputs pass4/inference/human_diagnostic/reader_output.jsonl --membership pass4/pipeline/human_diagnostic/reader_memberships.jsonl --cohort-queries pass4/pipeline/human_diagnostic/queries.jsonl --predictions pass4/pipeline/human/predictions.jsonl --labels pass3/protocol/human_test_confirmation_labels.jsonl --passages pass3/protocol/test_source_passages.jsonl --config pass4/protocol/config.json --output pass4/protocol/reader_diagnostic_scored --track context_sensitive_diagnostic
```

A portable release verifier can run the freeze check, execution audits, and both scorers by default.
Reserve the two complete retrieval replays for its full verification option.

## Interpretation of answer changes

These descriptive checks separate valid parsed changes from changes involving parser failure.
They leave all frozen metrics and denominators unchanged.

```bash
python pass4/protocol/audit_answer_changes.py --predictions pass4/protocol/reader_primary_scored/predictions_with_reader.jsonl --output pass4/protocol/reader_primary_change_audit.json
python pass4/protocol/audit_answer_changes.py --predictions pass4/protocol/reader_diagnostic_scored/predictions_with_reader.jsonl --output pass4/protocol/reader_diagnostic_change_audit.json
```
