import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_contract_audit import audit_source_tree, _container_defaults, main
import ast

ESTOP = '''"""ESTOP pause for NEW work only; in-flight jobs continue."""
def is_engaged(): return False
def engage(): pass
def disengage(): pass
def check_paused(): pass
'''
DOCKER = '''_BASE_SECURITY_ARGS = ["--cap-drop", "ALL", "--cap-add", "DAC_OVERRIDE"]
_NO_NEW_PRIVILEGES_ARGS = ["--security-opt", "no-new-privileges"]
'''
BACKEND = '''_CONTAINER_KEYS = (("docker_network", True), ("container_persistent", True), ("docker_persist_across_processes", True), ("docker_mount_cwd_to_workspace", False))
'''

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        self.write('agent/estop.py', ESTOP)
        self.write('tools/environments/docker.py', DOCKER)
        self.write('tools/terminal_tool_backends.py', BACKEND)

    def write(self, relative, text):
        path=self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def audit(self): return audit_source_tree(self.root)

    def test_three_sources_parsed(self):
        self.assertTrue(all(x['status']=='PARSED' for x in self.audit()['sources'].values()))
    def test_source_hashes_appear(self):
        self.assertTrue(all(len(x['sha256'])==64 for x in self.audit()['sources'].values()))
    def test_pins_no_paths_or_source_content(self):
        s=json.dumps(self.audit())
        self.assertNotIn(str(self.root), s)
        self.assertNotIn('_BASE_SECURITY_ARGS =',s)
    def test_new_work_only_flagged(self):
        self.assertIn('ESTOP_STATED_NEW_WORK_ONLY_NOT_KILL_SWITCH',self.audit()['risk_flags'])
    def test_entrypoints_identified(self):
        self.assertTrue(self.audit()['review_signals']['estop_entrypoints_declared'])
    def test_missing_entrypoint_flagged(self):
        self.write('agent/estop.py','"""Pause NEW work only; in-flight continues."""\ndef engage(): pass\n')
        self.assertIn('ESTOP_ENTRYPOINTS_MISSING',self.audit()['risk_flags'])
    def test_no_documentation_unknown_not_approved(self):
        self.write('agent/estop.py','def is_engaged(): pass\ndef engage(): pass\ndef disengage(): pass\ndef check_paused(): pass\n')
        self.assertIn('ESTOP_SCOPE_UNRESOLVED',self.audit()['risk_flags'])
    def test_network_default_true_flag(self):
        self.assertIn('DOCKER_NETWORK_DEFAULT_NOT_PROVEN_OFF',self.audit()['risk_flags'])
    def test_persistence_default_true_flag(self):
        self.assertIn('DOCKER_PERSISTENCE_DEFAULT_NOT_PROVEN_OFF',self.audit()['risk_flags'])
    def test_cross_process_persistence_flag(self):
        self.assertIn('CROSS_PROCESS_REUSE_DEFAULT_NOT_PROVEN_OFF',self.audit()['risk_flags'])
    def test_capability_additions_flag(self):
        self.assertIn('DOCKER_BASE_CAPABILITY_ADDITIONS_REQUIRE_REVIEW',self.audit()['risk_flags'])
    def test_no_new_privs_detected_but_not_attested(self):
        self.assertTrue(self.audit()['review_signals']['docker_no_new_privileges_flag_declared'])
        self.assertIn('WINDOWS_RUNTIME_UNVERIFIED',self.audit()['risk_flags'])
    def test_missing_no_new_privs_source(self):
        self.write('tools/environments/docker.py','_BASE_SECURITY_ARGS = []\n')
        self.assertIn('NO_NEW_PRIVILEGES_SOURCE_UNVERIFIED',self.audit()['risk_flags'])
    def test_off_defaults_not_enough_to_approve(self):
        self.write('tools/terminal_tool_backends.py',BACKEND.replace('True','False'))
        r=self.audit()
        self.assertEqual(r['review_signals']['docker_default_network'],False)
        self.assertEqual(r['production'],'HOLD')
    def test_missing_source(self):
        (self.root/'agent/estop.py').unlink()
        r=self.audit()
        self.assertEqual(r['sources']['estop']['status'],'MISSING')
        self.assertIn('ESTOP_SOURCE_UNAVAILABLE',r['risk_flags'])
    def test_invalid_syntax(self):
        self.write('tools/environments/docker.py','def oops(:')
        self.assertEqual(self.audit()['sources']['docker']['status'],'UNPARSEABLE')
    def test_encoding_error(self):
        (self.root/'agent/estop.py').write_bytes(b'\xff\xfe')
        self.assertEqual(self.audit()['sources']['estop']['status'],'UNPARSEABLE')
    def test_oversize_refused(self):
        (self.root/'agent/estop.py').write_bytes(b' '*(2*1024*1024+1))
        self.assertEqual(self.audit()['sources']['estop']['status'],'OVERSIZE_REFUSED')
    def test_symlink_refused(self):
        dest=self.root/'external.py';dest.write_text(ESTOP)
        (self.root/'agent/estop.py').unlink()
        try: (self.root/'agent/estop.py').symlink_to(dest)
        except (OSError,NotImplementedError): self.skipTest('No symlink capability')
        self.assertEqual(self.audit()['sources']['estop']['status'],'LINK_REFUSED')
    def test_parent_symlink_refused(self):
        lib=self.root/'other';lib.mkdir();(lib/'estop.py').write_text(ESTOP)
        (self.root/'agent/estop.py').unlink();(self.root/'agent').rmdir()
        try: (self.root/'agent').symlink_to(lib, target_is_directory=True)
        except (OSError,NotImplementedError): self.skipTest('No symlink capability')
        self.assertEqual(self.audit()['sources']['estop']['status'],'LINK_REFUSED')
    def test_variable_assignment_refused(self):
        self.write('tools/terminal_tool_backends.py','_CONTAINER_KEYS = some_function()\n')
        self.assertEqual(self.audit()['review_signals']['docker_default_network'],'UNKNOWN')
    def test_duplicate_key_defaults_unknown(self):
        self.write('tools/terminal_tool_backends.py','_CONTAINER_KEYS = (("docker_network", False), ("docker_network", True))\n')
        self.assertEqual(self.audit()['review_signals']['docker_default_network'],'UNKNOWN')
    def test_malformed_default_tuple(self):
        self.assertEqual(_container_defaults(ast.parse('_CONTAINER_KEYS = (("docker_network",),)')), {})
    def test_cli_structured_nonacceptance(self):
        with redirect_stdout(StringIO()) as output:
            code=main(['--source-root',str(self.root)])
        self.assertEqual(code,0)
        report=json.loads(output.getvalue())
        self.assertEqual(report['G0'],'NO-GO')
        self.assertEqual(report['assessment'],'HOLD')
        self.assertNotIn(str(self.root),output.getvalue())

if __name__=='__main__': unittest.main()
