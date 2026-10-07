"""Independently check source-only ranking invariants without reading labels."""
from __future__ import annotations
import argparse,builtins,hashlib,json,sys,time
from pathlib import Path
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read
from pass4.retrieval.ranking import TitleRanker,VARIANTS

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def run(args):
    start=time.time()
    units=read(args.units);queries=read(args.queries)
    previous={p['question_id']:p for p in read(args.pilot_predictions)}
    ranker=TitleRanker(units)
    paths=sorted({u['article_path'] for u in units})
    pathmap={p:f'sentinel-group-{i:06d}' for i,p in enumerate(paths)}
    renamed=[{**u,'article_path':pathmap[u['article_path']],'unit_id':f'sentinel-unit-{i:06d}'} for i,u in enumerate(units)]
    renamed_ranker=TitleRanker(renamed)
    expected=np.arange(len(units))
    counts={'full_permutations':0,'pilot_choice_matches':0,'default_api_matches':0,'metadata_counterfactuals':0,'opaque_source_identifier_counterfactuals':0,'file_access_blocked_calls':0,'deterministic_repeats':0,'stable_tie_checks':0,'title_priority_checks':0}
    for q in queries:
        for variant in VARIANTS:
            order,_,metadata=ranker.rank_with_metadata(q['question'],variant)
            assert np.array_equal(np.sort(order),expected),(q['question_id'],variant,'Not a full permutation')
            counts['full_permutations']+=1
            chosen=[units[i]['unit_id'] for i in order[:5]]
            assert chosen==previous[q['question_id']]['methods'][variant]['selected_unit_ids'],(q['question_id'],variant,'Pilot mismatch')
            counts['pilot_choice_matches']+=1
            if variant=='title_residual':
                assert ranker.rank(q['question'])[0]==order
                counts['default_api_matches']+=1
                altered={'question':q['question'],'question_id':'not-the-original-id','article_path':'not-the-source-article','date_range':'not-a-feature','answers':['poisoned answer'], 'relation_id':'poisoned relation'}
                assert ranker.rank(altered['question'])[0]==order
                counts['metadata_counterfactuals']+=1
                assert renamed_ranker.rank(q['question'])[0]==order
                counts['opaque_source_identifier_counterfactuals']+=1
                with patch.object(builtins,'open',side_effect=AssertionError('Unexpected file input')):
                    assert ranker.rank(q['question'])[0]==order
                counts['file_access_blocked_calls']+=1
                assert ranker.rank(q['question'])[0]==order
                counts['deterministic_repeats']+=1
                linked=set(metadata['article_paths'])
                if linked:
                    flags=[units[i]['article_path'] in linked for i in order]
                    assert flags==sorted(flags,reverse=True)
                    counts['title_priority_checks']+=1
    # An empty lexical query assigns all units equal zero scores.
    for variant in VARIANTS:
        assert ranker.rank('',variant)[0]==expected.tolist()
        counts['stable_tie_checks']+=1
    # A long title must beat a nested short title; unmatched queries must keep global BM25.
    toy=[{'title':'Ada Lovelace','article_path':'ada-long','text':'She worked in 1843.'}, {'title':'Ada','article_path':'ada-short','text':'A language from 1980.'}, {'title':'Grace Hopper','article_path':'grace','text':'She worked in 1944.'}]
    tr=TitleRanker(toy)
    assert tr.link('Where did Ada Lovelace work?')['article_paths']==['ada-long']
    unmatched='A nonexistent subject worked in 1843?'
    assert tr.rank(unmatched)[0]==tr.index.rank(unmatched)[0]
    result={'status':'passed','queries':len(queries),'units':len(units),'counts':counts,'features_read':'Visible question string, public source titles, source text, and source grouping identifiers only.','gold_label_files_opened':0,'file_access_guard':'builtins.open patched to fail during each selected rank call after index construction; ranking succeeded.','source_identifier_control':'Every source unit and article group received an opaque replacement identifier; complete rankings stayed unchanged.','question_metadata_control':'Question IDs, source article labels, relation labels, dates, and answer fields changed while the visible question stayed fixed; complete rankings stayed unchanged.','elapsed_seconds':time.time()-start,'input_sha256':{str(p):sha(p) for p in [args.units,args.queries,args.pilot_predictions,Path(__file__),Path(__file__).with_name('ranking.py')]}}
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--units',default='pass3/pipeline/pilot_final/units.jsonl');p.add_argument('--queries',default='pass3/protocol/dev_pilot_queries.jsonl');p.add_argument('--pilot-predictions',default='pass4/retrieval/pilot/predictions.jsonl');p.add_argument('--output',default='pass4/retrieval/rank_integrity.json');run(p.parse_args())
