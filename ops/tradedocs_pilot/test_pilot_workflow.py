import unittest
from datetime import date
from pilot_workflow import run

class WorkflowTests(unittest.TestCase):
 def test_synthetic_lc(self):
  data={'lc':{'lc_number':'SYNTH','currency':'USD','unit':'MT','quantity':'1000','amount':'324000'},'shipments':[{'lc_number':'SYNTH','shipment_id':'B1','status':'SHIPPED','quantity':'300','amount':'97200','bl_type':'HBL'}],'route':{'origin_country':'RU','export_country':'RU','import_country':'BR','commodity':'WHEAT','shipment_date':'2026-10-01'}}
  result=run(data,date(2026,10,25))
  self.assertEqual(result['balance']['remaining_nominal_quantity'],'700')
  self.assertEqual(result['balance']['remaining_face_value'],'226800')
  self.assertEqual(result['external_actions'],0)
  self.assertIn('HBL_LC_TERMS',[x['code'] for x in result['shipment_reviews'][0]['review']['alerts']])
  self.assertEqual(result['requirements']['status'],'NEEDS_JURISDICTION_AND_LC_REVIEW')
if __name__=='__main__': unittest.main()
