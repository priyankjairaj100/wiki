"""Independent source-offset scoring for frozen retrieval outputs.

This implementation intentionally does not import the primary scoring module.
It scores existing predictions and never invokes a ranking method.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,random,time
from pathlib import Path

def read(path):
    with open(path) as stream:
        return [json.loads(line) for line in stream if line.strip()]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def interval(rows,method,reference,repeats=2000,seed=20261006):
    grouped=collections.defaultdict(list)
    for row in rows:
        grouped[row['article']].append(row['scores'][method]['span_recall']-row['scores'][reference]['span_recall'])
    values=list(grouped.values());sums=[sum(g) for g in values];counts=[len(g) for g in values];rng=random.Random(seed);samples=[]
    for _ in range(repeats):
        indices=rng.choices(range(len(values)),k=len(values))
        samples.append(sum(sums[i] for i in indices)/sum(counts[i] for i in indices))
    samples.sort()
    return {'difference':sum(sums)/sum(counts),'ci95':[samples[math.floor(.025*(repeats-1))],samples[math.ceil(.975*(repeats-1))]],'clusters':len(values),'repetitions':repeats,'seed':seed,'sampler':'Python random.choices; independent resample sequence from primary scorer'}

def main(a):
    started=time.time();predictions=read(a.predictions);labels=read(a.labels);passages={p['passage_id']:p['text'] for p in read(a.passages)}
    lm={x['question_id']:x for x in labels};pm={x['question_id']:x for x in predictions}
    assert len(lm)==len(labels) and len(pm)==len(predictions) and set(lm)==set(pm)
    methods=sorted(predictions[0]['methods']);rows=[];context_count=0;anchor_count=0
    for qid in sorted(lm):
        label,pred=lm[qid],pm[qid];assert sorted(pred['methods'])==methods
        spans=label['gold_answer_spans'];assert spans
        for span in spans:
            assert passages[span['passage_id']][span['start_char']:span['end_char_exclusive']]==span['answer']
        anchor_count+=len(spans);scored={}
        for name,result in pred['methods'].items():
            contexts=result['contexts'];assert len(contexts)<=5;words=0;byparent=collections.defaultdict(list)
            for c in contexts:
                start,end=c['start_char'],c['end_char_exclusive'];text=passages[c['passage_id']]
                assert 0<=start<end<=len(text)
                assert all(end<=a or start>=b for a,b in byparent[c['passage_id']])
                byparent[c['passage_id']].append((start,end));rendered=text[start:end]
                if 'text' in c:assert c['text']==rendered
                words+=len(rendered.split());context_count+=1
            assert words<=768
            hits=[any(left<=s['start_char'] and s['end_char_exclusive']<=right for left,right in byparent[s['passage_id']]) for s in spans]
            scored[name]={'span_recall':sum(hits)/len(hits),'all_spans':int(all(hits)),'parent_hit':int(any(s['passage_id'] in byparent and byparent[s['passage_id']] for s in spans)),'words':words,'units':len(contexts)}
        rows.append({'question_id':qid,'article':label['history_id'].rsplit('#',1)[0],'scores':scored})
    contrasts=[('no_temporal_filter','original_bm25_latestyear'),('no_temporal_filter','original_bm25'),('possible_support','no_temporal_filter'),('guaranteed_support','possible_support'),('possible_support','interval_outer_control'),('latest_mentioned_year_top20','no_temporal_filter')]
    contrasts=[(m,r) for m,r in contrasts if m in methods and r in methods]
    summary={'status':'passed','queries':len(rows),'articles':len({r['article'] for r in rows}),'context_offsets_verified':context_count,'gold_anchors_verified':anchor_count,'metrics':{m:{metric:sum(r['scores'][m][metric] for r in rows)/len(rows) for metric in rows[0]['scores'][m]} for m in methods},'paired_span_contrasts':{m+' minus '+r:interval(rows,m,r) for m,r in contrasts},'elapsed_seconds':time.time()-started,'input_sha256':{str(p):sha(p) for p in [a.predictions,a.labels,a.passages,Path(__file__)]}}
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'question_scores.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--predictions',required=True);p.add_argument('--labels',required=True);p.add_argument('--passages',required=True);p.add_argument('--output',required=True);main(p.parse_args())
