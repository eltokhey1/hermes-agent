import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime_safety_audit import assess_config, audit_hermes_home, verify_backup, main


class ConfigSafetyTests(unittest.TestCase):
    def test_local_backend_refused(self):
        r=assess_config('terminal:\n  backend: local\n')
        self.assertEqual(r['backend'],'local')
        self.assertIn('BACKEND_NOT_DOCKER',r['risk_flags'])
        self.assertEqual(r['assessment'],'HOLD')

    def test_missing_config_holds(self):
        r=assess_config('name: hermes\n')
        self.assertEqual(r['terminal_section'],'MISSING')
        self.assertEqual(r['backend'],'UNKNOWN')

    def test_docker_default_network_marked_risky(self):
        r=assess_config('terminal:\n  backend: docker\n')
        self.assertEqual(r['docker_network'],'DEFAULT_TRUE_PER_REVIEWED_SOURCE')
        self.assertIn('NETWORK_NOT_PROVEN_DISABLED',r['risk_flags'])

    def test_explicit_network_false(self):
        r=assess_config('terminal:\n  backend: "docker"\n  docker_network: false\n')
        self.assertEqual(r['docker_network'],'FALSE')
        self.assertNotIn('NETWORK_NOT_PROVEN_DISABLED',r['risk_flags'])
        self.assertEqual(r['assessment'],'HOLD')

    def test_quoted_inline_comments(self):
        r=assess_config('terminal: # ok\n  backend: "docker"\n  docker_network: false # comment\n')
        self.assertEqual(r['backend'],'docker')
        self.assertEqual(r['docker_network'],'FALSE')

    def test_unsafe_mount_flags_without_leaking_secrets(self):
        secret='C:/USER-PRIVATE/supersecret:/root/.ssh'
        r=assess_config('terminal:\n  backend: docker\n  docker_volumes:\n    - '+secret+'\n')
        self.assertIn('docker_volumes',r['sensitive_keys_present'])
        self.assertNotIn(secret,json.dumps(r))
        self.assertIn('DOCKER_MOUNT_ENV_OR_EXTRA_ARGS_NEED_REVIEW',r['risk_flags'])

    def test_forwarded_secret_value_not_reported(self):
        val='DO_NOT_EXPOSE_TOKEN'
        r=assess_config('terminal:\n  backend: docker\n  docker_forward_env: ['+val+']\n')
        self.assertNotIn(val,json.dumps(r))

    def test_docker_host_cwd_mount_risk(self):
        r=assess_config('terminal:\n  backend: docker\n  docker_mount_cwd_to_workspace: true\n')
        self.assertIn('HOST_CWD_MOUNT_POSSIBLE',r['risk_flags'])

    def test_docker_persistence_default_risk(self):
        r=assess_config('terminal:\n  backend: docker\n  docker_network: false\n')
        self.assertIn('CONTAINER_OR_SESSION_PERSISTENCE_NOT_DISABLED',r['risk_flags'])

    def test_docker_persistence_both_false(self):
        r=assess_config('terminal:\n  backend: docker\n  docker_network: false\n  container_persistent: false\n  docker_persist_across_processes: false\n')
        self.assertNotIn('CONTAINER_OR_SESSION_PERSISTENCE_NOT_DISABLED',r['risk_flags'])
        self.assertIn('LIVE_RUNTIME_AND_TOOL_DISPATCH_UNVERIFIED',r['risk_flags'])

    def test_duplicate_terminal_keys(self):
        r=assess_config('terminal:\n  backend: docker\n  backend: local\n')
        self.assertIn('DUPLICATE_TERMINAL_KEYS',r['risk_flags'])

    def test_duplicate_terminal_sections(self):
        r=assess_config('terminal:\n  backend: docker\nother: true\nterminal:\n  backend: local\n')
        self.assertEqual(r['terminal_section'],'AMBIGUOUS')

    def test_yaml_alias_unknown(self):
        r=assess_config('terminal:\n  backend: *arbitrary\n')
        self.assertEqual(r['backend'],'UNKNOWN')

    def test_nested_key_does_not_override_direct(self):
        r=assess_config('terminal:\n  backend: docker\n  nested:\n    backend: local\n  docker_network: false\n')
        self.assertEqual(r['backend'],'docker')

    def test_irrelevant_value_not_disclosed(self):
        secret='sk-access-token-not-for-output'
        r=assess_config('terminal:\n  backend: docker\n  future_key: '+secret+'\n')
        self.assertNotIn(secret,json.dumps(r))

    def test_no_crash_on_huge_config(self):
        r=assess_config('terminal:\n'+'x'*1048600)
        self.assertEqual(r['terminal_section'],'TOO_LARGE')

    def test_snap_compat_risk(self):
        r=assess_config('terminal:\n  backend: docker\n  docker_snap_compat: true\n')
        self.assertIn('DOCKER_SNAP_COMPAT_WEAKENS_NNP',r['risk_flags'])


class HostReadOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def test_missing_config_does_not_claim_acceptance(self):
        r=audit_hermes_home(self.root,env={})
        self.assertEqual(r['config'],'MISSING_OR_INACCESSIBLE')
        self.assertEqual(r['production'],'HOLD')
        self.assertFalse(r['effective_backend_verified'])
        self.assertFalse(r['estop_dispatch_verified'])

    def test_present_estop_reports_without_modifying(self):
        (self.root/'ESTOP').write_text('not a real action')
        r=audit_hermes_home(self.root,env={})
        self.assertEqual(r['estop_marker_in_active_home'],'PRESENT')
        self.assertEqual((self.root/'ESTOP').read_text(),'not a real action')
        self.assertFalse(r['estop_cancels_in_flight_verified'])

    def test_env_names_not_values(self):
        secret='supersecret-123'
        r=audit_hermes_home(self.root,env={'TERMINAL_ENV':secret})
        self.assertIn('TERMINAL_ENV',r['environment_override_names'])
        self.assertNotIn(secret,json.dumps(r))
        self.assertIn('PROCESS_OVERRIDE_PRESENT_NOT_RESOLVED',r['terminal']['risk_flags'])

    def test_config_content_not_leaked(self):
        (self.root/'config.yaml').write_text('terminal:\n  backend: local\nprivate: SECRET_KEY_1\n')
        r=audit_hermes_home(self.root,env={})
        self.assertNotIn('SECRET_KEY_1',json.dumps(r))

    def test_linked_config_refused(self):
        outside=self.root/'secret';outside.write_text('secret-token')
        try:(self.root/'config.yaml').symlink_to(outside)
        except (OSError,NotImplementedError):self.skipTest('symlink not supported')
        r=audit_hermes_home(self.root,env={})
        self.assertEqual(r['config'],'LINK_OR_UNVERIFIED')

    def test_backup_sha_ok(self):
        backup=self.root/'dummy.gpg';backup.write_bytes(b'fake encrypted bytes')
        h=hashlib.sha256(backup.read_bytes()).hexdigest()
        self.assertEqual(verify_backup(backup,h)['result'],'SHA256_MATCH')
        self.assertEqual(verify_backup(backup,'0'*64)['result'],'SHA256_MISMATCH')

    def test_backup_no_raw_path(self):
        secretname=self.root/'sensitive-name.gpg'
        self.assertNotIn('sensitive-name',json.dumps(verify_backup(secretname,'0'*64)))

    def test_bad_expected_hash(self):
        self.assertEqual(verify_backup(self.root/'notthere','abc')['result'],'INVALID_EXPECTED_HASH')

    def test_main_does_not_mutate(self):
        (self.root/'config.yaml').write_text('terminal:\n  backend: local\n')
        old=(self.root/'config.yaml').read_bytes()
        captured=StringIO()
        with redirect_stdout(captured):
            code=main(['--hermes-home',str(self.root)])
        payload=json.loads(captured.getvalue())
        self.assertEqual(code,0)
        self.assertEqual(payload['production'],'HOLD')
        self.assertEqual(old,(self.root/'config.yaml').read_bytes())

if __name__=='__main__': unittest.main()
