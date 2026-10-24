# Hermes Controlled Agents Lab v3 (2026-10-21)

**STATUS: ISOLATED REFERENCE / NOT HERMES-RUNTIME-INTEGRATED / PRODUCTION = HOLD.**

This code implements a small, deterministic multi-agent *control* reference (not actual LLM calls). It is intended to evaluate acceptance, durable state and zero-paid-cost policies outside the main Hermes engine. No production connectors, shell commands, external requests or real robot I/O can run here.

## Modules

- `orchestrator.py`: SQLite-backed state transitions, atomic idempotency, bounded task contracts, deterministic risk classification, demo-only execution, UNKNOWN-on-recovery, tamper-evident (not independently anchored) event ledger, redacted metrics.
- `approvals.py`: distinct lab-only issuer/verifier interfaces, HMAC-SHA256 signed claims bound to task ID + spec hash + approver + decision + nonce + expiry (maximum 10 minutes). Do **not** treat free-text approver names as authenticated identities.
- `local_router.py`: proposal-only offline local routing to Hermes / Kilo / Aider / OpenCode with Ollama; fail-closed on unavailable model/service or worker. An optional `preferred_worker` accepts only an installed and explicitly allowed coding worker (kilo, aider, opencode). Unknown, unavailable, or cloud workers are rejected without fallback. It does NOT inspect your actual machine or execute anything.
- `patterns.py`: inert specialist proposals, bounded handoffs, fan-out synthesis and evaluation retries.
- `physical_sim.py`: entirely synthetic 2D virtual movement; never connects ROS2, Isaac, an actuator, or a robot.
- `tests/`: deterministic unittest-based tests, including tampered/expired/misbound/replayed approvals, concurrent idempotency and crash recovery.

Run on a trusted, isolated machine, from this directory:

```bash
python -m unittest discover -s tests -v
```

Expected at publication: **54 passing tests** (independent synthetic Python 3.13 container, 21 Oct 2026). The test count is not an assertion that P0/P1 is certified or Windows validated.

## Control contract

1. The Supervisor may propose a task but cannot assign its own risk, grant privileges, approve a payment, bypass verifier evidence or choose a paid provider.
2. Supported demo actions are only `demo.echo` (deterministic low risk) and `demo.review` (deterministic high risk). Both return inert previews. There is *no* executable code adapter in this archive.
3. Human approval for any real effect requires an independently authenticated approver and an authorization service isolated from LLM tooling. This lab **does not** authenticate approvers or isolate HMAC secrets from hostile same-process code; therefore real effects MUST remain disabled. Do not use this lab as a production policy engine.
4. Signed approval is revalidated at the execution reservation boundary; expiry, tampering, mismatched task/spec, duplicate receipt and missing verifier fail closed. Issuer API MUST NOT be exposed to the agent.
5. After a crash in RUNNING, mark UNKNOWN, reconcile, and never blindly replay. Idempotency keys keep retries from duplicating tasks, but **external exactly-once execution is NOT proven**.
6. The event hash chain lacks an independently protected external anchor, secure file ACL, encrypted assertions or anti-truncation guarantees. Ledger validity here is an *integrity smoke test*, not nonrepudiation.
7. No installation, network access, API spending, existing Hermes state modification, cloud environment, Git main merge or physical actuation is authorized by this package.

## Integration plan (hold until verified)

- **P0**: independently verify owner-Windows backup+restore, read-only inventory, protected ACLs/secrets, negative network and external effects tests.
- **P1**: compare existing Hermes Reliability & Recovery Engine / Acceptance & Evidence Engine with this reference and validate state and approval gate semantics end-to-end on host; guard UNKNOWN reconciliation and independently anchor ledger.
- **P2**: after P0/P1 PASS, add *one* CLI/skill/plugin adapter consumer for Kilo + Ollama or OpenCode, using trust-bounded config and verified tool paths. Only activate Shadow mode; require cost caps and audit evidence. LangGraph optional if measured win.
- **P3/P4**: radar and actual operator scenarios with shadow evals. Verdict-affecting changes restart observation window.
- **Physical AI** remains simulation-only research and needs its own independent safety case before future hardware work.

Repository policy: root `AGENTS.md` favors external skills/plugins over new core tools. This project is an **owner-lab prototype** under existing canonical portfolio packages (45 total), not a new root-level feature or framework dependency.

## October 21 follow-up integrity patch (isolated only)

Persistent specs are revalidated against their originally recorded digest on retrieval, approval, reservation and preview completion. Duplicate request lookup no longer trusts a corrupt stored task. Event ledger verification rejects missing or duplicate creation entries. `tests/test_persistent_integrity.py` contains six negative regression tests; focused and full synthetic tests: **60 passed**. See `REGRESSION_FIXES.md` and `PORTFOLIO_SYNC_AR.md` for the evidence and current single-source-of-truth mapping. No runtime integration is implied.

## State/Event reconciliation hardening (2026-10-21)

A second negative-test pass found that the former `verify_ledger` accepted a valid hash chain even if the stored task state was forged, a terminal event removed, or a syntactically valid but unauthorized transition appended. This is now **detected and denied** in the offline lab.

- The verifier replays per-task event transitions and compares the resulting state, contract digest, and stored result against SQLite; it rejects unknown event types, orphan/duplicate transitions, sequence gaps, corrupted contract hashes and missing terminal events.
- Critical local transition methods now check the same reconciliation invariant *inside the SQLite transaction* before changing state. This stops a forged READY state from skipping PREPARED in the synthetic lab.
- New regression file: `tests/test_state_ledger_integrity.py` (9 cases). Total isolated suite **69/69 PASS**, Python 3.13.5, `python -W error -m unittest discover -s tests -q`; `compileall` PASS. See `LEDGER_RECONCILIATION_RECEIPT.json`.
- This deliberately replays all events on each operation (prototype only), so scalability and multi-process locking must be benchmarked before integration. Because the ledger and tasks share the same SQLite database, this is **not protection against a malicious DB writer who rewrites everything**. External immutable anchoring, Windows ACLs, authenticated human identity, real Hermes process recovery and CI are still unverified. **PRODUCTION=HOLD**.

## Owner local Aider routing adapter (2026-10-24; proposal only)

The user's Windows inventory reported Aider 0.86.2, but this lab's proposal router previously omitted it. This scoped change supports Aider as a code worker without installing or invoking Aider. The default selection order is `kilo` → `aider` → `opencode`, while `preferred_worker="aider"` selects Aider only when present in *trusted supplied* inventory. An unavailable preferred worker fails closed instead of silently using another worker. General Hermes tasks never accept a coding-worker override. Any missing local Ollama listener/model continues to fail closed; the route remains `PROPOSAL_ONLY` and `estimated_cloud_usd=0`.

Regression coverage: `tests/test_local_router.py` includes default priority, Aider-only, preferred selection, denied unavailable workers, denied cloud aliases, wrong types, general-task override denial and Ollama-offline denial. These are **synthetic routing-contract tests**, not proof of actual Windows integration, sandbox isolation, credential safety, paid-API prevention at a real provider, or production readiness. Approval/ESTOP and host P0/P1 evidence remain mandatory; do not merge to `main` or enable side effects from this change alone.

## Approval receipt ↔ ledger consistency hardening (2026-10-24; offline only)

`verify_ledger()` now checks every `approval_nonces` row against a real task and its corresponding `APPROVAL_DECISION` event. It denies orphan/extra receipts, missing receipts, changes to a receipt's nonce/decision, missing approved assertions, and unexpected low-risk assertions; both approved and rejected paths remain supported. Historical approvals may expire without invalidating the immutable event/receipt consistency check: expiry is enforced **at reserve**, not when replaying the historical ledger. Negative tests are in `tests/test_state_ledger_integrity.py`.

This is **consistency checking within a single SQLite database**, not independent tamper resistance: a malicious process able to rewrite both tasks and events and receipts can still forge a new history. It does **not** authenticate a human, validate Windows ACLs, prove ESTOP, or enable external execution. P0/P1 and `PRODUCTION=HOLD` are unchanged.

## Signed historical approval integrity (2026-10-24; isolated lab only)

Approval receipts are now checked against the actual HMAC-signed approval assertion preserved for approved tasks, including the signed task ID, contract digest, nonce, decision and approver. Unlike execution authorization, the historical signature inspection intentionally does **not** reject previously valid tokens merely because their TTL expired. The existing `ApprovalVerifier.verify()` remains time-bounded and is still required at `reserve()`. A separate `inspect_historical()` API is **not** an authorization decision and must never be used for execution.

Synthetic regression tests cover modified signatures, random strings, separately signed approvals with a different nonce, assertions belonging to another task, forged ledger approver after a recalculated hash, and expired historic approvals. All checks remain scoped to the offline Owner Lab: HMAC keys in the same process do not provide a production authorization boundary; no authenticated real human identity, protected on-host secrets, external ledger anchor, or Windows P0/P1 acceptance is implied. `PRODUCTION=HOLD`.

## External audit-receipt comparison (2026-10-24; offline lab only)

`HermesReference.verify_external_anchor(expected_seq=..., expected_hash=...)` requires a caller-provided **independently retained, trusted** ledger sequence and head digest. It first verifies the complete current in-database event chain/task/approval consistency and then compares the latest event to that receipt. It fails closed on malformed receipts, a stale head, event rehashing and a deleted but internally consistent task/event tail. See `tests/test_external_anchor.py` for negative/positive synthetic examples.

This method is **inspection only**; it does not issue approval, start execution, produce an external receipt, write to external storage, or lock its own HMAC key. A digest copied from the same SQLite file, or held by the same untrusted worker, is NOT independent tamper protection. The real P1 gate still requires an actually protected append-only/off-device anchor, trusted ownership of receipts, authorization binding and tests on the owner's Windows host; `PRODUCTION=HOLD`.
