"""Run two ephemeral, separate OS processes for TEST-ONLY owner authority.

Process A keeps signed checkpoint root and root signer key.
Process B holds a synthetic owner-proof verifier and preview-only approvals.
Two authenticated loopback channels: agent (submit/inspect/preview) and owner
(begin_review/decide/estop), with different 32-byte capability keys.

No human login, no TLS, no protected OS accounts, and no real tool actions.
"""
from __future__ import annotations

import json
import os
from multiprocessing.connection import AuthenticationError, Client, Listener
import threading

from authority import Denied, OwnerAuthorityResearch, ProtectedRootResearch, SyntheticProofVerifier, canonical


def request(address, authkey: bytes, payload: dict) -> dict:
    with Client(address, authkey=authkey) as channel:
        channel.send_bytes(canonical(payload))
        if not channel.poll(10):
            raise Denied("IPC_SERVICE_TIMEOUT")
        return json.loads(channel.recv_bytes(65536))


class RootClient:
    def __init__(self, address, authkey):
        self.address, self.authkey = address, authkey

    def _call(self, op, **args):
        try:
            resp = request(self.address, self.authkey, {"op": op, **args})
        except (OSError, EOFError, AuthenticationError) as exc:
            raise Denied("PROTECTED_ROOT_UNAVAILABLE") from exc
        if not resp["ok"]:
            raise Denied(resp["error"])
        return resp["data"]

    def bootstrap(self, root):
        self._call("bootstrap", root=root)

    def read(self):
        d = self._call("read")
        return (d["epoch"], d["root"])

    def advance(self, previous, new_root):
        return self._call("advance", previous=list(previous), new_root=new_root)["epoch"]


def _response(action):
    try:
        return {"ok": True, "data": action()}
    except (Denied, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def _serve(listener, label, handler, stopping):
    while not stopping.is_set():
        try:
            conn = listener.accept()
        except (AuthenticationError, OSError):
            continue
        try:
            with conn:
                raw = conn.recv_bytes(65536)
                try:
                    req = json.loads(raw)
                    if not isinstance(req, dict):
                        raise Denied("INVALID_REQUEST")
                    response = _response(lambda: handler(label, req, stopping))
                except (ValueError, UnicodeError, TypeError) as exc:
                    response = {"ok": False, "error": str(exc)}
                conn.send_bytes(canonical(response))
        except (EOFError, OSError):
            continue


def root_process(root_path, root_key, server_authkey, ready_queue,
                 trusted_min_epoch=None):
    store = ProtectedRootResearch(root_path, root_key,
                                  trusted_min_epoch=trusted_min_epoch)
    stopping = threading.Event()
    def handler(_label, req, stop):
        op = req.get("op")
        if op == "read":
            epoch, root = store.read()
            return {"epoch": epoch, "root": root}
        if op == "bootstrap":
            store.bootstrap(req["root"])
            return {"bootstrapped": True}
        if op == "advance":
            prev = req["previous"]
            if not isinstance(prev, list) or len(prev) != 2:
                raise Denied("INVALID_PREVIOUS_CHECKPOINT")
            return {"epoch": store.advance((prev[0], prev[1]), req["new_root"])}
        if op == "shutdown":
            stop.set()
            return {"stopping": True}
        raise Denied("ROOT_OPERATION_DENIED")
    with Listener(("127.0.0.1", 0), authkey=server_authkey) as listener:
        ready_queue.put({"pid": os.getpid(), "root_address": listener.address})
        _serve(listener, "root", handler, stopping)


def authority_process(db_path, root_address, root_authkey,
                      agent_authkey, owner_authkey, identity_issuer_key,
                      approval_signer_key, ready_queue, bootstrap=False):
    witness = RootClient(root_address, root_authkey)
    state = OwnerAuthorityResearch(
        db_path, witness,
        SyntheticProofVerifier(identity_issuer_key, subject="synthetic-owner"),
        approval_signer_key, bootstrap=bootstrap
    )
    stopping = threading.Event()

    def handler(label, req, stop):
        op = req.get("op")
        if label == "agent":
            if op == "pid":
                return {"pid": os.getpid(), "preview_only": True}
            if op == "submit":
                return state.submit(req["action"])
            if op == "inspect":
                return state.inspect(req["task_id"])
            if op == "preview":
                return state.preview(req["task_id"], req["expected_hash"])
            raise Denied("AGENT_CHANNEL_CANNOT_APPROVE")
        if label == "owner":
            if op == "begin_review":
                return state.begin_review(req["task_id"], req["identity_proof"])
            if op == "decide":
                return state.decide(task_id=req["task_id"],
                                    expected_hash=req["expected_hash"],
                                    decision=req["decision"],
                                    synthetic_identity_proof=req["identity_proof"],
                                    csrf_challenge=req["challenge"],
                                    csrf_echo=req["csrf_echo"])
            if op == "estop":
                return state.emergency_stop()
            if op == "shutdown":
                stop.set()
                return {"stopping": True}
            raise Denied("OWNER_OPERATION_DENIED")
        raise Denied("INVALID_CHANNEL")

    with Listener(("127.0.0.1", 0), authkey=agent_authkey) as agent, \
         Listener(("127.0.0.1", 0), authkey=owner_authkey) as owner:
        ready_queue.put({"pid": os.getpid(),
                         "agent_address": agent.address,
                         "owner_address": owner.address})
        for label, listener in (("agent", agent), ("owner", owner)):
            thread = threading.Thread(target=_serve,
                                      args=(listener, label, handler, stopping), daemon=True)
            thread.start()
        stopping.wait()
