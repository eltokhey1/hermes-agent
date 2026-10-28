import unittest
from learning_unit import evaluate
from self_improvement import propose
from knowledge_transfer import prepare_lesson

def candidate(**changes):
    x={'id':'offline-fixture','status':'TESTED_SYNTHETIC','scores':{'security':5,'privacy':5,'compatibility':4,'quality':4,'cost':5,'maintenance':4},'evidence':[]}
    x.update(changes)
    return x

class OfflineTests(unittest.TestCase):
    def test_candidate_is_not_verified(self):
        self.assertEqual(evaluate(candidate())['decision'],'PILOT_CANDIDATE_UNVERIFIED')
    def test_low_security_blocks(self):
        x=candidate();x['scores']['security']=2
        self.assertEqual(evaluate(x)['decision'],'REJECT')
    def test_low_privacy_blocks(self):
        x=candidate();x['scores']['privacy']=1
        self.assertEqual(propose(x,'Hermes','test','verify')['status'],'BLOCKED')
    def test_fake_verified_rejected(self):
        self.assertEqual(evaluate(candidate(status='VERIFIED'))['decision'],'REJECT')
    def test_independent_evidence_required(self):
        x=candidate(status='VERIFIED',evidence=[{'url':'local://fixture','sha_or_version':'abc','test_result':'pass','independent_test':False}])
        self.assertEqual(evaluate(x)['decision'],'REJECT')
    def test_boolean_score_invalid(self):
        x=candidate();x['scores']['security']=True
        with self.assertRaises(ValueError):evaluate(x)
    def test_evidence_not_list_invalid(self):
        with self.assertRaises(ValueError):evaluate(candidate(evidence='fake'))
    def test_unknown_project_invalid(self):
        with self.assertRaises(ValueError):propose(candidate(),'Unknown','test','verify')
    def test_acceptance_required(self):
        with self.assertRaises(ValueError):propose(candidate(),'Hermes','test','')
    def test_proposal_never_executes(self):
        x=propose(candidate(),'TradeDocs AI','reduce errors','10 fixtures')
        self.assertFalse(x['executed'])
        self.assertEqual(x['production'],'HOLD')
    def test_lesson_not_distributed(self):
        x=prepare_lesson(candidate(),'Radar','learn','review','lesson')
        self.assertFalse(x['distributed'])
        self.assertEqual(x['status'],'REVIEW_REQUIRED')
    def test_lesson_deterministic(self):
        args=(candidate(),'Radar','learn','review','lesson')
        self.assertEqual(prepare_lesson(*args)['content_sha256'],prepare_lesson(*args)['content_sha256'])
    def test_empty_lesson_invalid(self):
        with self.assertRaises(ValueError):prepare_lesson(candidate(),'Radar','learn','review','')
    def test_self_attested_evidence_never_promotes(self):
        x=candidate(status='VERIFIED',evidence=[{'url':'https://example.org','sha_or_version':'abc','test_result':'PASS','independent_test':True}])
        self.assertEqual(evaluate(x)['decision'],'REJECT')
        self.assertIn('independent evidence requires external attestation',evaluate(x)['blockers'])
        self.assertEqual(evaluate(x)['production'],'HOLD')

if __name__=='__main__':unittest.main()
