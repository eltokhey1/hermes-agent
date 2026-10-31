# OpenBot selective integration review — 2026-10-31

Status: RESEARCH_ACCEPTED / INTEGRATION_NOT_EXECUTED / PRODUCTION_HOLD

Scope: Hermes Open Builder, TradeDocs AI, Shipment Intelligence, Designer and Radar. This is a documentation-only evaluation, not authorization to install, connect accounts, run code, or deploy.

## Decisions
1. CopilotKit/OpenBot (https://github.com/CopilotKit/OpenBot): Tier 1, **AG-UI adapter / governance UX reference**. Favor extracting the protocol adapter, approval and audit interaction patterns rather than deploying the full beta platform. The full stack requires Bun, Docker, PostgreSQL and CopilotKit Intelligence/licensing. Do not create a second independent authorization gateway; Hermes Guarded Runtime is authoritative.
2. regnull/openbot (https://github.com/regnull/openbot): Tier 2, **inbox/actor/handoff and SSE UI patterns**. Its shell tool is not sandboxed; do not connect execution tools. Study durable inbox, bounded handoff and HITL pause semantics.
3. meetopenbot/openbot (https://github.com/meetopenbot/openbot): Tier 2, **minimal event API prototype**. Study GET /api/events and GET /api/state. No direct tool execution or exposed listener until authenticated event validation and isolation are proven.
4. nightly-labs/openbot (https://github.com/nightly-labs/openbot): EXCLUDE from executable integration. Development preview defaults to danger-full-access / approvalPolicy never; current PolyForm Noncommercial license requires a separate commercial license for business use. Reference architecture only where license permits.

## Pilot contract (design only)
Hermes -> authenticated AG-UI read-only adapter -> user interface. Any tool request must go through the existing fail-closed Guarded Runtime (ESTOP, allowlist, per-action approval, budget, idempotency, audit); no tool execution from OpenBot's own runtime. Do not copy customer documents, LC/BL details, credentials, or sensitive context into an external service. No network exposure by default.

## Required acceptance evidence
- License and dependency audit with pinned revisions and SBOM
- Windows 10 Intel i5/16GB RAM compatibility and disk headroom assessment
- Offline schema/contract tests for AG-UI events, reconnect and SSE ordering
- Tenant and identity isolation; reject malicious redirects, private targets and forged approvals
- Durable checkpoint/replay tests with unknown outcomes and idempotency keys
- Negative tests proving ESTOP and denial are enforced before tools
- Performance and cost per successful task benchmark against Hermes baseline, rollback plan
- Independent verifier and authentic Windows native evidence

Do not modify pyproject.toml, uv.lock, running processes, services, secrets or CI workflow as part of this review.

Release seal: PRODUCTION=HOLD; G0/G-CODE/G1=NO-GO; HITL=REQUIRED.

## 2026-10-31 — Radar-assisted evidence review and isolated contract tests

**Decision:** GO for a minimal **read-only AG-UI status-projection design** in a separate sandbox, **NO-GO for full OpenBot runtime installation or any production integration**. This does not supersede the mandatory P0/P1 acceptance process.

### Evidence and source review
- Registry reused: `GEN1_AUTONOMOUS_TECH_RADAR_50_SOURCE_REGISTRY_2026-10-28.md` (GitHub Trending, PyPI, Privacy Guides, AG-UI official schema, and upstream repository code/README/license; no global install or 50-source scan).
- CopilotKit/OpenBot (MIT; beta): upstream README, `docs/architecture.md`, `docs/coworkers.md`, `docs/deployment.md` inspected. Runs Bun 1.4+, Docker/PostgreSQL, CopilotKit Intelligence and model credentials; the whole platform's published minimum is **4 GB disk**, **2 GB RAM** for one bot; recommended **8 GB disk**, **4 GB RAM**. `OPENBOT_SINGLE_USER=true` is admin-style demo access, not an acceptable multiuser production policy. The platform also refuses that mode when public-facing configured URLs are detected. Verify identity and licensing before use.
- regnull/openbot (MIT): useful actor/inbox/handoff/HITL patterns, but `run_shell` is explicitly *not sandboxed* and there is no packaged Windows build in the inspected README. Extract patterns only.
- meetopenbot/openbot (MIT through v0.5.3): lightweight SSE/state API, but README describes archived code/no newer work published; maintainability and security are **UNKNOWN**, so avoid adopting its runtime. A reference for event contracts only.
- nightly-labs/openbot (PolyForm Noncommercial 1.0.0): development preview with `danger-full-access` and `approvalPolicy: never`; **REJECT executable commercial integration** unless separate license/security review.
- AG-UI 1.0 sources: https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/spec/1.0/schema.mdx and https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/spec/1.0/basic/index.mdx. Delivery order, not event timestamp, is authoritative. Projections must not forward `rawEvent`, untrusted metadata, `TOOL_CALL_*` events or snapshots.

### Tests performed (not Hermes runtime)
- Synthetic local reference prototype: Python **3.13.5 on Linux**, stdlib `sqlite3` only; **36/36 unit tests PASS**, compileall PASS. Source, executable tests, output, hashes and instructions distributed separately in `Hermes_OpenBot_AGUI_Preflight_20261031.zip` in the conversation.
- Coverage: restricted AG-UI display event shapes, SSE serialization, idempotent replay after simulated process reopen, tenant/thread separation, status transitions, explicit REVIEW_REQUIRED pause, UNKNOWN emits generic RUN_ERROR and blocks retries, duplicate-key collision including cross-thread replay, rollback, invalid IDs, untrusted input/metadata, tool events, payload and protocol version blocking.
- This is a **minimal AG-UI-subset producer**, not a full protocol-compliant consumer. It does **not** connect to Hermes, CopilotKit/OpenBot, or actual SSE network endpoints. It does not perform real reconnect tests or prove that real Hermes tool calls are blocked. It contains no OpenBot license or business credentials.
- Evidence classifications: upstream license/spec = VERIFIED_SOURCE; 36 offline prototype tests = TESTED_SYNTHETIC; Hermes/OpenBot interoperability, native Windows, authentic restore/DR, same-SHA hosted CI, performance/cost and independent acceptance = **NOT_VERIFIED**.

### Gate-first development decision (only if evidence progresses)
1. **P0:** Independent review of source and fixture SHA; confirm host disk headroom, genuine Windows process/port/state/backup inventory before installing anything. Existing low disk headroom remains a no-install blocker until verified resolved.
2. **P1A:** Wire the minimal producer to **existing read-only Hermes status events** within a sandbox with no new dependency. Validate output against the official AG-UI JSON schema. Preserve Hermes Guarded Runtime as sole tool authority.
3. **P1B:** If P1A passes, run real isolated HTTP/SSE reconnect, malformed/misordered event, cross-tenant access, SSRF, forged-approval, ESTOP, concurrency, SQLite rollback and crash-replay tests. Need independently reviewed negative cases and genuine Windows native evidence.
4. **P1C:** Compare minimal AG-UI producer versus current Hermes UI/event route on the *same representative workload*, >=3 repetitions, error rate, p95 latency, memory/disk, and fully burdened cost/successful task. A/B uplift >20% is a *proposal condition*, not acceptance by itself. Document rollback.
5. **Decision:** Only after independent verifier, passing same-SHA CI, P0/P1 A01-A17 acceptance and explicit HITL approval could an actual OpenBot component be adopted. Otherwise keep the minimal existing Hermes stack. No full platform until a concrete unmet capability justifies memory/disk/licensing cost.

**No changes** to `pyproject.toml`, `uv.lock`, existing agents, tool permissions, live services, secrets, production or CI workflows. No merge, deploy or duplicate PR.

Release seal unchanged: `PRODUCTION=HOLD; G0/G-CODE/G1=NO-GO; HITL=REQUIRED`.

## Post-acceptance development candidates — universal agent architecture checklist (2026-10-31)

**Disposition: DEFERRED_AFTER_TESTS / NOT_EXECUTED.** The owner-supplied educational anatomy diagram (input/perception -> reasoning/planning -> memory -> guarded action -> observe/feedback) is an **architecture checklist**, not a reason to rebuild Hermes. Reuse the preexisting Supervisor/Router, one deterministic Guarded Runtime, Verifier, SQLite checkpoints and existing audit. The picture does not establish a security boundary, working backend, or acceptance evidence.

| Existing concern / possible gap to verify | Smallest possible improvement *only if the real tests expose a gap* | Preconditions / pass criterion |
| --- | --- | --- |
| Ingress/perception provenance, untrusted events | Validate per-channel schema, source identity, data classification and prompt-injection boundaries before creating planner state; ensure traceable original source IDs (especially TradeDocs LC/BL and shipment updates). | Synthetic malformed/forged payload negative tests, then representative approved/redacted fixtures; no unreviewed PII export. |
| Planner termination and action authority | Keep finite task/step/cost budgets and deterministic stop condition, with policy gate run immediately before each side effect; never let a model, AG-UI or tool output bypass approval. | ESTOP, allowlist, HITL forged approval, timeout, token-limit and direct-answer/no-tool tests on actual guarded dispatcher. |
| Durable memory and replay | Verify that only approved facts are persisted, tenant/channel reads are isolated, unknown side effects cannot be replayed automatically, and intent + effect receipts have stable idempotency keys. | Native SQLite restore/rollback/concurrency/crash restart with replay and cross-tenant tests; audit never stores raw chain-of-thought or secrets. |
| Verification, feedback and observability | Make independent Verifier result and redacted trace/cost per successful task visible in existing dashboard; prevent unverified model output automatically becoming trusted long-term memory or an external action. | Reproducible evidence with fail-closed negative cases, trace correlation, p95 latency, error rate, cost/task and rollback; no external telemetry by default. |
| Optional OpenBot AG-UI status projection | If existing UI fails a measured requirement, adapt existing read-only Hermes state events to AG-UI 1.0 display-only subset without new runtime or duplicate guardrails. | Full schema/transport validation, SSE reconnect ordering and access tests, Windows resource check, same-host A/B and explicit approval. |

**Sequencing:** (1) finish P0 disk/backup/restore, authentic Windows local inventory and isolation; (2) complete same-SHA CI and independent A01-A17 P0/P1 acceptance; (3) only then classify the above into **NEEDED / ALREADY_COVERED / REJECT** from test evidence; (4) implement only approved smallest changes on an existing non-production branch with rollback and fresh targeted tests; (5) return to independent review before any release decision. Research/documentation is not a test pass. The prior **36/36 synthetic AG-UI prototype tests are not Hermes interoperability or Windows acceptance**.

**Portfolio alignment:** mapped to the existing P0/P1 work packages and RAD-01, not an additional WP/ID/agent/project/PR or automatic job. No cache/vector database/LangGraph/OpenBot full platform unless a real gap and independent A/B justify new dependency. `PRODUCTION=HOLD; G0/G-CODE/G1=NO-GO; HITL=REQUIRED`.
