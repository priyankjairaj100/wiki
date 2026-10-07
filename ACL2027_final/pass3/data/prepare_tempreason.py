"""Verify and normalize the released TempReason L2 test data.

The natural context remains separate from all answer and temporal metadata.
The template-generated fact_context is never copied into model inputs.
"""
import collections
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import urllib.request

HERE = Path(__file__).resolve().parent


def norm(text):
    return " ".join(re.sub(r"[^\w ]", " ", unicodedata.normalize("NFKC", text).lower()).split())


def main():
    provenance = json.loads((HERE / "tempreason_provenance.json").read_text())
    source = HERE / "tempreason_test_l2.json"
    if not source.exists():
        with urllib.request.urlopen(provenance["immutable_url"], timeout=120) as response:
            source.write_bytes(response.read())
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == provenance["sha256"]
    rows = [json.loads(line) for line in raw.splitlines()]
    contexts, questions = {}, []
    answer_found, relations, subjects = 0, collections.Counter(), set()
    for row in rows:
        subject, relation = row["id"].split("_")[1:3]
        subjects.add(subject)
        relations[relation] += 1
        text = row["context"]
        digest = hashlib.sha256(text.encode()).hexdigest()
        context_id = digest[:24]
        contexts[context_id] = {
            "context_id": context_id, "text": text, "text_sha256": digest,
            "subject_qid": subject, "source_file": "test_l2.json", "source_field": "context",
        }
        questions.append({
            "question_id": row["id"], "question_text": row["question"],
            "context_id": context_id, "answers": row["text_answers"]["text"],
            "relation_id": relation, "source_date_metadata": row["date"],
            "source_date_semantics": "Original sampled day. Use the explicit question date for model input. Do not replace a month question with this day.",
        })
        answer_found += any(norm(answer) in norm(text) for answer in row["text_answers"]["text"])
    for name, records in [("contexts", contexts.values()), ("questions", questions)]:
        (HERE / f"tempreason_{name}.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records))
    summary = {
        "records": len(rows), "unique_subject_qids": len(subjects),
        "unique_contexts": len(contexts),
        "normalized_answer_occurs_in_context": answer_found,
        "relations": dict(relations),
        "interpretation": "Answer containment is a surface diagnostic. It does not establish relation or time entailment.",
    }
    (HERE / "tempreason_coverage_audit.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
