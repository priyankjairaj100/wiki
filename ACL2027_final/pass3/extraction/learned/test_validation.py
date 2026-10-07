import unittest
from pass3.extraction.learned.validate_outputs import date_field, source_span, names_match


class ValidationChecks(unittest.TestCase):
    def test_literal_quotes(self):
        text='A replaced B as director in 2001 .'
        s=source_span(text,'replaced B')
        self.assertEqual(text[s['start']:s['end']],s['text'])
        with self.assertRaises(ValueError):source_span(text,'A succeeded B')

    def test_year_precision(self):
        text='A replaced B as director in 2001 .';s=source_span(text,text)
        d=date_field('2001',s,{'text':text})
        self.assertEqual(d['lower_iso'],'2001-01-01')
        self.assertEqual(d['upper_iso'],'2001-12-31')

    def test_season_not_calendar_year(self):
        text='A replaced B after the 2001–02 season .';s=source_span(text,text)
        with self.assertRaises(ValueError):date_field('2001',s,{'text':text})

    def test_unbounded_date_not_closed_year(self):
        text='A replaced B before 2001 .';s=source_span(text,text)
        with self.assertRaises(ValueError):date_field('2001',s,{'text':text})

    def test_unknown_start_is_not_created(self):
        text='A replaced B in 2001 .';s=source_span(text,text)
        self.assertIsNone(date_field(None,s,{'text':text}))

    def test_alias_match_requires_exact_name_component(self):
        self.assertTrue(names_match('Gertrud Bing','Bing'))
        self.assertFalse(names_match('Bing','Bingham'))

if __name__=='__main__':unittest.main()
