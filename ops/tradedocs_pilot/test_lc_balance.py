import unittest
from lc_balance import calculate

LC={"lc_number":"SYNTH-1","currency":"USD","unit":"MT","quantity":"1000","amount":"324000","quantity_tolerance_pct":"10"}
def ship(ident, qty, amount, status="SHIPPED"):
    return {"lc_number":"SYNTH-1","shipment_id":ident,"quantity":qty,"amount":amount,"status":status}

class BalanceTests(unittest.TestCase):
    def test_two_shipments(self):
        r=calculate(LC,[ship("B1","300","97200"),ship("B2","200","64800")])
        self.assertEqual(r["remaining_nominal_quantity"],"500")
        self.assertEqual(r["remaining_face_value"],"162000")
    def test_planned_not_used(self):
        self.assertEqual(calculate(LC,[ship("B1",100,32400,"PLANNED")])["shipped_quantity"],"0")
    def test_cancelled_not_used(self):
        self.assertEqual(calculate(LC,[ship("B1",100,32400,"CANCELLED")])["remaining_face_value"],"324000")
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            calculate(LC,[ship("B1",100,32400),ship("B1",100,32400)])
    def test_mismatched_lc_rejected(self):
        with self.assertRaises(ValueError):
            calculate(LC,[dict(ship("B1",100,32400),lc_number="OTHER")])
    def test_overdraw_flag(self):
        self.assertIn("AMOUNT_EXCEEDS_LC_FACE_VALUE",calculate(LC,[ship("B1",1200,388800)])["warnings"])
    def test_decimal_exact(self):
        r=calculate({"lc_number":"SYNTH-1","currency":"USD","unit":"MT","quantity":"0.3","amount":"0.3"},[ship("B1","0.1","0.1")])
        self.assertEqual(r["remaining_face_value"],"0.2")
    def test_invalid_number(self):
        with self.assertRaises(ValueError):
            calculate(LC,[ship("B1","NaN",100)])
    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            calculate(LC,[ship("B1",-1,100)])
    def test_quantity_tolerance(self):
        self.assertEqual(calculate(LC,[])["quantity_limit_with_tolerance"],"1100")
if __name__=="__main__":
    unittest.main()
