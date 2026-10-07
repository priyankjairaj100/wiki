#!/usr/bin/env python3
"""Regression and integration checks for source-clause-v2."""
import collections,json,pathlib,re,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from pass4.extraction.source_adapter import extract_all
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
    def test_abbreviation_not_partial_value(self):self.assertEqual(self.records('She joined St . Johns College in 1941 .'),[])
    def test_two_direct_pairs(self):
        p=passage('Henri Frankfort succeeded Saxl as director in 1949 , and in 1955 was succeeded by Gertrud Bing . Bing was succeeded by Ernst Gombrich in 1959 .','Warburg_Institute',False)
        cs=extract_all([p]);validate_model_records(cs,[p]);units,modeled,rejected=make_units([p],cs)
        self.assertEqual(len(cs),3);self.assertEqual(len(build_pairs(cs)),2);self.assertEqual(rejected,[])
        compile_lifecycles([LifecycleClaim.from_record(c) for c in modeled],build_pairs(cs))
    def test_calibration_partition(self):
        ps=[json.loads(x) for x in (ROOT/'pass4/extraction/calibration_sources.jsonl').read_text().splitlines()]
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

if __name__=='__main__':unittest.main()
