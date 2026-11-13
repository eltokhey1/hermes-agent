"""Hermes owner approval authority — RESEARCH-ONLY offline IPC service core.

This module is NOT a human identity provider or a production trust root.
The test IdentityProofVerifier uses an HMAC synthetic issuer. Real deployments
must use an independently authenticated passkey/OIDC service, owner-side CSRF,
a different OS security principal, and an off-agent nonrollbackable epoch.
No action here can issue a real side effect: only inert demo.* previews.
"""
from __future__ import annotations

import base64
from contextlib import closing
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
import threading
import time


class Denied(ValueError):
    pass


def canonical(obj: object) -> bytes:
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise Denied("INVALID_CANONICAL_PAYLOAD") from exc


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mac(key: bytes, payload: bytes) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def _strong(key: bytes) -> bytes:
    if not isinstance(key, bytes) or len(key) < 32:
        raise Denied("MISSING_PROTECTED_SECRET")
    return key


def _hex(value: object, count: int) -> bool:
    return (isinstance(value, str) and len(value) == count and
            all(c in "0123456789abcdef" for c in value))


def _encode(obj: object, key: bytes) -> str:
    body = canonical(obj)
    return (base64.urlsafe_b64encode(body).decode("ascii").rstrip("=") +
            "." + mac(key, body))


def _decode(token: str, key: bytes) -> dict:
    if not isinstance(token, str) or len(token) > 4096 or token.count(".") != 1:
        raise Denied("MALFORMED_PROOF")
    payload, signature = token.split(".")
    if not payload or len(signature) != 64 or not _hex(signature, 64):
        raise Denied("MALFORMED_PROOF")
    if any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in payload):
        raise Denied("MALFORMED_PROOF")
    try:
        raw = base64.b64decode(payload + "=" * (-len(payload) % 4), altchars=b"-_", validate=True)
    except (ValueError, TypeError) as exc:
        raise Denied("MALFORMED_PROOF") from exc
    if not hmac.compare_digest(mac(key, raw), signature):
        raise Denied("INVALID_SIGNATURE")
    try:
        obj = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise Denied("MALFORMED_PROOF") from exc
    if not isinstance(obj, dict) or canonical(obj) != raw:
        raise Denied("NONCANONICAL_PROOF")
    return obj


ALLOWED_ACTIONS = frozenset(("demo.echo", "demo.review"))
ACTION_FIELDS = frozenset(("task_id", "effect", "target", "input_sha256", "cost_usd", "environment"))


def action_hash(action: dict) -> str:
    if not isinstance(action, dict) or set(action) != ACTION_FIELDS:
        raise Denied("INVALID_ACTION_CONTRACT")
    if (not _hex(action["task_id"], 32) or not _hex(action["input_sha256"], 64)
            or action["effect"] not in ALLOWED_ACTIONS
            or action["target"] != "synthetic-only"
            or type(action["cost_usd"]) is not int or action["cost_usd"] != 0
            or action["environment"] != "sandbox"):
        raise Denied("ACTION_OUTSIDE_RESEARCH_ALLOWLIST")
    return sha256(canonical(action))


class SyntheticProofVerifier:
    """Verifies attestation from a test-only simulated identity provider.

    The issuer key is NOT available to the agent client. No human login proof.
    """
    def __init__(self, key: bytes, *, subject: str, clock=time.time):
        self._key = _strong(key)
        self._subject = subject
        self._clock = clock

    def verify(self, assertion: str) -> dict:
        obj = _decode(assertion, self._key)
        now = int(self._clock())
        if (set(obj) != {"issuer", "audience", "subject", "session", "issued", "expires"}
                or obj["issuer"] != "hermes-synthetic-identity-v1"
                or obj["audience"] != "hermes-research-owner"
                or obj["subject"] != self._subject
                or not _hex(obj["session"], 32)
                or type(obj["issued"]) is not int or type(obj["expires"]) is not int
                or not 1 <= obj["expires"] - obj["issued"] <= 300
                or obj["issued"] > now + 2 or now >= obj["expires"]):
            raise Denied("OWNER_IDENTITY_PROOF_REJECTED")
        return obj


class ProtectedRootResearch:
    """Distinct SQLite checkpoint store with HMAC; not an actual protected root.

    A second DB on the SAME OS account is rollbackable. A separately protected
    trusted_min_epoch is required to detect a full two-store rollback.
    """
    def __init__(self, path: Path, key: bytes, *, trusted_min_epoch: int | None = None):
        if trusted_min_epoch is not None and (type(trusted_min_epoch) is not int or trusted_min_epoch < 1):
            raise Denied("INVALID_TRUSTED_EPOCH_FLOOR")
        self.path = Path(path)
        self._key = _strong(key)
        self.trusted_min_epoch = trusted_min_epoch
        if not self.path.parent.exists():
            raise Denied("ROOT_PARENT_NOT_PROVISIONED")

    def bootstrap(self, root: str) -> None:
        # Must only bootstrap an uninitialized research authority with zero events.
        if self.path.exists():
            raise Denied("ROOT_ALREADY_EXISTS")
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("CREATE TABLE checkpoints(epoch INTEGER PRIMARY KEY, root TEXT NOT NULL, mac TEXT NOT NULL)")
            db.execute("INSERT INTO checkpoints VALUES(?,?,?)", (1, root, mac(self._key, canonical([1, root]))))
            db.commit()

    def read(self) -> tuple[int, str]:
        if not self.path.exists():
            raise Denied("PROTECTED_ROOT_UNAVAILABLE")
        try:
            with closing(sqlite3.connect(self.path)) as db:
                row = db.execute("SELECT epoch,root,mac FROM checkpoints ORDER BY epoch DESC LIMIT 1").fetchone()
            if row is None:
                raise Denied("PROTECTED_ROOT_UNAVAILABLE")
            epoch, root, signature = row
            if type(epoch) is not int or epoch < 1 or not isinstance(root, str) or not isinstance(signature, str):
                raise Denied("PROTECTED_ROOT_INVALID")
            if not hmac.compare_digest(mac(self._key, canonical([epoch, root])), signature):
                raise Denied("PROTECTED_ROOT_TAMPERED")
            if self.trusted_min_epoch is not None and epoch < self.trusted_min_epoch:
                raise Denied("EXTERNAL_EPOCH_ROLLBACK")
            return epoch, root
        except sqlite3.DatabaseError as exc:
            raise Denied("PROTECTED_ROOT_UNAVAILABLE") from exc

    def advance(self, previous: tuple[int, str], new_root: str) -> int:
        epoch, root = self.read()
        if (epoch, root) != previous:
            raise Denied("PROTECTED_ROOT_CONFLICT")
        next_epoch = epoch + 1
        try:
            with closing(sqlite3.connect(self.path)) as db:
                db.execute("BEGIN IMMEDIATE")
                current = db.execute("SELECT epoch,root FROM checkpoints ORDER BY epoch DESC LIMIT 1").fetchone()
                if current != previous:
                    raise Denied("PROTECTED_ROOT_RACE")
                db.execute("INSERT INTO checkpoints VALUES(?,?,?)",
                           (next_epoch, new_root, mac(self._key, canonical([next_epoch, new_root]))))
                db.commit()
        except sqlite3.DatabaseError as exc:
            raise Denied("PROTECTED_ROOT_UNAVAILABLE") from exc
        return next_epoch


class OwnerAuthorityResearch:
    """Single deterministic gate; no direct external action dispatch.

    DB commit and protected checkpoint are intentionally separate: a crash in
    between makes future operations fail-closed, requiring human reconciliation.
    """
    def __init__(self, db_path: Path, root: ProtectedRootResearch,
                 proof_verifier: SyntheticProofVerifier, approval_key: bytes,
                 *, bootstrap: bool = False, clock=time.time):
        self.db_path = Path(db_path)
        self.root = root
        self.identity = proof_verifier
        self._approval_key = _strong(approval_key)
        self._clock = clock
        self.lock = threading.RLock()
        if not self.db_path.parent.exists():
            raise Denied("DB_PARENT_NOT_PROVISIONED")
        if bootstrap and self.db_path.exists():
            raise Denied("NO_AUTO_REBOOTSTRAP")
        if not bootstrap and not self.db_path.exists():
            raise Denied("AUTHORITY_DB_MISSING")
        if bootstrap:
            with self._conn() as db:
                db.executescript("""
                CREATE TABLE intents(task_id TEXT PRIMARY KEY, exact_hash TEXT NOT NULL,
                    action_json TEXT NOT NULL, state TEXT NOT NULL,
                    grant TEXT, granted_at INTEGER);
                CREATE TABLE challenges(challenge TEXT PRIMARY KEY, task_id TEXT NOT NULL,
                    owner_session TEXT NOT NULL, expires INTEGER NOT NULL, used INTEGER NOT NULL);
                CREATE TABLE audit(seq INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
                    event TEXT NOT NULL, previous TEXT NOT NULL, digest TEXT NOT NULL);
                CREATE TABLE control(id INTEGER PRIMARY KEY CHECK(id=1), estop INTEGER NOT NULL CHECK(estop IN (0,1)));
                INSERT INTO control VALUES(1,0);
                """)
            self.root.bootstrap(self._state_digest())
        self._integrity()

    def _conn(self):
        return closing(sqlite3.connect(self.db_path, timeout=10))

    def _state_digest(self) -> str:
        try:
            with self._conn() as db:
                intents = db.execute("SELECT * FROM intents ORDER BY task_id").fetchall()
                challenges = db.execute("SELECT * FROM challenges ORDER BY challenge").fetchall()
                events = db.execute("SELECT * FROM audit ORDER BY seq").fetchall()
                control = db.execute("SELECT * FROM control ORDER BY id").fetchall()
            if control not in ([(1, 0)], [(1, 1)]):
                raise Denied("ESTOP_STATE_INVALID")
            previous = "GENESIS"
            for seq, task_id, event, earlier, digest_value in events:
                if not isinstance(seq, int) or earlier != previous or digest_value != sha256(canonical([seq, task_id, event, earlier])):
                    raise Denied("AUDIT_CHAIN_INVALID")
                previous = digest_value
            return sha256(canonical({"intents": intents, "challenges": challenges,
                                     "events": events, "control": control}))
        except sqlite3.DatabaseError as exc:
            raise Denied("AUTHORITY_DB_CORRUPTED") from exc

    def _integrity(self) -> tuple[int, str]:
        snapshot = self.root.read()
        if snapshot[1] != self._state_digest():
            raise Denied("CHECKPOINT_DB_MISMATCH")
        return snapshot

    @staticmethod
    def _check_estop(db):
        row = db.execute("SELECT estop FROM control WHERE id=1").fetchone()
        if not row or row[0] != 0:
            raise Denied("ESTOP_LATCHED")

    @staticmethod
    def _append(db, task_id: str, event: str):
        prev = db.execute("SELECT digest FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        prior = prev[0] if prev else "GENESIS"
        seq = db.execute("SELECT COALESCE(MAX(seq),0)+1 FROM audit").fetchone()[0]
        db.execute("INSERT INTO audit VALUES(?,?,?,?,?)",
                   (seq, task_id, event, prior, sha256(canonical([seq, task_id, event, prior]))))

    def _transition(self, mutate):
        with self.lock:
            before = self._integrity()
            with self._conn() as db:
                db.execute("BEGIN IMMEDIATE")
                result = mutate(db)
                db.commit()
            # Crash here must cause a mismatch at next start, NOT silent replay.
            self.root.advance(before, self._state_digest())
            return result

    def submit(self, action: dict) -> dict:
        exact_hash = action_hash(action)
        task_id = action["task_id"]
        def mutate(db):
            self._check_estop(db)
            if db.execute("SELECT 1 FROM intents WHERE task_id=?", (task_id,)).fetchone():
                raise Denied("DUPLICATE_TASK_ID")
            db.execute("INSERT INTO intents VALUES(?,?,?,?,?,?)",
                       (task_id, exact_hash, canonical(action).decode(), "PENDING", None, None))
            self._append(db, task_id, "SUBMITTED")
            return {"task_id": task_id, "exact_action_hash": exact_hash, "state": "PENDING"}
        return self._transition(mutate)

    def inspect(self, task_id: str) -> dict:
        with self.lock:
            self._integrity()
            with self._conn() as db:
                row = db.execute("SELECT exact_hash,state FROM intents WHERE task_id=?", (task_id,)).fetchone()
            if not row:
                raise Denied("UNKNOWN_TASK")
            return {"task_id": task_id, "exact_action_hash": row[0], "state": row[1]}

    def begin_review(self, task_id: str, synthetic_identity_proof: str) -> dict:
        owner = self.identity.verify(synthetic_identity_proof)
        challenge = secrets.token_hex(16)
        expires = min(owner["expires"], int(self._clock()) + 180)
        def mutate(db):
            self._check_estop(db)
            task = db.execute("SELECT state FROM intents WHERE task_id=?", (task_id,)).fetchone()
            if not task or task[0] != "PENDING":
                raise Denied("TASK_NOT_PENDING")
            db.execute("INSERT INTO challenges VALUES(?,?,?,?,0)",
                       (challenge, task_id, owner["session"], expires))
            self._append(db, task_id, "OWNER_REVIEW_CHALLENGE")
            return {"review_challenge": challenge, "expires": expires}
        return self._transition(mutate)

    def decide(self, *, task_id: str, expected_hash: str, decision: str,
               synthetic_identity_proof: str, csrf_challenge: str, csrf_echo: str) -> dict:
        owner = self.identity.verify(synthetic_identity_proof)
        if decision not in ("approve", "reject"):
            raise Denied("INVALID_OWNER_DECISION")
        if (not isinstance(csrf_challenge, str) or not isinstance(csrf_echo, str)
                or not hmac.compare_digest(csrf_challenge, csrf_echo)
                or not _hex(csrf_challenge, 32)):
            raise Denied("CSRF_MISMATCH")
        now = int(self._clock())
        def mutate(db):
            self._check_estop(db)
            task = db.execute("SELECT exact_hash,state FROM intents WHERE task_id=?", (task_id,)).fetchone()
            challenge = db.execute("SELECT owner_session,expires,used FROM challenges WHERE challenge=? AND task_id=?",
                                   (csrf_challenge, task_id)).fetchone()
            if not task or task[1] != "PENDING" or not challenge:
                raise Denied("REVIEW_NOT_AUTHORIZED")
            if not hmac.compare_digest(task[0], expected_hash):
                raise Denied("EXACT_ACTION_HASH_MISMATCH")
            if challenge[0] != owner["session"] or challenge[2] != 0 or now >= challenge[1]:
                raise Denied("REVIEW_SESSION_INVALID_OR_REPLAYED")
            nonce = secrets.token_hex(16)
            token = _encode({"aud": "hermes-research-preview", "task": task_id,
                             "hash": expected_hash, "owner": owner["subject"],
                             "decision": decision, "nonce": nonce, "issued": now,
                             "expires": now + 120}, self._approval_key)
            db.execute("UPDATE challenges SET used=1 WHERE challenge=?", (csrf_challenge,))
            db.execute("UPDATE intents SET state=?, grant=?, granted_at=? WHERE task_id=?",
                       ("APPROVED" if decision == "approve" else "REJECTED", token if decision == "approve" else None,
                        now, task_id))
            self._append(db, task_id, "OWNER_" + decision.upper())
            return {"state": "APPROVED" if decision == "approve" else "REJECTED", "owner_proof": "SYNTHETIC_ONLY"}
        return self._transition(mutate)

    def emergency_stop(self) -> dict:
        """Owner-only synthetic latch; no external tool or watchdog is stopped."""
        def mutate(db):
            row = db.execute("SELECT estop FROM control WHERE id=1").fetchone()
            if not row:
                raise Denied("ESTOP_STATE_INVALID")
            if row[0] == 1:
                raise Denied("ESTOP_ALREADY_LATCHED")
            db.execute("UPDATE control SET estop=1 WHERE id=1")
            self._append(db, "ESTOP", "OWNER_ESTOP_LATCH")
            return {"estop": "LATCHED", "external_effects": False}
        return self._transition(mutate)

    def preview(self, task_id: str, expected_hash: str) -> dict:
        """Consumes a grant once; never executes a real tool or external effect."""
        now = int(self._clock())
        def mutate(db):
            self._check_estop(db)
            item = db.execute("SELECT action_json,exact_hash,state,grant FROM intents WHERE task_id=?", (task_id,)).fetchone()
            if not item or item[2] != "APPROVED" or not item[3]:
                raise Denied("NOT_APPROVED_OR_REPLAYED")
            if not isinstance(expected_hash, str) or not hmac.compare_digest(expected_hash, item[1]):
                raise Denied("EXACT_ACTION_HASH_MISMATCH")
            proof = _decode(item[3], self._approval_key)
            if (set(proof) != {"aud", "task", "hash", "owner", "decision", "nonce", "issued", "expires"}
                    or proof["aud"] != "hermes-research-preview" or proof["task"] != task_id
                    or proof["hash"] != item[1] or proof["decision"] != "approve"
                    or type(proof["issued"]) is not int or type(proof["expires"]) is not int
                    or now >= proof["expires"] or proof["issued"] > now + 2):
                raise Denied("APPROVAL_INVALID_OR_EXPIRED")
            action = json.loads(item[0])
            if action_hash(action) != item[1]:
                raise Denied("PERSISTED_ACTION_TAMPERED")
            db.execute("UPDATE intents SET state='CONSUMED',grant=NULL WHERE task_id=?", (task_id,))
            self._append(db, task_id, "DEMO_PREVIEW_CONSUMED")
            return {"task_id": task_id, "exact_action_hash": expected_hash,
                    "result": "INERT_PREVIEW", "external_effects": False, "production_allowed": False}
        return self._transition(mutate)
