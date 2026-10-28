"""Run only the offline learning unit tests; no external tools or network calls."""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
suite = unittest.defaultTestLoader.discover(str(ROOT), pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
print(f'OFFLINE_TESTS={result.testsRun} FAILURES={len(result.failures)} ERRORS={len(result.errors)}')
print('PRODUCTION=HOLD G0/G-CODE/G1=NO-GO')
sys.exit(0 if result.wasSuccessful() and result.testsRun >= 26 else 1)
