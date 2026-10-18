# Hermes backup encryption helper — isolated synthetic QA (2026-10-19)

**Status: 6/6 SYNTHETIC PASS; WINDOWS / LIVE HERMES UNVERIFIED; PRODUCTION HOLD.**

This is a public-safe technical note only. It does not include real archives, secrets, paths or customer data. Nothing was deployed, uploaded from Windows, connected to production or merged to `main`.

## Artifact being checked

The previously generated local owner handoff ZIP `Hermes_Consolidated_Control_2026-10-18.zip` contains:

- `NEXT_WINDOWS_GPG_BACKUP.ps1` — encryption orchestration (**static inspection only; not run on Windows**). SHA-256 `159d8b36ee4a0ed01e1e7d6c0376e86ce1a2ed12f29e5926407516565a72affc`.
- `verify_gpg_stream.py` — helper performing streaming GPG decryption into an in-memory SHA-256 digest, no decrypted disk file. SHA-256 `91b6517c732cb00d1babd81fee104613731df008195d15c05dfdff6fd1db8de0`.

These hashes identify the *helper source files* only; they are not hashes of any user's secret-bearing backup.

## Isolated test scope

Environment: Linux, Python 3.13.5, GnuPG 2.4.7. A generated mock ZIP with synthetic placeholder values was encrypted using GPG symmetric AES-256 and SHA-256 S2K. Decryption and streamed checksum were checked. The unmodified Python verification helper was then exercised through a **test-only GPG shim** supplying only the synthetic fixture passphrase. The shim was never added to an owner script or production path.

| Check | Observation |
|---|---|
| Real GPG AES-256 synthetic encrypt | PASS |
| Real GPG decrypt matches original synthetic ZIP SHA-256 | PASS |
| Unmodified streaming helper accepts matching digest | PASS |
| Helper refuses wrong digest | PASS |
| Helper refuses intentionally corrupted ciphertext | PASS |
| Helper refuses missing ciphertext | PASS |

The test completed **6/6**. No real Hermes data was opened or mounted. The PowerShell orchestrator was **not executed**; pinentry UX, Windows ACLs, GPG availability, operating-system compatibility, encrypted off-device copy, source archive coverage, and actual application-level restore are **not validated**.

## Follow-up acceptance, not a duplicate task registry

This is supporting evidence for canonical engineering gate **P0-03**, linked to the user's private canonical portfolio's existing package. It is **not** a new work package or a formal P0 PASS.

1. On the owner's Windows host, user manually approves and executes the **already packaged script** with interactive passphrase entry. Never paste secrets in chat, GitHub, command-line flags or logs.
2. Require a locally verified decrypted SHA-256 match, and preserve the original archive until protected off-device custody and separate functional restore both pass.
3. Do not publish ZIP/encrypted ZIP, extracted files, secret-bearing logs, private file paths, or real credentials in this public repository. Record only safe redacted metadata and independent review.
4. P0-04 still requires Hermes itself to start and complete a synthetic/offline smoke-test **from an isolated restored home**. Python container isolation and SQLite checks are insufficient.
5. No branch merge, deployment, external sends or spend; readiness remains **HOLD**.

Refer to [single owner checkpoint](../CONSOLIDATED_OWNER_CHECKPOINT_2026-10-18.md) and [decision policy](../READINESS_DECISION_POLICY.md) for the authoritative status and human approval gate.
