"""Frozen lexical retrieval on released TimeQA natural paragraphs.

Inference uses only published question text, paragraph text, and article titles.
Gold ranges enter templated question construction only. Gold spans only score.
Metrics concern annotated spans, not answer generation or semantic entailment.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import math
import pathlib
import random
import re
import time

HERE = pathlib.Path(__file__).resolve().parent
TOKEN = re.compile(r"\w+", re.UNICODE)
YEAR = re.compile(r"(?<!\d)([12]\d{3})(?!\d)")
RANGE = re.compile(r"(?<!\d)([12]\d{3})\s*(?:[-–—]|to|through|until|and)\s*([12]\d{3}|\d{2})(?!\d)", re.I)
METHODS = ["bm25", "latest_mentioned_year_top20", "year_envelope_filter",
           "explicit_range_filter", "range_support_top20"]


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def temporal_features(text):
    years = tuple(int(x) for x in YEAR.findall(text))
    ranges = []
    for a, b in RANGE.findall(text):
        a = int(a)
        if len(b) == 2:
            b = (a // 100) * 100 + int(b)
            if b < a:
                b += 100
        else:
            b = int(b)
        if a <= b:
            ranges.append((a, b))
    return {"years": years, "ranges": tuple(ranges)}


def query_years(text):
    # Every method reads the same text. No hidden annotation interval is used.
    years = [int(x) for x in YEAR.findall(text)]
    return (min(years), max(years)) if years else None


def overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


class BM25:
    def __init__(self, texts):
        counts = [collections.Counter(TOKEN.findall(t.lower())) for t in texts]
        self.n = len(counts)
        lengths = [sum(c.values()) for c in counts]
        avg = sum(lengths) / max(1, self.n)
        df = collections.Counter(w for c in counts for w in c)
        self.postings = collections.defaultdict(list)
        for i, c in enumerate(counts):
            for word, tf in c.items():
                idf = math.log(1 + (self.n - df[word] + .5) / (df[word] + .5))
                weight = idf * tf * 2.5 / (tf + 1.5 * (.25 + .75 * lengths[i] / avg))
                self.postings[word].append((i, weight))

    def rank(self, question):
        scores = collections.defaultdict(float)
        for word, count in collections.Counter(TOKEN.findall(question.lower())).items():
            for i, value in self.postings.get(word, ()):
                scores[i] += count * value
        # Zero-match paragraphs follow all positive matches in passage-ID order.
        ranked = sorted(scores, key=lambda i: (-scores[i], i))
        ranked.extend(i for i in range(self.n) if i not in scores)
        return ranked


def template_question(row, title, relations):
    template = relations[row["relation_id"]]["template"][0]
    dates = [x["raw"] for x in row["date_range"]]
    time_text = f"from {dates[0]} to {dates[1]}"
    point_text = f"in {dates[0]}" if dates[0] == dates[1] else time_text
    if "since $2" in template:
        point_text = dates[0]
    return template.replace("$1", title).replace("$4", time_text).replace("$2", point_text)


def orders(rank, features, question):
    qtime = query_years(question)
    result = {"bm25": rank}
    if qtime is None:
        return {method: rank for method in METHODS}

    def envelope_ok(i):
        years = features[i]["years"]
        return not years or overlap((min(years), max(years)), qtime)

    def ranges_ok(i):
        ranges = features[i]["ranges"]
        return not ranges or any(overlap(pair, qtime) for pair in ranges)

    def range_support(i):
        ranges = features[i]["ranges"]
        return 1 if not ranges else 2 if any(overlap(pair, qtime) for pair in ranges) else 0

    def latest(i):
        return max((year for year in features[i]["years"] if year <= qtime[1]), default=-math.inf)

    # Stable sorts preserve BM25 order for all temporal ties.
    result["latest_mentioned_year_top20"] = sorted(rank[:20], key=latest, reverse=True) + rank[20:]
    result["year_envelope_filter"] = [i for i in rank if envelope_ok(i)]
    result["explicit_range_filter"] = [i for i in rank if ranges_ok(i)]
    result["range_support_top20"] = sorted(rank[:20], key=range_support, reverse=True) + rank[20:]
    return result


def score(order, passages, row):
    top1 = {passages[i]["passage_id"] for i in order[:1]}
    top5 = {passages[i]["passage_id"] for i in order[:5]}
    gold = set(row["gold_passage_ids"])
    spans = row["gold_answer_spans"]
    return {"annotated_passage_hit1": int(bool(top1 & gold)),
            "annotated_passage_hit5": int(bool(top5 & gold)),
            "annotated_span_recall5": sum(s["passage_id"] in top5 for s in spans) / len(spans),
            "all_annotated_spans5": int(all(s["passage_id"] in top5 for s in spans))}


def bootstrap(rows, method, metric, repetitions=2000):
    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[row["article_path"]].append(row["methods"][method][metric] - row["methods"]["bm25"][metric])
    groups = list(grouped.values())
    rng = random.Random(20261006)
    draws = []
    for _ in range(repetitions):
        sample = [groups[rng.randrange(len(groups))] for _ in groups]
        draws.append(sum(sum(x) for x in sample) / sum(len(x) for x in sample))
    draws.sort()
    return {"delta": sum(sum(x) for x in groups) / sum(len(x) for x in groups),
            "ci95": [draws[int(.025 * repetitions)], draws[int(.975 * repetitions)]],
            "article_clusters": len(groups), "repetitions": repetitions, "seed": 20261006}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=pathlib.Path, default=HERE.parent / "naturaldata")
    ap.add_argument("--output", type=pathlib.Path, default=HERE / "timeqa_results")
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    normalized = args.data / "normalized"
    inputs = [normalized / name for name in ("test_passages.jsonl", "test_histories.jsonl",
              "test_annotations.jsonl", "human_test_questions.jsonl")]
    inputs.append(args.data / "raw/TimeQA_relations.json")
    protocol = {"protocol": "timeqa-natural-paragraph-evidence-v1",
                "methods_frozen_before_first_execution": True,
                "protocol_correction": "A pre-result run stopped after the source audit identified zero-length answer placeholders. Exclude these placeholders from positive retrieval scoring. No method or parameter changed.",
                "inputs": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                "script_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
                "methods": METHODS, "bm25": {"k1": 1.5, "b": .75, "idf": "log(1+(N-df+.5)/(df+.5))"},
                "candidate_pool": "All official test paragraphs, with visible article title appended once",
                "rank_ties": "passage_id ascending", "rerank_pool": 20, "context_k": 5,
                "temporal_features": "Regex year mentions and explicit year ranges from paragraph text only",
                "template": "First official relation template, subject from visible article title, published time constraint",
                "fit_or_tuning": "None. No development data or test labels fit any parameter.",
                "gold_use": "Verify source spans and score labeled paragraph/span coverage only",
                "interpretation": "Annotated-span retrieval. No generated answers, entailment scores, or inferred source dates.",
                "human_overlap": "Human questions are a subset of the same official test source; not an independent corpus."}
    save(args.output / "PROTOCOL.json", protocol)
    started = time.perf_counter()
    passages = sorted(read_jsonl(inputs[0]), key=lambda row: row["passage_id"])
    pmap = {p["passage_id"]: p for p in passages}
    titles = {p["article_path"]: p["text"] for p in passages if p["paragraph_index"] == 0}
    histories = {row["history_id"]: row for row in read_jsonl(inputs[1])}
    relations = json.loads(inputs[-1].read_text())
    texts = [titles[p["article_path"]] + "\n" + p["text"] for p in passages]
    # The features exclude gold span indices, dates, answers, relation IDs, and keys.
    features = [temporal_features(p["text"]) for p in passages]
    index = BM25(texts)
    audit = {"n_passages": len(passages), "n_articles": len(titles),
             "n_undated_passages": sum(not f["years"] for f in features),
             "n_explicit_range_passages": sum(bool(f["ranges"]) for f in features),
             "all_span_substrings_validated": True}
    results = {}
    for track, path in [("official_templates", inputs[2]), ("human_questions", inputs[3])]:
        queries = read_jsonl(path)
        records = []
        no_gold = 0
        for number, row in enumerate(queries):
            spans = [s for s in row["gold_answer_spans"] if s["answer"].strip()
                     and s["end_char_exclusive"] > s["start_char"]]
            if not spans:
                no_gold += 1
                continue
            row = dict(row, gold_answer_spans=spans,
                       gold_passage_ids=sorted({s["passage_id"] for s in spans}))
            for span in spans:
                text = pmap[span["passage_id"]]["text"]
                assert text[span["start_char"]:span["end_char_exclusive"]] == span["answer"]
            article = histories[row["history_id"]]["article_url"].split("wikipedia.org", 1)[1]
            question = row["question_text"] or template_question(row, titles[article], relations)
            assert "$" not in question, question
            rank = index.rank(question)
            all_orders = orders(rank, features, question)
            record = {"question_id": row["question_id"], "article_path": article,
                      "question": question, "question_year_envelope": query_years(question),
                      "n_gold_spans": len(spans), "methods": {}}
            for method, order in all_orders.items():
                record["methods"][method] = score(order, passages, row)
                record["methods"][method]["top5"] = [passages[i]["passage_id"] for i in order[:5]]
                # Gold-derived diagnostics remain in evaluation records only.
                if method.endswith("filter"):
                    kept = {passages[i]["passage_id"] for i in order}
                    record["methods"][method]["annotated_spans_removed"] = sum(s["passage_id"] not in kept for s in spans)
            records.append(record)
            if number and number % 500 == 0:
                print(track, number, "questions", flush=True)
        with (args.output / f"{track}_predictions.jsonl").open("w") as f:
            for row in records:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        metrics = ["annotated_passage_hit1", "annotated_passage_hit5", "annotated_span_recall5", "all_annotated_spans5"]
        results[track] = {"n_queries": len(records), "n_input_queries": len(queries),
                          "n_excluded_empty_gold": no_gold,
                          "n_articles": len({r["article_path"] for r in records}),
                          "n_queries_without_textual_year": sum(r["question_year_envelope"] is None for r in records),
                          "methods": {method: {metric: sum(row["methods"][method][metric] for row in records) / len(records)
                                      for metric in metrics} for method in METHODS},
                          "paired_article_bootstrap": {method: {metric: bootstrap(records, method, metric)
                                      for metric in ("annotated_passage_hit5", "annotated_span_recall5")}
                                      for method in METHODS if method != "bm25"},
                          "removed_span_counts": {method: sum(row["methods"][method]["annotated_spans_removed"] for row in records)
                                      for method in METHODS if method.endswith("filter")},
                          "total_annotated_spans": sum(row["n_gold_spans"] for row in records)}
        print(track, json.dumps(results[track]["methods"]), flush=True)
    save(args.output / "results.json", {"audit": audit, "results": results,
                                       "elapsed_seconds": time.perf_counter() - started})
    print("Done", round(time.perf_counter() - started, 3), flush=True)


if __name__ == "__main__":
    main()
