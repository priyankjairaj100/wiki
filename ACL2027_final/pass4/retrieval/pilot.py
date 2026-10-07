"""Choose a ranking on the pre-existing pilot only."""
from __future__ import annotations
import argparse,hashlib,json,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read,dump,lines,build_context
from pass3.protocol.score_predictions import context_scores,paired_bootstrap
from pass4.retrieval.ranking import TitleRanker,VARIANTS

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(a):
    started=time.time();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    inputs={str(p):sha(p) for p in [a.units,a.queries,a.labels,a.passages,Path(__file__),Path(__file__).with_name("ranking.py")]}
    dump(out/"input_manifest.json",inputs)
    units=read(a.units);queries=read(a.queries);labels={r["question_id"]:r for r in read(a.labels)};passages={r["passage_id"]:r for r in read(a.passages)}
    ranker=TitleRanker(units);pred=[];scores=[];links=[]
    for q in queries:
        methods={};metrics={}
        for variant in VARIANTS:
            order,_,link=ranker.rank_with_metadata(q["question"],variant)
            contexts=build_context(order,units,{},5,768)
            methods[variant]={"contexts":contexts,"selected_unit_ids":[units[i]["unit_id"] for i in order[:5]]}
            metrics[variant]=context_scores(methods[variant],labels[q["question_id"]],passages)
        pred.append({"question_id":q["question_id"],"question":q["question"],"methods":methods})
        scores.append({"question_id":q["question_id"],"article_path":labels[q["question_id"]]["history_id"].rsplit("#",1)[0],"methods":metrics})
        # Gold article is used only after the ranking has returned, for this diagnostic.
        links.append({"question_id":q["question_id"],**link,"contains_annotated_article":q["article_path"] in link["article_paths"]})
    summary={"n_queries":len(queries),"metrics":{v:{m:sum(r["methods"][v][m] for r in scores)/len(scores) for m in scores[0]["methods"][v]} for v in VARIANTS},"paired_span_vs_original_recency":{v:paired_bootstrap(scores,v,"bm25_latestyear","annotated_span_recall_at_5") for v in VARIANTS if v!="bm25_latestyear"},"linking":{"linked":sum(bool(x["article_paths"]) for x in links),"contains_annotated_article":sum(x["contains_annotated_article"] for x in links),"ambiguous":sum(len(x["article_paths"])>1 for x in links)},"elapsed_seconds":time.time()-started}
    lines(out/"predictions.jsonl",pred);lines(out/"scores.jsonl",scores);lines(out/"links.jsonl",links);dump(out/"summary.json",summary)
    assert all(sha(p)==h for p,h in inputs.items())
    dump(out/"manifest.json",{"inputs":inputs,"outputs":{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!="manifest.json"},"command":" ".join(sys.argv)})
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--units",default="pass3/pipeline/pilot_final/units.jsonl");p.add_argument("--queries",default="pass3/protocol/dev_pilot_queries.jsonl");p.add_argument("--labels",default="pass3/protocol/dev_pilot_labels.jsonl");p.add_argument("--passages",default="pass3/protocol/dev_source_passages.jsonl");p.add_argument("--output",default="pass4/retrieval/pilot");run(p.parse_args())
