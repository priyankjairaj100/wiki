#!/usr/bin/env python3
"""Verify this release; optionally rerun both saved CPU retrieval experiments."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--full", action="store_true", help="Also rerun the two CPU retrieval experiments (about 20 minutes in the recorded environment).")
args = parser.parse_args()
manifest = json.loads((ROOT / "MANIFEST.json").read_text())
for name, expected in manifest["files"].items():
    path = ROOT / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit("Saved file verification failed: " + name)
print(f"Verified {len(manifest['files'])} saved files.", flush=True)

out = ROOT / "reproduced"
stage = out / "workspace"
if stage.exists():
    raise SystemExit("Move or remove reproduced/workspace before running again.")
stage.mkdir(parents=True)
for name in ("theory", "independent", "baselines"):
    shutil.copytree(ROOT / "pass2" / name, stage / "pass2" / name,
                    ignore=shutil.ignore_patterns("__pycache__", "*.log"))
evaluation = stage / "pass2/evaluation"
evaluation.mkdir()
for path in (ROOT / "pass2/evaluation").glob("*.py"):
    shutil.copy2(path, evaluation / path.name)
shutil.copytree(ROOT / "pass2/evaluation/results", evaluation / "results",
                ignore=shutil.ignore_patterns("predictions.jsonl", "observations.jsonl", "evaluation_labels.jsonl", "source_transitions.jsonl"))
data = stage / "pass2/naturaldata/normalized"
data.mkdir(parents=True)
for name in ("test_passages.jsonl", "test_histories.jsonl", "test_annotations.jsonl", "human_test_questions.jsonl"):
    shutil.copy2(ROOT / "pass2/naturaldata/normalized" / name, data / name)
shutil.copytree(ROOT / "pass2/audit", stage / "pass2/audit", ignore=shutil.ignore_patterns("rendered"))
shutil.copytree(ROOT / "pass2/paper", stage / "pass2/paper")

with (out / "verification.log").open("w", encoding="utf-8") as log:
    def run(script):
        print(script, flush=True)
        result = subprocess.run([sys.executable, str(stage / script)], cwd=stage,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log.write(script + "\n" + result.stdout + "\n"); log.flush()
        if result.returncode:
            print(result.stdout[-5000:])
            raise SystemExit(result.returncode)

    for script in ("pass2/theory/test_uncertain_time.py", "pass2/theory/test_context_stability.py",
                   "pass2/independent/exhaustive_uncertain_time.py", "pass2/independent/check_future_prefix.py",
                   "pass2/independent/check_context_invariance.py", "pass2/baselines/verify_policies.py",
                   "pass2/evaluation/independent_timeqa_score.py", "pass2/audit/build_tables.py"):
        run(script)
    for name in ("fullsource.tex", "natural.tex", "sourceaudit.tex"):
        if (stage / "pass2/paper/tables" / name).read_bytes() != (ROOT / "pass2/paper/tables" / name).read_bytes():
            raise SystemExit("Table reconstruction differs: " + name)
    print("Compiler checks, independent rescoring, and all three table reconstructions passed.", flush=True)

    if args.full:
        shutil.copytree(ROOT / "inputs", stage / "inputs")
        shutil.copytree(ROOT / "work/external", stage / "work/external")
        shutil.copy2(ROOT / "pass2/evaluation/split_manifest.json", evaluation / "split_manifest.json")
        shutil.copytree(ROOT / "pass2/naturaldata/raw", stage / "pass2/naturaldata/raw")
        run("pass2/evaluation/run_full_benchmark.py")
        run("pass2/baselines/run_timeqa.py")
        old = json.loads((ROOT / "pass2/evaluation/results/full_results.json").read_text())
        new = json.loads((evaluation / "results/full_results.json").read_text())
        if old["results"] != new["results"]:
            raise SystemExit("Full-source retrieval metrics differ.")
        old = json.loads((ROOT / "pass2/baselines/timeqa_results/results.json").read_text())
        new = json.loads((stage / "pass2/baselines/timeqa_results/results.json").read_text())
        if old["results"] != new["results"]:
            raise SystemExit("TimeQA retrieval metrics differ.")
        print("Both full CPU retrieval experiments match the saved metrics.", flush=True)
print("PASS. Outputs are in reproduced/.")
