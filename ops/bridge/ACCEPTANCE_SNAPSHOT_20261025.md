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
