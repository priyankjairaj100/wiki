import json,pathlib,tempfile,unittest
from pass3.extraction.succession_rules import extract,run


def p(text):return {'passage_id':'fixture','article_path':'/wiki/Example_Institute','text':text}


class SuccessionRuleChecks(unittest.TestCase):
    def test_active_clause_dates_and_direction(self):
        source=p('Alex North succeeded Pat West as director in 1949 .')
        x=extract(source)[0]
        self.assertEqual((x['previous'],x['next']),('Pat West','Alex North'))
        self.assertEqual(x['slot_key'],'example institute :: director')
        self.assertEqual(x['date']['lower_iso'],'1949-01-01')
        self.assertEqual(x['date']['upper_iso'],'1949-12-31')

    def test_adjacent_coordinate_and_named_passive(self):
        source=p('Alex North succeeded Pat West as director in 1949 , and in 1955 was succeeded by Sam East . East was succeeded by Jo South in 1959 .')
        xs=extract(source)
        self.assertEqual(len(xs),3)
        self.assertEqual([x['date']['source_span']['text'] for x in xs],['1949','1955','1959'])
        self.assertEqual([(x['previous'],x['next']) for x in xs],[('Pat West','Alex North'),('Alex North','Sam East'),('East','Jo South')])

    def test_unrelated_year_does_not_become_end(self):
        source=p('Alex North succeeded Pat West as director in 1949 . The institute moved in 1958 .')
        self.assertEqual(len(extract(source)),1)
        self.assertEqual(extract(source)[0]['date']['source_span']['text'],'1949')

    def test_ordinary_appointment_creates_no_replacement(self):
        self.assertEqual(extract(p('In 1949 Alex North was appointed director . In 1955 Sam East became director .')),[])

    def test_role_scope_does_not_merge(self):
        xs=extract(p('Alex North succeeded Pat West as director in 1949 . Alex North succeeded Pat West as chairman in 1950 . North was succeeded by Sam East in 1955 .'))
        self.assertEqual(len(xs),2)
        self.assertEqual({x['role'] for x in xs},{'director','chairman'})

    def test_explicit_until_replacement_preserves_shared_event(self):
        source=p('In 1922 Alex North succeeded Pat West as president of the Society , holding this position until 1932 when he was replaced by Sam East .')
        xs=extract(source)
        self.assertEqual(len(xs),2)
        self.assertEqual(xs[1]['date']['source_span']['text'],'1932')
        self.assertTrue(xs[1]['previous_end_is_same_source_event'])
        self.assertEqual(xs[1]['slot_key'],'society :: president')

    def test_exact_source_offsets(self):
        source=p('Alex North succeeded Pat West as director in February 1949 , and in 1955 was succeeded by Sam East .')
        for x in extract(source):
            for s in (x['source_span'],x['date']['source_span']):
                self.assertEqual(source['text'][s['start']:s['end']],s['text'])

    def test_seasons_and_unknown_dates_stay_unmodeled(self):
        self.assertEqual(extract(p('Alex North succeeded Pat West as director in 1949–50 .')),[])
        self.assertEqual(extract(p('Alex North succeeded Pat West as director before 1949 .')),[])

    def test_missing_previous_start_is_never_invented(self):
        source=p('Alex North succeeded Pat West as director in 1949 , and in 1955 was succeeded by Sam East .')
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);(root/'source.jsonl').write_text(json.dumps(source)+'\n')
            run(root/'source.jsonl',root/'out')
            claims=[json.loads(x) for x in (root/'out/claims.jsonl').read_text().splitlines()]
            pairs=[json.loads(x) for x in (root/'out/pairs.jsonl').read_text().splitlines()]
            self.assertEqual({x['holder'] for x in claims},{'Alex North','Sam East'})
            self.assertEqual(len(pairs),1)
            by_id={x['claim_id']:x for x in claims}
            self.assertEqual(by_id[pairs[0]['target_id']]['holder'],'Alex North')
            self.assertEqual(by_id[pairs[0]['witness_id']]['holder'],'Sam East')

if __name__=='__main__':unittest.main()
