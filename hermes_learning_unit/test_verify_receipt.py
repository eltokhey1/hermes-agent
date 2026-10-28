import unittest
from verify_receipt import receipt

class ReceiptTests(unittest.TestCase):
    def test_receipt_never_claims_production(self):
        r = receipt()
        self.assertEqual(r['production'], 'HOLD')
        self.assertEqual(r['windows_native'], 'UNKNOWN')
        self.assertFalse(r['executed_external_tools'])

    def test_receipt_has_file_hashes(self):
        r = receipt()
        self.assertEqual(len(r['files_sha256']['learning_unit.py']), 64)
        self.assertGreaterEqual(r['tests_run'], 26)
