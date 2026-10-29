"""Regression checks: a green local verification must run real test cases."""
import tempfile
import unittest
from pathlib import Path

from local_verify import verify


class VerifyDiscoveryTests(unittest.TestCase):
    def test_no_test_files_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "No unittest test cases"):
                verify(Path(tmp))

    def test_filename_alone_is_not_a_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "test_empty.py").write_text("SAMPLE = 1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No unittest test cases"):
                verify(Path(tmp))

    def test_real_discovered_case_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "test_synthetic_guard.py").write_text(
                "import unittest\n"
                "class Synthetic(unittest.TestCase):\n"
                "    def test_true(self): self.assertTrue(True)\n",
                encoding="utf-8",
            )
            self.assertEqual(verify(Path(tmp)), 0)


if __name__ == "__main__":
    unittest.main()
