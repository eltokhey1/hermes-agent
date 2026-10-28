import unittest
from self_improvement import propose

BASE = {'id':'demo','status':'UNDER_STUDY','scores':dict.fromkeys(('security','privacy','compatibility','quality','cost','maintenance'),4),'evidence':[]}
class TestSelfImprovement(unittest.TestCase):
    def test_proposal_is_not_execution(self):
        r=propose(BASE,'Hermes','reduce cost','offline benchmark')
        self.assertEqual(r['status'],'PROPOSED_ONLY')
        self.assertIs(r['executed'],False)
        self.assertEqual(r['production'],'HOLD')
    def test_blocked_low_security(self):
        r={**BASE,'scores':{**BASE['scores'],'security':1}}
        self.assertEqual(propose(r,'Hermes','change','test')['status'],'BLOCKED')
    def test_reject_unknown_project(self):
        with self.assertRaises(ValueError): propose(BASE,'Unknown','change','test')
    def test_require_acceptance(self):
        with self.assertRaises(ValueError): propose(BASE,'Hermes','change','')
