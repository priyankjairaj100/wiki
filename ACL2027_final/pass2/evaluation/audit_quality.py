#!/usr/bin/env python3
"""Deterministic source integrity and per-relation audit summaries."""
import collections,hashlib,json,pathlib
H=pathlib.Path(__file__).resolve().parent;O=H/'results';source=H.parents[1]/'work/external/TempLAMA_official_test.json'
rows=list(map(json.loads,source.open()))
summary={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rows':len(rows),'duplicate_source_row_ids':len(rows)-len({x['id'] for x in rows}),'rows_with_duplicate_answer_ids':sum(len(x['answer'])!=len({a['wikidata_id'] for a in x['answer']}) for x in rows),'rows_without_answers':sum(not x['answer'] for x in rows),'years':sorted({int(x['date']) for x in rows}),'relations':sorted({x['relation'] for x in rows})}
(O/'source_integrity.json').write_text(json.dumps(summary,indent=2)+'\n')
counts=collections.defaultdict(collections.Counter)
for e in map(json.loads,(O/'source_transitions.jsonl').open()):
 if e['split']!='test':continue
 c=counts[e['key'].rsplit('_',1)[1]];c['transitions']+=1;c['first_changed']+=e['first_changed'];c['first_changed_previous_retained']+=e['first_changed'] and e['previous_first_retained'];c['set_changed']+=bool(e['added'] or e['absent_from_next_label']);c['set_changed_value_retained']+=bool(e['added'] or e['absent_from_next_label']) and bool(e['retained'])
(O/'source_audit_by_relation.json').write_text(json.dumps(dict(counts),indent=2)+'\n')
