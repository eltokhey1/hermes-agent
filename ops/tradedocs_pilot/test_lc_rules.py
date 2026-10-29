import unittest
from lc_rules import parse_fields, review

SAMPLE = ':20:LC-SYNTH-1\n:31D:271112FRANKFURT\n:44E:VYSOTSK\n:46A:CERTIFICATE OF INSPECTION\nCONTINUED\n:47A:THIRD PARTY BL ALLOWED'

class RulesTests(unittest.TestCase):
    def test_multiline(self):
        self.assertEqual(parse_fields(SAMPLE)['46A'], 'CERTIFICATE OF INSPECTION\nCONTINUED')
    def test_request_not_applied(self):
        r = review(SAMPLE, [{'status': 'REQUEST_ONLY', 'text': ':44E:DIFFERENT PORT'}])
        self.assertEqual(r['extracted_fields']['44E'], 'VYSOTSK')
        self.assertEqual(r['operative_amendments_applied'], 0)
        self.assertEqual(r['issues'][-1]['code'], 'NOT_PROVEN_OPERATIVE')
    def test_claimed_confirmation_not_applied(self):
        r = review(SAMPLE, [{'status': 'BANK_CONFIRMED'}])
        self.assertEqual(r['issues'][-1]['code'], 'REQUIRES_INDEPENDENT_AUTHENTICATION')
    def test_duplicate_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_fields(':20:ONE\n:20:TWO')
    def test_missing_reference_fails(self):
        with self.assertRaises(ValueError):
            review(':44E:PORT')
    def test_bad_amendment_fails(self):
        with self.assertRaises(ValueError):
            review(SAMPLE, [{'status': 'ACCEPTED'}])
    def test_empty_fields_need_review(self):
        self.assertEqual(review(SAMPLE)['status'], 'NEEDS_REVIEW')
        self.assertIn('44C', [x['field'] for x in review(SAMPLE)['issues'] if 'field' in x])

if __name__ == '__main__':
    unittest.main()
