"""Offline verification receipt; no network, no writes, no external commands."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SOURCES = ('learning_unit.py', 'self_improvement.py', 'knowledge_transfer.py',
           'test_learning_unit.py', 'test_self_improvement.py',
           'test_knowledge_transfer.py', 'test_adversarial_gates.py',
           'verify_offline.py', 'verify_receipt.py')


def receipt():
    suite = unittest.TestSuite(unittest.defaultTestLoader.discover(str(ROOT), pattern=name) for name in ('test_learning_unit.py', 'test_self_improvement.py', 'test_knowledge_transfer.py', 'test_adversarial_gates.py'))
    result = unittest.TestResult()
    suite.run(result)
    return {
        'schema': 'hermes.learning.offline_receipt.v1',
        'status': 'TESTED_SYNTHETIC' if result.wasSuccessful() and result.testsRun >= 26 else 'FAILED',
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'files_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES},
        'production': 'HOLD',
        'gates': 'G0/G-CODE/G1=NO-GO',
        'windows_native': 'UNKNOWN',
        'github_ci': 'UNKNOWN',
        'executed_external_tools': False,
    }


if __name__ == '__main__':
    result = receipt()
    print(json.dumps(result, sort_keys=True, indent=2))
    raise SystemExit(0 if result['status'] == 'TESTED_SYNTHETIC' else 1)
