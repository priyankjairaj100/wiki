"""Remove calibration articles before validation outcomes; retain the initial split."""
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return [json.loads(x) for x in p.read_text().splitlines() if x]
def write(p,rows):p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
def article(q):return q.get('article_path') or q['history_id'].rsplit('#',1)[0]

def main():
    old=HERE/'v1_original_split'
    old.mkdir(exist_ok=True)
    for name in ['split_manifest.json','dev_validation_queries.jsonl','dev_validation_labels.jsonl']:
        if not (old/name).exists():shutil.copyfile(HERE/name,old/name)
    succession_path=ROOT/'pass3/data/dev_succession_selection.json'
    audit_path=ROOT/'pass3/data/dev_source_audit.json'
    succession=json.loads(succession_path.read_text())
    audit=json.loads(audit_path.read_text())
    reasons={}
    for a in succession['article_paths']:reasons.setdefault(a,[]).append('Source-cue succession calibration; no question, answer, or outcome selection.')
    for x in audit['examples']:reasons.setdefault(x['article_path'],[]).append('Earlier qualitative source audit selected a gold anchor paragraph; exclude from validation.')
    reasons.setdefault('/wiki/Val_Ackerman',[]).append('Additional source paragraph inspected during extraction development.')
    queries=read(old/'dev_validation_queries.jsonl')
    labels=read(old/'dev_validation_labels.jsonl')
    kept_q=[q for q in queries if article(q) not in reasons]
    kept_l=[q for q in labels if article(q) not in reasons]
    removed_q=[q for q in queries if article(q) in reasons]
    removed_l=[q for q in labels if article(q) in reasons]
    write(HERE/'dev_validation_queries.jsonl',kept_q)
    write(HERE/'dev_validation_labels.jsonl',kept_l)
    write(HERE/'dev_additional_calibration_queries.jsonl',removed_q)
    write(HERE/'dev_additional_calibration_labels.jsonl',removed_l)
    assert len(kept_q)+len(removed_q)==len(queries)
    assert {q['question_id'] for q in kept_q}=={q['question_id'] for q in kept_l}
    manifest=json.loads((old/'split_manifest.json').read_text())
    manifest['version']=2
    amendment={'id':'exclude-calibration-20261006-v2','timing':'Before pass-3 validation comparative outcomes.',
      'initial_validation_queries':len(queries),'initial_validation_articles':len({article(q) for q in queries}),
      'removed_validation_queries':len(removed_q),'removed_validation_articles':len({article(q) for q in removed_q}),
      'remaining_validation_queries':len(kept_q),'remaining_validation_articles':len({article(q) for q in kept_q}),
      'calibration_article_reasons':reasons,
      'sources':{str(p.relative_to(ROOT)):digest(p) for p in [succession_path,audit_path]},
      'selection_scope':'The succession sample is source-only. Ten earlier audit articles were selected through gold anchors. All are excluded.',
      'source_exposure':'Initial regex development inspected text beyond the hash pilot. Remaining validation source text is not claimed completely unseen.',
      'preserved_original':'pass3/protocol/v1_original_split/'}
    manifest['amendments']=[amendment]
    manifest['development_status']='Hash pilot unchanged. Additional calibration articles excluded before validation outcomes. Source text outside pilot was inspected during initial regex development. No completely unseen-source claim.'
    manifest['partitions']['dev_validation']={'n_articles':len({article(q) for q in kept_q}),'n_queries':len(kept_q),
       'query_ids':[q['question_id'] for q in kept_q],
       'queries_sha256':digest(HERE/'dev_validation_queries.jsonl'),'labels_sha256':digest(HERE/'dev_validation_labels.jsonl')}
    manifest['partitions']['dev_additional_calibration']={'n_articles':len({article(q) for q in removed_q}),'n_queries':len(removed_q),
       'query_ids':[q['question_id'] for q in removed_q],
       'queries_sha256':digest(HERE/'dev_additional_calibration_queries.jsonl'),'labels_sha256':digest(HERE/'dev_additional_calibration_labels.jsonl')}
    (HERE/'split_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    (HERE/'split_amendment.json').write_text(json.dumps(amendment,indent=2,ensure_ascii=False)+'\n')
    config=json.loads((HERE/'config.json').read_text())
    config['tracks']['dev_validation'].update(articles=len({article(q) for q in kept_q}),questions=len(kept_q))
    config['tracks']['dev_additional_calibration']={'articles':len({article(q) for q in removed_q}),'questions':len(removed_q),'use':'Source calibration only. Excluded from validation before outcomes.'}
    (HERE/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    print(json.dumps({k:v for k,v in amendment.items() if k not in ['calibration_article_reasons','sources']},indent=2))
if __name__=='__main__':main()
