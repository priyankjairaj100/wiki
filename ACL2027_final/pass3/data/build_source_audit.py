"""Materialize a fixed ten-item development audit of source date semantics.

This audit is descriptive. It supplies neither model inputs nor test labels.
Selection: first ten distinct development histories with a gold anchor paragraph
containing two year strings and 51--1799 characters. The paragraph criterion
selects readable source examples, not successful method predictions.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT / "pass2/naturaldata/normalized"
OUT = pathlib.Path(__file__).resolve().parent


def rows(name):
    return [json.loads(line) for line in (BASE / name).read_text().splitlines()]


COMMENTS = {
    "/wiki/Ian_Gibson_(politician)": {
        "source_event": "Served as Member of Parliament for Norwich North from 1997 to 2009.",
        "start_expression": "1997", "start_precision": "year",
        "bounded_start_supported": True,
        "source_interval": ["1997", "2009"],
        "pitfall": "The paragraph also gives birth and death dates. These do not date the office.",
        "replacement_supported": False,
    },
    "/wiki/Esperanza_Aguirre": {
        "source_event": "Left the Liberal Party and joined Popular Alliance in 1987.",
        "start_expression": "1987", "start_precision": "year",
        "bounded_start_supported": True,
        "source_interval": None,
        "pitfall": "The annotated city-council role lacks its initial election date in this anchor. A party rename is not a new role.",
        "replacement_supported": True,
        "replacement_scope": "The explicit left/joined construction concerns party affiliation, not the annotated P39 office.",
    },
    "/wiki/Gerhard_Hirschfeld": {
        "source_event": "Fellow with the German Historical Institute London from 1978 to 1989.",
        "start_expression": "1978", "start_precision": "year",
        "bounded_start_supported": True,
        "source_interval": ["1978", "1989"],
        "pitfall": "The paragraph also dates education, a doctorate, and two earlier positions. Each date needs its own event.",
        "replacement_supported": False,
    },
    "/wiki/Evelyn_Berezin": {
        "source_event": "Founded Redactron Corporation in 1969.",
        "start_expression": "1969", "start_precision": "year",
        "bounded_start_supported": True,
        "source_interval": None,
        "pitfall": "Founding supports a founder event. It does not establish the annotated employment interval through 1976.",
        "replacement_supported": False,
    },
    "/wiki/Henry_Dundas,_1st_Viscount_Melville": {
        "source_event": "Appointed Lord Advocate in 1775.",
        "start_expression": "1775", "start_precision": "year",
        "bounded_start_supported": True,
        "source_interval": None,
        "pitfall": "The source gives year precision. The gold annotation gives month precision. Extraction must retain source precision.",
        "replacement_supported": False,
    },
    "/wiki/Steny_Hoyer": {
        "source_event": "Earned his J.D. from Georgetown University Law Center in 1966.",
        "start_expression": None, "start_precision": None,
        "bounded_start_supported": False,
        "source_interval": None,
        "pitfall": "Graduation dates mark completion. The paragraph does not state the 1963 enrollment start.",
        "replacement_supported": False,
    },
    "/wiki/Friedrich_Guggenberger": {
        "source_event": "Had entered the navy by 1934; transferred to the U-boat arm in October 1939.",
        "start_expression": "by 1934", "start_precision": "upper bound only",
        "bounded_start_supported": False,
        "source_interval": None,
        "pitfall": "The word 'by' permits earlier years. A bounded interval covering only 1934 would add unsupported information.",
        "replacement_supported": False,
    },
    "/wiki/Beatrix_Tugendhut_Gardner": {
        "source_event": "Attended Radcliffe College and received her bachelor's degree in 1954.",
        "start_expression": None, "start_precision": None,
        "bounded_start_supported": False,
        "source_interval": None,
        "pitfall": "The degree date supplies no enrollment start. Later degree dates also mark completion.",
        "replacement_supported": False,
    },
    "/wiki/Richard_Court": {
        "source_event": "Elected to represent Nedlands in March 1982.",
        "start_expression": "March 1982", "start_precision": "month",
        "bounded_start_supported": True,
        "source_interval": None,
        "pitfall": "The source dates several roles separately. Election, spokesperson, deputy leader, and leader require separate slots.",
        "replacement_supported": False,
    },
    "/wiki/Shelley_Sekula-Gibbs": {
        "source_event": "Served as a Houston city councilwoman from 2002 to 2006.",
        "start_expression": "2002", "start_precision": "year",
        "bounded_start_supported": True,
        "source_interval": ["2002", "2006"],
        "pitfall": "The paragraph also dates birth and a congressional role. A whole-paragraph date mask would combine distinct events.",
        "replacement_supported": False,
    },
}


def main():
    passages = {p["passage_id"]: p for p in rows("dev_passages.jsonl")}
    selected = []
    seen = set()
    for question in rows("dev_disjoint_nonempty_annotations.jsonl"):
        if question["history_id"] in seen:
            continue
        seen.add(question["history_id"])
        for pid in question["gold_passage_ids"]:
            paragraph = passages[pid]
            text = paragraph["text"]
            years = re.findall(r"(?<!\d)(?:1[4-9]\d{2}|20\d{2})(?!\d)", text)
            if len(years) >= 2 and 50 < len(text) < 1800:
                selected.append({
                    "question_id": question["question_id"],
                    "article_path": paragraph["article_path"],
                    "source_url": paragraph["article_url"],
                    "passage_id": pid,
                    "source_text": text,
                    "source_text_sha256": paragraph["text_sha256"],
                    "gold_question_range_for_audit_only": question["date_range"],
                    "audit": COMMENTS[paragraph["article_path"]],
                })
                break
        if len(selected) == 10:
            break
    assert len(selected) == 10
    (OUT / "dev_source_audit.json").write_text(json.dumps({
        "scope": "Manual qualitative source audit. No test examples. No benchmark accuracy claim.",
        "selection": __doc__,
        "source_manifest": "pass2/naturaldata/source_manifest.json",
        "examples": selected,
        "summary": {
            "examples": len(selected),
            "examples_with_bounded_source_start_for_some_event": sum(x["audit"]["bounded_start_supported"] for x in selected),
            "examples_with_no_bounded_start": sum(not x["audit"]["bounded_start_supported"] for x in selected),
            "explicit_replacement_same_annotated_relation": 0,
            "interpretation": "Source start precision can differ from the gold question range. Date mentions require event attachment.",
        },
    }, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
