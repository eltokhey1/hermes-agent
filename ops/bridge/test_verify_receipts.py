import copy
import hashlib
import unittest
from datetime import datetime, timezone
import verify_receipts as v

SOURCE='def sum_range(start, end):\n    return sum(range(start,end+1))\n'
JOB={'schema':'hermes.bridge.job.v1','job_id':'job-20261025-01','operation':'python_ast_check',
     'approval':'read_only','source':SOURCE,'source_sha256':hashlib.sha256(SOURCE.encode()).hexdigest()}
ACK={'schema':'hermes.bridge.receipt.v1','job_id':'job-20261025-01','operation':'python_ast_check',
     'status':'PASS','executed':False,'production':'HOLD','isolation':'NOT_PROVEN',
     'source_sha256':JOB['source_sha256'],'completed_at_utc':datetime.now(timezone.utc).isoformat()}

class Tests(unittest.TestCase):
 def test_01_happy(self): self.assertEqual(v.verify(JOB,ACK,JOB['job_id']),[])
 def test_02_malformed(self): self.assertIn('INVALID_JSON_OBJECT',v.verify([],ACK,JOB['job_id']))
 def test_03_replay(self):
  x=copy.copy(ACK);x['job_id']='job-20261025-02'
  self.assertIn('JOB_ID_MISMATCH',v.verify(JOB,x,JOB['job_id']))
 def test_04_wrong_hash(self):
  x=copy.copy(ACK);x['source_sha256']='0'*64
  self.assertIn('SOURCE_SHA256_MISMATCH',v.verify(JOB,x,JOB['job_id']))
 def test_05_exec(self):
  x=copy.copy(ACK);x['executed']=True
  self.assertIn('EXECUTED_NOT_FALSE',v.verify(JOB,x,JOB['job_id']))
 def test_06_prod(self):
  x=copy.copy(ACK);x['production']='ON'
  self.assertIn('PRODUCTION_NOT_HOLD',v.verify(JOB,x,JOB['job_id']))
 def test_07_auth(self):
  x=copy.copy(JOB);x['approval']='auto'
  self.assertIn('APPROVAL_INVALID',v.verify(x,ACK,JOB['job_id']))
 def test_08_no_tz(self):
  x=copy.copy(ACK);x['completed_at_utc']='2026-10-25T00:00:00'
  self.assertIn('INVALID_UTC_TIMESTAMP',v.verify(JOB,x,JOB['job_id']))
 def test_09_bad_status(self):
  x=copy.copy(ACK);x['status']='FAIL'
  self.assertIn('EXPECTED_AST_PASS',v.verify(JOB,x,JOB['job_id']))
 def test_10_negative_control(self):
  code='def broken(:\n    pass\n'
  j=copy.copy(JOB);j['source']=code;j['source_sha256']=hashlib.sha256(code.encode()).hexdigest()
  a=copy.copy(ACK);a.update({'source_sha256':j['source_sha256'],'status':'SYNTAX_ERROR','error_code':'SYNTAX_ERROR'})
  self.assertEqual(v.verify(j,a,j['job_id']),[])
 def test_11_negative_false_success(self):
  code='def broken(:\n    pass\n'
  j=copy.copy(JOB);j['source']=code;j['source_sha256']=hashlib.sha256(code.encode()).hexdigest()
  a=copy.copy(ACK);a.update({'source_sha256':j['source_sha256']})
  self.assertIn('EXPECTED_SYNTAX_ERROR',v.verify(j,a,j['job_id']))
 def test_12_wrong_operation(self):
  x=copy.copy(ACK);x['operation']='shell'
  self.assertIn('OPERATION_MISMATCH',v.verify(JOB,x,JOB['job_id']))

if __name__=='__main__': unittest.main(verbosity=2)
