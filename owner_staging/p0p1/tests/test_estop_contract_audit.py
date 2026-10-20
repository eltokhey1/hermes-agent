import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from estop_contract_audit import git_blob_sha1, inspect_estop_source, _read_source, main

SOURCE = '''"""Global ESTOP for new work only; in-flight work is never killed."""
SENTINEL_NAME = "ESTOP"
def is_engaged():
    saw_stat_error = False
    try:
        return marker.exists()
    except OSError:
        saw_stat_error = True
    return saw_stat_error
def engage():
    path.write_text("pause")
def disengage():
    path.unlink()
def check_paused():
    return is_engaged()
'''
CLI = '''"""CLI: In-flight work keeps running."""
def cmd_pause():
    engage()
def cmd_resume():
    disengage()
'''

class StaticSafetyTests(unittest.TestCase):
    def test_baseline_contract(self):
        r = inspect_estop_source(SOURCE, CLI)
        self.assertEqual((r['status'],r['checks_passed'],r['checks_total']),('STATIC_SOURCE_REVIEW_ONLY',7,7))
    def test_new_work_only_not_full_stop(self):
        r=inspect_estop_source(SOURCE,CLI)
        self.assertIn('IN_FLIGHT_WORK_NOT_CANCELLED_BY_ESTOP',r['blocking_findings'])
        self.assertFalse(r['hard_cancel_verified'])
    def test_tool_dispatch_unverified(self):
        r=inspect_estop_source(SOURCE,CLI)
        self.assertFalse(r['tool_dispatch_verified'])
        self.assertIn('NO_TOOL_DISPATCH_ENFORCEMENT_TEST',r['blocking_findings'])
    def test_always_hold(self):
        r=inspect_estop_source(SOURCE,CLI)
        self.assertEqual((r['G0'],r['G_CODE'],r['G1'],r['production']),('NO-GO','NO-GO','NO-GO','HOLD'))
    def test_missing_sentinel_literal(self):
        r=inspect_estop_source(SOURCE.replace('SENTINEL_NAME = "ESTOP"','SENTINEL_NAME = "PAUSE"'),CLI)
        self.assertIn('MISSING_SOURCE_CONTRACT:sentinel_name_literal_estop',r['blocking_findings'])
    def test_missing_engage_write(self):
        r=inspect_estop_source(SOURCE.replace('path.write_text("pause")','pass'),CLI)
        self.assertFalse(r['checks']['engage_writes_marker'])
    def test_missing_resume_unlink(self):
        r=inspect_estop_source(SOURCE.replace('path.unlink()','pass'),CLI)
        self.assertFalse(r['checks']['resume_removes_marker'])
    def test_missing_check_paused(self):
        r=inspect_estop_source(SOURCE.replace('return is_engaged()','return False'),CLI)
        self.assertFalse(r['checks']['check_paused_queries_state'])
    def test_missing_stat_error_guard(self):
        r=inspect_estop_source(SOURCE.replace('except OSError:', 'except RuntimeError:'),CLI)
        self.assertFalse(r['checks']['stat_error_guard_observed'])
    def test_no_stat_error_return(self):
        r=inspect_estop_source(SOURCE.replace('return saw_stat_error','return False'),CLI)
        self.assertFalse(r['checks']['stat_error_guard_observed'])
    def test_no_pause_cli(self):
        r=inspect_estop_source(SOURCE,'def cmd_resume():\n    disengage()')
        self.assertFalse(r['checks']['pause_cli_engages'])
    def test_no_resume_cli(self):
        r=inspect_estop_source(SOURCE,'def cmd_pause():\n    engage()')
        self.assertFalse(r['checks']['resume_cli_disengages'])
    def test_syntax_error_fails_safe(self):
        r=inspect_estop_source('def fail(!!!',CLI)
        self.assertEqual((r['status'],r['production']),('INVALID_SOURCE','HOLD'))
    def test_doc_change_yields_unknown(self):
        r=inspect_estop_source(SOURCE.replace('new work only; in-flight work is never killed','unspecified scope'),
                               CLI.replace('In-flight work keeps running','Unknown semantics'))
        self.assertIn('IN_FLIGHT_CANCELLATION_UNVERIFIED',r['blocking_findings'])
    def test_without_cli_does_not_pass(self):
        r=inspect_estop_source(SOURCE)
        self.assertFalse(r['checks']['pause_cli_engages'])
        self.assertFalse(r['checks']['resume_cli_disengages'])

class SourceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        (self.root/'estop.py').write_text(SOURCE,encoding='utf8')
        (self.root/'pause.py').write_text(CLI,encoding='utf8')
    def test_git_blob_digest(self):
        content=b'hello\n';digest=hashlib.sha1(b'blob 6\0'+content).hexdigest()
        self.assertEqual(git_blob_sha1(content),digest)
    def test_read_with_pin(self):
        p=self.root/'estop.py';sha=git_blob_sha1(p.read_bytes())
        src,r=_read_source(p,sha);self.assertEqual(src,SOURCE);self.assertTrue(r['pinned'])
    def test_wrong_pin_refused(self):
        with self.assertRaisesRegex(ValueError,'GIT_BLOB_SHA_MISMATCH'):
            _read_source(self.root/'estop.py','f'*40)
    def test_bad_pin_refused(self):
        with self.assertRaisesRegex(ValueError,'GIT_BLOB_SHA_MISMATCH'):
            _read_source(self.root/'estop.py','invalid')
    def test_zero_size_refused(self):
        p=self.root/'empty.py';p.touch()
        with self.assertRaisesRegex(ValueError,'SOURCE_SIZE_OUT_OF_BOUNDS'):_read_source(p,None)
    def test_missing_file_refused(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_NOT_REGULAR_FILE'):_read_source(self.root/'missing',None)
    def test_symlink_refused(self):
        p=self.root/'link.py'
        try:p.symlink_to(self.root/'estop.py')
        except OSError:self.skipTest('symlink unavailable')
        with self.assertRaisesRegex(ValueError,'LINKED_SOURCE_REFUSED'):_read_source(p,None)
    def test_large_file_refused(self):
        p=self.root/'large.py';p.write_bytes(b'x'*(512*1024+1))
        with self.assertRaisesRegex(ValueError,'SOURCE_SIZE_OUT_OF_BOUNDS'):_read_source(p,None)
    def test_cli_complete_with_pin(self):
        paths=[self.root/'estop.py',self.root/'pause.py']
        pins=[git_blob_sha1(p.read_bytes()) for p in paths]
        out=io.StringIO()
        with contextlib.redirect_stdout(out):rc=main(['--estop-source',str(paths[0]),'--pause-cli',str(paths[1]),'--estop-git-blob-sha1',pins[0],'--cli-git-blob-sha1',pins[1]])
        r=json.loads(out.getvalue())
        self.assertEqual(rc,0);self.assertEqual(r['production'],'HOLD')
        self.assertNotIn('SOURCE_PIN_UNVERIFIED',r['blocking_findings'])
    def test_cli_unpinned_not_certified(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):rc=main(['--estop-source',str(self.root/'estop.py'),'--pause-cli',str(self.root/'pause.py')])
        r=json.loads(out.getvalue());self.assertEqual(rc,0)
        self.assertIn('SOURCE_PIN_UNVERIFIED',r['blocking_findings'])
    def test_cli_wrong_pin_stops(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):rc=main(['--estop-source',str(self.root/'estop.py'),'--pause-cli',str(self.root/'pause.py'),'--estop-git-blob-sha1','0'*40])
        self.assertEqual(rc,2);self.assertEqual(json.loads(out.getvalue())['status'],'SAFE_STOP')

if __name__=='__main__':unittest.main()
