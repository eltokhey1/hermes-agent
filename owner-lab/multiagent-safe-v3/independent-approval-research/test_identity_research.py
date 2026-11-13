"""Test-only synthetic identity issuer. Not a real login/SSO implementation."""
from __future__ import annotations
import secrets
import time
from authority import _encode, _strong


class SyntheticIssuer:
    def __init__(self, key: bytes, clock=time.time):
        self._key = _strong(key)
        self.clock = clock

    def mint(self, subject: str = "synthetic-owner", session: str | None = None,
             ttl_seconds: int = 120) -> str:
        now = int(self.clock())
        return _encode({"issuer": "hermes-synthetic-identity-v1",
                        "audience": "hermes-research-owner", "subject": subject,
                        "session": session or secrets.token_hex(16),
                        "issued": now, "expires": now + ttl_seconds}, self._key)
