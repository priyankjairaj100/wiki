"""Exact stable unit budgets under the frozen complete lexical ranking.

The diagnostic varies the unit count without source-prefix token clipping.
Its modeled-context cohort remains fixed by the original five-unit run.
No reader or answer labels enter this calculation.
"""
from __future__ import annotations
import argparse,csv,json,os,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass3.pipeline.run_matched import read,dump,lines,sha,BM25
from pass3.extraction.source_adapter import build_pairs
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles

BUDGETS=(1,3,5,10,20)

def run(folder,queryfile):
    started=time.perf_counter();os.nice(10)
    folder=Path(folder);units=read(folder/'units.jsonl');records=read(folder/'claims.jsonl')
    audit=read(folder/'mechanism_questions.jsonl');queries={q['question_id']:q for q in read(queryfile)}
    claimmap={r['claim_id']:r for r in records};modeled=[(i,u['claim_id']) for i,u in enumerate(units) if u['claim_id']]
    life=compile_lifecycles([LifecycleClaim.from_record(claimmap[c]) for i,c in modeled],build_pairs(records))
    mi=np.array([i for i,c in modeled],dtype=np.int32)
    lower=np.array([life.certificates[c].lower for i,c in modeled]);upper=np.array([life.certificates[c].upper for i,c in modeled])
    possible_end=np.array([life.certificates[c].possible_end for i,c in modeled]);witness_lower=np.array([life.certificates[c].potential_witness_lower for i,c in modeled])
    bm25=BM25(units);rows=[];comparisons=0
    for saved in audit:
        if not saved['query_time_parsed']:continue
        qid=saved['question_id'];a,b=saved['query_window'];ranked,_=bm25.rank(queries[qid]['question']);ranked=np.asarray(ranked,dtype=np.int32)
        possible=np.ones(len(units),dtype=bool);guaranteed=np.ones(len(units),dtype=bool)
        possible[mi]=(lower<=b)&(a<possible_end)
        guaranteed[mi]=(upper<=b)&((a<=lower)|(a<witness_lower))
        assert np.all(~guaranteed|possible)
        possible_order=ranked[possible[ranked]];guaranteed_order=ranked[guaranteed[ranked]]
        unresolved=np.flatnonzero(~guaranteed[possible_order])
        r=int(unresolved[0])+1 if len(unresolved) else None
        stable={str(k):r is None or k<r for k in BUDGETS}
        for k in BUDGETS:
            assert stable[str(k)]==np.array_equal(possible_order[:k],guaranteed_order[:k]);comparisons+=1
        assert stable['5']==saved['claim_context_certificate']
        frozen_cohort=saved['shown_fallback_fraction']['possible_support']<1.0
        rows.append({'question_id':qid,'article_path':saved['article_path'],'query_window':[a,b],
          'fixed_modeled_top5_cohort':frozen_cohort,'first_unresolved_possible_rank':r,
          'largest_stable_unit_budget':r-1 if r is not None else None,
          'unbounded_stable_budget':r is None,
          'first_unresolved_unit_id':units[int(possible_order[r-1])]['unit_id'] if r else None,
          'stable_at_budget':stable,'possible_units':len(possible_order)})
    cohort=[r for r in rows if r['fixed_modeled_top5_cohort']]
    assert len(rows)==2296 and len(cohort)==375
    def summarize(selected):
        return {'queries':len(selected),'budgets':{str(k):{'stable':sum(r['stable_at_budget'][str(k)] for r in selected),'rate':sum(r['stable_at_budget'][str(k)] for r in selected)/len(selected)} for k in BUDGETS}}
    summary={'all_parsed':summarize(rows),'fixed_modeled_top5_cohort':summarize(cohort),
      'frozen_cohort_definition':'Parsed validation queries with at least one modeled excerpt in the original rendered possible-support context at k=5.',
      'scope':'Complete frozen BM25 ranking and independent modeled dates, with fixed fallback. Vary the source-unit budget without the 768-token clipping step.',
      'decision':'Let r be the first unresolved item in possible-filtered order. All k<r are stable. All k>=r are unstable. If no such item exists, every budget is stable.',
      'direct_context_equality_checks':comparisons,'matched_original_k5_certificates':len(rows),'gold_label_reads':0,'model_calls':0,
      'elapsed_seconds':time.perf_counter()-started,
      'input_sha256':{str(p):sha(p) for p in [folder/'units.jsonl',folder/'claims.jsonl',folder/'mechanism_questions.jsonl',queryfile,Path(__file__),ROOT/'pass3/pipeline/run_matched.py']}}
    lines(folder/'stable_budget_questions.jsonl',rows);dump(folder/'stable_budget_summary.json',summary)
    with (folder/'stable_budget.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['budget','stable_fixed_cohort','fixed_cohort_queries','rate_fixed_cohort','stable_all_parsed','all_parsed_queries','rate_all_parsed'])
        for k in BUDGETS:
            c=summary['fixed_modeled_top5_cohort']['budgets'][str(k)];allq=summary['all_parsed']['budgets'][str(k)]
            w.writerow([k,c['stable'],len(cohort),c['rate'],allq['stable'],len(rows),allq['rate']])
    tex=['% Generated from frozen validation query decisions.',r'\begin{tabular}{lrrrrr}',r'\toprule','Context units & '+ ' & '.join(map(str,BUDGETS))+r' \\',r'\midrule']
    tex.append('Stable contexts & '+' & '.join(f"{summary['fixed_modeled_top5_cohort']['budgets'][str(k)]['stable']}/375" for k in BUDGETS)+r' \\')
    tex.append('Stable (\%) & '+' & '.join(f"{100*summary['fixed_modeled_top5_cohort']['budgets'][str(k)]['rate']:.1f}" for k in BUDGETS)+r' \\')
    tex.extend([r'\bottomrule',r'\end{tabular}']);(folder/'stable_budget_table.tex').write_text('\n'.join(tex)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'ps.fonttype':42})
    fig,ax=plt.subplots(figsize=(3.25,1.9));ys=[100*summary['fixed_modeled_top5_cohort']['budgets'][str(k)]['rate'] for k in BUDGETS]
    ax.plot(BUDGETS,ys,color='#245778',marker='o',markersize=4,linewidth=1.5)
    for k,y in zip(BUDGETS,ys):ax.annotate(f'{y:.1f}',(k,y),xytext=(0,5),textcoords='offset points',ha='center',fontsize=7)
    ax.set(xlabel='Source units in context',ylabel='Stable contexts (%)',xticks=BUDGETS,ylim=(max(0,min(ys)-10),100));ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.tight_layout(pad=.5)
    for ext in ['pdf','svg','png']:fig.savefig(folder/f'stable_budget.{ext}',dpi=240,bbox_inches='tight')
    plt.close(fig)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',default='pass3/pipeline/validation');p.add_argument('--queries',type=Path,default=Path('pass3/protocol/dev_validation_queries.jsonl'));a=p.parse_args();run(a.folder,a.queries)
