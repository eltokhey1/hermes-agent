import unittest
from learning_unit import evaluate

BASE = {'id': 'example', 'status': 'UNDER_STUDY', 'scores': dict.fromkeys(('security','privacy','compatibility','quality','cost','maintenance'), 4), 'evidence': []}
class Tests(unittest.TestCase):
    def test_no_production(self):
        self.assertEqual(evaluate(BASE)['production'], 'HOLD')
    def test_unverified(self):
        self.assertEqual(evaluate(BASE)['decision'], 'PILOT_CANDIDATE_UNVERIFIED')
    def test_security_fail_closed(self):
        r = {**BASE, 'scores': {**BASE['scores'], 'security': 2}}
        self.assertEqual(evaluate(r)['decision'], 'REJECT')
    def test_verified_needs_evidence(self):
        self.assertIn('missing independent evidence', evaluate({**BASE, 'status':'VERIFIED'})['blockers'])
    def test_invalid_score(self):
        with self.assertRaises(ValueError): evaluate({**BASE, 'scores': {**BASE['scores'], 'cost': 6}})
    def test_rejected(self):
        self.assertEqual(evaluate({**BASE, 'status':'REJECTED'})['decision'], 'REJECT')
if __name__ == '__main__': unittest.main()

class EvidenceHardeningTests(unittest.TestCase):
    def test_reject_non_string_evidence(self):
        r = {**BASE, 'status': 'VERIFIED', 'evidence': [{'url': True, 'sha_or_version': 123, 'test_result': 'PASS', 'independent_test': True}]}
        self.assertEqual(evaluate(r)['decision'], 'REJECT')
    def test_reject_unreviewed_evidence(self):
        r = {**BASE, 'status': 'VERIFIED', 'evidence': [{'url': 'https://example.org', 'sha_or_version': 'abc', 'test_result': 'PASS'}]}
        self.assertEqual(evaluate(r)['decision'], 'REJECT')
    def test_accept_structurally_complete_independent_evidence(self):
        r = {**BASE, 'status': 'VERIFIED', 'evidence': [{'url': 'https://example.org', 'sha_or_version': 'abc', 'test_result': 'PASS', 'independent_test': True}]}
        self.assertEqual(evaluate(r)['decision'], 'PILOT_CANDIDATE')
        self.assertEqual(evaluate(r)['production'], 'HOLD')
