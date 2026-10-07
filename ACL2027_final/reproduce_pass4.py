#!/usr/bin/env python3
"""Verify the portable pass-4 release without downloads or new model inference.

Default: hashes, frozen inputs, source tests, independent retrieval rescoring,
table reconstruction, complete reader execution audits, and reader rescoring.
--full additionally replays every saved retrieval context and counterworld.
All generated files stay under reproduced_pass4. Frozen files are read only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
METHOD_COUNT = 10
TRACKS = {
    "human": ("test", "human_test_confirmation", 830),
    "validation": ("dev", "dev_validation", 2348),
}
READER_TRACKS = {
    "human": ("reader_primary_scored", "human_confirmation", "human", 193, 60),
    "human_diagnostic": ("reader_diagnostic_scored", "context_sensitive_diagnostic", "diagnostic", 45, 11),
}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


class Verification:
    def __init__(self, full=False):
        self.full = full
        parent = ROOT / "reproduced_pass4"
        parent.mkdir(exist_ok=True)
        self.output = Path(tempfile.mkdtemp(prefix="verification_", dir=parent))
        self.stage = self.output / "table_stage"
        self.stage.mkdir()
        self.log = (self.output / "verification.log").open("w", buffering=1)
        self.started = time.monotonic()
        self.report = {"status": "running", "full_retrieval_replay": full,
                       "model_inference_started": False, "checks": {}}
        self.env = {**os.environ, "PYTHONPATH": str(ROOT),
                    "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0", "PYTHONOPTIMIZE": "0",
                    "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                    "MKL_NUM_THREADS": "1"}

    def note(self, message):
        print(message, flush=True)
        self.log.write(message + "\n")

    def run(self, arguments, cwd=ROOT):
        command = [sys.executable, *map(str, arguments)]
        self.note("RUN " + " ".join(command))
        env = dict(self.env, PYTHONPATH=str(cwd))
        result = subprocess.run(command, cwd=cwd, env=env, stdout=self.log,
                                stderr=subprocess.STDOUT)
        require(result.returncode == 0,
                "Command failed with exit code " + str(result.returncode) +
                ": " + str(arguments[0]) + ". See " + str(self.output / "verification.log"))

    def manifest(self):
        manifest = load(ROOT / "MANIFEST.json")
        required = {"reproduce.py", "pass4/protocol/ALGORITHM_FREEZE.json",
                    "pass4/protocol/RESOURCE_AMENDMENT.json",
                    "pass4/audit/release/replay_confirmation_portable.py",
                    "pass4/pipeline/build_reader_results.py", "pass4/paper/tables/reader.tex",
                    "pass4/paper/tables/reader_main.tex",
                    "pass4/pipeline/paper_reader_results.json", "pass4/pipeline/reader_build_manifest.json",
                    "pass4/protocol/audit_answer_changes.py", "pass4/protocol/reader_primary_change_audit.json",
                    "pass4/protocol/reader_diagnostic_change_audit.json"}
        for track, (scored, _, audit, _, _) in READER_TRACKS.items():
            required.update({f"pass4/inference/{track}/reader_output.jsonl",
                             f"pass4/inference/{track}/reader_output.manifest.json",
                             f"pass4/protocol/{audit}_reader_execution_audit.json",
                             f"pass4/protocol/{scored}/summary.json"})
        files = manifest.get("files", {})
        require(required <= set(files), "MANIFEST.json is not the complete pass-4 release manifest. Missing: " +
                ", ".join(sorted(required - set(files))))
        byte_count = 0
        for name, expected in files.items():
            path = Path(name)
            require(not path.is_absolute() and ".." not in path.parts,
                    "Unsafe manifest path: " + name)
            path = ROOT / path
            require(path.is_file(), "Missing released file: " + name)
            require(digest(path) == expected, "Saved hash mismatch: " + name)
            byte_count += path.stat().st_size
        self.report["checks"]["release_manifest"] = {
            "files": len(files), "bytes": byte_count,
            "sha256": digest(ROOT / "MANIFEST.json"), "all_match": True}
        self.note(f"Verified {len(files)} released file hashes.")

    def freeze_and_tests(self):
        path = self.output / "freeze_verification.json"
        self.run(["pass4/protocol/verify_freeze.py", "--output", path])
        result = load(path)
        require(result["checked_files"] == 27 and result["all_files_match"],
                "The original 27-file freeze must match without exceptions.")
        require(result["original_hash_exceptions_allowed"] == 0 and
                result["resource_amendment_files_checked"] > 0,
                "The final resource amendment was not checked.")
        self.report["checks"]["algorithm_and_resource_freezes"] = result
        self.run(["pass4/extraction/test_source_adapter.py"])
        self.report["checks"]["source_regression_tests"] = {"passed": True, "tests": 11}
        self.note("The original freeze, final resource linkage, and eleven source tests pass.")

    def retrieval_scores(self):
        report = {}
        mapping = {"span_recall": "annotated_span_recall_at_5",
                   "all_spans": "all_annotated_spans_covered_at_5",
                   "parent_hit": "parent_passage_hit_at_5",
                   "words": "tokens_used", "units": "units_used"}
        for track, (source, label, expected_questions) in TRACKS.items():
            out = self.output / ("independent_" + track)
            self.run(["pass4/retrieval/independent_score.py", "--predictions",
                      f"pass4/pipeline/{track}/predictions.jsonl", "--labels",
                      f"pass3/protocol/{label}_labels.jsonl", "--passages",
                      f"pass3/protocol/{source}_source_passages.jsonl", "--output", out])
            fresh = load(out / "summary.json")
            saved = load(ROOT / f"pass4/retrieval/independent_{track}/summary.json")
            primary = load(ROOT / f"pass4/pipeline/{track}/scored/summary.json")
            require(fresh["queries"] == saved["queries"] == primary["n_questions"] == expected_questions,
                    track + ": retrieval question count differs.")
            methods = set(primary["metrics"])
            require(len(methods) == METHOD_COUNT and methods == set(fresh["metrics"]) == set(saved["metrics"]),
                    track + ": all ten methods must be present.")
            require(fresh["metrics"] == saved["metrics"], track + ": independent metric reconstruction differs.")
            require(fresh["paired_span_contrasts"] == saved["paired_span_contrasts"],
                    track + ": independent interval reconstruction differs.")
            require(rows(out / "question_scores.jsonl") ==
                    rows(ROOT / f"pass4/retrieval/independent_{track}/question_scores.jsonl"),
                    track + ": independent per-question retrieval scores differ.")
            for method in methods:
                for independent, original in mapping.items():
                    require(math.isclose(fresh["metrics"][method][independent],
                                         primary["metrics"][method][original], rel_tol=0, abs_tol=1e-12),
                            f"{track}: primary and independent scores differ: {method}/{original}")
            report[track] = {"questions": expected_questions, "methods": sorted(methods),
                             "metrics_per_method": len(mapping), "all_agree": True,
                             "context_offsets_verified": fresh["context_offsets_verified"]}
        save(self.output / "retrieval_score_agreement.json", report)
        self.report["checks"]["retrieval_rescoring"] = report
        self.note("Independent rescoring reproduces both tracks and matches all ten primary methods.")

    def tables(self):
        files = ["pass4/pipeline/build_paper_results.py", "pass3/protocol/score_predictions.py"]
        for track in TRACKS:
            files += [f"pass4/pipeline/{track}/scored/summary.json",
                      f"pass4/pipeline/{track}/scored/scored_questions.jsonl",
                      f"pass4/protocol/{track}_confirmation_audit.json"]
        for name in files:
            destination = self.stage / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)
        self.run(["pass4/pipeline/build_paper_results.py"], cwd=self.stage)
        matched = []
        for name in ["matched.tex", "mechanism.tex", "budget.tex"]:
            relative = "pass4/paper/tables/" + name
            require((ROOT / relative).read_bytes() == (self.stage / relative).read_bytes(),
                    "Paper table reconstruction differs: " + name)
            matched.append(name)
        require(load(ROOT / "pass4/pipeline/paper_results.json") ==
                load(self.stage / "pass4/pipeline/paper_results.json"),
                "Paper result reconstruction differs.")
        self.report["checks"]["paper_reconstruction"] = {
            "byte_identical_tables": matched, "paper_results_match": True,
            "stage_is_separate_copy": True}
        self.note("Three paper tables reconstruct byte for byte in a separate copy.")

    def reader(self):
        # Check both complete manifests before invoking either scorer.
        for track, (_, _, _, expected_jobs, _) in READER_TRACKS.items():
            path = ROOT / f"pass4/inference/{track}/reader_output.manifest.json"
            require(path.is_file(), "Reader batch has no completion manifest: " + track +
                    ". No partial reader cohort has been scored.")
            manifest = load(path)
            require(manifest.get("output_rows") == manifest.get("rows") == expected_jobs,
                    "Reader completion count differs: " + track)
        report = {}
        for track, (scored, selection, audit, expected_jobs, expected_questions) in READER_TRACKS.items():
            out = self.output / scored
            audit_path = self.output / (audit + "_reader_execution_audit.json")
            self.run(["pass4/protocol/audit_reader_run.py", "--outputs",
                      f"pass4/inference/{track}/reader_output.jsonl", "--jobs",
                      f"pass4/pipeline/{track}/reader_jobs.jsonl", "--output", audit_path])
            fresh_audit = load(audit_path)
            saved_audit = load(ROOT / f"pass4/protocol/{audit}_reader_execution_audit.json")
            require({k:v for k,v in fresh_audit.items() if k != "hashes"} ==
                    {k:v for k,v in saved_audit.items() if k != "hashes"},
                    track + ": independent execution audit reconstruction differs.")
            command = ["pass4/protocol/score_reader.py", "--jobs",
                       f"pass4/pipeline/{track}/reader_jobs.jsonl", "--outputs",
                       f"pass4/inference/{track}/reader_output.jsonl", "--membership",
                       f"pass4/pipeline/{track}/reader_memberships.jsonl", "--predictions",
                       "pass4/pipeline/human/predictions.jsonl", "--labels",
                       "pass3/protocol/human_test_confirmation_labels.jsonl", "--passages",
                       "pass3/protocol/test_source_passages.jsonl", "--config",
                       "pass4/protocol/config.json", "--output", out, "--track", selection]
            if track == "human_diagnostic":
                command += ["--cohort-queries", "pass4/pipeline/human_diagnostic/queries.jsonl"]
            self.run(command)
            fresh = load(out / "summary.json")
            saved = load(ROOT / f"pass4/protocol/{scored}/summary.json")
            # Input path spellings are machine-specific provenance, not results.
            require({k:v for k,v in fresh.items() if k != "input_sha256"} ==
                    {k:v for k,v in saved.items() if k != "input_sha256"},
                    track + ": reader summary reconstruction differs.")
            require(fresh["n_questions"] == expected_questions and
                    fresh["n_unique_generations_used"] == expected_jobs and
                    fresh["n_logical_conditions"] == expected_questions * METHOD_COUNT,
                    track + ": reader cohort count differs.")
            for filename in ["scored_questions.jsonl", "predictions_with_reader.jsonl", "reader_parse_audit.jsonl"]:
                require(rows(out / filename) == rows(ROOT / f"pass4/protocol/{scored}" / filename),
                        track + ": reader artifact reconstruction differs: " + filename)
            report[track] = {"questions": expected_questions, "unique_generations": expected_jobs,
                             "logical_conditions": fresh["n_logical_conditions"],
                             "parse_failures_unique": fresh["parse_failures_unique"],
                             "execution_audit_matches": True, "reader_scores_match": True}
        self.report["checks"]["reader_reconstruction"] = report
        self.note("Both complete reader batches pass execution audits and full rescoring.")

    def answer_changes(self):
        report = {}
        for role, questions in [("primary", 60), ("diagnostic", 11)]:
            out = self.output / ("reader_" + role + "_change_audit.json")
            self.run(["pass4/protocol/audit_answer_changes.py", "--predictions",
                      f"pass4/protocol/reader_{role}_scored/predictions_with_reader.jsonl",
                      "--output", out])
            fresh = load(out)
            saved = load(ROOT / f"pass4/protocol/reader_{role}_change_audit.json")
            require({k:v for k,v in fresh.items() if k != "hashes"} ==
                    {k:v for k,v in saved.items() if k != "hashes"},
                    role + ": descriptive answer-change audit reconstruction differs.")
            require(fresh["questions"] == questions and fresh["methods"] == METHOD_COUNT and
                    len(fresh["contrasts"]) == METHOD_COUNT * (METHOD_COUNT - 1) // 2,
                    role + ": descriptive answer-change cohort differs.")
            report[role] = {"questions": questions, "methods": METHOD_COUNT,
                            "contrasts": len(fresh["contrasts"]), "all_match": True}
        self.report["checks"]["answer_change_reconstruction"] = report
        self.note("Descriptive answer-change audits reproduce all 45 contrasts in each cohort.")

    def reader_table(self):
        source = "pass4/pipeline/build_reader_results.py"
        destination = self.stage / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / source, destination)
        for short, folder in [("primary", "reader_primary_scored"),
                              ("diagnostic", "reader_diagnostic_scored")]:
            target = self.stage / "reader_inputs" / short
            target.mkdir(parents=True, exist_ok=True)
            for name in ["summary.json", "scored_questions.jsonl", "reader_parse_audit.jsonl"]:
                shutil.copy2(ROOT / f"pass4/protocol/{folder}" / name, target / name)
        self.run([source, "--primary-score-dir", "reader_inputs/primary",
                  "--diagnostic-score-dir", "reader_inputs/diagnostic",
                  "--output-dir", "reader_results"], cwd=self.stage)
        outputs = {"reader.tex": "pass4/paper/tables/reader.tex",
                   "reader_main.tex": "pass4/paper/tables/reader_main.tex",
                   "paper_reader_results.json": "pass4/pipeline/paper_reader_results.json",
                   "reader_build_manifest.json": "pass4/pipeline/reader_build_manifest.json"}
        for name, original in outputs.items():
            require((self.stage / "reader_results" / name).read_bytes() == (ROOT / original).read_bytes(),
                    "Reader table construction differs: " + name)
        self.report["checks"]["reader_table_reconstruction"] = {
            "byte_identical_artifacts": list(outputs), "stage_is_separate_copy": True}
        self.note("Both reader tables, presentation results, and build manifest reconstruct byte for byte.")

    def full_replay(self):
        report = {}
        for track, (source, query, _) in TRACKS.items():
            out = self.output / (track + "_confirmation_audit.json")
            self.run(["pass4/audit/release/replay_confirmation_portable.py", "--folder",
                      f"pass4/pipeline/{track}", "--passages",
                      f"pass3/protocol/{source}_source_passages.jsonl", "--queries",
                      f"pass4/protocol/{query}_queries.jsonl", "--output", out])
            fresh = load(out)
            saved = load(ROOT / f"pass4/protocol/{track}_confirmation_audit.json")
            require({k:v for k,v in fresh.items() if k != "files"} ==
                    {k:v for k,v in saved.items() if k != "files"},
                    track + ": full retrieval replay differs.")
            report[track] = {"all_checks_passed": fresh["all_checks_passed"],
                             "counts": fresh["counts"], "counterworld_pairs": fresh["counterworld_pairs"]}
        self.report["checks"]["full_retrieval_replay"] = report
        self.note("Every stored retrieval context and counterworld replays independently.")

    def finish(self, error=None):
        self.report.update(status="failed" if error else "passed",
                           completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                           elapsed_seconds=round(time.monotonic() - self.started, 3))
        if error:
            self.report["error"] = str(error)
        save(self.output / "verification.json", self.report)
        self.note(("FAIL: " + str(error) if error else "PASS") + ". Verification outputs: " + str(self.output))
        self.log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true",
                        help="Also replay all 3,178 retrieval queries and 230 counterworlds. No model inference.")
    args = parser.parse_args()
    verification = Verification(args.full)
    try:
        verification.manifest()
        verification.freeze_and_tests()
        verification.retrieval_scores()
        verification.tables()
        verification.reader()
        verification.answer_changes()
        verification.reader_table()
        if args.full:
            verification.full_replay()
    except Exception as error:
        verification.finish(error)
        return 1
    verification.finish()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
