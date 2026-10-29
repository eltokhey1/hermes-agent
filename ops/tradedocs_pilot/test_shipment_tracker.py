import unittest
from datetime import date
from shipment_tracker import review, validate_drive_folder_url

class ShipmentTrackerTests(unittest.TestCase):
    def test_missing_fields(self):
        r = review({"lc_number":"SYNTH-1"},date(2026,10,25))
        self.assertEqual(r["status"],"NEEDS_REVIEW")
        self.assertTrue(any(x["code"]=="MISSING_DHL_TRACKING_NUMBER" for x in r["alerts"]))
    def test_dispatch_without_dhl(self):
        r=review({"lc_number":"SYNTH-1","documents_sent_date":"2026-10-20"},date(2026,10,25))
        self.assertIn("DHL_REQUIRED",[x["code"] for x in r["alerts"]])
    def test_payment_due(self):
        r=review({"lc_number":"SYNTH-1","payment_due_date":"2026-10-29"},date(2026,10,25))
        self.assertIn("UPCOMING_PAYMENT",[x["code"] for x in r["alerts"]])
    def test_payment_unverified(self):
        r=review({"lc_number":"SYNTH-1","payment_received_date":"2026-10-20"},date(2026,10,25))
        self.assertIn("UNVERIFIED_PAYMENT",[x["code"] for x in r["alerts"]])
    def test_hbl(self):
        r=review({"lc_number":"SYNTH-1","bl_type":"HBL"},date(2026,10,25))
        self.assertIn("HBL_LC_TERMS",[x["code"] for x in r["alerts"]])
    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            review({"lc_number":"SYNTH-1","vessel_eta":"tomorrow"})
    def test_drive_url(self):
        self.assertEqual(validate_drive_folder_url("https://drive.google.com/drive/folders/example"),"https://drive.google.com/drive/folders/example")
        with self.assertRaises(ValueError):
            validate_drive_folder_url("https://drive.google.com.evil.test/drive/folders/x")
    def test_no_notifications(self):
        self.assertEqual(review({"lc_number":"SYNTH-1"})["notifications_sent"],0)

if __name__=="__main__":
    unittest.main()
