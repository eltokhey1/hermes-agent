import unittest
from knowledge_transfer import prepare_lesson
BASE = {'id':'sample','status':'UNDER_STUDY','scores':dict.fromkeys(('security','privacy','compatibility','quality','cost','maintenance'),4),'evidence':[]}
class KnowledgeTransferTests(unittest.TestCase):
    def test_proposal_not_published(self):
        x=prepare_lesson(BASE,'Hermes','improve retrieval','offline evaluation','Use FTS5 first')
        self.assertEqual(x['status'],'REVIEW_REQUIRED')
        self.assertFalse(x['executed'])
        self.assertFalse(x['distributed'])
        self.assertEqual(len(x['content_sha256']),64)
    def test_deterministic_receipt(self):
        a=prepare_lesson(BASE,'Hermes','improve retrieval','offline evaluation','Use FTS5 first')
        b=prepare_lesson(BASE,'Hermes','improve retrieval','offline evaluation','Use FTS5 first')
        self.assertEqual(a,b)
    def test_blocked_security(self):
        bad={**BASE,'scores':{**BASE['scores'],'security':0}}
        self.assertEqual(prepare_lesson(bad,'Hermes','h','t','lesson')['status'],'BLOCKED')
    def test_empty_lesson(self):
        with self.assertRaises(ValueError): prepare_lesson(BASE,'Hermes','h','t',' ')
    def test_unknown_project(self):
        with self.assertRaises(ValueError): prepare_lesson(BASE,'other','h','t','lesson')
