# Hermes AI Business Portfolio — Design Backlog

**Recorded 2026-10-18. No changes to executable Hermes code. Design-only proposal, pending P0/P1 approval.**

## Governance and phase rules

- P0: verify actual local Windows state, non-destructive inventory, encrypted backup and a tested isolated restore, secret redaction, fail-closed policy tests, and a hard $0 cap.
- P1: durable intent; PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN; never auto-retry ambiguous external effects; independent acceptance/evidence audits; non-destructive watchdog and bounded retries.
- P2: source-specific licensed read integrations with provenance and time-stamped confidence.
- P3: commercial opportunity radar, 20 research dossiers, buyer interviews, optionally authorized paid pilots.
- P4: controlled resiliency, improvements and commercial workflows only after evidence and approval.
- This backlog grants no permission for installs, model-provider calls, data collection, contact, deployment, secrets handling, or spending.

## Twenty research reference projects

The following are **market research references**, not active coding work. Each is `UNDER_RESEARCH` pending buyer validation and source verification.

- HERMES-001: Chatbase
- HERMES-002: Rezi
- HERMES-003: Cometly
- HERMES-004: Comp AI
- HERMES-005: AEO Engine
- HERMES-006: GojiberryAI
- HERMES-007: SEOBOT
- HERMES-008: Postiz
- HERMES-009: LLM Gateway
- HERMES-010: AI B2B Lead Generation (Acquire listing)
- HERMES-011: AI Customer Support (Acquire listing)
- HERMES-012: AI Website Builder (Acquire listing)
- HERMES-013: AI Study Tool (Microns listing)
- HERMES-014: AI Motion Graphics Generator (Microns listing)
- HERMES-015: AI Landing Page Generator (Microns listing)
- HERMES-016: Desktop AI Financial Extraction (Microns listing)
- HERMES-017: AI Virtual Data Room (Microns listing)
- HERMES-018: AI Website Builder (Microns listing)
- HERMES-019: AI Video Automation Platform (Microns listing)
- HERMES-020: LandingAI Agentic Document Extraction

## Three commercial initiatives (separate from comparables)

1. **TradeDocs AI** — validate extract-and-compare workflow for invoice, packing list and bill of lading. Source-position citations, human review, 10 buyer interviews; no legal/customs autopilot.
2. **ExportLead AI** — validate licensed sources and human-approved buyer dossier workflow targeting Saudi Arabia/UAE; no bulk outbound or unauthorized scraping.
3. **Shipment Intelligence** — validate ETA/event discrepancy workflow; do not imply live carrier availability without signed licensed API access.

Each initiative remains `VALIDATION_BACKLOG`, **not** `IN_DEVELOPMENT`.

## Shared MCP and model adapter design

One read-only stdio MCP server initially, using JSON-RPC 2.0 and narrow JSON Schema tools. Optional Streamable HTTP only with server-side authentication and authorization. Read-only tool names: `portfolio.list_projects`, `portfolio.get_project`, `audit.get_fixture`, `audit.evaluate_plan`; advisory policy results **never** authorize action. Model-native adapters (OpenAI/Claude/Gemini/Ollama/OpenRouter) are planned **not verified**. Each needs separate tool-call, JSON, failure behavior, cost, residency and authorization tests. A model's ability to speak tool-calls is not equivalent to MCP compatibility.

For TrustMRR, prefer its official MCP service: https://trustmrr.com/mcp . For Startups.RIP, the public browse site https://startups.rip/browse may be researched; paid CLI described at https://startups.rip/cli requires a user-provided Pro credential. Do not invent an official Startups.RIP MCP endpoint.

## iFixAi candidate — independent acceptance and evidence

Reference: https://github.com/ifixai-ai/iFixAi . Apache-2.0 repository; upstream dependencies/version/commit must be pinned and inspected before installation. Turn telemetry off (`IFIXAI_TELEMETRY=0`, `DO_NOT_TRACK=1`); stage only synthetic input; protect complete prompts, checkpoints and scorecards. Real audits are not run and do not replace P0/P1 deterministic gate tests.

## Artifacts assembled separately, not committed to this repo

- Research dossiers for 20 comparables and 20 synthetic audit fixtures
- Evidence register deliberately marking project-level revenue claims unverified
- Separate business validation playbooks for 3 initiatives
- stdio MCP read-only prototype and 25 offline tests (environment-specific run, not production certification)
- Startups.RIP case-study reading list and hardening/readiness checklist

**Merge status:** This document is a proposal only. Human review before promotion to main or any changes to the running agent.
