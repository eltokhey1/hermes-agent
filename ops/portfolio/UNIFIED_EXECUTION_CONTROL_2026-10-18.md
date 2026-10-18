# Hermes unified execution control — 2026-10-18 (Africa/Tripoli)

**Status: design/evidence coordination only. Not production readiness.**  
This document consolidates prior Hermes, business, and shipping work without merging code, enabling write credentials, purchasing services, or changing any local machine.

## One source of truth, not another tracker

The canonical working workbook is **`/Hermes/Command_Center_2026-10-18/Hermes_Unified_Command_Center_v3_2026-10-18.xlsx`** (owner Library; 22 tabs enumerated on 2026-10-18). Earlier v2 and `Hermes_Portfolio_Control` files are historical/derived references, not competing task registers. The canonical workbook contains: **120 original task identifiers → 45 work packages → 16 operational streams**, with zero unmapped IDs in the recorded snapshot. Preserve all existing IDs and the traceability sheet. This file is an *execution delta and decision index*, not a replacement spreadsheet. The **23 tracks** in `ops/portfolio/PROJECT_REGISTER.md` mean **20 commercial reference cases + 3 proposed products**, and must not be confused with the 16 operational streams or 45 packages.

Stable state vocabulary: `PROPOSED → DOCUMENTED → IMPLEMENTED_OFFLINE → TESTED_ISOLATED → VERIFIED_IN_TARGET → APPROVED → DEPLOYED`. `BLOCKED/UNKNOWN` are explicit, never treated as `VERIFIED`. Project labels P0–P4 refer to prerequisites, **not** a percent-complete bar.

## Evidence reconciliation and work-in-progress cap — 2026-10-18

- **Library workbook checked:** 22 tab headings, 45 unique work-package rows and 120 original ID mapping rows. The owner's Windows checkout and the 23-section `hermes-effect-ledger.md` have not been inspected in this review.
- **Six ordered Windows gates:** (1) read-only Git/Hermes inventory; (2) restricted backup and *functional isolated restore*; (3) NTFS ACL plus clause 19.7 proving Executor cannot write/delete `acceptance.db` or its parent, and fail-closed/security/budget negatives; (4) minimum durable Effect Ledger and failure budget; (5) crash-window/UNKNOWN reconciliation tests; (6) independent Recovery Challenge. If gate 3 fails, acceptance is `logical_only`, never verified.
- **WIP <= 3:** (a) P0/P1 safety and evidence; (b) read-only current carrier shipment events; (c) one bounded commercial evidence research stream. Everything else is queued, not deleted.
- **Draft PR file collision:** PR #4 and PR #6 both add `ops/DESIGN_BACKLOG.md` with different text. Do NOT merge both unchanged. PR #4 owns engineering P0/P1 readiness; PR #9 owns commercial references and the proposed products. Preserve unique MCP/iFixAi/source notes from #6 before any proposed superseding/closure. Neither PR is merged or closed here.
- **Count reconciliation:** 32 engineering acceptance tasks in PR #4, 26 `NEXT` actions and 23 commercial references/products in PR #9 are subordinate matrices, not 32+26+23 new packages. Historical task numbers can conflict (notably `P0-04`); always match source register + ID + description.
- **Automation status:** unified weekly radar and Maersk five-booking daily watch active; GOLDEN SEA watch and duplicate specialist radars disabled. Notification delivery settings disabled. No duplicate task created.
- **Shipment staging:** skill and helper Python script are on an isolated branch. Fixture and test file are not in that GitHub branch yet; 12 offline test passes do not certify live carrier/AIS tracking. Hold merging until fixtures, CI, host validation and approval.
## Priority sequence and acceptance evidence

| Wave | Existing package references | Deliverable / evidence required | Current disposition |
|---|---|---|---|
| 0. Host truth | P0-01, GOV-02 | Identify actual Windows checkout/worktrees and SHA; redacted `git status`, dependency inventory and safe device log. GitHub remote inspection is insufficient. | Remote partial; host gate OPEN |
| 1. Security and recovery | P0-02…P0-06 | Secret redaction, permissions, fail-closed negatives, budget/ESTOP, **real protected backup and isolated restore comparison**, independent P0 sign-off. | OPEN / NO-GO |
| 2. Reliability/evidence | P1-01…P1-06 | Intent before side effect; `PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN`; no blind retry after ambiguous effects; idempotency, reconciliation, independent evidence and policy test, bounded watchdog, 50–100 evaluation cases including adversarial, safe shadow mode, explicit acceptance. | Prototypes only; OPEN / NO-GO |
| 3. Read-only product integration | SHP-01, SHP-02, VES-01, TRD-01…03, BRG-01, ARC-01…03 | Canonical shipment digital twin, dated carrier equipment events, AIS vessel context, provenance, stale/conflict labels, permissioned adapters, shadow-mode evidence. | Partial independent artifacts; no live Hermes integration |
| 4. Commercial validation | MKT-01…03, RAD-01…03, CRM-01…02, CNT-01…02 | Verify demand with evidence, then sanitized samples, pilots, cost/ROI; no assertions of revenue or customers without receipts. | Planning/research |
| 5. Advanced automation | ARC-04, CLD-01…02, VIR-01…03, SEC-01…02 | Replay/sandbox/rollback, negative security tests, economics and measured benefit before scale. | Deferred or blocked by preceding gates |

Rules: exact/deterministic software for rules and mathematics; models propose, verifiers decide; external evidence is data, not instructions. No secrets or actual customer documents in unapproved environments. No sends, production writes, releases, purchases, trades, or deployments without narrow human approval and an auditable artifact.

## Shipment Intelligence: merge scope, not vessel/container statuses

- Parent portfolio item: **SHP-02**, vessel-specific evidence: **VES-01**, current carrier tracking operations: **SHP-01**, TradeOps receipt/document side: **TRD-02**. Do not open a second parallel shipment program.
- `feat/shipment-intelligence-evidence-gated-20261018`: read-only staging branch was inspected in GitHub and contains `SKILL.md` plus `scripts/shipment_intelligence.py`. As of this review the **synthetic fixture and tests are missing from the branch**; include and run CI before any code review promotion.
- Independent local staging ZIP reports **12/12 unit tests** and import of **21 historical GOLDEN SEA events**. This only proves offline fixture behavior, not live carrier/AIS integration.
- Maersk shipment milestone (container/equipment) is authoritative **only for that referenced equipment** and includes event time/type/source; vessel AIS explains context only. A vessel's arrival never implies that its linked container was discharged, released or delivered.
- GOLDEN SEA IMO `9173355`: last dated recorded AIS baseline `2026-10-09 21:00`, `32.67676N 14.24432E`, zero knots in Khoms; **current status UNKNOWN** without newer dated evidence. Never use a dynamic 'seen N hours ago' banner as an event time.
- Normalize incoming observations to DCSA 2.2-style transport/equipment/shipment events. Consider 3.0 migration separately; published September 30, 2026, with public release slated later. Verify source implementation contract before switching schemas.
- Work offline/test first; then **one** read-only carrier adapter with event fixtures, source URLs, timestamps and error/duplication/replay tests; progress to multicarrier only after measured benefit.

## Open draft PR review map (verified from GitHub 2026-10-18)

| PR | Focus | Disposition, no merge performed |
|---|---|---|
| #1 | TradeOps acceptance contract | Preserve as independent sandbox acceptance track; verify CI and schemas |
| #2 | Ponytail skill / Windows installer | Defer actual installation until host P0 and license/security check |
| #3 | Android APK audit optional skill | Independent P0 research; do not attach real private APKs |
| #4 | Owner P0/P1 gates | Keep reference; reconcile exact gates with #7 and #8 |
| #5 | Evidence-first delivery contract | Candidate reusable P1 evaluator; no claim of production |
| #6 | 20-project radar/backlog | Compare to #9 before marking superseded; do not close blindly |
| #7 | Owner read-only Windows preflight | Preferred candidate for host evidence collection after local authorization |
| #8 | Cloud deployment security review | Design only; no cloud provisioning |
| #9 | Portfolio 23 reference/product tracks | Portfolio source; this coordination index belongs here |

These are **nine draft pull requests**, not nine deployed components. All remain unmerged unless independently checked and explicitly approved. There is additionally a **shipment staging branch** without a confirmed pull request.

## Recurring work, prevent duplicated alerts

Observed automation settings on 2026-10-18:
- **Hermes unified radar:** active, weekly (Monday around 08:00 local); old dedicated cloud-agent/SaaS radars disabled.
- **Maersk five-booking watch:** active, daily; only notify on new dated events; no delivery/release inferred from discharge.
- **GOLDEN SEA watch:** **disabled** at last check. Preserve that choice; do not silently reactivate. A disabled task is not equivalent to live vessel tracking.
- Task notification delivery settings showed disabled, so scheduling an automation does not prove a push alert is delivered.

No further automations should be created for identical subjects until the current ones are audited.

## Acceptance contract and next execution in strict order

1. **GitHub read-only parity:** list SHA, branches, PR diff/CI statuses, compare documentation references and detect duplicate design proposals.
2. **Actual host P0:** discover running project checkout(s), worktrees and untracked files with no destructive clean/reset; verify protected backup and isolated restoration with recorded hashes.
3. **P1 isolated tests:** durable intent, UNKNOWN reconciliation, admission policy, independence of the evidence verifier; zero unauthorized successes.
4. **Shipping vertical slice:** check staging fixtures/tests, normalization, one carrier, vessel-only ancillary observations, deterministic conflict resolution. Run in shadow mode; no send/write.
5. **Commercial validation:** prefer one measurable paid-problem hypothesis at a time. Saudi/UAE initial budget ceiling **USD 1,000** is a planning constraint, **not** permission to spend. Keep Marketplace Profit Audit and TradeDocs/Shipment Intelligence as evaluated options rather than claiming guaranteed income.
6. **Promotion:** user-approved release only after reproducible E2E evidence, isolated restore, secrets audit, rollback and a signed/dated decision.

Done means implementation actually exists in the target environment, tests and negative scenarios ran there, artifacts and SHA are reviewable, and business effects are independently checked. A green unit suite alone never means Hermes P0/P1 is complete.

## Follow-up quality metrics

- Critical-field event accuracy measured on real/sanitized golden cases.
- `false_allow` for unauthorised high-risk actions = **0**.
- Recovery: no duplicate external effects after crash/timeout; unknowns require reconciliation.
- Freshness: each displayed carrier/AIS event has distinct `occurred_at` and `retrieved_at`.
- Every claimed milestone has at least one stable attributable source and a confidence grade.
- Economic claims are quotations/scenarios/pilots, never 'guaranteed profit'.


## Branch-file collision review (read-only, 2026-10-18)

Ten topic branches were compared against fork `main` using GitHub compare. **One exact path collision is confirmed**: `docs/owner-readiness-20261018` and `docs/hermes-portfolio-p0-p1-design-20261018` independently add **different content** to `ops/DESIGN_BACKLOG.md`. Do not merge those branches sequentially without reconciling the file. Treat the owner-readiness P0/P1 constraints as the control baseline; copy any unique P3 market ideas into the existing portfolio backlog, preserving provenance, not into a second operating system.

Other **semantic overlaps, not verified Git merge conflicts**:
- PR #4 owner gates vs #5 evidence validator and #7 safe read-only host probe: keep independent roles and re-run isolated tests; none passes the Windows/ACL gate merely by existing.
- PR #4 owner portfolio control vs #9 commercial 20+3 portfolio: canonical 45-package tracker remains the authority; #9 is a researched-products appendix, not a second task register.
- Shipment Intelligence staging currently changes only `SKILL.md` and `shipment_intelligence.py` (two files); the corresponding committed fixture and regression tests were **not found in the compared branch diff**. This is not a claim that no tests exist elsewhere.

Branch comparison confirms path changes and ahead-of-main status only, **not** CI success, mergability after updates, or current draft PR state. Do not auto-close or merge any PR. The private canonical workbook and real customer/shipment data must remain outside the public fork.

**Next safe action:** inspect local Windows checkout and exact branch/working-tree identity read-only; then verify a restricted backup and isolated *functional* restore before any test/code installation. Current P0/P1 status remains OPEN / NO-GO.
