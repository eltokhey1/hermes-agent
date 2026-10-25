# Hermes Open Builder — GitHub transport acceptance snapshot

Date: 2026-10-25. Source of work-package truth remains the existing Hermes 45-WP/120-ID portfolio; this file is a **gate evidence snapshot**, not a parallel work backlog.

## Verified using GitHub and Windows reply

- ChatGPT GitHub connector created a SHA256-pinned one-shot smoke task on `sandbox/hermes-transport-smoke-20261025` and fetched it back, exact match.
- A Windows-local process using GitHub CLI executed the *pinned, fixed smoke fixture* and uploaded `ops/smoke_tests/ack_transport_smoke_20261025.json`; GitHub-side fetch confirmed `status=PASS`, `returncode=0`, `production=HOLD`, `isolation=NOT_PROVEN`.
- Read-only code transport job `ops/bridge/inbox/job-20261025-01.json` received Windows-local acknowledgment `ops/bridge/outbox/job-20261025-01.json`, `status=PASS`, `executed=false`, `function_names=['sum_range']`, source SHA256 matched.
- `PASS` here means successful **data transport and Python AST syntax analysis**. It is NOT Hermes runtime integration or successful code execution by Aider.

## Pending independent checks

- Job `ops/bridge/inbox/job-20261025-02.json` (`average`) was submitted. Its reply was **not yet seen** as of this snapshot. Cannot assert the background poller remains alive.
- `hermes_bridge_supervisor_v1.py` was published as an **opt-in** recovery wrapper for the previously verified local bridge file. It pins the worker SHA256, writes a local `status.json`, retries transient failures up to five times, and never runs submitted code.
- Tests: `test_bridge_v1.py` (35 cases), `test_supervisor_v1.py` (20 cases) are published for deterministic offline execution. **Do not mark these suites VERIFIED without a real test-run transcript/CI evidence linked to an exact commit.**
- Windows-side supervisor process, process lifetime across sleep/restart, ESTOP, OS process isolation, offline network isolation, and host backup/functional restore: UNKNOWN / NO-GO.

## Security / policy

- Public GitHub transport is limited to nonsensitive test snippets. No customer data, LC documents, passwords or secrets.
- The current v1 bridge **never executes untrusted code**; only `ast.parse()` is used on validated input. This is a syntax check, not safety certification or behavioral testing.
- Do not treat GH commit/receipt as authorization to run arbitrary model-generated code. A future Aider runner needs independently accepted local sandbox, pinned job permissions, HITL policy gate, bounded retries, allowlisted files, audit log, and replay protection.
- No merges, automated production deploys, external messages, secrets linking, spend, service auto-start, or new accounts.
- `G0=NO-GO; G-CODE=NO-GO; G1=NO-GO; PRODUCTION=HOLD`.

## Suggested next safe milestone

Verify the pending `average` receipt or diagnose Windows supervisor local status. Then run the 35+20 synthetic suites on Windows and capture SHA256 and process exit codes. Only after read-only transport is reliable should a separately authorized, fixed-fixture Aider+Ollama worker be piloted in an isolated non-production workspace.

## 2026-10-25 — independent receipt verifier and second negative-control task

- Job `job-20261025-03` was queued on the isolated branch at commit `a4a1b4ddd3cf82a3d96f3e0461109b3b0a651d1e` as a deliberately **invalid Python syntax** negative control. Its correct eventual receipt is `status=SYNTAX_ERROR`, `error_code=SYNTAX_ERROR`, `executed=false`. Do not report PASS for it.
- At the time of this update the GitHub outbox contains the Windows-confirmed receipt for `job-20261025-01` only; replies for `job-20261025-02` and `job-20261025-03` were not present. **Background Windows bridge health remains UNKNOWN.**
- A standalone read-only verifier `verify_receipts.py` and tests `test_verify_receipts.py` were added on the same isolated branch. The **exact published Git blobs** match the independently tested local copies (blob SHA `88bd0fe025d2b9a06d7b26220aec78f136727029` and `fc8d1a2f6f910362fb87c76fa4f3c3cf21c45682`). SHA-256 of the verifier is `8532ed9be2eb25089a5a61abbc4bfd20bb7ef5f4224a119c9c4f22e4627b11e4`.
- **TESTED_SYNTHETIC:** `python -m unittest -v test_verify_receipts.py`: **12/12 PASS**, exit 0, on the independent Linux Python execution environment. These tests cover request/receipt SHA mismatch, replayed job ID, production/execution markers, missing approvals, timestamp, positive syntax, and negative-control false success. **No Windows/CI run of this new suite has been established.**
- The verifier is read-only (`gh api` GET), and `VERIFIED_TRANSPORT_ONLY` asserts neither Windows process identity nor isolation nor any execution of submitted Python code. No merge, production, Aider auto-run or account/secret change was made.
