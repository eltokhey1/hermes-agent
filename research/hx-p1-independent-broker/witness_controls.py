"""Same-host observer of a protected synthetic receipt log and broker replies."""
import json
import multiprocessing as mp
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile

import independent_gate as gate
from cryptography.hazmat.primitives import serialization


def connect_worker(path, channel):
    # Establish peer credentials before lending this connected descriptor to the observer.
    with socket.socket(socket.AF_UNIX) as client, socket.socket(fileno=channel) as ipc:
        client.connect(path)
        socket.send_fds(ipc, [b"W"], [client.fileno()])


def observe_request(path, request, uid, gid):
    parent, child = socket.socketpair()
    with parent, child:
        subprocess.run(["setpriv", f"--reuid={uid}", f"--regid={gid}", "--clear-groups",
                        "--no-new-privs", "--bounding-set=-all", sys.executable, "-B",
                        __file__, "connect", path, str(child.fileno())],
                       check=True, pass_fds=(child.fileno(),), timeout=8)
        _, descriptors, _, _ = socket.recv_fds(parent, 1, 1)
        fd, = descriptors
    with socket.socket(fileno=fd) as stream:
        stream.settimeout(5)
        stream.sendall(gate.canon(request) + b"\n")
        with stream.makefile("rb") as reader:
            return json.loads(reader.readline(20000))


def raw(key):
    return key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                             serialization.NoEncryption())


def public(key):
    return key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def main():
    uid, gid = int(os.environ["HX_RUNNER_UID"]), int(os.environ["HX_RUNNER_GID"])
    sha = os.environ["HX_SOURCE_SHA"]
    assert os.getuid() == 0 and uid != 0 and len(sha) == 40
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        base.chmod(0o711)
        audit = base / "effects.jsonl"
        audit.touch(mode=0o600)
        broker, witness = str(base / "broker"), str(base / "witness")
        owner, signer = (gate.Ed25519PrivateKey.generate() for _ in range(2))
        ctx = mp.get_context("fork")
        processes = []
        try:
            for path, service, mode in [
                (witness, gate.Witness(public(owner), raw(signer), audit), 0o600),
                (broker, gate.Broker(raw(owner), public(owner), witness, base, sha, uid), 0o666),
            ]:
                ready = ctx.Queue()
                process = ctx.Process(target=gate.serve, args=(path, service, mode, ready))
                process.start()
                processes.append(process)
                assert ready.get(timeout=5) == "ready"
            for action in sorted(gate.ALLOWED):
                task = secrets.token_hex(16)
                args = {"fixture": action}
                approval = gate.call(broker, dict(op="approve", action=action, task_id=task,
                                     sha=sha, args_sha256=gate.digest(args), ttl=30))
                grant = approval["grant"]
                request = dict(op="dispatch", action=action, task_id=task, sha=sha, args=args,
                               grant=grant, signature=approval["signature"])
                before = audit.read_bytes()
                denied = observe_request(broker, dict(request, signature=gate.b64(bytes(64))), uid, gid)
                assert denied == {"ok": False, "code": "INVALID_SIGNATURE"}
                assert audit.read_bytes() == before
                allowed = observe_request(broker, request, uid, gid)
                receipt = allowed["receipt"]
                event = {k: grant[k] for k in ("action", "task_id", "sha", "args_sha256", "nonce")}
                event["result"] = "SYNTHETIC_PREVIEW_ONLY"
                after = audit.read_bytes()
                assert after.startswith(before) and len(after[len(before):].splitlines()) == 1
                assert json.loads(after[len(before):]) == receipt and allowed["ok"] is True
                assert receipt["payload"]["event_sha256"] == gate.digest(event)
                assert gate.verify(signer.public_key(), receipt["payload"], receipt["signature"])
                print(json.dumps(dict(action=action, task_id=task, sha=sha, denied=denied["code"],
                                      denied_receipts=0, allowed_receipts=1)), flush=True)
        finally:
            for process in reversed(processes):
                process.terminate()
                process.join(5)


if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "connect":
        connect_worker(sys.argv[2], int(sys.argv[3]))
    else:
        main()
