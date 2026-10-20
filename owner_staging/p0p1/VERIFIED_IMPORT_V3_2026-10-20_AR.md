# Hermes Open Builder — P0/P1 Verified ZIP Import V3 (OFFLINE)

2026-10-20 | Non-production, staged-only, additive release.

## Actual fixed issue

`local_stage_hardened_v2.py` hashes the ZIP file, then opens its *path* anew for extraction. A synthetic race replaced the ZIP file after verification but before extraction. V2 extracted `swapped.txt` even though the receipt still referenced the hash of the original ZIP. **This is a proven source time-of-check/time-of-use race**, not a claim of external compromise.

`local_stage_verified_v3.py` reads up to `MAX_ZIP_BYTES+1` bytes once through one file handle, computes the SHA256 of these exact bytes, and passes an in-memory BytesIO containing the SAME bytes to ZipFile. This prevents a replacement-on-disk after that snapshot from changing extracted content. The archive bytes are held in memory with a maximum of 80 MiB; unpacked members and member counts remain capped by the previous constraints. V2 is preserved, not silently overwritten.

## Evidence and tests

Command: `python -m unittest discover -s tests -p 'test_*.py' -q`.
Executed on an isolated Linux Python 3.13 environment: **153/153 tests PASS**, including 13 new V3 tests and all 140 prior unit tests. Repeated after extracting the delivery ZIP into a fresh directory and verifying manifest checksums. Synthetic filesystem and source-contract tests only; these are NOT an integration test of Hermes on Windows or independent CI.

A direct synthetic attack fixture demonstrated:
- V2: `swapped.txt` extracted instead of the originally verified `safe.txt` — vulnerability reproduced.
- V3: `safe.txt` extracted and `swapped.txt` absent, despite the source ZIP file being replaced at the ZipFile opening boundary.

## Trust boundaries

Use only in a trusted, offline isolated staging directory. Verify the ZIP SHA256 against an *out-of-band* signed/pinned value before executing this Python code. This still does not guarantee Windows race-free destination directories or security against malicious code within a loaded ZIP, and the tool is NOT a security sandbox. It never imports extracted files or modifies actual Hermes. Network isolation and ESTOP still require real on-host proof.

Do not replace `C:\Users\m\AppData\Local\hermes` or live repos. No `git pull`, no `git reset`, no backup overwrite, no privileged ownership or ACL changes.

P0 gaps unchanged: full native backup (pending_messages Access Denied), functional restore, ESTOP of in-flight work, effective Hermes Docker sandbox verification. G0, G-CODE, G1 = NO-GO; PRODUCTION = HOLD.

Canonical portfolio mapping: 45 work packages, 120 historical IDs, 16 streams. This is an additive evidence delta, not a replacement tracker.
