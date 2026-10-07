#!/usr/bin/env python3
"""Regression and integration checks for source-clause-v3."""
import collections,json,pathlib,re,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass5.extraction.source_adapter import extract_all
from pass3.extraction.source_adapter import validate_model_records,build_pairs
from pass3.pipeline.run_matched import make_units
from pass3.theory.lifecycle import LifecycleClaim,compile_lifecycles

def passage(text,title='Jane_Smith',person=True):
    return {'passage_id':'example','article_path':'/wiki/'+title,'paragraph_index':0,'text':('Jane Smith was born in 1950 . ' if person else '')+text}

class AdapterTests(unittest.TestCase):
    def records(self,text,title='Jane_Smith',person=True):return extract_all([passage(text,title,person)])
    def test_between_duration(self):
        c=self.records('She served as president between 1995 and 1999 .')[0]
        self.assertEqual((c['start']['lower_iso'],c['end']['upper_iso']),('1995-01-01','1999-12-31'))
    def test_modifier_and_precise_duration(self):
        c=self.records('From January 2000 to February 2001 she also concurrently served as director of Science House .')[0]
        self.assertEqual(c['end']['upper_iso'],'2001-02-28')
    def test_coordination_disjoint(self):
        p=passage('She served as mayor from 1991 to 1994 and as president from 2001 to 2005 .')
        cs=extract_all([p]);self.assertEqual(len(cs),2)
        self.assertLessEqual(cs[0]['atomic_span']['end'],cs[1]['atomic_span']['start'])
    def test_organisation_pronoun_rejected(self):self.assertEqual(self.records('She was president from 1932 to 1952 .','An_Organisation',False),[])
    def test_crossed_coordinate_rejected(self):
        cs=self.records('Smith was director , and from 1991 to 2001 Nicholas Mann was director .')
        self.assertEqual([c['subject']['canonical'] for c in cs],['Nicholas Mann'])
    def test_appearance_date_not_tenure(self):self.assertEqual(self.records('She played for Example , making nine appearances between 1952 and 1959 .'),[])
    def test_relative_duration_not_open(self):self.assertEqual(self.records('In 1928 she moved to Oxford for three years .'),[])
    def test_end_cue_not_open(self):self.assertEqual(self.records('In 1973 she became manager of Example , but quit in April 1974 .'),[])
    def test_abbreviation_not_partial_value(self):self.assertEqual(self.records('She joined St . Johns College in 1941 .')[0]['value'],'St . Johns College')
    def test_two_direct_pairs(self):
        p=passage('Henri Frankfort succeeded Saxl as director in 1949 , and in 1955 was succeeded by Gertrud Bing . Bing was succeeded by Ernst Gombrich in 1959 .','Warburg_Institute',False)
        cs=extract_all([p]);validate_model_records(cs,[p]);units,modeled,rejected=make_units([p],cs)
        self.assertEqual(len(cs),3);self.assertEqual(len(build_pairs(cs)),2);self.assertEqual(rejected,[])
        compile_lifecycles([LifecycleClaim.from_record(c) for c in modeled],build_pairs(cs))
    def test_calibration_partition(self):
        ps=[json.loads(x) for x in (ROOT/'pass5/extraction/calibration_sources.jsonl').read_text().splitlines()]
        cs=extract_all(ps);validate_model_records(cs,ps);units,modeled,rejected=make_units(ps,cs)
        self.assertEqual(rejected,[]);self.assertEqual(len(modeled),len(cs))
        mids={c['claim_id'] for c in modeled};self.assertTrue(all(a in mids and b in mids for a,b in build_pairs(cs)))
        by=collections.defaultdict(list)
        for u in units:by[u['passage_id']].append(u)
        for p in ps:
            last=0
            for u in sorted(by[p['passage_id']],key=lambda x:x['start_char']):
                self.assertLessEqual(last,u['start_char']);self.assertFalse(re.search(r'\w',p['text'][last:u['start_char']]))
                self.assertEqual(p['text'][u['start_char']:u['end_char_exclusive']],u['text']);last=u['end_char_exclusive']
            self.assertFalse(re.search(r'\w',p['text'][last:]))

    def test_no_cross_paragraph_pronoun(self):
        ps=[passage('Smith was a scientist .'),{'passage_id':'other','article_path':'/wiki/Jane_Smith','paragraph_index':1,'text':'She joined Example Institute in 2000 .'}]
        self.assertEqual(extract_all(ps),[])
    def test_local_foreign_holder(self):
        c=self.records('Archibald was a director of Example . He served as manager from 1991 to 1995 .')[0]
        self.assertEqual(c['subject']['canonical'],'Archibald')
    def test_unresolved_pronoun(self):
        self.assertEqual(extract_all([{'passage_id':'a','article_path':'/wiki/Jane_Smith','paragraph_index':0,'text':'She joined Example in 2000 .'}]),[])
    def test_abbreviation_acronym(self):
        c=self.records('In 2000 Smith joined A.F.C . Totton .')[0]
        self.assertEqual(c['value'],'A.F.C . Totton')
    def test_initial_inside_name(self):
        c=self.records('In 2000 Smith joined J . Smith Institute .')[0]
        self.assertEqual(c['value'],'J . Smith Institute')
    def test_liga_period(self):
        c=self.records('In 2000 Smith joined German 3 . Liga club Example .')[0]
        self.assertEqual(c['value'],'German 3 . Liga club Example')
    def test_foreign_event_date(self):
        self.assertEqual(self.records('Following a reorganisation in 2000 , Smith became director of Example .'),[])
    def test_finite_predicate_cut(self):
        c=self.records('In 2000 Smith became director of Example and continued to work abroad .')[0]
        self.assertEqual(c['value'],'director of Example')
    def test_coordinated_roles_rejected(self):
        self.assertEqual(self.records('Smith served as Culture Secretary and Work Secretary from 2000 to 2005 .'),[])
    def test_calendar_departure(self):
        c=self.records('In 2000 Smith became director of Example . Smith resigned from Example in 2005 .')[0]
        self.assertEqual(c['end']['lower_iso'],'2005-01-01')
    def test_calendar_sacking(self):
        c=self.records('Smith became manager of Example in 2000 . Smith was sacked in October 2005 .')[0]
        self.assertEqual(c['end']['upper_iso'],'2005-10-31')
    def test_held_until(self):
        c=self.records('Smith became minister in 2000 . She held her position until 16 January 2005 .')[0]
        self.assertEqual(c['end']['lower_iso'],'2005-01-16')
    def test_ambiguous_end_not_attached(self):
        cs=self.records('Smith became director of Example in 2000 . Smith became manager of Elsewhere in 2001 . Her term ended in 2005 .')
        self.assertEqual(len(cs),2);self.assertTrue(all(c['end'] is None for c in cs))
    def test_about_year_fallback(self):
        self.assertEqual(self.records('In 2000 Smith joined Example for about a year .'),[])
    def test_abbreviated_duration_fallback(self):
        self.assertEqual(self.records('In 2000 Smith joined Example in Washington , D.C. , for a six-month term .'),[])
    def test_trial_expiry_fallback(self):
        self.assertEqual(self.records('In 2000 Smith joined Example on trial . Her trial expired without an offer .'),[])

if __name__=='__main__':unittest.main()
