import datetime as dt
import unittest
from pass3.extraction.source_adapter import add_source_context, extract_passage, parse_date, validate_model_records, build_pairs


def passage(text, **kwargs):
    return {'passage_id':'p','article_path':'/wiki/Jane_Smith','text':text,'paragraph_index':5,'article_person_evidence':True,**kwargs}


class AdapterTests(unittest.TestCase):
    def test_source_precision(self):
        y=parse_date('2000');m=parse_date('February 2000');d=parse_date('29 February 2000')
        self.assertEqual(y['upper']-y['lower'],365)
        self.assertEqual(m['upper']-m['lower'],28)
        self.assertEqual(d['lower'],dt.date(2000,2,29).toordinal())
        self.assertEqual(d['lower'],d['upper'])
        self.assertIsNone(parse_date('around 2000'))
        self.assertIsNone(parse_date('31 February 2000'))

    def test_duration_uses_distinct_endpoints(self):
        p=passage('She was director of Example Institute from 2001 to 2005 .')
        c=extract_passage(p)[0]
        self.assertEqual(c['temporal_kind'],'validity_duration')
        self.assertEqual(c['start']['upper_iso'],'2001-12-31')
        self.assertEqual(c['end']['lower_iso'],'2005-01-01')
        self.assertTrue(validate_model_records([c],[p]))

    def test_no_ordinary_membership_exclusion(self):
        p=passage('In 2001 she joined Example Institute . In 2004 she joined Example Society .')
        cs=extract_passage(p)
        self.assertEqual(len(cs),2)
        self.assertEqual(build_pairs(cs),[])

    def test_temporary_occurrences_remain_fallback(self):
        for text in ['In 2001 she joined Example on loan until 2004 .',
                     'In 2001 she signed for Example on a three-year contract .',
                     'In 2001 she moved to Example for the rest of the season .',
                     'In 2001 she was appointed director for three years .']:
            self.assertEqual(extract_passage(passage(text)),[],text)

    def test_election_does_not_become_start(self):
        self.assertEqual(extract_passage(passage('On 5 December 2012 she was elected president for 2013 .')),[])

    def test_date_in_later_clause_is_rejected(self):
        self.assertEqual(extract_passage(passage('She became president after serving as director in 2018 .')),[])

    def test_compound_tenure_does_not_attach_second_interval(self):
        p=passage('She was director from 2001 to 2005 and then again from 2008 to 2010 .')
        cs=extract_passage(p)
        self.assertEqual(len(cs),1)
        self.assertEqual(cs[0]['start']['lower_iso'],'2001-01-01')
        self.assertEqual(cs[0]['end']['lower_iso'],'2005-01-01')
        self.assertNotIn('2008',cs[0]['atomic_span']['text'])

    def test_source_span_credit_is_atomic(self):
        p=passage('In 2001 she joined Example , and she became director in 2008 .')
        c=extract_passage(p)[0]
        self.assertNotIn('2008',c['atomic_span']['text'])
        self.assertEqual(c['coverage_scope'],'atomic_clause_only')
        self.assertTrue(validate_model_records([c],[p]))

    def test_nonperson_article_does_not_resolve_she(self):
        p=passage('She was president from 2001 to 2005 .',article_path='/wiki/Example_Council',article_person_evidence=False)
        self.assertEqual(extract_passage(p),[])

    def test_answer_fields_are_unused(self):
        p=passage('In 2001 she joined Example .')
        original=extract_passage(p)
        p.update(answers=['Wrong'],date_range=[{'year':1}],relation_id='wrong')
        self.assertEqual(original,extract_passage(p))

    def test_inclusive_through_is_not_end_instant(self):
        self.assertEqual(extract_passage(passage('She was director from 2001 through 2005 .')),[])

if __name__=='__main__':unittest.main()
