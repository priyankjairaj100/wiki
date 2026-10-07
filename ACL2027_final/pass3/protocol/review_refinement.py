"""Independent finite checks for constructive worlds and ranking hardness.

This script implements its own world semantics. It does not call the theory
module's world evaluator or its certificate predicates to judge generated worlds.
"""
import itertools
import json
from pathlib import Path
import random
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'pass3/theory'))
from lifecycle import LifecycleClaim,compile_lifecycles
from refinement import context_counterworlds

def context(index,dates,rank,a,b,k,fallback=()):
    active=set(fallback)
    for cid in index.claims:
        if dates[cid]>b:continue
        later=[dates[d] for d,target in index.event_pairs if target==cid and dates[d]>dates[cid]]
        if not later or min(later)>a:active.add(cid)
    return tuple(c for c in rank if c in active)[:k]

def check_worlds():
    rng=random.Random(68091)
    result={'configurations':0,'contexts_checked':0,'counterworld_pairs_checked':0,'legal_worlds_enumerated':0}
    for _ in range(120):
        n=rng.randint(1,3)
        claims=[]
        for i in range(n):
            l=rng.randrange(3);u=rng.randrange(l,4)
            if i==0 and rng.random()<.5:
                end=u+1;claims.append(LifecycleClaim(str(i),'source',l,u,end,end+2))
            else:claims.append(LifecycleClaim(str(i),'source',l,u))
        pairs=[(str(i),str(j)) for i in range(n) for j in range(n) if i!=j and rng.random()<.55]
        index=compile_lifecycles(claims,pairs)
        fallback=['unknown_0','unknown_1'] if rng.random()<.5 else []
        rank=[str(i) for i in range(n)]+fallback;rng.shuffle(rank)
        for a,b in [(0,0),(1,1),(2,2),(3,3),(1.5,1.5),(0,4),(1,3)]:
            ids=list(index.events)
            values=[]
            for eid in ids:
                e=index.events[eid]
                values.append(sorted({v for v in [e.lower,e.upper,a,b,(e.lower+e.upper)/2] if e.lower<=v<=e.upper}))
            worlds=[dict(zip(ids,x)) for x in itertools.product(*values)]
            result['legal_worlds_enumerated']+=len(worlds)
            for k in range(len(rank)+1):
                contexts={context(index,d,rank,a,b,k,fallback) for d in worlds}
                counter=context_counterworlds(index,rank,a,b,k=k,unknown_ids=fallback)
                assert (counter is None)==(len(contexts)==1)
                result['contexts_checked']+=1
                if counter:
                    for w in [counter.support_world,counter.exclusion_world]:
                        assert set(w.event_dates)==set(index.events)
                        for eid,t in w.event_dates.items():assert index.events[eid].lower<=t<=index.events[eid].upper
                        assert w.selected_context==context(index,w.event_dates,rank,a,b,k,fallback)
                    assert counter.pivot_id in counter.support_world.selected_context
                    assert counter.pivot_id not in counter.exclusion_world.selected_context
                    result['counterworld_pairs_checked']+=1
        result['configurations']+=1
    return result

def check_bipartite_reduction():
    universe=set(range(3));sets=[{i for i in universe if mask&(1<<i)} for mask in range(8)]
    count=0;world_count=0
    for family in itertools.product(sets,repeat=3):
        for budget in [1,2,3]:
            original=any(set().union(*(family[j] for j in chosen))==universe
               for size in range(budget+1) for chosen in itertools.combinations(range(3),size))
            variables=[LifecycleClaim('v'+str(j),'',1,3) for j in range(3)]
            elements=[LifecycleClaim(f'e{i}_{r}','',0,0) for i in universe for r in range(budget+1)]
            claims=variables+elements+[LifecycleClaim('candidate','',0,0)]
            pairs=[('v'+str(j),f'e{i}_{r}') for j,S in enumerate(family) for i in S for r in range(budget+1)]
            index=compile_lifecycles(claims,pairs)
            rank=[x.cid for x in claims]
            feasible=False
            # [1,3] has exactly two relevant query states. Interior values give
            # the same masks as 1 (at/before query) or 3 (after query).
            for dates in itertools.product([1,3],repeat=3):
                world={x.cid:x.lower for x in claims};world.update(zip([x.cid for x in variables],dates))
                feasible|='candidate' in context(index,world,rank,2,2,budget+1)
                world_count+=1
            assert original==feasible
            count+=1
    return {'set_cover_instances':count,'date_worlds_checked':world_count}

if __name__=='__main__':
    result={'independent_counterworld_check':check_worlds(),'independent_hardness_reduction_check':check_bipartite_reduction(),
      'interpretation':'Constructed correctness checks. Finite checks supplement the proofs; they are not benchmark observations.'}
    Path(__file__).with_name('independent_refinement_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
