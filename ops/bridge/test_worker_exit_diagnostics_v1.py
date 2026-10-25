"""Offline tests for worker exit diagnostics; no GitHub or Windows access."""
import unittest
from worker_exit_diagnostics_v1 import classify_worker_exit


class WorkerExitDiagnosticsTests(unittest.TestCase):
    def test_success(self):
        self.assertEqual(classify_worker_exit(0), "WORKER_OK")

    def test_nonzero(self):
        self.assertEqual(classify_worker_exit(1), "WORKER_EXIT_1")

    def test_timeout_code(self):
        self.assertEqual(classify_worker_exit(124), "WORKER_EXIT_124")

    def test_negative(self):
        self.assertEqual(classify_worker_exit(-9), "WORKER_SIGNAL")

    def test_out_of_range(self):
        self.assertEqual(classify_worker_exit(999), "WORKER_EXIT_OUT_OF_RANGE")

    def test_rejects_text(self):
        with self.assertRaises(TypeError):
            classify_worker_exit("gho_secret")

    def test_rejects_bool(self):
        with self.assertRaises(TypeError):
            classify_worker_exit(True)


if __name__ == "__main__":
    unittest.main()
