"""Independent synthetic acceptance-contract checks. No Hermes runtime imports."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from acceptance_gate import inspect_report

def sample():
    return {'case_id':'CASE001','decision':'READY_FOR_HUMAN_REVIEW_ONLY',
            'human_approval_required':True,'automated_release_authorized':False,
            'flags':[],'document_review':{'findings':[]},'lc_check':{'missing':[]},
            'eta_evidence':[],'scope':'synthetic fields only'}

class AcceptanceContract(unittest.TestCase):
    def test_valid_review_only(self):
        r=inspect_report(sample())
        self.assertTrue(r['contract_valid'])
        self.assertFalse(r['release_authorized'])
    def test_cannot_approve_release(self):
        r=sample();r['automated_release_authorized']=True
        self.assertFalse(inspect_report(r)['contract_valid'])
    def test_cannot_disable_human_review(self):
        r=sample();r['human_approval_required']=False
        self.assertFalse(inspect_report(r)['contract_valid'])
    def test_flags_require_blocked_decision(self):
        r=sample();r['flags']=['DOCUMENT_FINDINGS']
        self.assertFalse(inspect_report(r)['contract_valid'])
    def test_blocked_with_evidence(self):
        r=sample();r['flags']=['LC_DOCUMENT_MISSING'];r['decision']='BLOCK_FOR_REVIEW'
        self.assertTrue(inspect_report(r)['contract_valid'])
    def test_hidden_eta_conflict(self):
        r=sample();r['eta_evidence']=[{'status':'CONFLICT_REQUIRES_REVIEW'}]
        self.assertFalse(inspect_report(r)['contract_valid'])
    def test_missing_required_field(self):
        r=sample();del r['lc_check']
        self.assertFalse(inspect_report(r)['contract_valid'])
    def test_malicious_extra_flag(self):
        r=sample();r['allow_payment']=True
        self.assertFalse(inspect_report(r)['contract_valid'])
    def test_unhashable_decision(self):
        r=sample();r['decision']=[]
        self.assertFalse(inspect_report(r)['contract_valid'])
if __name__=='__main__':unittest.main()
