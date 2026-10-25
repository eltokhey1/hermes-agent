"""Verify Hermes bridge GitHub receipts without running untrusted code.

Read-only: uses 'gh api' GET requests against the fixed pilot branch.
A matching receipt is transport evidence, not proof of Windows identity or isolation.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import re
import subprocess
from urllib.parse import quote

REPO = 'eltokhey1/hermes-agent'
BRANCH = 'sandbox/hermes-transport-smoke-20261025'
JOB_NAME = re.compile(r'job-[0-9]{8}-[0-9]{2}\Z')
LIMIT = 32768


def github_read(path):
    endpoint = f'repos/{REPO}/contents/ops/bridge/{path}?ref={quote(BRANCH, safe="")}'
    result = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=35, check=False)
    if result.returncode:
        if '404' in result.stderr:
            return None
        raise RuntimeError('GitHub read failed (check authorization/connection)')
    data = json.loads(result.stdout)
    if data.get('type') != 'file' or data.get('encoding') != 'base64':
        raise ValueError('INVALID_GITHUB_FILE')
    if not isinstance(data.get('size'), int) or not 0 <= data['size'] <= LIMIT:
        raise ValueError('FILE_SIZE_INVALID')
    raw = base64.b64decode(''.join(data['content'].split()), validate=True)
    if len(raw) != data['size']:
        raise ValueError('FILE_SIZE_MISMATCH')
    return json.loads(raw)


def verify(job, receipt, requested_id):
    """Fail closed on a mismatched/replayed or improperly marked receipt."""
    errors = []
    if not isinstance(job, dict) or not isinstance(receipt, dict):
        return ['INVALID_JSON_OBJECT']
    if job.get('schema') != 'hermes.bridge.job.v1': errors.append('REQUEST_SCHEMA')
    if receipt.get('schema') != 'hermes.bridge.receipt.v1': errors.append('RECEIPT_SCHEMA')
    if job.get('job_id') != requested_id or receipt.get('job_id') != requested_id:
        errors.append('JOB_ID_MISMATCH')
    if job.get('operation') != 'python_ast_check' or receipt.get('operation') != 'python_ast_check':
        errors.append('OPERATION_MISMATCH')
    if job.get('approval') != 'read_only': errors.append('APPROVAL_INVALID')
    if receipt.get('executed') is not False: errors.append('EXECUTED_NOT_FALSE')
    if receipt.get('production') != 'HOLD': errors.append('PRODUCTION_NOT_HOLD')
    if receipt.get('isolation') != 'NOT_PROVEN': errors.append('ISOLATION_CLAIM_UNSUPPORTED')
    if receipt.get('status') == 'PASS' and receipt.get('error_code') is not None: errors.append('PASS_WITH_ERROR_CODE')
    source = job.get('source')
    if not isinstance(source, str) or len(source.encode('utf-8')) > 8192:
        errors.append('SOURCE_INVALID')
    else:
        digest = hashlib.sha256(source.encode('utf-8')).hexdigest()
        if job.get('source_sha256') != digest or receipt.get('source_sha256') != digest:
            errors.append('SOURCE_SHA256_MISMATCH')
        try:
            import ast
            ast.parse(source)
        except SyntaxError:
            if receipt.get('status') != 'SYNTAX_ERROR' or receipt.get('error_code') != 'SYNTAX_ERROR':
                errors.append('EXPECTED_SYNTAX_ERROR')
        else:
            if receipt.get('status') != 'PASS': errors.append('EXPECTED_AST_PASS')
    stamp = receipt.get('completed_at_utc')
    try:
        parsed = dt.datetime.fromisoformat(stamp)
        if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
            errors.append('INVALID_UTC_TIMESTAMP')
    except (ValueError, TypeError):
        errors.append('INVALID_UTC_TIMESTAMP')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only verification of Hermes bridge response')
    parser.add_argument('job_id', help='Example: job-20261025-01')
    opts = parser.parse_args(argv)
    if not JOB_NAME.fullmatch(opts.job_id): parser.error('job_id must match job-YYYYMMDD-NN')
    filename = opts.job_id + '.json'
    job = github_read('inbox/' + filename)
    receipt = github_read('outbox/' + filename)
    if job is None:
        print('VERDICT=REQUEST_MISSING')
        return 2
    if receipt is None:
        print('VERDICT=PENDING_NO_RECEIPT')
        return 3
    errors = verify(job, receipt, opts.job_id)
    print(json.dumps({'job_id': opts.job_id, 'verdict': 'VERIFIED_TRANSPORT_ONLY' if not errors else 'REJECTED',
                      'errors': errors, 'executed': False if not errors else 'UNVERIFIED',
                      'production': 'HOLD'}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print('VERDICT=READ_ERROR', type(exc).__name__)
        raise SystemExit(4)
