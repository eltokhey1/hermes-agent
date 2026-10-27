# Hermes AI Business Portfolio — Design Backlog

**Recorded 2026-10-18. No changes to executable Hermes code. Design-only proposal, pending P0/P1 approval.**

## Curated agent skills and plugins (2026-10-24)

See [30 Claude Code plugin/skill candidates with verified repository links and P0/P1 safety triage](./CLAUDE_CODE_30_SKILLS_PLUGIN_CANDIDATES_2026-10-24.md). This is a source/research register only: no installation, new canonical work packages, paid tools, runtime activation, or production readiness claim.

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

## 2026-10-24 — Enterprise AI architecture reference assessment

**Status: RESEARCH_ONLY / CANDIDATE_DEFERRED.** Prashant Rathi's *High-Level Architecture of an AI System* infographic is a useful coverage checklist, not a target blueprint or proof that any named product is installed, configured, licensed or deployed in Hermes. This assessment is based on repository evidence in this draft branch; absence of evidence remains `NOT_EVIDENCED`, not an implementation gap or authorization to build.

Evidence labels used below: **VERIFIED_PRESENT** means a current repository path or public Hermes document shows the capability; **PARTIAL** means Hermes has a narrower analogue but not the depicted enterprise service; **CANDIDATE_DEFERRED** means evaluate only after a measured need and the applicable gates; **NOT_EVIDENCED** means this review found no deployment proof.

| Infographic layer | Hermes / PR #6 assessment | Evidence-led disposition |
|---|---|---|
| Clients, gateway and orchestration | **VERIFIED_PRESENT / PARTIAL:** Hermes documents CLI, messaging gateway, desktop/TUI, provider routing, MCP integration, bounded tool execution and human approvals. The infographic's FastAPI microservice mesh, LangGraph/CrewAI orchestrator and Kong/Apigee-style gateway are **NOT_EVIDENCED**. | Reuse the existing narrow-waist core. LangGraph, FastAPI service decomposition and external API gateways remain **CANDIDATE_DEFERRED** until an eval or load boundary proves the simpler path insufficient. |
| Model, safety and routing | **VERIFIED_PRESENT / PARTIAL:** provider adapters (including OpenRouter support), provider routing, prompt caching, command approval, protected-path controls and secret/output redaction exist in repository documentation/code. A separate LiteLLM/OpenRouter gateway deployment, NeMo/Guardrails AI policy enforcement and a separate semantic cache are **NOT_EVIDENCED** by this review. | Preserve current controls and provider abstraction. A separate model gateway, named guardrail products and Redis caching remain **CANDIDATE_DEFERRED** with cost, privacy, cache-correctness and fail-closed tests. |
| Knowledge, RAG and memory | **VERIFIED_PRESENT / PARTIAL:** Hermes documents persistent memory and optional memory-provider plugins. A production hybrid RAG service, pgvector/vector database, graph database, reranker, search cluster and isolated document-ingestion pipeline are **NOT_EVIDENCED**. | Measure retrieval failures first. pgvector, rerankers, GraphRAG and document parsers remain **CANDIDATE_DEFERRED**; any future evaluation requires provenance, prompt-injection isolation and tenant-boundary tests. |
| Ingestion, data and events | **PARTIAL:** repository-backed state, cron and gateway mechanisms exist; the depicted Airbyte/Fivetran, Airflow/dbt, Kafka/Debezium and cloud object-store estate is **NOT_EVIDENCED**. | Keep PR #6 read-only, source-specific and licensed. Add connectors, queues or ETL only for a verified throughput/replay requirement and never treat source availability as permission. |
| Infrastructure and delivery | **PARTIAL:** Hermes supports local/container/remote execution options and CI assets, but AWS/Azure/GCP deployment, Kubernetes, serverless functions, ArgoCD and cloud IAM are **NOT_EVIDENCED** for the owner runtime. | All cloud, Kubernetes, serverless and GitOps choices remain **CANDIDATE_DEFERRED** pending target-state inventory, cost ceiling, threat model, rollback and explicit owner approval. |
| Observability, evaluation and governance | **PARTIAL:** repository logging, approval/audit-related paths, offline eval assets, security guidance and an optional OTLP export path exist. Enabled OpenTelemetry export, Langfuse/LangSmith, RAGAS/DeepEval release gates, SIEM and enterprise RBAC deployment are **NOT_EVIDENCED**. | First define redacted local evidence and success thresholds. Telemetry export and external eval vendors remain **CANDIDATE_DEFERRED**, opt-in only, with data-flow, retention, secrets and cost review. |

### Curated attributed source registry

| Registry ID | Source and attribution | Why retained / boundary |
|---|---|---|
| EA-REF-001 | Prashant Rathi, [*AI System Design: Beyond the Model*](https://www.linkedin.com/posts/prashantrathi1_enterpriseai-cloudarchitecture-genai-activity-7505974053275623425-glcc), LinkedIn; the attached image itself displays `Prashant Rathi @prashantrathi1`. | Verifiable source post associated with the supplied visual and matching its enterprise-layer claims. Retained as the only infographic attribution; copyright/originality beyond that association is not asserted, and the post is practitioner guidance rather than deployment evidence or a normative standard. |
| EA-CAN-001 | [Hermes Security](https://hermes-agent.nousresearch.com/docs/user-guide/security), [MCP integration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp), and [Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory). | Canonical public Hermes capability documentation; repository state remains authoritative for this branch. |
| EA-CAN-002 | [Model Context Protocol specification](https://modelcontextprotocol.io/specification/latest). | Canonical protocol reference for any future MCP contract; it does not grant tool permissions or prove server compatibility. |
| EA-CAN-003 | [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence). | Canonical design reference only; LangGraph remains **CANDIDATE_DEFERRED / NOT_EVIDENCED** in this owner runtime. |
| EA-CAN-004 | [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/). | Vendor-neutral observability reference only; export remains **CANDIDATE_DEFERRED**, opt-in and redaction-gated. |
| EA-CAN-005 | [OWASP LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/). | Security threat reference for retrieved content and tool-output boundaries; it supplements, never replaces, Hermes P0/P1 tests. |
| EA-CAN-006 | [FastAPI security](https://fastapi.tiangolo.com/tutorial/security/). | Canonical framework guidance if an HTTP boundary is later justified; FastAPI services remain **CANDIDATE_DEFERRED** here. |
| EA-CAN-007 | [pgvector](https://github.com/pgvector/pgvector). | Upstream project documentation for a possible PostgreSQL vector-search extension; adoption remains **CANDIDATE_DEFERRED** pending retrieval evals and operations review. |
| EA-CAN-008 | [RAGAS documentation](https://docs.ragas.io/). | Upstream evaluation reference; RAGAS remains **CANDIDATE_DEFERRED** and no score or release gate is claimed. |

### Gate retention

This reference adds no work ahead of the existing queue. **P0** still requires verified owner-state inventory, encrypted/off-device backup plus isolated restore, redaction, fail-closed policy/ESTOP tests and a hard `$0` cap. **P1** still requires durable intent/status, `UNKNOWN` handling for ambiguous effects, bounded retries and independent acceptance evidence. No technology named by the infographic or registry becomes `IMPLEMENTED`, `TESTED`, `INSTALLED`, `CONFIGURED` or `VERIFIED_IN_TARGET` without separate target-runtime evidence. The hard NO-GO above remains unchanged: no main merge, deployment, runtime/config/dependency change, secret or permission grant, external write, paid call or purchase is authorized by this annex.


## 2026-10-25 — AffectUI shared Designer/Radar UI candidate

**Status: DESIGN_REGISTERED / UI_PILOT_UNMOUNTED / RUNTIME_NOT_TESTED; PRODUCTION=HOLD.** Add [AffectUI](https://www.affectui.com/) and its [official LLM docs](https://www.affectui.com/llms.txt) as a reusable **Designer/component-source candidate** under the existing RAD-01/MKT-01 evaluation, not as a new product, schedule, dependency or auto-activated integration. Official MCP discovery endpoint: https://www.affectui.com/api/mcp — **NOT_CONNECTED**. Free components may be evaluated without buying Pro; Pro source requires license and may not be copied into the repository without authorization. Reuse existing React 19 / Nous UI / Hermes theme first.

The cross-project UI contract and project-by-project design map for Hermes/Open Builder, TradeDocs AI, Shipment Intelligence, ExportLead, WhatsApp B2B, AEO, Crypto Desk, Universal Analyzer, Crystal Agro and future projects are in [AFFECTUI_DESIGNER_RADAR_ADOPTION_2026-10-25.md](./AFFECTUI_DESIGNER_RADAR_ADOPTION_2026-10-25.md). An original, unmounted single-file React inbox pilot is staged at `web/src/components/AgentWorkInbox.tsx`. This changes neither runtime routes nor server-side HITL policy. Retain the portfolio IDs and current acceptance gates; reconcile PR #9 at review. No release, paid component installation, secrets, messages, production merge or change to the owner's Windows instance is authorized by this addition.

## 2026-10-26 — 13 viral AI tools and tips cross-project radar

**Status: RESEARCH_ONLY / DESIGN_REGISTERED / PRODUCTION=HOLD.** Owner-approved addition of the 13-image-item source register, independent 2026-10-26 official-link checks, original-vs-new-prompt provenance, cost/permission/accuracy controls, and a single cross-project reuse matrix: [VIRAL_AI_13_RADAR_GUIDE_2026-10-26.md](./VIRAL_AI_13_RADAR_GUIDE_2026-10-26.md). Covers Hermes/Open Builder/Designer, TradeDocs AI, Shipment Intelligence, Crystal Agro/ExportLead/AEO, Crypto Desk and optional shared learning/content references. Image claims are not automatically verified: its printed Oct-2024 date conflicts with documented 2026 releases. No new work-package IDs, duplicated project radar, installations, secrets, notifications, spending, external writes, main merge or runtime changes. **Production remains HOLD pending independently accepted gates.**

## 2026-10-26 — AI 50-tool discovery register + REA teaching/playbook

**Status: RESEARCH_REGISTERED / NOT_INSTALLED / PRODUCTION=HOLD.** Owner-provided fifty AI tools (10 video, 10 image, 8 automation, 7 coding, 7 LLM/writing, 8 audio/research) are now linked to the single shared RAD-01/MKT-01 portfolio, *not* verified as an actual top-50 ranking and not allocated fifty independent work packages. The [AI_50_TOOLS_REA_RESEARCH_2026-10-26.md](./AI_50_TOOLS_REA_RESEARCH_2026-10-26.md) annex includes direct supplied domains and official status/version corrections (including Sora discontinuation), REA `morluto/rea` official sources and 6.8.0 readiness/gating, 3-tool evaluation workflows, cross-project adoption, and a 30-minute teaching kit. Only authorized reverse-engineering targets; existing Hermes Windows/P0/P1 and HITL boundaries remain unchanged. No tool installs, external account connections, paid calls, runtime changes, publication, wallet actions, main merge or deployment. 


## 2026-10-26 — No-code and community discovery sources

**Status: SOURCE_REGISTERED / RESEARCH_ONLY / NOT_INSTALLED / PRODUCTION=HOLD.** Owner-approved addition to the existing shared RAD-01/MKT-01 research queue; do not create duplicate work packages or schedules.

| Source | URL | Priority | Intended evaluation | Trust boundary |
| --- | --- | --- | --- | --- |
| NoCode.Tech tools | https://www.nocode.tech/tools | HIGH | No-code/low-code app builders, automation, internal tools, customer portals; compare free tiers, API access, exportability and vendor lock-in | Directory listings are leads, not verified vendor capabilities |
| Stacker | https://stacker.ai/ | CONDITIONAL | Candidate internal/customer portal for TradeDocs AI and Shipment Intelligence; benchmark against existing React stack and deployment costs | Validate current official features, pricing, data permissions and portability before pilot |
| MakerPad tools | https://www.makerpad.co/tools | HIGH | AI-assisted app-building examples, workflows and coding-tool comparisons for Open Builder and Designer | Verify each product at official source; respect licenses and provenance |
| PHCorner popular today | https://phcorner.org/popular-today/ | LOW / CAUTION | Idea discovery only; independently verify anything promising | No forum downloads, cracked software, credentials, scripts, license bypasses or untrusted executables |

**Reusable learning contract:** Capture for each candidate: official URL, function, target project, free/paid licensing, integration/API/export, privacy/security risk, local compatibility, benchmark evidence, cost per successful task, and decision `REFERENCE_ONLY` / `SANDBOX_EVALUATION` / `REJECTED`. Share only reviewed findings with Hermes Supervisor, Open Builder, Designer, TradeDocs AI, Shipment Intelligence and Commercial Radar through the existing single-source backlog. Prioritize existing tools and zero-cost experiments. This entry does not establish that any tool was installed, agent knowledge synchronized, or provider integration tested. No external communications, purchases, new account links, production deployment, main merge, or permission changes. Keep P0/P1 acceptance and human approval gates intact.

## 2026-10-26 — Hermes Knowledge Stack (Obsidian + Hermes + MiniMax M3)

**State: UNDER_STUDY / IMPLEMENTATION_PREPARED / PILOT_NOT_EXECUTED / PRODUCTION=HOLD.** Register the user-requested Karpathy-style knowledge stack as a subordinate **shared knowledge-infrastructure candidate** in existing RAD-01 / MKT-01. See [Hermes Knowledge Stack study and implementation-ready pilot](./HERMES_KNOWLEDGE_STACK_OBSIDIAN_MINIMAX_M3_STUDY_2026-10-26.md). Source: [Mr. Buzzoni on X](https://x.com/Mr_Buzzoni/status/2066904909849440434); MiniMax official [M3 model release](https://www.minimax.io/blog/minimax-m3). Evaluate local Markdown/Obsidian as a versioned knowledge view; existing Hermes as a governed operator; M3 as an optional approved long-context candidate versus deterministic/local retrieval. Practitioner performance anecdotes are self-reported; full-context does **not** eliminate hallucinations. Scope: synthetic-only read-only offline pilot, proposed A/B/C benchmark and 25 adversarial cases, explicit provenance/diff/HITL gates and zero-cost default. No new commercial ID, work package, separate tracker/schedule, model key, paid API, cloud vault upload, Windows runtime change, merge, deploy or production acceptance. Reconcile canonical register PR #9 before any adoption.

## 2026-10-27 — Product discovery 50 × Vibe Coding 50 (Perplexity task pointer)

**Status: RESEARCH_REGISTERED / FULL_PERPLEXITY_OUTPUT_NOT_ACCESSIBLE / 50+50 INDEPENDENT CANDIDATE INVENTORY / NOT_INSTALLED / PRODUCTION=HOLD.** The [curated Product Discovery × Vibe Coding annex](./PRODUCT_DISCOVERY_VIBE_CODING_50X50_RADAR_2026-10-27.md) registers the owner-supplied [Perplexity Computer task](https://www.perplexity.ai/computer/tasks/1a37ff34-6347-448f-9113-a78af154dc72) and a separately researched list of 50 discovery channels plus 50 *candidate* free/open/freemium/adjacent development tools, with explicit primary-source and pricing gaps. It does **not** claim to reproduce the unavailable Perplexity response, verify that all 50 tools are genuinely no-cost, or promote them into execution. Existing RAD-01/MKT-01 and Designer/Hermes/TradeDocs/Shipment teams reuse the annex via one shared source, with license/cost/privacy/Windows 16GB/security testing and HITL gates. No new work packages, autonomous agent sync, schedules, installations, paid usage, secrets, publication, external actions, production activation or main merge.


## 2026-10-27 — Supervisor / Specialists / HITL / Observability architecture

**Status: VERIFIED_PRIMARY_SOURCES / DESIGN_ONLY / 25 ADVERSARIAL_TESTS_PLANNED_NOT_RUN / NO_NEW_RUNTIME / PRODUCTION=HOLD.** The [shared governed-agent orchestration and Physical AI safety reference](./SUPERVISOR_SPECIALISTS_HITL_OBSERVABILITY_REFERENCE_2026-10-27.md) records a single-supervisor, bounded-specialist, deterministic verifier, state/checkpoint, independent policy/HITL, executor and trace pattern for Hermes, Open Builder, TradeDocs AI, Shipment Intelligence, Designer and Radar. Compare existing Hermes implementation **first**; LangGraph/CrewAI/OpenAI Agents SDK/Microsoft Agent Framework/Mastra/Pydantic AI are contextual evaluation candidates, not approved installs. Physical AI (ROS 2/Isaac/LeRobot) is a separate research-only concept with independent robot safety interlocks and absolutely no motor commands from LLMs. Primary documentation links and 25 proposed adversarial tests are in the annex. No claim of autonomous knowledge synchronization, Windows test passes, hardware integration, production readiness or new revenue work packages. Approval gates, P0/P1 evidence and main merge HOLD persist.


## 2026-10-27 — User-supplied 200 AI sources/tools consolidated into RAD-01

**Status: 200_ROWS_CAPTURED / 10_CATEGORIES / USER_SUPPLIED_NOT_FULLY_VERIFIED / FREE_STATUS_UNKNOWN / DESIGN_ONLY / PRODUCTION=HOLD.** The [shared 200-entry AI discovery and tools inventory](./AI_200_SOURCE_TOOL_INVENTORY_AND_SCREENING_2026-10-27.md) records 20 directories and 180 additional tool/service/education/model/infrastructure entries supplied by the owner, with links and research triage, plus six supplemental GitHub-list names (two repo owners unresolved). This supplements, rather than duplicates or supersedes, the earlier [Product Discovery 50 × Vibe Coding 50](./PRODUCT_DISCOVERY_VIBE_CODING_50X50_RADAR_2026-10-27.md) and the [governed supervisor workflow](./SUPERVISOR_SPECIALISTS_HITL_OBSERVABILITY_REFERENCE_2026-10-27.md). **Do not report 300 unique tools** before canonicalization. Verified correction: Tome Slides officially sunset 2025-04-30; legacy CodeWhisperer folded into Amazon Q Developer 2024-04-30; PlayHT reported unavailable pending official confirmation. Most commercial/free limits unverified. Cross-project reference only for Hermes/Core, TradeDocs, Shipment Intelligence, Designer, Research/QA and Commercial Radar; not runtime agent memory sync. Zero installation, external write, paid use, publishing, scheduled work, main merge or production change; native safety acceptance pending.


## 2026-10-27 — Executed AI tool candidate screening (source + synthetic policy)

**Status: SOURCE_AUDIT_COMPLETED / EXACT_URL_DUPLICATES_RESOLVED_FOR_50_DIRECTORIES_VS_200_INPUT / SYNTHETIC_POLICY_25_OF_25_PASS_LINUX / REAL_TOOL_BENCHMARK_NOT_RUN / WINDOWS_NOT_VERIFIED / PRODUCTION=HOLD.** Published the [dated vendor documentation comparison, no-install shortlist decisions, exact URL dedup, reproducible offline policy-gate test results and real Windows A/B metric contract](./AI_TOOL_EVALUATION_SOURCE_AUDIT_AND_SYNTHETIC_GATE_2026-10-27.md). The [Node-only 25-case read-only test suite](./evals/candidate_gate.test.mjs) was executed in an isolated Linux Node 22.16 sandbox: 25 pass, 0 fail; **not** an Aider/model performance comparison, penetration test, actual Windows run or P0/P1 acceptance. Compared 50 earlier URL-bearing discovery rows with all 200 user-supplied rows; 10 normalized exact URL duplicates; 240 distinct URLs across those 250 links only (previous 50 name-only coding candidates excluded from URL comparison). Official vendor audit changes: Continue abandoned/read-only -> no new adoption; Langfuse multi-service -> defer on 16GB without benefit evidence; Recraft Free -> no commercial use; n8n SUL -> internal-only conditional; Activepieces MIT core -> sandbox research; MLflow SQLite -> conditional reference; ComfyUI CPU-only possible -> unbenchmarked. Default existing Aider+Ollama, existing logs + SQLite, no extra install or production deploy. Shared research reference for Supervisor, QA, TradeDocs, Shipment, Designer, Commercial Radar; no agent memory sync. **G0/G-CODE/G1=NO-GO; PR #6 remains draft.**

## 2026-10-27 — @ridark_eth GitHub 50 screened for shared learning

**Status: 50_SOURCE_ITEMS_REGISTERED / 15_REPOSITORY_METADATA_CHECKED / LICENSE_SPOT_CHECKS / PERFORMANCE_NOT_BENCHMARKED / NOT_INSTALLED / PRODUCTION=HOLD.** Owner-provided [@ridark_eth 50-repository post](https://x.com/ridark_eth/status/2057418685791220031?s=46) was indexed from a third-party cache because direct X access returned 403. Added [GitHub 50 shared learning and acceptance-gated candidate screen](./RIDARK_GITHUB_50_HERMES_SHARED_LEARNING_SCREEN_2026-10-27.md) to the existing RAD-01/MKT-01, without creating a separate tracker. Fifteen GitHub repository metadata checks completed; current AIHawk status contradicts archive claim in cached translation. Key practical study references: Docling/TradeDocs, Repomix/RTK coding-token hygiene, Crawl4AI/Firecrawl/Radar, MegaParse OCR challenger, n8n-MCP permission model, OpenHands coding challenger, optional CPU faster-whisper, while ClawRouter payments and API bypass sources are not approved. Shared teaching matrix covers Hermes Supervisor/QA, Open Builder/Designer, TradeDocs, Shipment Intelligence, Knowledge Stack and Radar. **No live agents retrained or synchronized, no Windows/head-to-head tests, installs, extra schedules, external actions, PR merge or deployment. G0/G-CODE/G1=NO-GO.**
