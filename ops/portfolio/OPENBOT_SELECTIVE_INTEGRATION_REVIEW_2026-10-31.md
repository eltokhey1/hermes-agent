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
