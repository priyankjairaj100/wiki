# Portable pass-4 verification

Run `python reproduce.py` from any directory after extracting the complete source bundle.
Install the pinned dependencies from `requirements.txt` first.
The verifier uses the project root containing its own source file.
The extracted folder may have any name.

The default command checks every release hash and the original 27-file algorithm freeze.
It checks the final reader resource amendment without hash exceptions.
It runs eleven current source tests and independently rescores both retrieval tracks.
Five retrieval metrics must match the primary scorer for all ten methods.
Three retrieval tables must reconstruct byte for byte in a separate copy.
Both complete reader batches receive execution audits and full rescoring.
The rebuilt reader summaries and per-question outputs must match their saved versions.
Descriptive answer-change audits must reproduce all 45 method contrasts for each reader cohort.
Both reader tables, presentation results, and build manifest must also reconstruct byte for byte.

Run `python reproduce.py --full` to also replay every saved context and alternative timeline.
This option uses the original independent audit and its strict input hashes.
A wrapper resolves historical absolute project paths to the extracted project root.
It does not change the original audit, manifests, or expected hashes.

Neither command downloads weights or starts model inference.
Saved server commands contain historical model paths for provenance only.
The execution audit checks their settings without opening those model paths.
Incomplete reader batches fail before either reader scorer runs.

Each invocation creates a unique directory below `reproduced_pass4`.
Its `verification.json` records the outcome and each completed check.
Its `verification.log` contains full subprocess output and any failure.
The table stage and rebuilt scores remain available for inspection.
Exclude `reproduced_pass4` from release packaging.

Verification establishes reproducibility of the saved evidence.
It does not rerun the language model or create new benchmark evidence.
