# Hermes Controlled Agents Lab v3 (2026-10-21)

**STATUS: ISOLATED REFERENCE / NOT HERMES-RUNTIME-INTEGRATED / PRODUCTION = HOLD.**

This code implements a small, deterministic multi-agent *control* reference (not actual LLM calls). It is intended to evaluate acceptance, durable state and zero-paid-cost policies outside the main Hermes engine. No production connectors, shell commands, external requests or real robot I/O can run here.

## Modules

- `orchestrator.py`: SQLite-backed state transitions, atomic idempotency, bounded task contracts, deterministic risk classification, demo-only execution, UNKNOWN-on-recovery, tamper-evident (not independently anchored) event ledger, redacted metrics.
- `approvals.py`: distinct lab-only issuer/verifier interfaces, HMAC-SHA256 signed claims bound to task ID + spec hash + approver + decision + nonce + expiry (maximum 10 minutes). Do **not** treat free-text approver names as authenticated identities.
- `local_router.py`: proposal-only offline local routing to Hermes / Kilo / OpenCode with Ollama; fail-closed on unavailable model/service or worker. It does NOT inspect your actual machine or execute anything.
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
