# Exact Certificates for Temporal Evidence

Final ACL 2027 project: **When Do Uncertain Dates Change Retrieval? Exact Certificates for Temporal Evidence**.

The paper has eight main pages. References and appendices follow those pages.

## Paper

- [Final paper](deliverables/ACL2027_final_paper.pdf)
- [Overleaf bundle](deliverables/ACL2027_final_overleaf.zip)
- [Project instructions](ACL2027_final/README.md)
- [Current project state](ACL2027_final/SESSION_STATE.md)
- [Revision notes](ACL2027_final/REVISION_NOTES.md)

## Restore and verify

Use Python 3.12. Large files use gzip compression for upload through the GitHub app.
The following command restores their exact original bytes. It checks each checksum before installation.

```bash
python restore_large_runs.py
cd ACL2027_final
python -m pip install -r requirements.txt
python verify_submission.py
```

Use `py` instead of `python` if required on Windows.
The default verification uses saved results. It does not start model inference.
Use `python verify_submission.py --full` to replay retrieval decisions.

## Continue work

Read `ACL2027_final/SESSION_STATE.md` and `ACL2027_final/README.md` first.
The current manuscript is `ACL2027_final/pass5/paper/main.tex`.
The current implementation, results, citation audits, and run records are under `ACL2027_final/pass5/`.
Earlier directories preserve dependencies and project history.
The release contains 68 new reader executions and 166 exact response reuses.
The complete history contains 306 reader executions.
The project manifest records all 1,480 released files and their checksums.
The recorded verification passed before this upload.

The project includes model download instructions and checksums. It excludes model weights and runtime binaries.
The anonymous review supplements can be rebuilt with `ACL2027_final/pass5/release/build_final_packages.py`.
