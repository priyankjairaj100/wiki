# Exact Certificates for Temporal Evidence

Current ACL 2027 manuscript and reproducible project, revision pass6.

- [Paper](deliverables/ACL2027_final_paper.pdf)
- [Overleaf bundle](deliverables/ACL2027_final_overleaf.zip)
- [Project instructions](ACL2027_final/README.md)
- [Current state](ACL2027_final/SESSION_STATE.md)
- [Revision notes](ACL2027_final/REVISION_NOTES.md)

## Restore and verify

Use Python 3.12. Restore compressed files before verification:

```bash
python restore_large_runs.py
cd ACL2027_final
python -m pip install -r requirements.txt
python verify_revision.py
```

Use `py` on Windows if required. Verification uses saved results and starts no model inference.
The restoration tool checks every original checksum before installing each file.

## Continue work

Read `ACL2027_final/SESSION_STATE.md` and `ACL2027_final/README.md` first.
The current manuscript is `ACL2027_final/pass6/paper/main.tex`.
Current implementations, results, and audit records are under `ACL2027_final/pass6/`.
Earlier directories preserve dependencies and historical runs.
The project manifest records 1,733 released files and their checksums.
The release verification passed against that exact manifest.
The repository excludes model weights and runtime binaries.
Rebuild submission bundles with `ACL2027_final/pass6/release/build_final_packages.py`.
