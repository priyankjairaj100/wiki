"""Normalize model extraction dates and enforce literal source grounding.

This is an optional inference interface. No model-generated extraction result
is used in the deterministic pilot. Semantic entailment needs a source audit.
"""
from __future__ import annotations
import copy
from .source_adapter import parse_date, stable_id, validate_model_records, VERSION


def normalize_model_output(payload, passage):
    result=[]
    for index,raw in enumerate(payload.get('records',[])):
        row=copy.deepcopy(raw)
        if row['passage_id']!=passage['passage_id']:raise ValueError('Passage identifier mismatch.')
        if row['article_path']!=passage['article_path']:raise ValueError('Article identifier mismatch.')
        for key in ('start','end'):
            if row.get(key) is None:continue
            source=row[key]['source_span'];date=parse_date(source['text'],source['start'])
            if date is None:raise ValueError('Unsupported or approximate date.')
            if row[key].get('precision')!=date['precision']:raise ValueError('Model date precision differs from source.')
            row[key]=date
        row.setdefault('claim_id',stable_id(passage['passage_id'],'model',index,row['atomic_span']['start']))
        row['coverage_scope']='atomic_clause_only'
        row['adapter_version']=VERSION+'-model-normalizer'
        row['replacement_policy']='explicit_succession_only'
        row['compiler_eligible']=row.get('end') is None or row['end']['lower']>row['start']['upper']
        row['state_text']=f"{row['subject']['canonical']}: {row['slot']} = {row['value']}."
        bounds=row['atomic_span']
        required=[row['subject']['source_span'],row['value_span'],row['start']['source_span']]
        if row.get('end'):required.append(row['end']['source_span'])
        if any(s['start']<bounds['start'] or s['end']>bounds['end'] for s in required):
            raise ValueError('Atomic excerpt omits a required grounding span.')
        result.append(row)
    # Caller supplies candidate claims when validating cross-record exclusions.
    without_pairs=copy.deepcopy(result)
    for row in without_pairs:row['exclusion_assertion']=None
    validate_model_records(without_pairs,[passage])
    return result
