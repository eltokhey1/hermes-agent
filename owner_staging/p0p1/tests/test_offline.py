from __future__ import annotations
import json, shutil, tempfile, unittest, zipfile, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mutation_gate import classify_test_process,evaluate
from local_stage import stage_archive,hash_file,host_snapshot
class ClassifierTests(unittest.TestCase):
    def test_kill_assertion(self):
        self.assertEqual(classify_test_process(1,'FAIL: test_x\nAssertionError: 1 != 2\nRan 3 tests in 0.1s\nFAILED (failures=1)',3)['classification'],'KILLED_ASSERTION')
    def test_import_error_never_killed(self):
        self.assertEqual(classify_test_process(1,'FAIL: test_x\nModuleNotFoundError: aaa\nRan 3 tests in 0.1s\n',3)['classification'],'INVALID_IMPORT')
    def test_failed_test_marker(self):
        self.assertEqual(classify_test_process(1,'_FailedTest\nRan 1 test in 0.1s',1)['classification'],'INVALID_IMPORT')
    def test_runtime_never_killed(self):
        self.assertEqual(classify_test_process(1,'AssertionError\nsqlite3.IntegrityError: wrong\nRan 3 tests in 0.1s',3)['classification'],'INVALID_RUNTIME')
    def test_no_discovery(self):self.assertEqual(classify_test_process(1,'oops',3)['classification'],'INVALID_DISCOVERY')
    def test_mismatched_discovery(self):self.assertEqual(classify_test_process(1,'AssertionError\nRan 2 tests in 0.1s',3)['classification'],'INVALID_DISCOVERY')
    def test_timeout(self):self.assertEqual(classify_test_process(124,'',3,True)['classification'],'INVALID_TIMEOUT')
    def test_survived(self):self.assertEqual(classify_test_process(0,'Ran 3 tests in 0.1s\nOK',3)['classification'],'SURVIVED')
    def test_zero_tests(self):self.assertEqual(classify_test_process(0,'Ran 0 tests in 0.1s\nOK',None)['classification'],'INVALID_DISCOVERY')
    def test_error_case(self):self.assertEqual(classify_test_process(1,'ERROR: test_x\nAssertionError\nRan 3 tests in 0.1s',3)['classification'],'INVALID_RUNTIME')

class StrictRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'tests').mkdir();(self.root/'lib').mkdir()
        (self.root/'lib'/'logic.py').write_text('def truth():\n    return True\n')
        (self.root/'tests'/'test_logic.py').write_text('import sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path.cwd()/"lib"))\nfrom logic import truth\nimport unittest\nclass T(unittest.TestCase):\n def test_truth(self):self.assertTrue(truth())\n')
    def test_detects_mutant(self):
        r=evaluate(self.root,['tests','lib'],[{'path':'lib/logic.py','old':'return True','new':'return False'}]);self.assertEqual((r['baseline_tests'],r['killed_assertion'],r['invalid']),(1,1,0))
        self.assertIn('return True',(self.root/'lib'/'logic.py').read_text())
    def test_survival(self):
        r=evaluate(self.root,['tests','lib'],[{'path':'lib/logic.py','old':'def truth():','new':'def truth():  # harmless'}]);self.assertEqual(r['survived'],1)
    def test_missing_dep(self):self.assertEqual(evaluate(self.root,['tests','missing'],[])['status'],'INVALID_BASELINE')
    def test_bad_path(self):
        r=evaluate(self.root,['tests','lib'],[{'path':'../lib/logic.py','old':'True','new':'False'}]);self.assertEqual(r['invalid'],1)
    def test_import_error_invalid(self):
        r=evaluate(self.root,['tests','lib'],[{'path':'lib/logic.py','old':'return True','new':'import nonexistent_library\n    return True'}]);self.assertEqual(r['mutations'][0]['classification'],'INVALID_IMPORT')
    def test_discovery_break_invalid(self):
        r=evaluate(self.root,['tests','lib'],[{'path':'tests/test_logic.py','old':'def test_truth(self):','new':'def ignore_truth(self):'}]);self.assertEqual(r['mutations'][0]['classification'],'INVALID_DISCOVERY')
    def test_mutation_missing_token(self):
        r=evaluate(self.root,['tests','lib'],[{'path':'lib/logic.py','old':'doesnotexist','new':'boom'}]);self.assertEqual(r['mutations'][0]['classification'],'INVALID_SETUP')

class StageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def make_zip(self,name='a.txt',data='hello'):
        p=self.root/'source.zip'
        with zipfile.ZipFile(p,'w') as z:z.writestr(name,data)
        return p
    def test_correct_hash_stages(self):
        z=self.make_zip();r=stage_archive(z,hash_file(z),self.root/'dst');self.assertEqual(r['files'],1);self.assertEqual((self.root/'dst/a.txt').read_text(),'hello')
    def test_rejects_wrong_hash(self):
        z=self.make_zip();self.assertRaises(ValueError,stage_archive,z,'0'*64,self.root/'dst')
    def test_blocks_traversal(self):
        z=self.make_zip('../secret');self.assertRaises(ValueError,stage_archive,z,hash_file(z),self.root/'dst')
    def test_blocks_absolute(self):
        z=self.make_zip('/abs');self.assertRaises(ValueError,stage_archive,z,hash_file(z),self.root/'dst')
    def test_blocks_case_collision(self):
        z=self.root/'source.zip'
        with zipfile.ZipFile(z,'w') as f:f.writestr('A.txt','a');f.writestr('a.txt','b')
        self.assertRaises(ValueError,stage_archive,z,hash_file(z),self.root/'dst')
    def test_no_overwrite(self):
        z=self.make_zip();(self.root/'dst').mkdir();self.assertRaises(FileExistsError,stage_archive,z,hash_file(z),self.root/'dst')
    def test_reserved_win(self):
        z=self.make_zip('CON.txt');self.assertRaises(ValueError,stage_archive,z,hash_file(z),self.root/'dst')
    def test_host_snapshot_not_verified(self):
        self.assertFalse(host_snapshot(self.root)['host_verified'])

if __name__=='__main__':unittest.main()

class NegativeSecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def zip_name(self, name):
        z=self.root/'bad.zip'
        with zipfile.ZipFile(z,'w') as f:f.writestr(name,'content')
        return z

    def test_refuses_receipt_spoofing(self):
        z=self.zip_name('STAGING_RECEIPT.json')
        self.assertRaises(ValueError,stage_archive,z,hash_file(z),self.root/'out')

    def test_refuses_noncanonical_name(self):
        for candidate in ('./x.txt','x//y','x/../y'):
            z=self.zip_name(candidate)
            self.assertRaises(ValueError,stage_archive,z,hash_file(z),self.root/'out')

    def test_refuses_windows_parent_case_collision(self):
        z=self.root/'bad.zip'
        with zipfile.ZipFile(z,'w') as f:
            f.writestr('Ab/x.txt','a');f.writestr('aB/y.txt','b')
        self.assertRaises(ValueError,stage_archive,z,hash_file(z),self.root/'out')

    def test_refuses_nested_dependency_symlink(self):
        (self.root/'tests').mkdir();(self.root/'lib').mkdir()
        (self.root/'tests'/'test_empty.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_a(self): self.assertTrue(True)\n')
        (self.root/'secret').write_text('do-not-copy')
        try: (self.root/'lib'/'link').symlink_to(self.root/'secret')
        except (OSError,NotImplementedError): self.skipTest('symlinks unavailable')
        result=evaluate(self.root,['tests','lib'],[])
        self.assertEqual(result['status'],'INVALID_BASELINE')

    def test_refuses_runtime_error_mixed_with_assertion(self):
        result=classify_test_process(1,'FAIL: test_x\nAssertionError: boom\nERROR: test_y\nRuntimeError: broken\nRan 2 tests in 0.1s\nFAILED (failures=1, errors=1)',2)
        self.assertEqual(result['classification'],'INVALID_RUNTIME')

    def test_refuses_missing_failed_summary(self):
        result=classify_test_process(1,'FAIL: test_x\nAssertionError: boom\nRan 2 tests in 0.1s\n',2)
        self.assertEqual(result['classification'],'INVALID_RUNTIME')

    def test_rejects_duplicate_required_paths(self):
        (self.root/'tests').mkdir()
        self.assertRaises(ValueError,evaluate,self.root,['tests','tests'],[])

    def test_refuses_unchanged_mutation(self):
        (self.root/'tests').mkdir()
        (self.root/'tests'/'test_a.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_a(self):self.assertTrue(True)\n')
        r=evaluate(self.root,['tests'],[{'path':'tests/test_a.py','old':'True','new':'True'}])
        self.assertEqual(r['invalid'],1)

    def test_sha_must_be_external_and_hex(self):
        z=self.zip_name('sample.txt')
        self.assertRaises(ValueError,stage_archive,z,'auto',self.root/'out')

