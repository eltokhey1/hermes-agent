"""Static browser-script smoke checks without third-party dependencies."""
from pathlib import Path
import unittest

class BrowserScriptTests(unittest.TestCase):
    def test_no_double_escaped_regex(self):
        html = Path(__file__).with_name("global_pilot.html").read_text(encoding="utf-8")
        self.assertIn("/^[0-9]{6}$/", html)
        self.assertIn("/^[0-9]+(?:[.][0-9]+)?$/", html)
        self.assertNotIn(r"/^\\d", html)
        self.assertIn("fetch('/review'", html)

    def test_failed_review_does_not_claim_route_recorded(self):
        html = Path(__file__).with_name("global_pilot.html").read_text(encoding="utf-8")
        self.assertIn("No compliance result was produced.", html)
        self.assertNotIn("LOCAL_REVIEW_UNAVAILABLE — '+messages[lang.value].result", html)

    def test_javascript_string_does_not_contain_raw_newline(self):
        html = Path(__file__).with_name("global_pilot.html").read_text(encoding="utf-8")
        self.assertIn(chr(39) + chr(92) + "n'+JSON.stringify", html)
        self.assertNotIn("'\n'+JSON.stringify", html)

if __name__ == "__main__":
    unittest.main()
