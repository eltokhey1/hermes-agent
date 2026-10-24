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


## 2026-10-24 — Made With Models revenue-evidence expansion

**Status: RESEARCH_ONLY / DEFERRED. Owner-directed research registration, not an implementation order.** This is a subordinate annex to the existing canonical RAD-01 / MKT-01 commercial radar, not a new tracker, a duplicate agent platform, or a change to the historical 16 streams / 45 packages / 120 mapped IDs. Reconcile with PR #9's \`ops/portfolio/PROJECT_REGISTER.md\` at review before any merge. Existing initiative names remain stable.

### Five revenue hypotheses (not predictions; not five new repositories)

| Priority for *research* | Product hypothesis | Narrow first paying customer | Smallest paid problem | Reference evidence class | Pilot order |
|---|---|---|---|---|---|
| 1 | Shipment Intelligence (existing IDEA-003 / SHP-02) | Food importers & forwarders | Exception alerts on verified booking/BL/container ETA changes; reconcile email and native events | Logistics *cost savings*, not proven SaaS MRR | First **candidate** pilot, subject to unified-plan prioritisation |
| 2 | TradeDocs AI (existing IDEA-001) | SME import/export operators | Human-reviewed commercial invoice/packing list/BL consistency report with page-field citations | Document copilots with revenue are *adjacent*, not validation of trade-compliance demand | Second candidate |
| 3 | ExportLead AI (existing IDEA-002) | Citrus, onion and frozen-food exporters | 10 source-backed, legally sourced qualified buyer dossiers per account | B2B lead-gen subscriptions have processor-verified comparables | Paid concierge validation before software |
| 4 | WhatsApp B2B Sales Agent (provisional, no canonical ID until register reconciliation) | Food wholesalers | Approved price-quote drafts and order intake from current catalog | Support agent subscription comparables; WhatsApp inventory award is *prize, not MRR* | After core and approvals |
| 5 | Export AEO / AI Search Visibility (provisional, no canonical ID until register reconciliation) | Exporters/manufacturers/industrial suppliers | Repeated, source-linked AI-search visibility audit and changes | Verified revenue comparables; agency revenue and SaaS MRR must stay separate | Last exploratory lane |

**Do not silently override PR #9's earlier TradeDocs-first validation ordering.** The Shipment-first order above is an updated proposed operational pilot sequence because synthetic shipment fixtures already exist in PR #10; requires reconciliation in canonical register/owner review. These ideas are hypotheses. Minimum economic arithmetic for \$1,000,000 annual recurring revenue is \$83,333.33 monthly; never equate ARR with net profit or assume zero churn. Indicative *test only* price/customer scenarios: Shipment \$699 × 120 clients × 12 = \$1,006,560; TradeDocs \$799 × 105 × 12 = \$1,006,740; ExportLead \$499 × 168 × 12 = \$1,005,984; WhatsApp \$399 × 210 × 12 = \$1,005,480; AEO \$999 × 84 × 12 = \$1,006,992. No price point has been validated by paying customers.

### Source directory — provenance and licensing

1. **Financial evidence / discovery:** https://madewithmodels.com/money/ (receipt-grade labels and capture dates); https://trustmrr.com/ (payment-linked benchmarks where actually verified); https://acquire.com/ ; https://www.microns.io/ . Never conflate processor-verified MRR with seller claims, savings, a one-off sale, ARR, investment or prize.
2. **Demand and competitors:** https://www.producthunt.com/ ; https://www.indiehackers.com/ ; https://www.g2.com/ ; https://www.capterra.com/ ; https://www.reddit.com/r/SaaS/ ; https://github.com/trending ; https://www.ycombinator.com/companies . These suggest ideas; reviews and launch popularity are not validation of willingness to pay.
3. **Domain specifications:** https://dcsa.org/standards/track-and-trace (canonical event vocabulary); https://developer.maersk.com/api-catalogue/maersk-visibility-studio (carrier API); https://api-portal.cma-cgm.com/ (carrier API); https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview (Microsoft Graph); https://learn.microsoft.com/en-us/exchange/permissions-exo/application-rbac (Exchange application mailbox scoping); https://developers.facebook.com/docs/whatsapp/ (WhatsApp Business Platform); https://developers.google.com/search/docs/appearance/ai-features (Google AI-search visibility guidance). A docs URL is **not** proof of commercial API entitlement, pricing, live coverage or connector installation.
4. **Skills format / candidate libraries:** https://agentskills.io/ ; https://github.com/agentskills/agentskills ; https://github.com/anthropics/skills ; https://github.com/mattpocock/skills . Audit license, current version, dependencies, prompts and executable scripts before adoption. Never call a repository "installed" merely because linked.

**Dated receipt examples recorded on 2026-10-24:** traxy.ai \$48,261 processor-verified MRR and MimikFlow \$9,918 processor-verified MRR (adjacent to ExportLead); Adelante \$17,837 processor-verified MRR (adjacent to service automation); Rank Prompt \$45,976 processor-verified MRR (adjacent to AEO); AEO Engine \$131,614 processor-verified MRR is described as an AI SEO **agency**, not necessarily SaaS license MRR; Atlas \$25,749 processor-verified MRR is a study copilot, not a TradeDocs competitor; Formula Bot \$26,000 *reported* monthly revenue is maker claim; TradeWeave \$70,000/year is *claimed software saving*, not product sales; TRAMA \$50,000 is an XPRIZE award, not recurring customer revenue. Each future evidence record must include exact receipt URL, maker, product, original label, verified/source class, snapshot date, currency, periodicity, expense exclusions, and independent corroboration status. Recheck figures before presenting or ranking; receipt updates may change them.

### Minimal execution tools, existing-first

- **Core / first-choice:** existing Hermes repo and control gates; Python stdlib, SQLite, existing tests and offline synthetic fixtures; current Aider CLI + local Ollama models where proven. Reuse existing code paths (not a new framework), avoid extra dependencies.
- **Only after P2 integration security verification:** FastAPI only if an HTTP boundary is required; PostgreSQL only with concurrent multi-tenant load; Microsoft Graph \`Mail.Read\` with Exchange RBAC application scopes or appropriately constrained delegated read access; DCSA-aligned carrier adapters with provider event IDs, native timestamps and source provenance.
- **Only if demonstrably required:** n8n for multi-source visual workflows, LangGraph for checkpointed multi-step orchestration (not for simple jobs), Supabase for multi-tenant Auth/DB, external model APIs for failure cases approved by owner, paid market intelligence or CRM sources after license and ROI review.
- **Prohibited shortcuts:** unapproved scraping/bulk messaging, outbound sends without Prepare→Approve→Send, inferring equipment ETA from AIS alone, accepting user-provided PDF text as instructions, exposing mailbox/body/attachments to cloud without permission, implicit subscriptions or unbounded token/spend.

### Agent and skill role map (design candidates — NOT installed)

Use **one governed Hermes core**, not a swarm:
- \`Opportunity Researcher\`: \`opportunity-intake\` — discover ideas, identify ICP/pain/source URLs; read-only metadata intake.
- \`Evidence Analyst\`: \`revenue-evidence-grade\` — classify Stripe/RevenueCat vs documented vs seller claim vs prize/savings, distinguish MRR/ARR/cumulative figures, prevent duplicate cases.
- \`Unit-Economics Analyst\`: \`saas-economics\` — price scenarios, gross margin after per-tenant API, churn sensitivity, CAC/payback, \`$0\` default spend budget.
- \`Domain Worker\`: \`trade-document-diff\`, \`shipment-event-provenance\` — smallest offline deterministic transforms; trace every extracted field and ETA event.
- \`Independent Verifier\`: \`source-and-acceptance-review\` — negative/fail-closed tests, unsupported claims audit, signed-off acceptance evidence.
- \`Commercial Validation\`: \`buyer-interview-pilot\` — consent-based interview scripts, pilot offers and real purchase signals; no automated outreach or publication.
- \`Supervisor/Router\` routes bounded tasks, but **deterministic Policy Gate** owns permissions and \`Executor\` requires human approval for consequential changes; no agent may self-approve.

Candidate SKILL.md packs must follow https://agentskills.io/specification (name/description frontmatter and optional scripts/references), carry reproducible offline tests, license/security review and ownership, and be added only after existing skills are checked for reuse.

### Opportunity record minimum schema

\`id, existing_portfolio_ref, hypothesis, customer, pain, workflow, alternative, pricing_assumption, target_market, comparable_product, evidence_url, evidence_type, metric_kind, metric_amount, currency, as_of_date, independent_verification, build_scope, required_integrations, terms_and_license, sensitive_data, dependency_gate, confidence, next_validation, experiment_cost_cap, decision, status\`.

Deduplicate by \`(source_url, product, metric_kind, as_of_date)\`. Maintain immutable source pointers and change history; unknown/missing data must remain \`UNKNOWN\`, never inferred. Formulaic opportunity ranking is advisory only, not a budget approval.

### Deferred execution order and acceptance gates

1. **NOW: DESIGN_ONLY:** preserve the unified command center and priority queue; record the five hypotheses and sources in existing \`RAD-01 / MKT-01\` without increasing canonical work-package counts or creating duplicate watches/PRs. No installs, scheduled scrapers, new mail access, external writes or paid calls.
2. **FIRST: finish Hermes unified plan and helpers:** prove owner Windows P0 encrypted + off-device backup, isolated functional restore, ACL isolation, fail-closed secrets/budget/ESTOP, then P1 durable ledger/UNKNOWN, independent P0/P1 evidence and policy-gate acceptance; finish approved P2 local worker/verifier skills and bounded integrations. \`PRODUCTION=HOLD\` until independent acceptance and owner release.
3. **THEN: P3 shadow validation:** ingest permitted public receipts read-only with immutable provenance, collect 10–20 customer interviews per shortlisted hypothesis with consent, score cost/risk/demand; test synthetic/offline fixtures. No sale/outbound automation by default.
4. **THEN: owner-approved paid pilot:** begin with **one** vertical and 1–3 design partners, require signed terms + lawful payment entity/provider + data-processing policy, price validation, measurable customer impact, negative security tests, spend cap and explicit owner approval. Expand to next vertical only after validated retention and measured contribution margin.
5. **P4 only if proven:** controlled improvements with canary/rollback and cost alerts, no autonomous promotions.

**Hard NO-GO remains:** no merge into \`main\`, live production deploy, changes to Windows runtime, Mail.Read permission grant, WhatsApp outbound messages, customer docs, purchases, or API token creation by this radar update. Research/backlog edit is not \`IMPLEMENTED\`, \`TESTED\`, or \`VERIFIED_IN_TARGET\`.
