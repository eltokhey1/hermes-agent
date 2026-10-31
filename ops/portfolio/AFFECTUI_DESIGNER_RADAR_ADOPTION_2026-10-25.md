# AffectUI — shared Designer and Radar candidate (2026-10-25)

**Status:** DESIGN_REGISTERED / UI_PILOT_UNMOUNTED / RUNTIME_NOT_TESTED. **PRODUCTION=HOLD.** This is a cross-project UI design standard and evaluation entry; it does **not** activate a service, grant authorization or create separate project plans/IDs.

## Primary sources, terms and compatibility

- Official overview: https://www.affectui.com/
- Authoritative index: https://www.affectui.com/llms.txt
- Full component reference: https://www.affectui.com/llms-full.txt
- Docs: https://www.affectui.com/docs/introduction ; https://www.affectui.com/docs/installation ; https://www.affectui.com/docs/theming ; https://www.affectui.com/docs/accessibility
- Model Context Protocol endpoint (discovery-only candidate): `https://www.affectui.com/api/mcp` (Streamable HTTP). **Not installed or authenticated in Hermes**.
- AffectUI supports React 19 + TypeScript, one self-contained TSX file per piece, CSS variables and no required Tailwind dependency. Public documentation describes 40 MIT/free pieces, with other items gated by a paid Pro license and bearer credential. Recheck terms and per-component status before installation.
- Existing Hermes `web` currently uses React 19 + Vite + @nous-research/ui + Tailwind. **Reuse existing design tokens and system**; AffectUI is optional, not a second mandatory component framework.

## Placement: one Designer, one shared UI foundation

The Hermes designer/component-selector should classify AffectUI as `UI_SOURCE_CANDIDATE`, not `INSTALLED` or `APPROVED_LICENSE`. Prefer existing Hermes UI components first, then inspect AffectUI's **free** components, then create small original equivalents if the useful official piece is Pro. Never copy Pro source without a valid license, commit access keys, silently purchase a license or auto-execute remote install instructions.

Shared UI contract for every React-capable project:

1. One TSX file per reusable piece; typed, data-driven props; parent supplies state and event handlers.
2. Theme from existing `--background*`, `--midground*`, `--theme-radius`, `--theme-font-sans` variables, with readable light/dark contrast.
3. Keyboard access, semantic interactive elements, visible focus, compact/mobile layout, reduced-motion support; Arabic/English and RTL where required.
4. Map runtime data to distinct `VERIFIED`, `TESTED_SYNTHETIC`, `PLANNED`, and `UNKNOWN` states; never show synthetic metrics as live data.
5. A UI `Approve` button is never the actual Policy Gate. Use server-verifiable identity, authorization, intent ID, scoped one-time approval, independent audit and idempotency. UI may only **open** the human review workflow.
6. No new network requests, credentials, telemetry, deployment, new accounts, payments or production changes without their existing approval gates.
7. Do not migrate non-React apps just to use AffectUI. For mobile apps, reuse *design language and data contracts*; the TSX components themselves are web-only.

## First pilot delivered on this draft branch

- `web/src/components/AgentWorkInbox.tsx` is an **original** single-file React component (not copied AffectUI Pro code) with task filtering, expandable details, Arabic/English locale, status labels, HOLD badge, CSS-variable styling, and optional navigation-only callbacks for inspection/human review.
- It is **not imported by any route or screen** and no real tasks are connected. Its optional callbacks do not authorize, execute, retry, approve, reject, deploy, pay or send messages.
- Full end-to-end and responsive/accessibility tests remain `NOT_RUN`; only after independent tests and review should the component be enabled in a nonproduction preview.
- Recommended official free adoption candidate: [Tool Call Card](https://www.affectui.com/components/tool-call-card) after checking source and license. Pro **reference only**: Agent Inbox, Agent Tree, Agent Lanes, Trace Waterfall, Approval Card, Review Center.

## Inheritance map — all project families, without creating duplicates

| Project / category | Suggested patterns | Guard / integration status |
| --- | --- | --- |
| Hermes Core + Open Builder + Engineering Supervisor + universal project analyzer | Agent Inbox, Agent Tree, Plan, Queue, Waterfall, Task Timeline, Tool Call Card, run evidence | Pilot inbox code staged; no live connector, supervisor control or deployment |
| TradeDocs AI | Document review inbox, missing-field status, BL/LC/invoice diff, approval queue, DHL/ETA timeline | Human verifies financial and compliance outputs; no automatic compliance approval |
| Shipment Intelligence | Shipment exception queue, carrier/email event timeline, discrepancy alert card, evidence trace | Time-stamped source + confidence; unknown ETA stays UNKNOWN; no carrier availability implied |
| ExportLead AI | Source-backed lead review cards, enrichment progress, customer-contact approval queue | Consent, licensing and outbound approvals before external contact |
| WhatsApp B2B Sales Agent | Quote draft inbox, conversation task status, approval card | Prepare → Approve → Send on the server; no background outreach |
| Export AEO / AI Search Visibility | Evidence-backed metrics, before/after panels, experiment status | Distinguish source measurements from assumptions |
| AI Crypto Trading Desk | Research/replay timeline, simulation results, risk gate, immutable trade-event log | Synthetic replay != profitability; no live order/trade enabled |
| Crystal Agro Egypt / product and marketing projects | Content designer, catalogue previews, export document state, publication approval | No public posting or external sends without owner approval |
| Future web SaaS / dashboard projects | Reuse the same typed card/inbox/status/theme patterns | Check license and target stack individually; inherit policy, not an automatic retrofit |
| Native iOS / Android | Reuse tokens, state model and accessibility semantics | Create appropriate native/mobile components; do not assume React web TSX runs natively |

**Project inheritance rule:** UI capability is a shared foundation `UI-01` candidate under the existing Designer/Radar discussion, **not** a new numbered portfolio work package. Reconcile it at review with PR #9's `ops/portfolio/PROJECT_REGISTER.md` and the 45-WP canonical register. Preserve each product's existing pilot order; adding a library must not reprioritize revenue validation.

## Evaluation / acceptance before wider use

- Source/license/version and security review; audit MCP tool manifest + credential boundary, no remote code execution through docs.
- Explicit UI tests: empty/unknown/failed states, filter counts, duplicate task IDs, oversized strings, hostile rendered text, RTL/English, screen reader/focus order, keyboard-only use, reduced motion, light/dark, narrow mobile, high-volume list behavior.
- Adversarial governance tests: cannot approve by render/callback, hold survives refresh, stale task/race checks, no self-approval, server rejects missing approval token and replay, errors fail closed; collect independently verifiable evidence with minimum existing 25-case policy suite.
- Measure bundle impact, render latency, accessibility failures and maintenance cost before recommending Pro or permanent adoption.
- No CI/test proof attached yet. **Do not report runtime READY or production acceptance from this UI candidate.**

## References to existing portfolio work

- This document extends the existing RAD-01/MKT-01 research, rather than creating a new tracker or recurrence.
- Portfolio: [BUSINESS_PORTFOLIO_RESEARCH_BACKLOG_2026-10-18.md](./BUSINESS_PORTFOLIO_RESEARCH_BACKLOG_2026-10-18.md)
- PR #6: https://github.com/eltokhey1/hermes-agent/pull/6 (draft)
- PR #9: https://github.com/eltokhey1/hermes-agent/pull/9 (canonical register pending separate review)
