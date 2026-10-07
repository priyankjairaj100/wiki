"""Select and certify only the ranked prefix needed for a context.

The input ranking must contain every source unit once in a fixed strict order.
The caller validates this invariant when constructing the ranking.
Fallback units remain eligible and carry no temporal guarantee.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping,Sequence,Iterable
from pass3.theory.lifecycle import LifecycleIndex

@dataclass(frozen=True)
class LazySelection:
    possible_unit_ids: tuple[str,...]
    unresolved_frontier: tuple[str,...]
    stable: bool
    examined_candidates: int
    possible_checks: int
    guaranteed_checks: int
    selected_modeled: int
    selected_fallback: int

    @property
    def support_checks(self):
        return self.possible_checks+self.guaranteed_checks


def select_lazy(ranking: Iterable[int], units: Sequence[Mapping], index: LifecycleIndex,
                query_window: tuple[float,float], k: int=5) -> LazySelection:
    """Return the possible context and its exact stability decision in O(j).

    Here j is the number of ranked candidates examined through the kth eligible
    unit, or the full ranking length when fewer than k units are eligible.
    Compilation and relevance ranking happen before this function.
    The returned frontier contains selected possible but unguaranteed units.
    Stability concerns unit selection before source-word truncation.
    """
    if not isinstance(k,int) or k<0:raise ValueError('k must be a nonnegative integer')
    a,b=query_window
    if a>b:raise ValueError('Query window must be nonempty and ordered')
    chosen=[];frontier=[];examined=possible=guaranteed=fallback=modeled=0
    if k:
        for position in ranking:
            unit=units[position];examined+=1;cid=unit.get('claim_id')
            if cid is None:
                chosen.append(unit['unit_id']);fallback+=1
            else:
                certificate=index.certificates[cid];possible+=1
                if not certificate.possible(a,b):continue
                chosen.append(unit['unit_id']);modeled+=1;guaranteed+=1
                if not certificate.guaranteed(a,b):frontier.append(unit['unit_id'])
            if len(chosen)==k:break
    return LazySelection(tuple(chosen),tuple(frontier),not frontier,examined,possible,guaranteed,modeled,fallback)
