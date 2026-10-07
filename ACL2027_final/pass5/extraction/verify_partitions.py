#!/usr/bin/env python3
"""Verify literal source grounding and complete, disjoint retrieval partitions."""
import argparse,collections,hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import make_units
from pass3.extraction.source_adapter import validate_model_records,build_pairs
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles

def verify(source,claims_path,out):
    ps=[json.loads(x) for x in pathlib.Path(source).read_text().splitlines()]
    cs=[json.loads(x) for x in pathlib.Path(claims_path).read_text().splitlines()]
    validate_model_records(cs,ps);us,ms,rejected=make_units(ps,cs)
    assert not rejected,rejected
    ids={c['claim_id'] for c in ms};pairs=build_pairs(cs)
    assert all(a in ids and b in ids for a,b in pairs)
    compile_lifecycles([LifecycleClaim.from_record(c) for c in ms],pairs)
    by=collections.defaultdict(list)
    for u in us:by[u['passage_id']].append(u)
    for p in ps:
        last=0
        for u in sorted(by[p['passage_id']],key=lambda x:x['start_char']):
            assert last<=u['start_char']
            assert not re.search(r'\w',p['text'][last:u['start_char']])
            assert u['text']==p['text'][u['start_char']:u['end_char_exclusive']]
            last=u['end_char_exclusive']
        assert not re.search(r'\w',p['text'][last:])
    result={'input_passages':len(ps),'records':len(cs),'units':len(us),'modeled_units':len(ms),'fallback_units':len(us)-len(ms),
            'rejected_records':rejected,'pairs':len(pairs),'pair_endpoints_survive':True,'all_source_words_preserved':True,
            'modeled_unit_percent':100*len(ms)/len(us),
            'source_sha256':hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest(),
            'claims_sha256':hashlib.sha256(pathlib.Path(claims_path).read_bytes()).hexdigest()}
    pathlib.Path(out).write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--claims',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    print(json.dumps(verify(args.source,args.claims,args.out),indent=2))
