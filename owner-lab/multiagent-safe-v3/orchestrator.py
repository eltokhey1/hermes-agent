"""Hermes bounded offline reference v3. No network, subprocess or production actions.

SQLite is only the durable lab state store. HMAC assertions are not proof of
human login; the production identity, storage ACL and external audit anchor
must be independently verified before adapting any real action.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from approvals import ApprovalVerifier, ApprovalDenied


class GateError(Exception):
    pass


def canonical(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# Privilege/risk comes from deterministic allowlisted action policy, NOT model input.
ACTION_POLICY = {"demo.echo": "low", "demo.review": "high"}
SPEC_FIELDS = {"action", "input", "estimated_cost_usd", "network_allowed", "target_environment"}


class HermesReference:
    def __init__(self, db_path: str | Path, *, verifier: ApprovalVerifier):
        if not isinstance(verifier, ApprovalVerifier):
            raise GateError("Trusted approval verifier required")
        self.db_path, self.verifier = str(db_path), verifier
        with self._conn() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    spec TEXT NOT NULL,
                    spec_hash TEXT NOT NULL,
                    state TEXT NOT NULL,
                    approval_assertion TEXT,
                    result TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS approval_nonces (
                    nonce TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL UNIQUE,
                    decision TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
            """)

    @contextmanager
    def _conn(self):
        db = sqlite3.connect(self.db_path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def _event(self, db: sqlite3.Connection, task_id: str, kind: str, payload: dict):
        head = db.execute("SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        prior = head["event_hash"] if head else "GENESIS"
        moment = utcnow()
        body = {"task_id": task_id, "event_type": kind, "payload": payload,
                "previous_hash": prior, "timestamp": moment}
        db.execute("INSERT INTO events(task_id,event_type,payload,previous_hash,event_hash,timestamp) VALUES(?,?,?,?,?,?)",
                   (task_id, kind, canonical(payload), prior, digest(body), moment))

    @staticmethod
    def _validate_spec(spec: dict) -> str:
        if not isinstance(spec, dict) or set(spec) != SPEC_FIELDS:
            raise GateError("Invalid task contract: model cannot specify risk or privileges")
        action = spec["action"]
        if not isinstance(action, str) or action not in ACTION_POLICY:
            raise GateError("Action denied")
        if not isinstance(spec["input"], str) or len(spec["input"]) > 2000:
            raise GateError("Invalid bounded input")
        if type(spec["estimated_cost_usd"]) not in (int, float) or spec["estimated_cost_usd"] != 0:
            raise GateError("Only zero-cost actions allowed")
        if spec["network_allowed"] is not False or spec["target_environment"] != "sandbox":
            raise GateError("External effects denied")
        return ACTION_POLICY[action]

    @classmethod
    def _stored_spec(cls, row) -> dict:
        """Fail closed if persistent task data differs from its original digest.

        Does not defend against an attacker who can rewrite both the DB and
        all hashes; a separately protected anchor and ACL remain mandatory.
        """
        try:
            spec = json.loads(row["spec"])
            cls._validate_spec(spec)
            if digest(spec) != row["spec_hash"]:
                raise GateError("Persisted task spec integrity mismatch")
            return spec
        except (ValueError, TypeError, KeyError) as exc:
            if isinstance(exc, GateError):
                raise
            raise GateError("Invalid persisted task spec") from exc

    def submit(self, spec: dict, *, idempotency_key: str) -> str:
        risk = self._validate_spec(spec)
        if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 128:
            raise GateError("Invalid idempotency key")
        now, task_id = utcnow(), uuid.uuid4().hex
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            self._require_integrity(db)
            current = db.execute("SELECT task_id,spec,spec_hash FROM tasks WHERE idempotency_key=?", (idempotency_key,)).fetchone()
            if current:
                self._stored_spec(current)
                if current["spec_hash"] != digest(spec):
                    raise GateError("Idempotency key collision with changed task")
                return current["task_id"]
            db.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?)",
                       (task_id, idempotency_key, canonical(spec), digest(spec), "PENDING", None, None, now, now))
            self._event(db, task_id, "SUBMITTED", {"policy_risk": risk, "spec_hash": digest(spec)})
        return task_id

    def task(self, task_id: str) -> dict:
        with self._conn() as db:
            self._require_integrity(db)
            row = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            raise GateError("Task not found")
        data = dict(row)
        data.pop("approval_assertion", None)  # don't disclose the signed bearer assertion
        data["spec"] = self._stored_spec(data)
        data["result"] = json.loads(data["result"]) if data["result"] else None
        return data

    def prepare(self, task_id: str) -> str:
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            self._require_integrity(db)
            item = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not item or item["state"] != "PENDING":
                raise GateError("Task missing or not PENDING")
            risk = self._validate_spec(self._stored_spec(item))
            state = "WAITING_APPROVAL" if risk == "high" else "READY"
            db.execute("UPDATE tasks SET state=?,updated_at=? WHERE task_id=?", (state, utcnow(), task_id))
            self._event(db, task_id, "PREPARED", {"state": state})
        return state

    def approve(self, task_id: str, token: str) -> str:
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            self._require_integrity(db)
            item = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not item or item["state"] != "WAITING_APPROVAL":
                raise GateError("Task is not awaiting approval")
            self._stored_spec(item)
            try:
                claims = self.verifier.verify(token, task_id=task_id, spec_hash=item["spec_hash"])
            except ApprovalDenied as exc:
                raise GateError(str(exc)) from exc
            new_state = "READY" if claims["decision"] == "approve" else "REJECTED"
            try:
                db.execute("INSERT INTO approval_nonces VALUES(?,?,?)",
                           (claims["nonce"], task_id, claims["decision"]))
            except sqlite3.IntegrityError as exc:
                raise GateError("Approval already consumed") from exc
            db.execute("UPDATE tasks SET state=?,approval_assertion=?,updated_at=? WHERE task_id=?",
                       (new_state, token if new_state == "READY" else None, utcnow(), task_id))
            self._event(db, task_id, "APPROVAL_DECISION", {"decision": claims["decision"],
                       "approver": claims["approver"], "nonce_hash": digest(claims["nonce"])})
        return new_state

    def reserve(self, task_id: str) -> dict:
        """Durably transition to RUNNING, without making any external effect."""
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            self._require_integrity(db)
            item = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not item or item["state"] != "READY":
                raise GateError("Task cannot reserve from current state")
            spec = self._stored_spec(item)
            risk = self._validate_spec(spec)
            if risk == "high":
                try:
                    claims = self.verifier.verify(item["approval_assertion"], task_id=task_id,
                                                  spec_hash=item["spec_hash"])
                except ApprovalDenied as exc:
                    raise GateError(str(exc)) from exc
                if claims["decision"] != "approve":
                    raise GateError("Approval denied")
                used = db.execute("SELECT decision FROM approval_nonces WHERE task_id=? AND nonce=?",
                                  (task_id, claims["nonce"])).fetchone()
                if not used or used["decision"] != "approve":
                    raise GateError("Approval receipt missing")
            db.execute("UPDATE tasks SET state='RUNNING',updated_at=? WHERE task_id=?", (utcnow(), task_id))
            self._event(db, task_id, "STARTED", {"action": spec["action"]})
        return spec

    def finish_demo(self, task_id: str) -> dict:
        """No tool execution; finalize the deterministic inert preview only."""
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            self._require_integrity(db)
            item = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not item or item["state"] != "RUNNING":
                raise GateError("Task is not RUNNING")
            spec = self._stored_spec(item)
            self._validate_spec(spec)
            result = {"action": spec["action"], "preview": spec["input"], "external_effects": False,
                      "accepted_by": "deterministic-demo-only"}
            db.execute("UPDATE tasks SET state='SUCCEEDED',result=?,updated_at=? WHERE task_id=?",
                       (canonical(result), utcnow(), task_id))
            self._event(db, task_id, "SUCCEEDED", {"result_hash": digest(result)})
        return result

    def execute_demo(self, task_id: str) -> dict:
        prior = self.task(task_id)
        if prior["state"] == "SUCCEEDED":
            return prior["result"]
        self.reserve(task_id)
        return self.finish_demo(task_id)

    def recover_interrupted(self) -> int:
        """Mark work stranded in RUNNING as UNKNOWN; never blindly replay it."""
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            self._require_integrity(db)
            stuck = db.execute("SELECT task_id FROM tasks WHERE state='RUNNING' ORDER BY task_id").fetchall()
            for row in stuck:
                db.execute("UPDATE tasks SET state='UNKNOWN',updated_at=? WHERE task_id=?",
                           (utcnow(), row["task_id"]))
                self._event(db, row["task_id"], "RECOVERY_UNKNOWN", {"retry": "DENIED"})
        return len(stuck)

    def status_summary(self) -> dict:
        """Redacted operational snapshot; event root is unanchored in this lab."""
        with self._conn() as db:
            self._require_integrity(db)
            by_state = db.execute("SELECT state,COUNT(*) AS n FROM tasks GROUP BY state").fetchall()
            last = db.execute("SELECT seq,event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        return {"tasks_by_state": {row["state"]: row["n"] for row in by_state},
                "last_event_seq": last["seq"] if last else 0,
                "ledger_head_unanchored": last["event_hash"] if last else "GENESIS",
                "model_api_cost_usd": 0, "external_effects_enabled": False}

    @classmethod
    def _require_integrity(cls, db: sqlite3.Connection) -> None:
        if not cls._verify_ledger(db):
            raise GateError("Durable task state and ledger are inconsistent")

    def verify_ledger(self) -> bool:
        """Reconcile hash chain AND recorded transitions with durable task records.

        A database-local hash chain is not an independent anchor. A writer who
        controls every SQLite table can still rewrite history; host ACL and an
        independently protected anchor are mandatory for real actions.
        """
        with self._conn() as db:
            return self._verify_ledger(db)

    @classmethod
    def _verify_ledger(cls, db: sqlite3.Connection) -> bool:
        records = db.execute("SELECT * FROM tasks").fetchall()
        events = db.execute("SELECT * FROM events ORDER BY seq").fetchall()
        state = {}
        try:
            tasks = {}
            for row in records:
                spec = cls._stored_spec(row)
                tasks[row["task_id"]] = (row, spec, ACTION_POLICY[spec["action"]])
            # Reconcile approval receipts with transition events as well as tasks.
            # A ledger hash chain alone cannot detect edits to another SQLite table.
            receipt_rows = db.execute("SELECT nonce,task_id,decision FROM approval_nonces").fetchall()
            receipts = {}
            for receipt in receipt_rows:
                task_id = receipt["task_id"]
                if (task_id not in tasks or task_id in receipts or
                        not isinstance(receipt["nonce"], str) or len(receipt["nonce"]) != 32 or
                        receipt["decision"] not in ("approve", "reject")):
                    return False
                receipts[task_id] = receipt
            approval_events = {}
            prior, last_seq = "GENESIS", 0
            for row in events:
                task_id = row["task_id"]
                if task_id not in tasks or row["seq"] != last_seq + 1:
                    return False
                payload = json.loads(row["payload"])
                if not isinstance(payload, dict):
                    return False
                body = {"task_id": task_id, "event_type": row["event_type"],
                        "payload": payload, "previous_hash": row["previous_hash"],
                        "timestamp": row["timestamp"]}
                if row["previous_hash"] != prior or row["event_hash"] != digest(body):
                    return False
                prior, last_seq = row["event_hash"], row["seq"]
                record, spec, risk = tasks[task_id]
                current, kind = state.get(task_id), row["event_type"]
                if kind == "SUBMITTED" and current is None:
                    if payload != {"policy_risk": risk, "spec_hash": record["spec_hash"]}:
                        return False
                    next_state = "PENDING"
                elif kind == "PREPARED" and current == "PENDING":
                    next_state = "WAITING_APPROVAL" if risk == "high" else "READY"
                    if payload != {"state": next_state}:
                        return False
                elif kind == "APPROVAL_DECISION" and current == "WAITING_APPROVAL":
                    decision = payload.get("decision")
                    if decision not in ("approve", "reject"):
                        return False
                    if not isinstance(payload.get("approver"), str):
                        return False
                    if not isinstance(payload.get("nonce_hash"), str) or len(payload["nonce_hash"]) != 64:
                        return False
                    approval_events[task_id] = (decision, payload["nonce_hash"])
                    next_state = "READY" if decision == "approve" else "REJECTED"
                elif kind == "STARTED" and current == "READY":
                    if payload != {"action": spec["action"]}:
                        return False
                    next_state = "RUNNING"
                elif kind == "SUCCEEDED" and current == "RUNNING":
                    if not record["result"]:
                        return False
                    result = json.loads(record["result"])
                    if not isinstance(result, dict) or result.get("external_effects") is not False:
                        return False
                    if result.get("action") != spec["action"]:
                        return False
                    if payload != {"result_hash": digest(result)}:
                        return False
                    next_state = "SUCCEEDED"
                elif kind == "RECOVERY_UNKNOWN" and current == "RUNNING":
                    if payload != {"retry": "DENIED"}:
                        return False
                    next_state = "UNKNOWN"
                else:
                    return False
                state[task_id] = next_state
            if state.keys() != tasks.keys():
                return False
            for task_id, (record, _, risk) in tasks.items():
                if state[task_id] != record["state"]:
                    return False
                if (record["state"] == "SUCCEEDED") != (record["result"] is not None):
                    return False
                event = approval_events.get(task_id)
                receipt = receipts.get(task_id)
                if (event is None) != (receipt is None):
                    return False
                if risk != "high" and (event is not None or record["approval_assertion"] is not None):
                    return False
                if event is None:
                    if record["approval_assertion"] is not None:
                        return False
                else:
                    decision, nonce_hash = event
                    if receipt["decision"] != decision or digest(receipt["nonce"]) != nonce_hash:
                        return False
                    if decision == "approve":
                        if not isinstance(record["approval_assertion"], str) or not record["approval_assertion"]:
                            return False
                    elif record["approval_assertion"] is not None:
                        return False
            return True
        except (ValueError, TypeError, KeyError, GateError):
            return False
