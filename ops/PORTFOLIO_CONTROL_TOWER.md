# Hermes Portfolio Control Tower — October 18, 2026

**REVIEW ONLY — NOT PRODUCTION READY.**

This is a **portfolio overlay**, not a second engineering task queue. The only canonical 32 engineering task IDs remain in [MASTER_IMPLEMENTATION_MATRIX.csv](./MASTER_IMPLEMENTATION_MATRIX.csv); acceptance rules remain in [READINESS_DECISION_POLICY.md](./READINESS_DECISION_POLICY.md). Windows P0/P1 formal gates remain UNVERIFIED/HOLD.

## Seven linked programs

| Program | Reuse rather than duplicate | Gate / next decision |
|---|---|---|
| A. Hermes Core & Security | P0/P1 (18 canonical tasks), draft PRs #4/#5/#7 | Local read-only inventory; encrypted custody; **functional isolated restore**, fail-closed, budget |
| B. Hermes Cloud & Bridge | Draft PR #8; cloud local V3; separate Hermes Bridge v0.4 | VM/Gemini/Gateway **NOT DEPLOYED**; preview Terraform/IAM/cost, do not apply; Bridge not integrated |
| C. Trade / Maritime Intelligence | Draft PR #1 and P3-03 | BL/HBL, carrier events, AIS, ETA/confidence; **never infer container state from AIS alone** |
| D. GCC Revenue & SaaS | Draft PRs #6/#9, P3-01/P3-02/P3-04 | Procurement/Supplier Intelligence → Shipment → ExportLead; Saudi/UAE; available startup capital up to $1,000 is **not authorized spend** |
| E. Viral Kit / CRM / Content | Reuse P1 evidence/permissions before autonomous tools | Scope real version and tests, no outbound messages/publishing without separate approval |
| F. Agent / Workflow Research Radar | Draft PRs #6/#9 and P1-06 | Single source registry: trace → verify → dedupe → benchmark → adopt/reject |
| G. Quant / Trading Research | Isolated research only | Simulation; no brokerage, live trading, or real money |

## No duplicate initiatives

- **#4** owns readiness tasks and approval truth.
- **#5** supplies an evidence-validator *candidate*, not production proof.
- **#6 and #9** must be deduplicated into one research/evidence view before any integration.
- **#8** is a cloud-design draft; its offline tests do not prove Google Cloud deployment.
- **#1** is a TradeOps design/prototype, not a live shipping deployment.
- **#2 and #3** are optional/deferred specialist reviews.
- **#7** is a candidate read-only preflight, not evidence of a Windows run.
- Keep all these PRs in **Draft**; no main merge or runtime changes by this plan.

## Decision sequence

1. **P0:** inspect true Windows checkout/dirty state → encrypted backup/off-device custody → functional isolated restore → least privilege, timeout/empty/malformed/network DENY, leak canary, hard $0 spend baseline.
2. **P1:** durable pre-action intent → PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN and no blind retry → bound approvals → progress watchdog → trustworthy evidence and red-team tests → independent go/no-go.
3. **P2:** data/provenance, scoped MCP/tools, model routing and events only when measured.
4. **P3:** customer problem validation and tightly gated Trade/Revenue/Viral pilots.
5. **P4:** resilience/counterfactuals/self-improvement behind regression and approval gates.

**Safe independent parallel work now:** public research and market qualification; design-only shipment source schema; Cloud Terraform plan review; tool/source radar dedup. **Blocked:** Windows mutation without secure audit/restore, paid Google resources without scoped cost approval, secrets into public GitHub, public Gateway, outbound messaging/publishing/trades.

## Working operating model

Observe → Verify → Predict → Economics → Risk → Plan → Human Approval → Sandbox/Execute → Audit → Learn. These are logical responsibilities under **Hermes Core**, not authorization for a competing free-form multi-agent OS.

New ideas go to an INBOX, are deduplicated against a canonical task ID/PR, receive dependencies + measurable evidence, then move through DESIGN_ONLY → IMPLEMENTED → TESTED → VERIFIED. Runtime UNKNOWN means stop and reconcile, **never automatically retry an uncertain external effect**. Product income claims require observed receipts/outcomes, not forecasts.

The full Arabic portfolio handbook and spreadsheet are exported as a separate review package outside the public repo; **do not upload private paths, log contents, keys, customer data, backup archives or Terraform state to GitHub**.

## Product Hunt October 2026 — research-only mapping

**Snapshot date: 2026-10-18; non-authoritative for final monthly positions.** The requested [monthly leaderboard](https://www.producthunt.com/leaderboard/monthly/2026/10) was not directly retrievable in the review environment. Candidates below were cross-checked against individual Product Hunt product pages and [official week-42 leaderboard](https://www.producthunt.com/leaderboard/weekly/2026/42). No votes, reviews, followers, or positions prove revenue, product-market fit, enterprise readiness, or GCC buyer demand.

This is a **source-intake overlay** to the 32 canonical task IDs in `MASTER_IMPLEMENTATION_MATRIX.csv`, **not** a new task queue or dependency change. Do not install any candidate based on Product Hunt publicity.

| Candidate | Existing problem / portfolio track | Existing task IDs | Phase decision | Source |
|---|---|---|---|---|
| Pancake | ExportLead / sales GTM infra reference | P3-02, P3-04 | Research-only; no sending | https://www.producthunt.com/products/pancake-6 |
| ReSO AI | GCC generative-search visibility hypothesis | P3-01, P3-02 | Research-only; validate paid demand | https://www.producthunt.com/products/reso |
| Formalini | TradeDocs / document data extraction | P3-01, P2-02 | Sanitized-data validation candidate | https://www.producthunt.com/products/formalini |
| GenPage 3.0 | Landing-page experiment for marketing/Viral Kit | P3-02 | Research-only; no ad spend | https://www.producthunt.com/products/genpage |
| Articos MCP | Simulated buyer messages | P3-01, P3-02 | Advisory only; never substitute actual interviews | https://www.producthunt.com/products/articos |
| Navige | Hard budget/kill switch/reference for orchestration | P0-07, P2-04 | Security evaluation later; no agent proxy | https://www.producthunt.com/products/navige |
| Inferock | Independent call-cost receipts and observability | P1-05, P2-05 | Design reference, not validated integration | https://www.producthunt.com/products/inferock |
| Harness by Autonomous | Multi-device coding-agent control | P2-03, P1-03 | Security review later; no remote-control deploy | https://www.producthunt.com/products/harness-by-autonomous |
| IrisGo | Watch-and-learn workflow UX | P2-03, P3-05 | UX benchmark only; preserve existing Hermes core | https://www.producthunt.com/products/irisgo-public-beta |
| OpenSwarm | Parallel agent operating environment | P4-03, P1-09 | Deferred; no company-OS replacement | https://www.producthunt.com/products/openswarm-3 |
| Polylane | Proposed PR and incident-risk evidence | P1-05, P4-02 | Optional review only | https://www.producthunt.com/products/polylane |
| Spira Maxima | Creative/video content signal | P3-01, P3-02 | Later research; no autopublish | https://www.producthunt.com/products/spira-ai |

**Commercial acceptance rule:** Each candidate needs a real buyer-problem hypothesis, validated source/legal right, cost and privacy review, and actual customer evidence (interviews, verified pain points, or payment intent) before it can enter a project-specific pilot. Track forecasts separately from actual revenue and reject purely vote-based scoring. All sensitive customer information stays out of this public repository.

**No-go remains unchanged:** All P0/P1 runtime gates UNVERIFIED, `PRODUCTION_READY=NO`. `main` remains untouched, and this PR remains Draft. Maintain the existing active weekly research radar rather than creating duplicate automations.
