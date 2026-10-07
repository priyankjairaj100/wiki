"""Freeze TimeQA source-only pilot and validation partitions before pass-3 runs."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'pass2/naturaldata'
SEED='acl2027-pass3-protocol-20261006-v1'

def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def write_jsonl(path,rows):
    path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))

def article(row):
    return row['history_id'].rsplit('#',1)[0]

def hash_article(name):
    return hashlib.sha256((SEED+'\0'+name).encode()).hexdigest()

def main():
    paths={name:SOURCE/'normalized'/name for name in ['dev_disjoint_nonempty_annotations.jsonl','dev_passages.jsonl','test_passages.jsonl','human_test_nonempty_questions.jsonl']}
    paths['relations']=SOURCE/'raw/TimeQA_relations.json'
    dev=read(paths['dev_disjoint_nonempty_annotations.jsonl'])
    human=read(paths['human_test_nonempty_questions.jsonl'])
    articles=sorted({article(q) for q in dev},key=hash_article)
    pilot_articles=set(articles[:50])
    partitions={'dev_pilot':[q for q in dev if article(q) in pilot_articles],
                'dev_validation':[q for q in dev if article(q) not in pilot_articles],
                'human_test_confirmation':human}
    relations=json.loads(paths['relations'].read_text())
    sys.path.insert(0,str(ROOT/'pass2/baselines'))
    from run_timeqa import template_question
    dev_passages=read(paths['dev_passages.jsonl'])
    test_passages=read(paths['test_passages.jsonl'])
    all_dev_articles={p['article_path'] for p in dev_passages}
    all_test_articles={p['article_path'] for p in test_passages}
    overlaps=all_dev_articles & all_test_articles
    dev_passages=[p for p in dev_passages if p['article_path'] not in overlaps]
    titles={p['article_path']:p['text'] for p in dev_passages+test_passages if p['paragraph_index']==0}
    source_fields=('passage_id','article_path','paragraph_index','text')
    for name,rows in [('dev',dev_passages),('test',test_passages)]:
        write_jsonl(HERE/(name+'_source_passages.jsonl'),[{k:p[k] for k in source_fields} for p in rows])
    manifest={'version':1,'seed':SEED,'selection':'50 smallest SHA256(seed NUL article_path) among separated dev articles',
              'pilot_article_paths':sorted(pilot_articles),'dev_test_overlap_articles_removed':sorted(overlaps),
              'inputs':{str(p.relative_to(ROOT)):digest(p) for p in paths.values()},
              'test_status':'Previously inspected pass-2 baseline results. This is a confirmation track, not untouched test evidence.',
              'development_status':'Pilot selection uses article hashes only. Validation labels must remain unopened until configuration freeze.',
              'partitions':{}}
    for name,rows in partitions.items():
        rows=sorted(rows,key=lambda q:q['question_id'])
        queries=[]
        for q in rows:
            question=q['question_text'] or template_question(q,titles[article(q)],relations)
            assert '$' not in question
            queries.append({'question_id':q['question_id'],'question':question,'article_path':article(q),
                            'question_kind':'published_human' if q['question_text'] else 'official_template'})
        write_jsonl(HERE/(name+'_queries.jsonl'),queries)
        write_jsonl(HERE/(name+'_labels.jsonl'),rows)
        manifest['partitions'][name]={'n_articles':len({article(q) for q in rows}), 'n_queries':len(rows),
          'query_ids':[q['question_id'] for q in rows], 'queries_sha256':digest(HERE/(name+'_queries.jsonl')),
          'labels_sha256':digest(HERE/(name+'_labels.jsonl'))}
    assert not ({article(q) for q in partitions['dev_pilot']} & {article(q) for q in partitions['dev_validation']})
    assert not ({article(q) for q in dev} & all_test_articles)
    save(HERE/'split_manifest.json',manifest)
    print(json.dumps({k:{a:b for a,b in v.items() if a!='query_ids'} for k,v in manifest['partitions'].items()},indent=2))
if __name__=='__main__':main()
