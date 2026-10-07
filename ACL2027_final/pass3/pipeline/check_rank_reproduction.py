"""Check that sorted token accumulation reproduces every recorded context."""
import argparse,datetime as dt,itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read,BM25,YEAR,sha

def check(folder):
    folder=Path(folder);units=read(folder/'units.jsonl');index=BM25(units);comparisons=0;mismatches=[]
    with (folder/'predictions.jsonl').open() as f:
        for line in f:
            p=json.loads(line);ranked,_=index.rank(p['question']);window=p['query_window']
            for name,item in p['methods'].items():
                order=ranked
                if name=='latest_mentioned_year_top20' and window:
                    year=dt.date.fromordinal(window[1]).year
                    def latest(i):return max([int(y) for y in YEAR.findall(units[i]['text']) if int(y)<=year],default=0)
                    order=sorted(ranked[:20],key=lambda i:-latest(i))+ranked[20:]
                removed=set(item['filtered_unit_ids'])
                selected=list(itertools.islice((units[i]['unit_id'] for i in order if units[i]['claim_id'] not in removed),5))
                comparisons+=1
                if selected!=item['selected_unit_ids']:mismatches.append({'question_id':p['question_id'],'method':name,'recorded':item['selected_unit_ids'],'deterministic':selected})
    result={'comparisons':comparisons,'mismatches':mismatches,'deterministic_accumulation_sha256':sha(ROOT/'pass3/pipeline/run_matched.py'),'original_run_sha256':sha(ROOT/'pass3/pipeline/run_matched_v1.py'),'scope':'All selected top-five units before source-prefix clipping','status':'passed' if not mismatches else 'failed'}
    (folder/'rank_reproduction_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not mismatches
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',required=True);a=p.parse_args();check(a.folder)
