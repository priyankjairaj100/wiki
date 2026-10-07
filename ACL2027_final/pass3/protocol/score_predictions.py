"""Score matched contexts and complete answer lists against frozen TimeQA labels.

Prediction schema:
{"question_id": ..., "methods": {"possible_support": {
  "contexts": [{"passage_id": ..., "start_char": 0,
                "end_char_exclusive": 250}],
  "answers": ["optional reader answer"],
  "filtered_passage_ids": ["optional IDs removed by temporal filtering"]}}}

Offsets describe the actual text given to the reader. Gold never enters retrieval.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import re
import unicodedata

TOKEN=re.compile(r'\w+',re.UNICODE)


def read(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x]


def normalize(text):
    # Keep articles. Single-letter names and literal answer strings remain valid.
    return ' '.join(TOKEN.findall(unicodedata.normalize('NFKC',text).casefold()))


def tokens(text):
    return collections.Counter(normalize(text).split())


def token_f1(a,b):
    a,b=tokens(a),tokens(b)
    na,nb=sum(a.values()),sum(b.values())
    if not na or not nb:
        return float(na==nb)
    overlap=sum((a&b).values())
    return 2*overlap/(na+nb)


def answer_scores(predicted,gold):
    if not all(isinstance(x,str) for x in predicted):
        raise ValueError('Reader answers must be a list of strings.')
    pred=sorted({normalize(x) for x in predicted if normalize(x)})
    target=sorted({normalize(x) for x in gold if normalize(x)})
    matched=len(set(pred)&set(target))
    precision=matched/len(pred) if pred else float(not target)
    recall=matched/len(target) if target else float(not pred)
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    result={'exact_annotated_answer_set':float(pred==target),
            'annotated_answer_set_precision':precision,
            'annotated_answer_set_recall':recall,
            'annotated_answer_set_f1':f1,
            'predicted_answer_count':len(pred)}
    if pred and target:
        from scipy.optimize import linear_sum_assignment
        similarities=[[token_f1(a,b) for b in target] for a in pred]
        ii,jj=linear_sum_assignment(similarities,maximize=True)
        soft=sum(similarities[i][j] for i,j in zip(ii,jj))
    else:
        soft=0.0
    sp=soft/len(pred) if pred else float(not target)
    sr=soft/len(target) if target else float(not pred)
    result.update(annotated_answer_soft_precision=sp,
                  annotated_answer_soft_recall=sr,
                  annotated_answer_soft_f1=2*sp*sr/(sp+sr) if sp+sr else 0.0)
    return result


def context_scores(method,label,passages,unit_limit=5,word_limit=768):
    contexts=method['contexts']
    ids=[c['passage_id'] for c in contexts]
    if len(ids)>unit_limit:
        raise ValueError('Source-unit context budget exceeded.')
    selected=collections.defaultdict(list)
    words=0
    for c in contexts:
        text=passages[c['passage_id']]['text']
        a,b=c['start_char'],c['end_char_exclusive']
        if not 0<=a<b<=len(text):
            raise ValueError('Context offset is outside its source passage.')
        if any(max(a,x)<min(b,y) for x,y in selected[c['passage_id']]):
            raise ValueError('Context excerpts overlap within one passage.')
        selected[c['passage_id']].append((a,b))
        words+=len(text[a:b].split())
    if words>word_limit:
        raise ValueError('Word context budget exceeded.')
    spans=label['gold_answer_spans']
    if not spans:
        raise ValueError('Positive scoring requires nonempty source spans.')
    seen=[]
    for s in spans:
        text=passages[s['passage_id']]['text']
        a,b=s['start_char'],s['end_char_exclusive']
        if text[a:b]!=s['answer']:
            raise ValueError('Gold span does not match its source substring.')
        ctx=selected.get(s['passage_id'],[])
        seen.append(any(x<=a and b<=y for x,y in ctx))
    gold_strings={normalize(x) for x in label['answers'] if normalize(x)}
    seen_strings={normalize(s['answer']) for s,hit in zip(spans,seen) if hit}
    gold_passages={s['passage_id'] for s in spans}
    result={'parent_passage_hit_at_5':float(bool(set(ids)&gold_passages)),
            'annotated_span_recall_at_5':sum(seen)/len(spans),
            'all_annotated_spans_covered_at_5':float(all(seen)),
            'annotated_string_recall_at_5':len(gold_strings&seen_strings)/len(gold_strings),
            'all_annotated_strings_covered_at_5':float(gold_strings<=seen_strings),
            'tokens_used':words,'units_used':len(ids), 'passages_used':len(set(ids))}
    if 'filtered_passage_ids' in method or 'filtered_contexts' in method:
        removed=set(method.get('filtered_passage_ids',[]))
        removed_excerpts=method.get('filtered_contexts',[])
        result['annotated_support_removed']=sum(s['passage_id'] in removed or any(
            r['passage_id']==s['passage_id'] and r['start_char']<=s['start_char']
            and s['end_char_exclusive']<=r['end_char_exclusive'] for r in removed_excerpts)
            for s in spans)/len(spans)
    if 'answers' in method:
        result.update(answer_scores(method['answers'],label['answers']))
    return result


def paired_bootstrap(rows,method,reference,metric,repetitions=2000,seed=20261006):
    grouped=collections.defaultdict(list)
    for r in rows:
        grouped[r['article_path']].append(r['methods'][method][metric]-r['methods'][reference][metric])
    groups=list(grouped.values())
    if not groups:
        return None
    rng=random.Random(seed)
    totals=[sum(x) for x in groups]
    counts=[len(x) for x in groups]
    samples=[]
    for _ in range(repetitions):
        sampled=[rng.randrange(len(groups)) for _ in groups]
        samples.append(sum(totals[i] for i in sampled)/sum(counts[i] for i in sampled))
    samples.sort()
    # Nearest observed bootstrap quantiles avoid silent interpolation changes.
    return {'delta':sum(totals)/sum(counts),
            'ci95':[samples[math.floor(.025*(repetitions-1))],samples[math.ceil(.975*(repetitions-1))]],
            'article_clusters':len(groups),'repetitions':repetitions,'seed':seed}


def run(labels,predictions,passages,config):
    label_map={r['question_id']:r for r in labels}
    pred_map={r['question_id']:r for r in predictions}
    if len(label_map)!=len(labels) or len(pred_map)!=len(predictions):
        raise ValueError('Duplicate question IDs are not allowed.')
    if set(label_map)!=set(pred_map):
        raise ValueError(f'Question mismatch: missing={len(set(label_map)-set(pred_map))}; extra={len(set(pred_map)-set(label_map))}')
    required=set(config['methods'])
    rows=[]
    for qid in sorted(label_map):
        label=label_map[qid]
        pred=pred_map[qid]
        if set(pred['methods'])!=required:
            raise ValueError(f'{qid}: Every method must supply every frozen question.')
        row={'question_id':qid,'article_path':label['history_id'].rsplit('#',1)[0],'methods':{}}
        for method,item in pred['methods'].items():
            row['methods'][method]=context_scores(item,label,passages,
              config['contexts']['unit_limit'],config['contexts']['word_limit'])
        rows.append(row)
    if not rows:
        raise ValueError('No questions to score.')
    metrics=set.intersection(*(set(r['methods'][m]) for r in rows for m in required))
    # Every condition either supplies reader answers, or none does.
    reader_flags={('answers' in p['methods'][m]) for p in predictions for m in required}
    if len(reader_flags)>1:
        raise ValueError('Reader output is missing for some methods or questions.')
    summary={'n_questions':len(rows),'n_articles':len({r['article_path'] for r in rows}),
       'metrics':{m:{x:sum(r['methods'][m][x] for r in rows)/len(rows) for x in sorted(metrics)} for m in sorted(required)},
       'paired_intervals':{}}
    reference=config['statistics']['primary_comparator']
    for m in sorted(required-{reference}):
        summary['paired_intervals'][m]={x:paired_bootstrap(rows,m,reference,x,
              config['statistics']['paired_resamples'],config['statistics']['seed'])
              for x in sorted(metrics) if x not in {'tokens_used','units_used','passages_used','predicted_answer_count'}}
    return rows,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--labels',required=True,type=Path)
    p.add_argument('--predictions',required=True,type=Path)
    p.add_argument('--passages',required=True,type=Path)
    p.add_argument('--config',type=Path,default=Path(__file__).with_name('config.json'))
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    config=json.loads(args.config.read_text())
    passages={r['passage_id']:r for r in read(args.passages)}
    rows,summary=run(read(args.labels),read(args.predictions),passages,config)
    summary['input_sha256']={str(x):hashlib.sha256(x.read_bytes()).hexdigest()
        for x in (args.labels,args.predictions,args.passages,args.config,Path(__file__))}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'scored_questions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'n_questions':summary['n_questions'],'n_articles':summary['n_articles'],'metrics':summary['metrics']},indent=2))
if __name__=='__main__':main()
