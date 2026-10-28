"""Adversarial checks for fail-closed learning evaluation (stdlib only)."""
import unittest
from learning_unit import evaluate
from self_improvement import propose
from knowledge_transfer import prepare_lesson

SCORES = dict.fromkeys(('security', 'privacy', 'compatibility', 'quality', 'cost', 'maintenance'), 4)
BASE = {'id': 'adversarial', 'status': 'VERIFIED', 'scores': SCORES, 'evidence': []}

class AdversarialGateTests(unittest.TestCase):
    def test_fake_verified_without_evidence_rejected(self):
        self.assertEqual(evaluate(BASE)['decision'], 'REJECT')

    def test_independence_false_rejected(self):
        e = {'url':'https://example.invalid','sha_or_version':'sha','test_result':'PASS','independent_test':False}
        self.assertEqual(evaluate({**BASE,'evidence':[e]})['decision'], 'REJECT')

    def test_evidence_string_instead_of_list_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({**BASE, 'evidence': 'PASS'})

    def test_boolean_score_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({**BASE, 'scores': {**SCORES, 'quality': True}})

    def test_low_privacy_blocks_proposal(self):
        x = {**BASE, 'scores': {**SCORES, 'privacy': 0}}
        self.assertEqual(propose(x,'Hermes','better retrieval','offline tests')['status'], 'BLOCKED')

    def test_low_privacy_blocks_knowledge_transfer(self):
        x = {**BASE, 'scores': {**SCORES, 'privacy': 0}}
        self.assertEqual(prepare_lesson(x,'Hermes','improve','offline test','lesson')['status'], 'BLOCKED')

    def test_proposal_never_executes(self):
        x = {**BASE, 'status':'UNDER_STUDY'}
        self.assertIs(propose(x,'Hermes','improve','offline test')['executed'], False)

    def test_lesson_never_distributes(self):
        x = {**BASE, 'status':'UNDER_STUDY'}
        result = prepare_lesson(x,'Hermes','improve','offline test','lesson')
        self.assertIs(result['distributed'], False)
        self.assertEqual(result['status'], 'REVIEW_REQUIRED')

if __name__ == '__main__':
    unittest.main()
