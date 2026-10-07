"""Summarize certificate coverage without treating fallback text as modeled."""
import argparse,json
from pathlib import Path

def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x]
def summarize(folder):
    folder=Path(folder);pred={p['question_id']:p for p in read(folder/'predictions.jsonl')};audit=read(folder/'mechanism_questions.jsonl')
    def active(r,method):return any(c['kind']=='modeled' for c in pred[r['question_id']]['methods'][method]['contexts'])
    def stats(rows):
        parsed=[r for r in rows if r['query_time_parsed']]
        return {'n_questions':len(rows),'n_parsed':len(parsed),'stable_claim_contexts':sum(r['claim_context_certificate'] is True for r in parsed),'stable_fraction_of_parsed':sum(r['claim_context_certificate'] is True for r in parsed)/len(parsed) if parsed else None,'completion_sensitive':sum(r['completion_sensitive'] for r in rows),'possible_differs_interval':sum(r['possible_differs_interval'] for r in rows),'possible_differs_no_filter':sum(r['possible_differs_no_filter'] for r in rows)}
    result={
      'all_questions':stats(audit),
      'possible_context_has_modeled_unit':stats([r for r in audit if active(r,'possible_support')]),
      'lexical_top5_has_modeled_unit':stats([r for r in audit if active(r,'no_temporal_filter')]),
      'lexical_top20_has_modeled_unit':stats([r for r in audit if r['temporal_extraction_active']]),
      'possible_context_all_fallback':stats([r for r in audit if not active(r,'possible_support')]),
      'interpretation':'Stability certifies only modeled independent dates. Fallback source text remains fixed and unresolved.'}
    (folder/'conditioned_mechanism.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',required=True);a=p.parse_args();summarize(a.folder)
