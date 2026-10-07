"""Strict reader parsing, fixed before response inspection.

Accept one complete JSON object, optionally inside one markdown code fence.
Never extract a JSON-looking substring from narrative. Never consult gold labels.
Malformed or truncated outputs become empty answers with a failure flag.
"""
import json
import re

FENCE=re.compile(r'\A```(?:json)?\s*\n?(.*?)\n?```\s*\Z',re.I|re.S)

def parse_response(text,context_count,finish_reason='stop'):
    def fail(reason):return {'answers':[],'evidence':[],'parse_ok':False,'parse_failure':reason}
    if finish_reason!='stop':return fail('non_stop_finish')
    if not isinstance(text,str):return fail('non_string_response')
    stripped=text.strip()
    fenced=FENCE.fullmatch(stripped)
    if fenced:stripped=fenced.group(1).strip()
    try:obj=json.loads(stripped)
    except (ValueError,TypeError):return fail('invalid_complete_json')
    if not isinstance(obj,dict):return fail('not_an_object')
    if not isinstance(obj.get('answers'),list):return fail('answers_not_list')
    if not isinstance(obj.get('evidence'),list):return fail('evidence_not_list')
    if any(not isinstance(x,str) or not x.strip() for x in obj['answers']):return fail('invalid_answer_element')
    if any(type(i) is not int or not 1<=i<=context_count for i in obj['evidence']):return fail('invalid_evidence_index')
    return {'answers':[x.strip() for x in obj['answers']],'evidence':sorted(set(obj['evidence'])),
            'parse_ok':True,'parse_failure':None}
