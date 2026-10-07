"""Rebuild every empirical main-body table from saved result cards."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "tables"
OUT.mkdir(exist_ok=True)

def read(path):
    return json.loads((ROOT / path).read_text())

def table(name, columns, header, rows, caption, label, small="small", spacing="4pt"):
    lines = [r"\begin{table}[t]", r"\centering", "\\"+small,
             r"\setlength{\tabcolsep}{"+spacing+"}",
             r"\begin{tabular}{"+columns+"}", r"\toprule", *header, r"\midrule"]
    lines.extend(" & ".join(row)+r" \\" for row in rows)
    lines += [r"\bottomrule", r"\end{tabular}", r"\caption{"+caption+"}",
              r"\label{"+label+"}", r"\end{table}"]
    (OUT / name).write_text("\n".join(lines)+"\n")

annual = read("evaluation/results/full_results.json")["results"]["test"]["all"]
methods = [("BM25", "bm25"), ("BM25 + recent ties", "bm25_recent_tie"),
           ("Age weighting", "age_development_selected"), ("Date-first ranking", "date_full_pool"),
           ("Original predicate", "old_earliest"), ("Graphiti kernel", "graphiti_policy"),
           ("Query latest-value", "query_latest_single"), ("Query latest-batch", "query_latest_batch")]
rows = [[label]+[f"{100*annual['methods'][key][metric]:.2f}" for metric in
        ("hit1", "value_recall5", "stale_value_exposure5")] for label, key in methods]
table("fullsource.tex", "lrrr", [r"Policy & H@1 $\uparrow$ & R@5 $\uparrow$ & S@5 $\downarrow$ \\"], rows,
      r"Annual source-label retrieval on 25,752 held-out questions. All values are percentages. H@1: first-result accuracy; R@5: answer recall; S@5: target-label stale exposure.", "tab:fullsource")

natural = read("baselines/timeqa_results/results.json")["results"]
methods = [("BM25", "bm25"), ("Latest year", "latest_mentioned_year_top20"),
           ("Year envelope", "year_envelope_filter"), ("Explicit range", "explicit_range_filter"),
           ("Range support", "range_support_top20")]
rows = [[label]+[f"{100*natural[track]['methods'][key][metric]:.2f}"
         for track in ("human_questions", "official_templates")
         for metric in ("annotated_passage_hit5", "annotated_span_recall5")] for label, key in methods]
table("natural.tex", "lrrrr", [r"& \multicolumn{2}{c}{Human} & \multicolumn{2}{c}{Templates} \\",
      r"Policy & H@5 & R@5 & H@5 & R@5 \\"], rows,
      r"TimeQA paragraph retrieval percentages. H@5 measures annotated-passage coverage; R@5 measures annotated-span recall. The tracks contain 830 human questions and 2,613 template questions.",
      "tab:natural", spacing="3.5pt")

audit = read("evaluation/results/source_audit_intervals.json")["rates"]
rows=[]
for label,key in [("Multiple answers", "multiple_annual_answers"),
                  ("Old first retained", "changed_first_answer_retains_previous_first"),
                  ("Any answer retained", "changed_answer_set_retains_value")]:
    item = audit[key]
    rows.append([label, f"{item['numerator']:,}/{item['denominator']:,}",
                 f"{100*item['estimate']:.1f} [{100*item['ci95'][0]:.1f}, {100*item['ci95'][1]:.1f}]"])
table("sourceaudit.tex", "lrr", [r"Source-label property & Count & Rate (95\% CI) \\"], rows,
      r"Answer-set properties on held-out source keys. The last two rows condition on first-answer changes and complete-set changes, respectively. Rates and intervals are percentages.",
      "tab:sourceaudit", small="footnotesize", spacing="3pt")
print("Rebuilt 3 empirical tables from saved result cards.")
