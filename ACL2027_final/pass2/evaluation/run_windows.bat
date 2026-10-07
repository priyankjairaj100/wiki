@echo off
setlocal
cd /d "%~dp0\..\.."
py pass2\evaluation\freeze_split.py || exit /b 1
py pass2\evaluation\run_full_benchmark.py || exit /b 1
py pass2\evaluation\audit_ambiguity.py || exit /b 1
py pass2\evaluation\audit_intervals.py || exit /b 1
py pass2\evaluation\audit_quality.py || exit /b 1
py pass2\evaluation\verify_matched_policies.py || exit /b 1
py pass2\evaluation\summarize.py || exit /b 1
echo Full benchmark evaluation completed.
