"""Select development source paragraphs using only lexical succession cues."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "pass3/protocol/dev_source_passages.jsonl"
CUE = re.compile(r"\b(?:replaced|succeeded|took over|succeeding|replacing)\b", re.I)
ROLE = re.compile(r"\b(?:chair(?:man|woman|person)?|president|governor|moderator|host|coach|bishop|leader)\b", re.I)
YEAR = re.compile(r"\b(?:1[5-9]\d{2}|20\d{2})\b")


def main():
    raw = SOURCE.read_bytes()
    ranked = []
    for row in map(json.loads, raw.splitlines()):
        text = row["text"]
        cues, years = list(CUE.finditer(text)), list(YEAR.finditer(text))
        if not cues or len(years) < 2 or not 60 <= len(text) <= 2500:
            continue
        near = sum(bool(YEAR.search(text[max(0, m.start()-200):m.end()+200])) for m in cues)
        score = 4*min(near, 3) + 3*min(len(cues), 3) + 2*bool(ROLE.search(text)) + min(len({m.group() for m in years}), 4)
        ranked.append((score, row, cues))
    ranked.sort(key=lambda x: (-x[0], len(x[1]["text"]), x[1]["passage_id"]))
    selected, counts = [], {}
    for score, row, cues in ranked:
        article = row["article_path"]
        if counts.get(article, 0) >= 2:
            continue
        counts[article] = counts.get(article, 0) + 1
        selected.append(dict(row, selection_rank=len(selected)+1, selection_score=score,
            selection_cues=[{"text": m.group(), "start": m.start(), "end": m.end()} for m in cues],
            selection_scope="Source-only DEV cue calibration. No questions or answer labels inspected."))
        if len(selected) == 30:
            break
    (HERE / "dev_succession_candidates.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selected))
    manifest = {
        "source_file": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "selection": "At least two years, 60-2500 characters, one explicit succession cue. Rank 4*min(date-near-cues,3)+3*min(cues,3)+2*role-present+min(distinct-years,4). At most two paragraphs per article. Tie: short text then passage ID.",
        "candidate_count": len(ranked), "selected_count": len(selected),
        "article_paths": sorted(counts),
        "must_remove_from_validation_before_use_as_calibration": True,
        "no_question_answer_or_outcome_selection": True,
    }
    (HERE / "dev_succession_selection.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
