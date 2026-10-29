import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz
from pdf_review import inspect_pdf, main


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


    def test_output_create_once_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            args = ["pdf_review.py", "synthetic.pdf", "--output", str(output)]
            with patch("sys.argv", args), patch("pdf_review.inspect_pdf", return_value={"status": "NEEDS_REVIEW"}):
                main()
                self.assertEqual(output.read_text(encoding="utf-8"), '{\n  "status": "NEEDS_REVIEW"\n}'.replace("\\n", "\n"))
                with self.assertRaises(SystemExit):
                    main()
            self.assertIn("NEEDS_REVIEW", output.read_text(encoding="utf-8"))

    def test_output_rejects_dangling_symlink_without_writing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            target = Path(tmp) / "not-created.json"
            try:
                output.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("File symlink unsupported")
            args = ["pdf_review.py", "synthetic.pdf", "--output", str(output)]
            with patch("sys.argv", args), patch("pdf_review.inspect_pdf", return_value={"status": "NEEDS_REVIEW"}):
                with self.assertRaises(SystemExit) as error:
                    main()
            self.assertEqual(error.exception.code, 2)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
