"""Offline synthetic/adversarial tests for the read-only Hermes GitHub bridge."""
import base64
import hashlib
import json
import unittest

import hermes_bridge_v1 as b


def job(code='def safe():\n    return 1\n', **updates):
    data = {'schema': 'hermes.bridge.job.v1', 'job_id': 'job-20261025-01',
            'operation': 'python_ast_check', 'approval': 'read_only',
            'source': code, 'source_sha256': hashlib.sha256(code.encode()).hexdigest()}
    data.update(updates)
    return json.dumps(data).encode()


def r(raw, name='job-20261025-01.json'):
    return b.review_task(name, raw)


class BridgeTests(unittest.TestCase):
    def test_01_valid(self):
        self.assertEqual(r(job())['status'], 'PASS')

    def test_02_function(self):
        self.assertEqual(r(job())['function_names'], ['safe'])

    def test_03_class(self):
        self.assertEqual(r(job('class Example:\n    pass\n'))['class_names'], ['Example'])

    def test_04_async(self):
        self.assertEqual(r(job('async def safe():\n    pass\n'))['function_names'], ['safe'])

    def test_05_syntax_error(self):
        self.assertEqual(r(job('def x(:\n    pass'))['status'], 'SYNTAX_ERROR')

    def test_06_syntax_line(self):
        self.assertEqual(r(job('def x(:\n    pass'))['line'], 1)

    def test_07_hash_mismatch(self):
        self.assertEqual(r(job(source_sha256='0'*64))['error_code'], 'SOURCE_HASH_MISMATCH')

    def test_08_schema_rejected(self):
        self.assertEqual(r(job(schema='different'))['error_code'], 'SCHEMA_INVALID')

    def test_09_job_id_rejected(self):
        self.assertEqual(r(job(job_id='evil'))['error_code'], 'JOB_ID_OR_OPERATION_INVALID')

    def test_10_operation_rejected(self):
        self.assertEqual(r(job(operation='shell_exec'))['error_code'], 'JOB_ID_OR_OPERATION_INVALID')

    def test_11_approval_rejected(self):
        self.assertEqual(r(job(approval='auto_execute'))['error_code'], 'APPROVAL_INVALID')

    def test_12_source_type_rejected(self):
        self.assertEqual(r(job(source=15))['error_code'], 'SOURCE_INVALID')

    def test_13_missing_source_rejected(self):
        data = json.loads(job()); data.pop('source')
        self.assertEqual(r(json.dumps(data).encode())['error_code'], 'SOURCE_INVALID')

    def test_14_nul_rejected(self):
        self.assertEqual(r(job('a\x00b'))['error_code'], 'SOURCE_INVALID')

    def test_15_oversize_source_rejected(self):
        self.assertEqual(r(job('x' * (b.MAX_SOURCE + 1)))['error_code'], 'SOURCE_INVALID')

    def test_16_oversize_job_rejected(self):
        self.assertEqual(r(b'x' * (b.MAX_FILE + 1))['error_code'], 'JOB_TOO_LARGE')

    def test_17_invalid_json_rejected(self):
        self.assertEqual(r(b'{oops')['error_code'], 'MALFORMED_JOB')

    def test_18_invalid_utf8_rejected(self):
        self.assertEqual(r(b'\xff')['error_code'], 'MALFORMED_JOB')

    def test_19_json_list_rejected(self):
        self.assertEqual(r(b'[]')['error_code'], 'SCHEMA_INVALID')

    def test_20_never_exec_raise(self):
        value = r(job('raise RuntimeError("UNTRUSTED_CODE_WOULD_HAVE_RUN")\n'))
        self.assertEqual(value['status'], 'PASS')
        self.assertIs(value['executed'], False)

    def test_21_never_exec_import(self):
        self.assertEqual(r(job('import os\nos.system("echo BAD")\n'))['status'], 'PASS')

    def test_22_source_sha_recorded(self):
        value = r(job())
        self.assertEqual(value['source_sha256'], hashlib.sha256('def safe():\n    return 1\n'.encode()).hexdigest())

    def test_23_read_only_marker(self):
        value = r(job())
        self.assertEqual(value['production'], 'HOLD')
        self.assertEqual(value['isolation'], 'NOT_PROVEN')

    def test_24_line_count(self):
        self.assertEqual(r(job())['line_count'], 2)

    def test_25_missing_inbox(self):
        self.assertEqual(b.scan_once(lambda path, **kwargs: None), 0)

    def test_26_listing_too_large(self):
        with self.assertRaises(RuntimeError):
            b.scan_once(lambda path, **kwargs: [{}] * 51)

    def test_27_invalid_listing_type(self):
        with self.assertRaises(RuntimeError):
            b.scan_once(lambda path, **kwargs: {'bad':'value'})

    def test_28_wrong_file_skipped(self):
        self.assertEqual(b.scan_once(lambda path, **kwargs: [{'name':'evil.py','type':'file'}]), 0)

    def test_29_subdirectory_skipped(self):
        self.assertEqual(b.scan_once(lambda path, **kwargs: [{'name':'job-20261025-01.json','type':'dir'}]), 0)

    def test_30_duplicate_suppressed(self):
        received = {b.INBOX:[{'name':'job-20261025-01.json','type':'file'}],
                    b.OUTBOX+'/job-20261025-01.json': {'already':'exists'}}
        def api(path, **kwargs): return received.get(path)
        self.assertEqual(b.scan_once(api), 0)

    def test_31_response_write_and_replay(self):
        body=job()
        state={b.INBOX:[{'name':'job-20261025-01.json','type':'file'}],
               b.INBOX+'/job-20261025-01.json':{
                   'type':'file','encoding':'base64','size':len(body),
                   'content':base64.b64encode(body).decode()}}
        writes=[]
        def api(path, *, method='GET', fields=None):
            if method=='GET': return state.get(path)
            writes.append(path)
            state[path]={'type':'file','encoding':'base64','size':1,'content':fields['content']}
        self.assertEqual(b.scan_once(api), 1)
        self.assertEqual(b.scan_once(api), 0)
        self.assertEqual(len(writes), 1)
        receipt=json.loads(base64.b64decode(state[writes[0]]['content']))
        self.assertEqual(receipt['status'], 'PASS')
        self.assertIs(receipt['executed'], False)

    def test_32_bad_base64_type(self):
        with self.assertRaises(ValueError):
            b.decode_content({'type':'dir','encoding':'base64','size':5,'content':'eA=='})

    def test_33_bad_file_size(self):
        with self.assertRaises(ValueError):
            b.decode_content({'type':'file','encoding':'base64','size':b.MAX_FILE+1,'content':'eA=='})

    def test_34_file_pattern_restriction(self):
        self.assertIsNone(b.JOB_RE.fullmatch('../job-20261025-01.json'))
        self.assertIsNone(b.JOB_RE.fullmatch('job-20261025-01.json/../../bad'))

    def test_35_read_only_receipt(self):
        self.assertIs(r(job())['executed'], False)

    def test_36_corrupt_base64_rejected(self):
        with self.assertRaises(ValueError):
            b.decode_content({'type':'file','encoding':'base64','size':1,'content':'eA==$'})

    def test_37_declared_size_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            b.decode_content({'type':'file','encoding':'base64','size':2,'content':'eA=='})

    def test_38_wrapped_github_base64_accepted(self):
        self.assertEqual(b.decode_content({'type':'file','encoding':'base64','size':1,
                                           'content':'eA==\\n'.replace('\\n', '\n')}), b'x')


if __name__ == '__main__':
    unittest.main(verbosity=2)
