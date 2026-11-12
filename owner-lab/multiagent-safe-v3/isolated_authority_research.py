"""Research-only, separate-process owner approval gate for existing Owner Lab v3.

Reuses approvals.py and orchestrator.py. There are NO production tools, calls,
network destinations, or side effects: only demo.echo and demo.review previews.

Two separately authenticated loopback IPC listeners use JSON bytes (NOT pickle).
The owner channel is not available to a simulated agent client. Session keys
and the demo HMAC signing key are not returned by either channel.

NOT a production human authenticator: both subprocesses share an OS account in
CI; a real deployment requires distinct OS identities/ACLs and a trusted,
CSRF-protected owner endpoint that no agent tool can reach. The in-memory
event anchor is lost on restart and must be durably protected independently.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import secrets
import threading
from multiprocessing.connection import AuthenticationError, Client, Listener
from pathlib import Path

from approvals import ApprovalIssuer, ApprovalVerifier
from durable_anchor_research import DurableAnchorResearch
from orchestrator import GateError, HermesReference


def _pack(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def exchange(address, session_key: bytes, command: dict) -> dict:
    """Test-only IPC helper; the agent must never receive the owner key."""
    with Client(address, authkey=session_key) as conn:
        conn.send_bytes(_pack(command))
        return json.loads(conn.recv_bytes(65536))


class _Boundary:
    """Only this independent process can issue an approval assertion."""

    def __init__(self, db_path, *, checkpoint_path=None, signing_key=None,
                 bootstrap=False):
        if signing_key is None:
            signing_key = secrets.token_bytes(32)  # transient legacy demo mode
        self.issuer = ApprovalIssuer(signing_key)
        self.core = HermesReference(db_path, verifier=ApprovalVerifier(signing_key))
        self.lock = threading.RLock()
        self.anchor = (DurableAnchorResearch(checkpoint_path, signing_key)
                       if checkpoint_path is not None else None)
        self.estop = False
        if self.anchor is not None:
            # Explicit bootstrap is NEVER allowed on a nonempty DB.
            if bootstrap and not self.anchor.path.exists():
                self.anchor.bootstrap(self._snapshot())
            record = self.anchor.load()  # missing or forged checkpoint => no start
            self.last_sealed_root = {
                "expected_seq": record["seq"], "expected_hash": record["root"]
            }
            self.estop = record["estop"]
            if not self.core.verify_external_anchor(**self.last_sealed_root):
                raise GateError("EXTERNAL_ANCHOR_MISMATCH")
        else:
            self.last_sealed_root = self._snapshot()

    def _snapshot(self):
        snap = self.core.status_summary()
        return {"expected_seq": snap["last_event_seq"],
                "expected_hash": snap["ledger_head_unanchored"]}

    def _assert_integrity(self):
        if self.anchor is not None:
            record = self.anchor.load()
            if (record["seq"] != self.last_sealed_root["expected_seq"]
                    or record["root"] != self.last_sealed_root["expected_hash"]
                    or record["estop"] != self.estop):
                raise GateError("ANCHOR_CHANGED_UNEXPECTEDLY")
        if not self.core.verify_external_anchor(**self.last_sealed_root):
            raise GateError("EXTERNAL_ANCHOR_MISMATCH")

    def _refresh_anchor(self):
        snapshot = self._snapshot()
        if self.anchor is not None:
            self.anchor.advance(previous=self.last_sealed_root,
                                current=snapshot, estop=self.estop)
        self.last_sealed_root = snapshot

    def _check_stop(self):
        if self.estop:
            raise GateError("ESTOP_LATCHED")

    def agent(self, req: dict):
        with self.lock:
            op = req.get("op")
            self._assert_integrity()
            if op == "pid":
                return {"pid": os.getpid(), "preview_only": True}
            if op == "submit":
                self._check_stop()
                task_id = self.core.submit(req["spec"], idempotency_key=req["idempotency_key"])
                state = self.core.task(task_id)["state"]
                if state == "PENDING":
                    self.core.prepare(task_id)
                task = self.core.task(task_id)
                self._refresh_anchor()
                return {"task_id": task_id, "spec_hash": task["spec_hash"],
                        "state": task["state"]}
            if op == "status":
                task = self.core.task(req["task_id"])
                return {"state": task["state"], "spec_hash": task["spec_hash"]}
            if op == "dispatch":
                self._check_stop()
                task = self.core.task(req["task_id"])
                if not isinstance(req.get("spec_hash"), str) or req["spec_hash"] != task["spec_hash"]:
                    raise GateError("EXACT_ACTION_HASH_MISMATCH")
                result = self.core.execute_demo(req["task_id"])
                self._refresh_anchor()
                return {"result": result, "state": self.core.task(req["task_id"])["state"]}
            raise GateError("AGENT_OPERATION_DENIED")

    def owner(self, req: dict, stop: threading.Event):
        with self.lock:
            op = req.get("op")
            if op == "shutdown":
                stop.set()
                return {"shutdown": True}
            self._assert_integrity()
            if op == "estop":
                self.estop = True
                self._refresh_anchor()  # durable latch after an agent crash/restart
                return {"estop_latched": True}
            if op == "decision":
                self._check_stop()
                if req.get("decision") not in ("approve", "reject"):
                    raise GateError("INVALID_OWNER_DECISION")
                task = self.core.task(req["task_id"])
                if task["state"] != "WAITING_APPROVAL":
                    raise GateError("NOT_WAITING_APPROVAL")
                if req.get("spec_hash") != task["spec_hash"]:
                    raise GateError("EXACT_ACTION_HASH_MISMATCH")
                ttl = req.get("ttl_seconds", 180)
                token = self.issuer.issue(
                    task_id=req["task_id"], spec_hash=task["spec_hash"],
                    approver="synthetic-owner-channel", decision=req["decision"],
                    ttl_seconds=ttl
                )
                state = self.core.approve(req["task_id"], token)
                self._refresh_anchor()
                return {"state": state, "spec_hash": task["spec_hash"]}
            raise GateError("OWNER_OPERATION_DENIED")


def _serve(listener: Listener, label: str, state: _Boundary, stopped: threading.Event):
    while not stopped.is_set():
        try:
            conn = listener.accept()
        except (AuthenticationError, OSError):
            # Bad HMAC handshake and socket teardown never grant privileges.
            continue
        try:
            with conn:
                command = json.loads(conn.recv_bytes(65536))
                if not isinstance(command, dict):
                    raise ValueError("INVALID_COMMAND")
                try:
                    result = state.agent(command) if label == "agent" else state.owner(command, stopped)
                    response = {"ok": True, "data": result}
                except (GateError, ValueError, KeyError, TypeError) as exc:
                    response = {"ok": False, "error": str(exc)}
                conn.send_bytes(_pack(response))
        except (EOFError, json.JSONDecodeError, OSError, ValueError):
            # Do not let malformed client bytes crash the authority process.
            continue


def serve_authority(db_path: str, agent_key: bytes, owner_key: bytes, ready_queue,
                    checkpoint_path=None, signing_key=None, bootstrap=False):
    """Spawn target. Key must come from isolated authority in real deployment."""
    state = _Boundary(Path(db_path), checkpoint_path=checkpoint_path,
                      signing_key=signing_key, bootstrap=bootstrap)
    stopped = threading.Event()
    with Listener(("127.0.0.1", 0), authkey=agent_key) as agent_listener, \
         Listener(("127.0.0.1", 0), authkey=owner_key) as owner_listener:
        ready_queue.put({"pid": os.getpid(), "agent_address": agent_listener.address,
                         "owner_address": owner_listener.address})
        for label, listener in (("agent", agent_listener), ("owner", owner_listener)):
            t = threading.Thread(target=_serve, args=(listener, label, state, stopped), daemon=True)
            t.start()
        stopped.wait()
