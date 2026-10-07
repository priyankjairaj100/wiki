"""Source annotations for the second expansion panel. No outcomes enter."""
from pathlib import Path
import sys
import json
import hashlib
import datetime

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from pass3.extraction.source_adapter import parse_date

OUT = ROOT / 'pass6/replacement'
rows = [json.loads(x) for x in (OUT / 'expanded_sample.jsonl').read_text().splitlines()]
specs = {
    262: ('Assistant Secretary of State for Western Hemisphere Affairs',
          [('Thomas A. Shannon Jr.', 'October 2005', None), ('Arturo Valenzuela', 'November 2009', None)],
          [(1, 0)],
          'The paragraph directly dates Shannon becoming Assistant Secretary and his replacement by Valenzuela. The when clause links the November 2009 endpoint and succession.'),
    277: ('coach of Châteauroux',
          [('Jean-Pierre Papin', '29 December 2009', None), ('Didier Tholot', 'May 2010', None)],
          [(1, 0)],
          'The title identifies the hired coach. The second sentence coordinates his May 2010 departure with replacement by Tholot.'),
    321: ('manager of FCI Levadia Tallinn',
          [('Valeri Bondarenko', '2001', None), ('Pasi Rautiainen', 'November 2001', None),
           ('Franco Pancheri', 'January 2003', 'June 2003')],
          [(1, 0), (2, 1), (2, 0)],
          'The paragraph supplies three dated managers in an explicit replacement sequence. The final-to-first edge follows the declared ordered-succession rule. Known order remains recorded because the first two start bounds overlap. Pancheri has a separate June 2003 end. Rüütli lacks an explicit appointment date and is excluded.'),
    323: ('president of PEN America',
          [('Jennifer Egan', '2018', None), ('Ayad Akhtar', 'December 2 , 2020', None)],
          [(1, 0)],
          'The paragraph expressly dates Egan becoming president and Akhtar succeeding her. The later list of other committee offices does not affect this pair.'),
    334: ('President of the Board of Education',
          [('Herwald Ramsbotham', 'April 1940', None), ('R . A . Butler', 'July 1941', None)],
          [(1, 0)],
          'The first sentence dates Ramsbotham entering this office. The next sentence keeps the same office and dates Butler succeeding him.'),
    346: ('manager of FC Flora',
          [('Arno Pijpers', 'January 2017', None), ('Jürgen Henn', 'January 2018', None)],
          [(1, 0)],
          'The paragraph dates Pijpers taking over as manager and Henn being appointed in his place. The December 2017 announcement is not treated as an actual tenure endpoint. Earlier managers lack suitable dates in this paragraph.'),
    349: ('Member of Parliament for North Dorset',
          [('David James', '1970', None), ('Sir Nicholas Baker', '1979', None)],
          [(1, 0)],
          'The paragraph dates James being elected for North Dorset and explicitly links his 1979 retirement with Baker succeeding him. The separate Brighton seat is excluded from this graph.'),
}

nonposition = {257, 258, 261, 264, 265, 269, 270, 271, 274, 275, 276, 281,
               282, 285, 287, 289, 291, 293, 296, 297, 302, 307, 309, 312,
               317, 319, 327, 328, 329, 330, 331, 347, 351, 352, 353, 355,
               358, 359, 362, 363, 364, 366, 369, 370, 372, 375, 378, 381, 383}
specific = {
    259: ('uncertain', 'The source dates Comencini holding office since 1994. September 1998 dates his attempted party split. His later expulsion and Gobbo replacement have no explicit bounded date.'),
    272: ('reject', 'The source describes intermittent match captaincy and a tactical replacement for one match. It does not establish continuous tenures between the two dates.'),
    308: ('uncertain', 'The source dates Lumsden becoming headmistress and resigning. The next sentence identifies Dove as replacement but does not date that appointment.'),
    314: ('uncertain', 'The broadcast interval does not explicitly date Brink becoming host. Wouters takes over after 1993, without a bounded appointment date.'),
    333: ('uncertain', 'Rautiainen replaces Kivisild after the 2005 season. That relative date does not define a bounded calendar start. Rüütli returning for 2009 does not supply the missing first start.'),
    345: ('excluded_exposure', 'This reviewer inspected a Zambia question and a source pivot during the current editorial audit before screening this panel. The paragraph otherwise supplies a dated pair. Exclude it from the source challenge.'),
    360: ('excluded_exposure', 'Ruud Lubbers is a known exposed article under the expansion instructions.'),
    373: ('reject', 'The paragraph dates two office events but does not identify the caretaker successor. The named-holder challenge does not invent that identity.'),
}


def get_date(text, raw, anchor=None):
    pos = text.index(raw, text.index(anchor) if anchor else 0)
    result = parse_date(raw, pos)
    assert result is not None
    return result


judgments = []
candidates = []
for index in range(256, 384):
    passage = rows[index]
    assert passage['review_index'] == index
    if index in specs:
        status = 'candidate_accept'
        reason = specs[index][3]
    elif index in specific:
        status, reason = specific[index]
    elif index in nonposition:
        status = 'reject'
        reason = 'The cue concerns success, a non-position replacement, or different relations. It does not establish two dated holders of one exclusive position.'
    else:
        status = 'reject'
        reason = 'The paragraph does not date both required starts for the same position. An undated, relative, projected, or unrelated event cannot supply the missing start.'
    judgments.append({'review_index': index, 'passage_id': passage['passage_id'],
                      'article_path': passage['article_path'], 'source_split': passage['source_split'],
                      'status': status, 'reason': reason, 'assessment': 'model-assisted source interpretation'})
    if index not in specs:
        continue
    role, items, edges, note = specs[index]
    text = passage['text']
    full_span = {'start': 0, 'end': len(text), 'text': text}
    claims = []
    for number, (holder, start_raw, end_raw) in enumerate(items):
        anchor = 'became president' if index == 323 and number == 0 else None
        start = get_date(text, start_raw, anchor)
        end = get_date(text, end_raw) if end_raw else None
        claims.append({'claim_id': f'r{index:03d}_c{number}', 'holder': holder, 'role': role,
                       'start': start, 'end': end,
                       'temporal_kind': 'validity_duration' if end else 'occurrence_start',
                       'source_span': full_span, 'source_order': number})
    candidates.append({'record_id': f'r{index:03d}', 'review_index': index, 'passage': passage,
                       'role': role, 'claims': claims,
                       'directed_pairs': [{'witness_id': claims[new]['claim_id'],
                                           'target_id': claims[old]['claim_id'], 'source_span': full_span,
                                           'reason': note,
                                           'derivation': 'ordered_succession_closure' if new-old > 1 else 'explicit_consecutive_replacement'}
                                          for new, old in edges],
                       'annotation_note': note,
                       'known_precedence': [[claims[old]['claim_id'], claims[new]['claim_id']] for new, old in edges],
                       'status': 'pending_independent_review', 'exposure_status': 'eligible_for_independent_review'})

assert len(judgments) == 128
for name, records in [('extra_judgments_b.jsonl', judgments), ('extra_candidates_b.jsonl', candidates)]:
    (OUT / name).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in records))
manifest = {'stage': 'Source annotation before certificate outcomes and independent review',
            'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'reviewed_indices': [256, 383], 'reviewed_paragraphs': len(judgments),
            'candidate_graphs': len(candidates),
            'candidate_claims': sum(len(r['claims']) for r in candidates),
            'candidate_edges': sum(len(r['directed_pairs']) for r in candidates),
            'assessment': 'model-assisted source interpretation',
            'files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [Path(__file__), OUT/'expanded_sample.jsonl', OUT/'expansion_freeze.json',
                                OUT/'extra_judgments_b.jsonl', OUT/'extra_candidates_b.jsonl']}}
(Path(__file__).parent / 'extra_b_annotation_freeze.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({key: value for key, value in manifest.items() if key != 'files'}, indent=2))
