"""Synthetic acceptance tests for offline parser evaluation, no dependencies."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from parser_challenger_gate import InputError, evaluate, main, MAX_INPUT_BYTES

SAMPLE = Path(__file__).with_name("parser_challenger_synthetic.sample.json")


class ParserGateTests(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def reject(self, mutation):
        obj = copy.deepcopy(self.sample)
        mutation(obj)
        with self.assertRaises(InputError):
            evaluate(obj)

    def test_sample_is_only_candidate_not_approval(self):
        result = evaluate(self.sample)
        self.assertEqual(result["decision"], "CANDIDATE_FOR_APPROVED_NATIVE_TEST")
        self.assertEqual(result["challenger"]["correct"], 6)
        self.assertEqual(result["baseline"]["correct"], 4)
        self.assertFalse(result["tool_promotion_authorized"])
        self.assertEqual(result["production"], "HOLD")
        self.assertEqual(result["evidence"], "TESTED_SYNTHETIC_ONLY")

    def test_tie_retains_baseline(self):
        self.sample["cases"][0]["challenger"] = self.sample["cases"][0]["baseline"].copy()
        self.sample["cases"][1]["challenger"] = self.sample["cases"][1]["baseline"].copy()
        self.assertEqual(evaluate(self.sample)["decision"], "RETAIN_BASELINE")

    def test_more_total_correct_but_critical_error_retains(self):
        self.sample["cases"][0]["challenger"]["container_count"] = "100"
        self.assertEqual(evaluate(self.sample)["decision"], "RETAIN_BASELINE")

    def test_challenger_extra_hallucinated_field_retains(self):
        self.sample["cases"][0]["challenger"]["invented_bank"] = "FAKE"
        self.assertEqual(evaluate(self.sample)["decision"], "RETAIN_BASELINE")

    def test_missing_field_count(self):
        self.sample["cases"][0]["baseline"].pop("eta")
        result = evaluate(self.sample)
        self.assertEqual(result["baseline"]["missing"], 1)
        self.assertEqual(result["baseline"]["critical_errors"], 2)

    def test_false_synthetic_refused(self):
        self.reject(lambda d: d.update(synthetic=False))

    def test_unknown_root_key_refused(self):
        self.reject(lambda d: d.update(remote_url="http://example.test"))

    def test_duplicate_cases_refused(self):
        self.reject(lambda d: d["cases"].append(copy.deepcopy(d["cases"][0])))

    def test_unknown_critical_field_refused(self):
        self.reject(lambda d: d["cases"][0]["critical"].append("not_expected"))

    def test_malformed_expected_value_refused(self):
        self.reject(lambda d: d["cases"][0]["expected"].update(amount=1e9))

    def test_secret_like_values_never_printed(self):
        self.sample["cases"][0]["expected"]["bl_number"] = "PRIVATE_SENTINEL"
        self.sample["cases"][0]["baseline"]["bl_number"] = "PRIVATE_SENTINEL"
        self.sample["cases"][0]["challenger"]["bl_number"] = "PRIVATE_SENTINEL"
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(evaluate(self.sample)))

    def test_cli_outputs_provenance_without_values(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "fixture.json"
            p.write_text(json.dumps(self.sample), encoding="utf-8")
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = main([str(p)])
            self.assertEqual(code, 0)
            result = json.loads(buffer.getvalue())
            self.assertEqual(len(result["fixture_sha256"]), 64)
            self.assertNotIn("FAKEBL001", buffer.getvalue())

    def test_cli_rejects_oversize(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "too_big.json"
            p.write_bytes(b" " * (MAX_INPUT_BYTES + 1))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(p)]), 2)

    @unittest.skipUnless(hasattr(Path, "symlink_to"), "symlinks unavailable")
    def test_cli_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder) / "source.json"
            original.write_text(json.dumps(self.sample))
            alias = Path(folder) / "alias.json"
            try:
                alias.symlink_to(original)
            except OSError:
                self.skipTest("symlink requires platform privilege")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(alias)]), 2)


if __name__ == "__main__":
    unittest.main()
