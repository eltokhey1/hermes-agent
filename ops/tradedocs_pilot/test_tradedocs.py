import unittest
from tradedocs import audit


class AuditTests(unittest.TestCase):
    def test_conflict(self):
        result = audit({"invoice": {"lc_number": "LC-1"}, "letter_of_credit": {"lc_number": "LC-2"}})
        self.assertIn({"field": "lc_number", "code": "CONFLICT", "sources": ["invoice", "letter_of_credit"]}, result["issues"])

    def test_consistent(self):
        data = {field: "x" for field in ("invoice_number", "lc_number", "bl_number", "currency", "total_amount", "port_of_discharge")}
        self.assertEqual(audit({"invoice": data, "packing_list": data})["status"], "NO_DETECTED_CONFLICTS")

    def test_invalid(self):
        with self.assertRaises(ValueError):
            audit({"invoice": {"total_amount": {"unsafe": "object"}}})

    def test_bad_document(self):
        with self.assertRaises(ValueError):
            audit({"unknown": {}})

    def test_missing(self):
        self.assertTrue(any(i["code"] == "MISSING" for i in audit({"invoice": {}})["issues"]))


if __name__ == "__main__":
    unittest.main()
