import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from local_api import Handler

class LocalApiTests(unittest.TestCase):
 def test_loopback_review_and_ui(self):
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
  worker=threading.Thread(target=server.serve_forever,daemon=True)
  worker.start()
  try:
   conn=HTTPConnection('127.0.0.1',server.server_port,timeout=3)
   conn.request('GET','/')
   response=conn.getresponse()
   self.assertEqual(response.status,200)
   self.assertIn(b'global',response.read().lower())
   payload={'lc':{'lc_number':'SYNTH','currency':'USD','unit':'MT','quantity':'1000','amount':'324000'},'shipments':[{'lc_number':'SYNTH','shipment_id':'S1','status':'SHIPPED','quantity':'300','amount':'97200'}],'route':{'origin_country':'RU','export_country':'RU','import_country':'BR','commodity':'100199','shipment_date':'2026-10-01'}}
   conn.request('POST','/review',body=json.dumps(payload),headers={'Content-Type':'application/json'})
   response=conn.getresponse()
   self.assertEqual(response.status,200)
   self.assertEqual(json.loads(response.read())['balance']['remaining_face_value'],'226800')
   conn.request('GET','/',headers={'Host':'evil.example'})
   response=conn.getresponse()
   self.assertEqual(response.status,403)
   response.read()
   conn.request('POST','/review',body='{}',headers={'Content-Type':'text/plain'})
   response=conn.getresponse()
   self.assertEqual(response.status,415)
   response.read()
   conn.request('POST','/review',body='{',headers={'Content-Type':'application/json'})
   response=conn.getresponse()
   self.assertEqual(response.status,400)
   response.read()
   conn.close()
  finally:
   server.shutdown()
   server.server_close()
if __name__=='__main__':unittest.main()
