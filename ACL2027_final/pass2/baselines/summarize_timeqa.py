"""Create small tables from completed TimeQA run files."""
import csv
import json
import pathlib

root = pathlib.Path(__file__).resolve().parent / "timeqa_results"
report = json.loads((root / "results.json").read_text())
rows = []
for track, result in report["results"].items():
    for method, metrics in result["methods"].items():
        rows.append(dict(track=track, method=method, n_queries=result["n_queries"], **metrics))
with (root / "metrics.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
lines = ["# Natural TimeQA paragraph retrieval", "",
         "All numbers measure annotated-span coverage, not generated-answer accuracy.", "",
         "| Track | Method | N | Passage Hit@1 | Passage Hit@5 | Span recall@5 | All spans@5 |",
         "|---|---|---:|---:|---:|---:|---:|"]
for row in rows:
    vals = [f"{100 * row[key]:.2f}" for key in ("annotated_passage_hit1",
            "annotated_passage_hit5", "annotated_span_recall5", "all_annotated_spans5")]
    lines.append(f"| {row['track']} | {row['method']} | {row['n_queries']} | " + " | ".join(vals) + " |")
lines += ["", "Human questions overlap the official templated track's source records.",
          "No parameter was fitted on either track.", ""]
(root / "RESULTS.md").write_text("\n".join(lines))
print("Saved metrics.csv and RESULTS.md")
