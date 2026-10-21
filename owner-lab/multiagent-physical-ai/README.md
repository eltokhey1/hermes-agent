# Hermes: Controlled Multi-Agent & Physical AI Boundary (2026-10-21)

Status: **DRAFT / NO GO / DESIGN + OFFLINE REFERENCE ONLY**. Scope maps to canonical 45-package portfolio; do not create duplicate work packages.

## Decision
- Reuse existing P1 durable task/acceptance engine first; compare LangGraph checkpoint/human-interrupt features as an optional adapter, not automatic migration.
- Orchestration: planner/supervisor -> route -> a few bounded specialists -> independent verifier -> deterministic policy/approval gate -> authorized executor -> evidence/reconciliation.
- The model never self-grants privileges, labels its own risk for enforcement, authorizes expenses, or bypasses a failed verification.
- Task persistence includes PENDING/READY/RUNNING/WAITING_APPROVAL/SUCCEEDED/FAILED/UNKNOWN/REJECTED. After uncertain external effects: UNKNOWN, reconcile first, never blind retry.
- Keep model/tool tracing local and redacted, with cost budgets, provenance and stable task IDs. Human approval must be authenticated, content-hash-bound, time-limited and checked before external effect.
- Prefer existing CLI/skill/plugin/MCP edges, not new Hermes core tools. Local model routing must never silently fall back to paid providers.
- Physical AI is a *separate, simulation-only* research direction. No actual robot command, ROS 2 actuator, VLA, GR00T, or hardware bridge is authorized. Future deployment needs an independent physical safety case, controller and owner approval.

## Offline reference evidence
A **separate downloadable archive delivered in the owner's ChatGPT conversation**, named `Hermes_MultiAgent_PhysicalAI_Reference_2026-10-21_v2.zip`, contains:
- `orchestrator.py`: state + idempotency + SQLite event-chain + inert `demo.echo` only.
- `patterns.py`: allowlisted router, bounded handoffs, evidence-aware fan-out and evaluator retry bounds.
- `physical_sim.py`: synthetic 2D collision, step limit and latched virtual emergency-stop checks.
- `tests/`: 27 synthetic Python unittest tests, locally executed, all passing (21 Oct 2026 in isolated Python 3.13.5 Linux).
ZIP SHA256: `3394da7ca6f624a2ff5c94d47bc365dc5b6d864859825ae829e80414dcfd027e`.

**These exact local tests were not run on GitHub or on the actual Windows Hermes checkout. Source files have NOT been committed in this documentation-only PR.** No production claim.

## Evaluation and rejection gates
- Before P2 runtime adapter: P0 verified recovery + Windows write ACL / trust boundary; P1 durability, independent acceptance, retry, event ledger anchor and shadow tests.
- Reproduce local tests in trusted isolated environment and inspect provenance, user identity and signed approvals. Build an actual adapter consumer before touching core.
- No installs, external requests, personal source data, API keys, cloud resource creation, robot controls, spends, merges or production deployment by this change.
- If any gate remains unverified, status remains NO GO.

## Up-to-date vendor note
Google's official robotics docs say Gemini Robotics ER 1.6 was deprecated 2026-08-31 in favor of ER 2; don't build a new adapter to 1.6.
References:
- https://ai.google.dev/gemini-api/docs/robotics-overview
- https://github.com/RobotecAI/rai
- https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
- https://github.com/langchain-ai/langgraph-supervisor-py
- https://github.com/langchain-ai/langgraph-swarm-py

## Offline v3 lab follow-up — 2026-10-21

The owner-directed standalone reference was upgraded to **Hermes_MultiAgent_Safe_Lab_v3_2026-10-21.zip**, stored as a ChatGPT conversation artifact (not checked into this public repository). SHA-256: `26429cab4dafada07e11e295a5d5c29c56dd1bf787a73325a8149e5a43beda1a`.

Changes evaluated: deterministic action/risk classification; separate HMAC lab issuer/verifier interfaces with task/spec binding, nonce and TTL; signature/expiry/replay denial; SQLite idempotency under concurrent submits; interrupted RUNNING → UNKNOWN without replay; redacted status snapshot; no-paid-cloud planning to local Ollama/Kilo/OpenCode; simulation-only robotics.

**Validation:** 54/54 isolated Python 3.13 `unittest` cases passed, including re-test after extracting the ZIP, with warnings-as-errors for SQLite ResourceWarning. The GitHub branch **does not contain these lab source files**, and GitHub Actions/Windows tests have **not** executed on this branch.

**Safety qualifications:** HMAC lab signing **does not authenticate a human** and its verifier secret is not safe if given to untrusted code in the same process. Before any real action use separate authenticated approval issuance/isolation, P0/P1 negative tests, Windows backup+restore, protected audit anchor and shadow-mode evaluation. Status remains **DRAFT / PRODUCTION HOLD**. This is evidence for the existing P0/P1/P2 packages, not a new canonical work package.
