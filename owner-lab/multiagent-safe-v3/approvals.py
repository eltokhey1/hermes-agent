"""Lab HMAC approval envelope: bounded, task-bound, replay-resistant assertions.

Issuer and verifier are distinct interfaces. Neither establishes human identity:
production issuance must be behind separately authenticated, isolated service.
Verifier key MUST NOT be accessible to any LLM tool or untrusted process.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from collections.abc import Callable


class ApprovalDenied(ValueError):
    pass


AUDIENCE = "hermes-lab-v3"
FIELDS = {"aud", "task_id", "spec_hash", "approver", "decision", "issued_at", "expires_at", "nonce"}


def _key(value: bytes) -> bytes:
    if not isinstance(value, bytes) or len(value) < 32:
        raise ApprovalDenied("Strong out-of-band approval key required")
    return value


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _decode(data: str) -> bytes:
    if not data or len(data) > 4096 or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in data):
        raise ApprovalDenied("Malformed approval")
    try:
        return base64.b64decode(data + ("=" * (-len(data) % 4)), altchars=b"-_", validate=True)
    except (ValueError, TypeError) as exc:
        raise ApprovalDenied("Malformed approval") from exc


class ApprovalIssuer:
    """Issuer-side lab only. Identity supplied to issue() is NOT authenticated here."""

    def __init__(self, key: bytes, *, clock: Callable[[], float] = time.time):
        self.__key, self.clock = _key(key), clock

    def issue(self, *, task_id: str, spec_hash: str, approver: str,
              decision: str, ttl_seconds: int = 180) -> str:
        if not isinstance(approver, str) or not 1 <= len(approver) <= 128:
            raise ApprovalDenied("Invalid approver")
        if decision not in ("approve", "reject") or type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 600:
            raise ApprovalDenied("Invalid decision or validity interval")
        if not isinstance(task_id, str) or len(task_id) != 32 or not isinstance(spec_hash, str) or len(spec_hash) != 64:
            raise ApprovalDenied("Malformed approval binding")
        now = int(self.clock())
        payload = {"aud": AUDIENCE, "task_id": task_id, "spec_hash": spec_hash,
                   "approver": approver, "decision": decision, "issued_at": now,
                   "expires_at": now + ttl_seconds, "nonce": secrets.token_hex(16)}
        packed = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        mac = hmac.new(self.__key, packed, hashlib.sha256).digest()
        return _encode(packed) + "." + _encode(mac)


class ApprovalVerifier:
    """A verifier-only interface. HMAC requires a protected trust boundary in production."""

    def __init__(self, key: bytes, *, clock: Callable[[], float] = time.time):
        self.__key, self.clock = _key(key), clock

    def verify(self, token: str, *, task_id: str, spec_hash: str) -> dict:
        """Authorize only currently valid claims (never use archive inspection here)."""
        return self._inspect(token, task_id=task_id, spec_hash=spec_hash, enforce_expiry=True)

    def inspect_historical(self, token: str, *, task_id: str, spec_hash: str) -> dict:
        """Integrity inspection only: expired signatures cannot authorize execution."""
        return self._inspect(token, task_id=task_id, spec_hash=spec_hash, enforce_expiry=False)

    def _inspect(self, token: str, *, task_id: str, spec_hash: str, enforce_expiry: bool) -> dict:
        if not isinstance(token, str) or len(token) > 4096 or token.count(".") != 1:
            raise ApprovalDenied("Malformed approval")
        payload64, signature64 = token.split(".")
        packed, actual = _decode(payload64), _decode(signature64)
        expected = hmac.new(self.__key, packed, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, actual):
            raise ApprovalDenied("Invalid approval signature")
        try:
            claims = json.loads(packed)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApprovalDenied("Malformed claims") from exc
        if not isinstance(claims, dict) or set(claims) != FIELDS:
            raise ApprovalDenied("Invalid claim set")
        now = self.clock()
        iat, exp = claims["issued_at"], claims["expires_at"]
        if (claims["aud"] != AUDIENCE or claims["task_id"] != task_id or
                claims["spec_hash"] != spec_hash or claims["decision"] not in ("approve", "reject") or
                not isinstance(claims["approver"], str) or not 1 <= len(claims["approver"]) <= 128 or
                type(iat) is not int or type(exp) is not int or not 1 <= exp-iat <= 600 or
                (enforce_expiry and (iat > now + 2 or now >= exp)) or
                not isinstance(claims["nonce"], str) or len(claims["nonce"]) != 32):
            raise ApprovalDenied("Approval expired, invalid or misbound")
        return claims
