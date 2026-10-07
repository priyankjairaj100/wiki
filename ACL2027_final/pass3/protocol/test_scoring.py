"""Focused safeguards for complete answers and actual shown source excerpts."""
import json
from pathlib import Path
import unittest
from score_predictions import answer_scores,context_scores,run

class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.passages={'p':{'text':'Alpha was first. Beta was next.'}}
        self.label={'question_id':'q','history_id':'article#relation',
          'answers':['Alpha','Beta'],'gold_answer_spans':[
            {'passage_id':'p','start_char':0,'end_char_exclusive':5,'answer':'Alpha'},
            {'passage_id':'p','start_char':17,'end_char_exclusive':21,'answer':'Beta'}]}
    def test_two_excerpts_same_passage(self):
        m={'contexts':[{'passage_id':'p','start_char':0,'end_char_exclusive':16},
                       {'passage_id':'p','start_char':17,'end_char_exclusive':31}]}
        result=context_scores(m,self.label,self.passages)
        self.assertEqual(result['annotated_string_recall_at_5'],1)
        self.assertEqual(result['units_used'],2)
        self.assertEqual(result['passages_used'],1)
    def test_parent_hit_does_not_credit_unshown_span(self):
        m={'contexts':[{'passage_id':'p','start_char':6,'end_char_exclusive':16}]}
        result=context_scores(m,self.label,self.passages)
        self.assertEqual(result['parent_passage_hit_at_5'],1)
        self.assertEqual(result['annotated_span_recall_at_5'],0)
    def test_complete_set_does_not_use_containment(self):
        scores=answer_scores(['Alpha extra'],['Alpha'])
        self.assertEqual(scores['exact_annotated_answer_set'],0)
        self.assertEqual(scores['annotated_answer_set_recall'],0)
    def test_duplicates_do_not_get_extra_credit(self):
        scores=answer_scores(['Alpha','Alpha'],['Alpha','Beta'])
        self.assertEqual(scores['annotated_answer_set_recall'],.5)
        self.assertEqual(scores['predicted_answer_count'],1)
        self.assertEqual(scores['annotated_answer_soft_recall'],.5)
    def test_overlap_rejected(self):
        with self.assertRaises(ValueError):
            context_scores({'contexts':[{'passage_id':'p','start_char':0,'end_char_exclusive':16},
                 {'passage_id':'p','start_char':10,'end_char_exclusive':21}]},self.label,self.passages)
    def test_missing_query_rejected(self):
        with self.assertRaises(ValueError):run([self.label],[],self.passages,{'methods':{}})

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ScoreTests))
    Path(__file__).with_name('scoring_tests.json').write_text(json.dumps({'tests_run':result.testsRun,
          'failures':len(result.failures),'errors':len(result.errors),'kind':'Constructed scoring checks, not benchmark evidence.'},indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
