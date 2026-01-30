from django.test import TestCase
from interview_engine.utils import calculate_final_score, check_for_cheating

class ScoringTestCase(TestCase):
    def test_base_score(self):
        scores = {
            "technical_depth": 10,
            "relevance": 10,
            "clarity": 10,
            "communication": 10
        }
        # (0.4*10 + 0.3*10 + 0.2*10 + 0.1*10) = 4+3+2+1 = 10
        self.assertEqual(calculate_final_score(scores, 0, False), 10.0)

    def test_penalties(self):
        scores = {"technical_depth": 10, "relevance": 10, "clarity": 10, "communication": 10}
        # 1 tab switch = 20% reduction -> 8.0
        self.assertEqual(calculate_final_score(scores, 1, False), 8.0)
        # 5 tab switches = 100% reduction -> 0.0
        self.assertEqual(calculate_final_score(scores, 5, False), 0.0)
        # Cheating flagged = 50% reduction -> 5.0
        self.assertEqual(calculate_final_score(scores, 0, True), 5.0)

    def test_cheating_detection(self):
        self.assertTrue(check_for_cheating("As an AI language model, I can say...")[0])
        self.assertFalse(check_for_cheating("I have extensive experience with React and Node.js.")[0])
