import unittest
from requirements_registry import assess

C={"origin_country":"RU","export_country":"RU","import_country":"LY","commodity":"WHEAT","shipment_date":"2026-10-01"}
class RegistryTests(unittest.TestCase):
 def test_no_blanket_requirements(self):
  self.assertEqual(assess(C,{},[])["findings"],[])
 def test_invoice_missing_field(self):
  self.assertTrue(any(x["field"]=="invoice_number" for x in assess(C,{"COMMERCIAL_INVOICE":{}},[])["findings"]))
 def test_sourced_rule_missing_document(self):
  rule={"rule_id":"SYNTH","source":"synthetic-test-only","effective_date":"2026-01-01","jurisdiction":"LY","commodity":"WHEAT","document":"CERTIFICATE_OF_ORIGIN"}
  self.assertEqual(assess(C,{},[rule])["findings"][0]["rule_id"],"SYNTH")
 def test_future_rule_not_applied(self):
  rule={"rule_id":"SYNTH","source":"synthetic-test-only","effective_date":"2027-01-01","jurisdiction":"LY","commodity":"WHEAT","document":"CERTIFICATE_OF_ORIGIN"}
  self.assertEqual(assess(C,{},[rule])["findings"],[])
 def test_unattributed_rule_rejected(self):
  with self.assertRaises(ValueError):
   assess(C,{},[{"document":"COMMERCIAL_INVOICE"}])
 def test_missing_context(self):
  with self.assertRaises(ValueError):
   assess({}, {}, [])
if __name__=="__main__": unittest.main()
