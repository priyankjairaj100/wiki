#!/usr/bin/env python3
"""Normalize published TimeQA annotations without generating evidence or question text."""
from __future__ import annotations
import collections, datetime, hashlib, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parent
RAW=ROOT/'raw'; OUT=ROOT/'normalized'; OUT.mkdir(exist_ok=True)
REPO='https://github.com/wenhuchen/Time-Sensitive-QA'
TREE=json.loads((RAW/'timeqa_tree.json').read_text()); COMMIT=TREE['sha']
FILES={x['path']:x for x in TREE['tree'] if x['type']=='blob'}
relations=json.loads((RAW/'TimeQA_relations.json').read_text())

def write_rows(path,rows):
    with path.open('w',encoding='utf8') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def date_record(t):
    months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    p=t.split();return {'raw':t,'year':int(p[-1]),'month':months.index(p[0])+1 if len(p)==2 else None,'precision':'month' if len(p)==2 else 'year'}
def norm_answer(s):return ' '.join(s.split()) # no alias merging and no lowercase collapsing
manifest={'dataset':'TimeQA','paper':'A Dataset for Answering Time-Sensitive Questions','paper_url':'https://arxiv.org/abs/2108.06314','official_repository':REPO,'commit':COMMIT,'retrieved_utc':json.loads((ROOT/'source_manifest.json').read_text()).get('retrieved_utc') if (ROOT/'source_manifest.json').exists() else datetime.datetime.now(datetime.timezone.utc).isoformat(),'license_path':'raw/TimeQA_LICENSE','license_statement':'Authors release data and code under BSD 3-Clause. Wikipedia text remains third-party source content. Preserve attribution and applicable Wikipedia terms.','files':[]}
manifest['source_tree']={'path':'raw/timeqa_tree.json','source_url':f'https://api.github.com/repos/wenhuchen/Time-Sensitive-QA/git/trees/{COMMIT}?recursive=1','sha256':digest(RAW/'timeqa_tree.json')}
for local,remote in [('TimeQA_README.md','README.md'),('TimeQA_LICENSE','LICENSE'),('TimeQA_relations.json','relations.json'),('TimeQA_annotated_test.json','dataset/annotated_test.json'),('TimeQA_annotated_dev.json','dataset/annotated_dev.json'),('TimeQA_human_annotated_test.json','dataset/human_annotated_test.json')]:
    p=RAW/local;b=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert blob==FILES[remote]['sha'],(local,blob,FILES[remote]['sha'])
    manifest['files'].append({'path':str(p.relative_to(ROOT)),'source_url':f'https://raw.githubusercontent.com/wenhuchen/Time-Sensitive-QA/{COMMIT}/{remote}','github_blob_sha1':blob,'sha256':digest(p),'bytes':len(b),'source_split':'dev' if 'annotated_dev' in local else 'test' if 'annotated_test' in local else None})
(ROOT/'source_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
summary={'dataset':'TimeQA','normalization':'Preserve original questions, original date strings, source paragraphs, and exact gold answer spans. No generated prose.','splits':{},'scope':'Dates are published annotation ranges, not document publication dates or arrival times. Use question-level gold spans. Do not invalidate whole paragraphs from one retired fact.'}
raw_splits={}; normalized={}
for split in ['dev','test']:
    data=json.loads((RAW/f'TimeQA_annotated_{split}.json').read_text());raw_splits[split]=data
    histories=[];questions=[];passages={};span_matches=0;span_count=0;trans=collections.Counter();answer_card=collections.Counter()
    for row,record in enumerate(data):
        ids=[]
        for n,text in enumerate(record['paras']):
            # An article paragraph can serve several relation histories; preserve one source identity.
            pid=hashlib.sha256((record['link']+'\0'+str(n)+'\0'+text).encode()).hexdigest()[:24]
            ids.append(pid)
            passage={'passage_id':pid,'article_url':'https://en.wikipedia.org'+record['link'],'article_path':record['link'],'paragraph_index':n,'text':text,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'source_split':split}
            if pid in passages:assert passages[pid]['text']==text
            passages[pid]=passage
        history={'history_id':record['index'],'article_url':'https://en.wikipedia.org'+record['link'],'relation_id':record['type'],'relation_label':relations.get(record['type'],{}).get('meaning'),'relation_mode':relations.get(record['type'],{}).get('mode'),'source_split':split,'source_row':row,'paragraph_ids':ids,'question_ids':[]}
        states=[]
        for qn,(dates,answers) in enumerate(record['questions']):
            qid=f"{record['index']}#annotation{qn}";history['question_ids'].append(qid);spans=[]
            for a in answers:
                para=record['paras'][a['para']];found=para[a['from']:a['end']]
                assert found==a['answer'],(record['index'],qn,a,found)
                span_matches+=found==a['answer'];span_count+=1
                spans.append({'passage_id':ids[a['para']],'paragraph_index':a['para'],'start_char':a['from'],'end_char_exclusive':a['end'],'answer':a['answer']})
            values=sorted({norm_answer(x['answer']) for x in answers});states.append(set(values));answer_card[len(values)]+=1
            questions.append({'question_id':qid,'history_id':record['index'],'source_split':split,'source_row':row,'annotation_index':qn,'relation_id':record['type'],'question_text':None,'question_text_kind':'no natural-language question in this annotated source','date_range':[date_record(x) for x in dates],'date_semantics':'Published annotation range; year/month precision. No day-level validity or publication date is inferred.','answers':values,'gold_answer_spans':spans,'gold_passage_ids':sorted({s['passage_id'] for s in spans})})
        for j,(before,after) in enumerate(zip(states,states[1:])):
            trans['adjacent_annotation_pairs']+=1
            trans['retained_answer_pairs']+=bool(before&after)
            trans['answer_removed_pairs']+=bool(before-after)
            trans['answer_added_pairs']+=bool(after-before)
            trans['partial_answer_removal_pairs']+=bool(before-after) and bool(before&after)
            if record['questions'][j][0][1]==record['questions'][j+1][0][0]:
                trans['matching_boundary_pairs']+=1
                trans['matching_boundary_retained_pairs']+=bool(before&after)
                trans['matching_boundary_partial_removal_pairs']+=bool(before-after) and bool(before&after)
        histories.append(history)
    write_rows(OUT/f'{split}_histories.jsonl',histories);write_rows(OUT/f'{split}_annotations.jsonl',questions);write_rows(OUT/f'{split}_passages.jsonl',passages.values())
    normalized[split]={'histories':histories,'questions':questions,'passages':passages}
    summary['splits'][split]={'histories':len(histories),'unique_articles':len({d['link'] for d in data}),'relations':len({d['type'] for d in data}),'annotations':len(questions),'source_paragraphs_before_deduplication':sum(len(d['paras']) for d in data),'unique_passages':len(passages),'gold_spans':span_count,'exact_gold_span_matches':span_matches,'answer_cardinality':dict(sorted(answer_card.items())),'multi_answer_annotations':sum(v for k,v in answer_card.items() if k>1),'date_range_equal_endpoints':sum(q['date_range'][0]['raw']==q['date_range'][1]['raw'] for q in questions),'adjacent_annotation_audit':dict(trans)}
# Human questions align exactly, in order, with the released test annotations.
human=json.loads((RAW/'TimeQA_human_annotated_test.json').read_text());base={r['index']:r for r in raw_splits['test']};nq={q['question_id']:q for q in normalized['test']['questions']};hqs=[]
for d in human:
    orig=base[d['index']]
    assert orig['paras']==d['paras']
    assert [q[1] for q in orig['questions']]==[q[1] for q in d['questions']]
    for i,(text,_) in enumerate(d['questions']):
        q=dict(nq[f"{d['index']}#annotation{i}"]);q.update(question_text=text,question_text_kind='published human-authored question',question_source_file='raw/TimeQA_human_annotated_test.json');hqs.append(q)
write_rows(OUT/'human_test_questions.jsonl',hqs)
summary['human_test']={'histories':len(human),'questions':len(hqs),'source': 'Published human-authored subset of test; not a separate independent split.','all_paragraphs_and_answer_annotations_match_parent_test':True,'multi_answer_questions':sum(len(q['answers'])>1 for q in hqs)}
# Audit source separation at history, article and literal paragraph levels.
dev=raw_splits['dev'];test=raw_splits['test'];dt={x['index'] for x in dev}&{x['index'] for x in test};da={x['link'] for x in dev}&{x['link'] for x in test}
# Ignore section-heading fragments when auditing literal text overlap.
dtexts={p['text_sha256'] for p in normalized['dev']['passages'].values() if len(p['text'])>=100};ttexts={p['text_sha256'] for p in normalized['test']['passages'].values() if len(p['text'])>=100}
summary['split_overlap']={'dev_test_history_ids':len(dt),'dev_test_article_paths':len(da),'dev_test_identical_paragraphs_min_100_characters':len(dtexts&ttexts),'overlap_article_paths':sorted(da),'overlap_history_ids':sorted(dt),'test_human_history_overlap':len(human)}
(ROOT/'timeqa_audit.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(summary,indent=2))
