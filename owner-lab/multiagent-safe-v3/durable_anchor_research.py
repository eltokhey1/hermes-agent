"""Research-only durable checkpoint for an isolated Owner Lab approval process.

This is NOT an independently protected production trust root. Both SQLite and
checkpoint are writable by the SAME hosted CI OS account. The synthetic secret
is injected into authority subprocess from the test harness; no user secret.
If an attacker can obtain that key and rewrite both files, the evidence is
forgeable. Replaying *both* a valid checkpoint and SQLite snapshot is also
undetectable without an external protected monotonic counter.

Production requires hardened signer identity, separate OS account/ACL or HSM,
trusted monotonic epoch, authenticated owner UI and independent watchdog.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
from pathlib import Path

from orchestrator import GateError


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


class DurableAnchorResearch:
    """Synthetic process-private signing key + separate on-disk receipt.

    There is no automatic bootstrap. An explicit first-time bootstrap is
    permitted ONLY for an empty new ledger with the caller's trusted key.
    """

    def __init__(self, path: str | Path, secret: bytes, *, minimum_expected_epoch=None):
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise GateError("ANCHOR_KEY_REQUIRED")
        if minimum_expected_epoch is not None and (
                type(minimum_expected_epoch) is not int or minimum_expected_epoch < 1):
            raise GateError("TRUSTED_EPOCH_REQUIRED")
        # This value MUST come from an independent, protected system. A caller
        # reading it from the same checkpoint defeats the rollback protection.
        self.minimum_expected_epoch = minimum_expected_epoch
        self.path = Path(path)
        self._mac_key = hmac.new(secret, b"hermes-owner-anchor-research-v1", hashlib.sha256).digest()

    def _seal(self, body: dict) -> dict:
        return {**body, "mac": hmac.new(self._mac_key, _canonical(body), hashlib.sha256).hexdigest()}

    def _read_raw(self) -> dict:
        try:
            if self.path.stat().st_size > 4096:
                raise GateError("ANCHOR_MALFORMED")
            return json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise GateError("ANCHOR_MISSING") from exc
        except (OSError, ValueError, UnicodeError) as exc:
            raise GateError("ANCHOR_MALFORMED") from exc

    def load(self) -> dict:
        record = self._read_raw()
        if not isinstance(record, dict) or set(record) != {"version", "epoch", "seq", "root", "estop", "mac"}:
            raise GateError("ANCHOR_MALFORMED")
        body = {key: record[key] for key in ("version", "epoch", "seq", "root", "estop")}
        if (body["version"] != 1 or type(body["epoch"]) is not int or body["epoch"] < 1
            or type(body["seq"]) is not int or body["seq"] < 0
            or type(body["estop"]) is not bool or not isinstance(body["root"], str)
            or not isinstance(record["mac"], str)):
            raise GateError("ANCHOR_MALFORMED")
        if not ((body["seq"] == 0 and body["root"] == "GENESIS") or
                (body["seq"] > 0 and len(body["root"]) == 64 and
                 all(c in "0123456789abcdef" for c in body["root"]))):
            raise GateError("ANCHOR_MALFORMED")
        actual = hmac.new(self._mac_key, _canonical(body), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(record["mac"], actual):
            raise GateError("ANCHOR_SIGNATURE_MISMATCH")
        if (self.minimum_expected_epoch is not None
                and body["epoch"] < self.minimum_expected_epoch):
            raise GateError("ANCHOR_ROLLBACK_DETECTED")
        return body

    def bootstrap(self, current: dict) -> None:
        """Only initial empty DB and an explicitly requested research bootstrap."""
        if current != {"expected_seq": 0, "expected_hash": "GENESIS"}:
            raise GateError("BOOTSTRAP_REQUIRES_EMPTY_LEDGER")
        body = {"version": 1, "epoch": 1, "seq": 0, "root": "GENESIS", "estop": False}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.path, "x", encoding="utf-8") as handle:
                handle.write(_canonical(self._seal(body)).decode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError as exc:
            raise GateError("ANCHOR_ALREADY_EXISTS") from exc

    def advance(self, *, previous: dict, current: dict, estop: bool):
        """Atomic research checkpoint write. DB and checkpoint are NOT atomic together.

        A crash between a DB transition and this write will fail closed at
        restart and needs owner reconciliation, not an agent-initiated replay.
        """
        old = self.load()
        if ({"expected_seq": old["seq"], "expected_hash": old["root"]} != previous
                or old["estop"] and not estop):
            raise GateError("ANCHOR_CONFLICT")
        if not isinstance(estop, bool) or current["expected_seq"] < old["seq"]:
            raise GateError("ANCHOR_SEQUENCE_INVALID")
        if current == previous and old["estop"] == estop:
            return
        if current["expected_seq"] == old["seq"] and current["expected_hash"] != old["root"]:
            raise GateError("ANCHOR_REWRITE_DENIED")
        body = {"version": 1, "epoch": old["epoch"] + 1,
                "seq": current["expected_seq"], "root": current["expected_hash"], "estop": estop}
        packed = _canonical(self._seal(body))
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), prefix=".research-anchor-")
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(packed)
                out.flush()
                os.fsync(out.fileno())
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
