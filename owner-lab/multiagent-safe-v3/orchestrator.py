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

    def submit(self, spec: dict, *, idempotency_key: str) -> str:
        risk = self._validate_spec(spec)
        if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 128:
            raise GateError("Invalid idempotency key")
        now, task_id = utcnow(), uuid.uuid4().hex
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT task_id,spec_hash FROM tasks WHERE idempotency_key=?", (idempotency_key,)).fetchone()
            if current:
                if current["spec_hash"] != digest(spec):
                    raise GateError("Idempotency key collision with changed task")
                return current["task_id"]
            db.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?)",
                       (task_id, idempotency_key, canonical(spec), digest(spec), "PENDING", None, None, now, now))
            self._event(db, task_id, "SUBMITTED", {"policy_risk": risk, "spec_hash": digest(spec)})
        return task_id

    def task(self, task_id: str) -> dict:
        with self._conn() as db:
            row = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            raise GateError("Task not found")
        data = dict(row)
        data.pop("approval_assertion", None)  # don't disclose the signed bearer assertion
        data["spec"] = json.loads(data["spec"])
        data["result"] = json.loads(data["result"]) if data["result"] else None
        return data

    def prepare(self, task_id: str) -> str:
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            item = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not item or item["state"] != "PENDING":
                raise GateError("Task missing or not PENDING")
            risk = self._validate_spec(json.loads(item["spec"]))
            state = "WAITING_APPROVAL" if risk == "high" else "READY"
            db.execute("UPDATE tasks SET state=?,updated_at=? WHERE task_id=?", (state, utcnow(), task_id))
            self._event(db, task_id, "PREPARED", {"state": state})
        return state

    def approve(self, task_id: str, token: str) -> str:
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            item = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not item or item["state"] != "WAITING_APPROVAL":
                raise GateError("Task is not awaiting approval")
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
            item = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not item or item["state"] != "READY":
                raise GateError("Task cannot reserve from current state")
            spec = json.loads(item["spec"])
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
            item = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not item or item["state"] != "RUNNING":
                raise GateError("Task is not RUNNING")
            spec = json.loads(item["spec"])
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
            stuck = db.execute("SELECT task_id FROM tasks WHERE state='RUNNING' ORDER BY task_id").fetchall()
            for row in stuck:
                db.execute("UPDATE tasks SET state='UNKNOWN',updated_at=? WHERE task_id=?",
                           (utcnow(), row["task_id"]))
                self._event(db, row["task_id"], "RECOVERY_UNKNOWN", {"retry": "DENIED"})
        return len(stuck)

    def status_summary(self) -> dict:
        """Redacted operational snapshot; event root is unanchored in this lab."""
        with self._conn() as db:
            by_state = db.execute("SELECT state,COUNT(*) AS n FROM tasks GROUP BY state").fetchall()
            last = db.execute("SELECT seq,event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        return {"tasks_by_state": {row["state"]: row["n"] for row in by_state},
                "last_event_seq": last["seq"] if last else 0,
                "ledger_head_unanchored": last["event_hash"] if last else "GENESIS",
                "model_api_cost_usd": 0, "external_effects_enabled": False}

    def verify_ledger(self) -> bool:
        with self._conn() as db:
            rows = db.execute("SELECT * FROM events ORDER BY seq").fetchall()
        prior = "GENESIS"
        try:
            for row in rows:
                body = {"task_id": row["task_id"], "event_type": row["event_type"],
                        "payload": json.loads(row["payload"]), "previous_hash": row["previous_hash"],
                        "timestamp": row["timestamp"]}
                if row["previous_hash"] != prior or row["event_hash"] != digest(body):
                    return False
                prior = row["event_hash"]
        except (ValueError, TypeError, KeyError):
            return False
        return True
