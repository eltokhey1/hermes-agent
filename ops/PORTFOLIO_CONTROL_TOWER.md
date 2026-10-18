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