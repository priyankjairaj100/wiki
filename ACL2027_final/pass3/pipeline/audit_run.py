"""Audit source partitioning, shown offsets, budgets, and compiler invariants."""
import argparse, collections, json, re
from pathlib import Path

def read(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x]
def audit(folder,source):
    folder=Path(folder);passages={p['passage_id']:p for p in read(source)}
    units=read(folder/'units.jsonl');by_id={u['unit_id']:u for u in units};by_p=collections.defaultdict(list)
    assert len(by_id)==len(units)
    for u in units:
        text=passages[u['passage_id']]['text'];a,b=u['start_char'],u['end_char_exclusive']
        assert text[a:b]==u['text'];assert 0<=a<b<=len(text)
        by_p[u['passage_id']].append((a,b))
    for pid,p in passages.items():
        cursor=0
        for a,b in sorted(by_p[pid]):
            assert a>=cursor,'Units overlap'
            assert not re.search(r'\w',p['text'][cursor:a]),'Substantive source text disappeared'
            cursor=b
        assert not re.search(r'\w',p['text'][cursor:]),'Substantive suffix disappeared'
    predictions=read(folder/'predictions.jsonl');ncontexts=0
    for p in predictions:
        for m,item in p['methods'].items():
            contexts=item['contexts'];assert len(contexts)<=5
            assert len({c['unit_id'] for c in contexts})==len(contexts)
            assert sum(len(c['text'].split()) for c in contexts)<=768
            for c in contexts:
                original=by_id[c['unit_id']]
                assert original['start_char']==c['start_char']
                assert c['end_char_exclusive']<=original['end_char_exclusive']
                assert passages[c['passage_id']]['text'][c['start_char']:c['end_char_exclusive']]==c['text']
                if c['kind']=='fallback':assert c['temporal_status']=='unknown'
            ncontexts+=1
    result={'source_passages':len(passages),'source_units':len(units),'queries':len(predictions),'method_contexts':ncontexts,'checks':['Exact source offsets','Disjoint source units','All substantive source characters retained','Maximum five shown units','Maximum 768 whitespace tokens','Fallback never marked guaranteed'],'status':'passed'}
    (folder/'integration_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',required=True);p.add_argument('--source',default='pass3/protocol/dev_source_passages.jsonl');a=p.parse_args();audit(a.folder,a.source)
