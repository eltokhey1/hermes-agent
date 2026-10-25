"""One-shot, pinned Hermes GitHub transport test. No daemon or production access.

This script fetches ONE allowlisted, SHA-256-pinned smoke-test Python file,
runs it in a temporary directory without site packages, and writes a minimal
acknowledgement to an isolated test branch. It is NOT a security sandbox.
"""
import base64
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = 'eltokhey1/hermes-agent'
BRANCH = 'sandbox/hermes-transport-smoke-20261025'
SOURCE = 'ops/smoke_tests/transport_smoke_20261025.py'
RECEIPT = 'ops/smoke_tests/ack_transport_smoke_20261025.json'
EXPECTED_SHA256 = '78b6d037ee867299da091ffabfb0066b4f9ed589d62888b58a422eab4a74d196'


def gh_api(path, *options, allow_missing=False):
    command = ['gh', 'api', path, *options]
    result = subprocess.run(command, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=30)
    if result.returncode:
        if allow_missing and ('404' in result.stderr or 'Not Found' in result.stderr):
            return None
        raise RuntimeError('GitHub CLI request failed: ' + result.stderr.strip()[:500])
    return json.loads(result.stdout)


def get_content(path, allow_missing=False):
    import urllib.parse
    name = urllib.parse.quote(BRANCH, safe='')
    data = gh_api(f'repos/{REPO}/contents/{path}?ref={name}', allow_missing=allow_missing)
    if data is None:
        return None
    if data.get('type') != 'file' or data.get('encoding') != 'base64':
        raise ValueError('GitHub content response is not a base64 file')
    return base64.b64decode(data['content'], validate=False)


def main():
    if not shutil.which('gh'):
        raise RuntimeError('gh CLI is missing from PATH')
    payload = get_content(SOURCE)
    digest = hashlib.sha256(payload).hexdigest()
    print('TRANSPORT_READ_SHA256=' + digest, flush=True)
    if digest != EXPECTED_SHA256:
        raise RuntimeError('REFUSED: task SHA256 is not in pinned allowlist')

    previous = get_content(RECEIPT, allow_missing=True)
    if previous is not None:
        record = json.loads(previous.decode('utf-8'))
        if record.get('request_sha256') != digest or record.get('status') != 'PASS':
            raise RuntimeError('Existing receipt conflict; no overwrite allowed')
        print('RECEIPT_ALREADY_EXISTS=' + RECEIPT, flush=True)
        return

    with tempfile.TemporaryDirectory(prefix='hermes_transport_') as root:
        local = pathlib.Path(root) / 'smoke.py'
        local.write_bytes(payload)
        env = {k: v for k, v in os.environ.items() if k.upper() in
               ('PATH', 'PATHEXT', 'SYSTEMROOT', 'WINDIR', 'COMSPEC')}
        env.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1',
                    'HOME': root, 'USERPROFILE': root})
        completed = subprocess.run([sys.executable, '-I', '-B', '-S', str(local)],
                                   cwd=root, env=env, capture_output=True, text=True,
                                   encoding='utf-8', errors='replace', timeout=15)
        stdout = completed.stdout.strip()
        expected_line = 'PAYLOAD_SHA256=' + hashlib.sha256(b'HERMES_TRANSPORT_SMOKE_V1').hexdigest()
        if completed.returncode != 0 or completed.stderr or stdout.splitlines() != ['HERMES_SMOKE_OK', expected_line]:
            raise RuntimeError('Pinned smoke test returned unexpected result; no receipt uploaded')

    ack = {
        'schema': 'hermes.transport.smoke.ack.v1',
        'status': 'PASS',
        'request_path': SOURCE,
        'request_sha256': digest,
        'code_stdout': stdout.splitlines(),
        'returncode': completed.returncode,
        'completed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'production': 'HOLD',
        'isolation': 'NOT_PROVEN',
    }
    encoded = base64.b64encode((json.dumps(ack, sort_keys=True, indent=2) + '\n').encode('utf-8')).decode('ascii')
    gh_api(f'repos/{REPO}/contents/{RECEIPT}', '--method', 'PUT',
           '-f', 'message=test: acknowledge isolated Hermes transport probe [skip ci]',
           '-f', f'branch={BRANCH}', '-f', f'content={encoded}')
    print('LOCAL_SMOKE=PASS', flush=True)
    print('GITHUB_ACK_UPLOADED=' + RECEIPT, flush=True)
    print('PRODUCTION=HOLD', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print('TRANSPORT_SMOKE_FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
