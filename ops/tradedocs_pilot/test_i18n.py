import unittest
from i18n import LANGUAGES, MESSAGES, translate, check_catalog
class TranslationTests(unittest.TestCase):
 def test_complete(self): self.assertTrue(check_catalog())
 def test_four_languages(self): self.assertEqual(len(LANGUAGES),4)
 def test_all_keys_translate(self):
  for key in MESSAGES:
   for language in LANGUAGES: self.assertTrue(translate(key,language))
 def test_invalid_language(self):
  with self.assertRaises(ValueError): translate("app_title","de")
if __name__=="__main__": unittest.main()
