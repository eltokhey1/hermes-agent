import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz
from pdf_review import inspect_pdf


class PdfTests(unittest.TestCase):
    def test_extract_page_and_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic.pdf"
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), "LC SYNTHETIC ONLY")
            doc.save(p)
            doc.close()
            result = inspect_pdf(p)
            self.assertEqual(result["pages"][0]["page"], 1)
            self.assertIn("LC SYNTHETIC ONLY", result["pages"][0]["text"])
            self.assertEqual(result["status"], "NEEDS_REVIEW")

    def test_image_only_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "scan.pdf"
            doc = fitz.open()
            doc.new_page()
            doc.save(p)
            doc.close()
            self.assertTrue(inspect_pdf(p)["pages"][0]["requires_manual_review"])

    def test_missing(self):
        with self.assertRaises(ValueError):
            inspect_pdf("/not/there.pdf")

    def test_too_large(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "oversized.pdf"
            p.write_bytes(b"x")
            with patch("pdf_review.MAX_BYTES", 0):
                with self.assertRaises(ValueError):
                    inspect_pdf(p)


if __name__ == "__main__":
    unittest.main()
