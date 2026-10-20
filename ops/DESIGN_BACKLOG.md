# Hermes design backlog — not implementation

Status: **DESIGN_ONLY**. Owner-side roadmap for a fork, not an upstream feature proposal or permission to auto-install.

## Priorities and anti-duplication rule

1. **P0 — truth before changes:** inspect the real local state, review upstream differences, take restricted backup and pass a separate restore test.
2. **P1 — safe and provable execution:** fail-closed tool guards, secret isolation, immutable evidence, budget hard stops, reliability/recovery with `UNKNOWN` reconciliation, Acceptance & Evidence Engine.
3. **P2 — existing-component integration:** approved MCP/API integrations, per-source provenance, event ledger and economical model routing. Prefer shipped Hermes skill/plugin/cron primitives. Do not add a new core tool when a skill or plugin suffices.
4. **P3 — commercial opportunities:** TradeDocs AI, Shipment Intelligence, ExportLead AI, Procurement Copilot, WhatsApp Sales Agent; validate demand/competition/revenue evidence before investment.
5. **P4 — controlled improvement:** simulation, bounded self-improvement, reliability resilience, ongoing evals; no autonomy without measured acceptance and approval.

## Proposed reusable project operating model

`Structured project state (digital twin) → Observer → Verifier → Predictor → Economist → Risk → Planner → Executor → Auditor → Actual outcome → Learning`.

These are **logical roles** and can be functions or fixed workflows. Do not create nine independent LLM agents by default. Separate raw immutable source records from derived judgments; track confidence and provenance at field level. Sensitive outward effects require human approval.

## Candidate libraries, not approved dependencies

| Capability | Candidate references | Evaluation criteria |
|---|---|---|
| Skill engineering | Agent Skills, Codebase Memory, Superdesign Skill | license, prompt-injection exposure, tests, fit with built-in Hermes skills |
| Source research | Semantic Scholar, DOAJ, Unpaywall, Elicit, Consensus, Defuddle, Agent Reach | source rights, accessible API, attribution, rate limits, reliability |
| AI/agent quality | Braintrust, iFixAi, test fixtures, red-team playbooks | measurable acceptance, cost, provenance, rollback |
| Developer tooling | Aider, Codex, Cursor, Windsurf, GitHub Copilot | redundancy vs existing tools, supported connectors, human control |
| UI engineering | Superdesign, UI Layouts, Motion Primitives, Canvas UI | accessibility, RTL, performance, licensing |
| Market radar | Acquire.com, Microns, Flippa, Product Hunt, Indie Hackers, G2, Capterra, TrustMRR, GitHub Trending | revenue/demand evidence, legal permitted access, freshness |
| Work/persistent workflows | Hermes built-in cron/skills/plugins, Gmail/Drive/Calendar integrations | idempotency, scope, rate limit, approval boundary |

No automatic harvesting or scraping against service terms; credentials never enter logs. Unverified URLs/repositories are **discovery leads**, not endorsed.

## Resource intake schema

Fields: `name, canonical_url, domain, category, use_case, phase, status, source_checked_at, license, api_mcp, privacy_risk, security_risk, expected_cost, evidence_link, owner, next_action`.

Statuses: `DISCOVERED → SOURCE_VERIFIED → SECURITY_REVIEWED → SANDBOX_TESTED → APPROVED → ENABLED`. Disallowed jumps: discovery → enabled, or sandbox test → production without approval.

## Decision prompts for each new tool

- Which **measured bottleneck** does this remove?
- What shipped Hermes capability already solves it?
- What are the strongest contrary findings or simpler alternatives?
- Which data, scopes, secrets, financial charges and outbound effects can this component access?
- What is the smallest isolated experiment, objective acceptance threshold, and cost cap?
- What proves the result **worked** externally (not just a model saying "done")?

## Explicitly deferred

- Broad multi-agent organization, arbitrary tools/skills installation, autonomous purchasing/marketing/publishing, production self-modifying code.
- OpenHands until credible Docker/remote isolation; Odysseus only after independent architecture/license comparison; Tier-1 iFixAi only as an evaluated candidate.
- Automated shipment or CRM outbound updates until provenance, idempotency and approvals are validated.

## Outcome ledger

For each experiment record `hypothesis | baseline | accepted change | observed outcome | cost | evidence | final decision`. A report is not a validated integration.

## Mandatory constraint

Nothing in this file authorizes changes to the owner's Windows machine, credentials, live GitHub `main`, customer systems, payments, emails or deployments.
