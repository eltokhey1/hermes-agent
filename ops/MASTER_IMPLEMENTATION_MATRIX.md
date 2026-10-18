# Hermes Master Implementation Matrix — 2026-10-18

**Status: REVIEW-ONLY / NOT PRODUCTION READY.** This ledger is a proposal built from the AI implementation mindmap and nine existing Draft PRs. It is **not** an observed Windows status report. No core code, credentials, dependencies, CI, budget, or production settings are changed here.

## Single source of truth

- Machine-readable work queue: [MASTER_IMPLEMENTATION_MATRIX.csv](./MASTER_IMPLEMENTATION_MATRIX.csv)
- Gate policy: [READINESS_DECISION_POLICY.md](./READINESS_DECISION_POLICY.md)
- Existing P0/P1 requirements: [OWNER_READINESS_GATES.md](./OWNER_READINESS_GATES.md)
- Existing deferred design: [DESIGN_BACKLOG.md](./DESIGN_BACKLOG.md)
- **Rows:** 32 (P0: 9, P1: 9, P2: 6, P3: 5, P4: 3).
- **Baseline observation:** All P0/P1 gates marked UNVERIFIED until independently tested on the target Windows instance. P2–P4 are DESIGN_ONLY. A draft PR or synthetic local test is not proof of working integration.

## Safe critical path

`P0-01 → P0-03 → P0-04 → P0-05/P0-06/P0-07 → P1-01 → P1-02 → P1-05/P1-06/P1-07 → P1-09 → P2 → P3 → P4`

- Before **any** installing, syncing, code execution on the owner host: compare repository identity and local dirty state, scope and complete a restricted backup and real isolated restore; preserve local changes.
- **UNKNOWN** external outcomes require stop/reconciliation and human review, not retry.
- A tool/provider is installed only when existing Hermes skills/plugins cannot meet measured need; API keys never enter public evidence.
- Gate `P1-09` is a blocking decision node; no phase transition, financial activity, outward communication, data export, or production approval follows from a model-generated claim.
- Project planning status and runtime operation status are separate: `DESIGN_ONLY`/`UNVERIFIED` here are not the runtime operation state `UNKNOWN`.

## Ten mindmap workstreams covered

- **AI Governance:** P0-08, P0-09, P1-05, P1-09
- **Data Foundation:** P2-01, P2-02, P3-03
- **Delivery & Operations:** P0-03, P0-04, P1-01, P1-02, P1-04, P2-05, P4-02
- **People & Change:** P3-05
- **Platform & Architecture:** P0-01, P2-03, P2-04
- **Responsible AI:** P1-06, P4-01, P4-03
- **Risk & Compliance:** P1-08, P2-06
- **Security & Privacy:** P0-02, P0-05, P0-06, P1-03, P1-07
- **Strategy & Value:** P0-07, P3-04
- **Use-Case Portfolio:** P3-01, P3-02

## Existing draft PR consolidation (no duplicate implementation)

| Draft PR | Existing work to reuse | Relationship to matrix |
| --- | --- | --- |
| [#1](https://github.com/eltokhey1/hermes-agent/pull/1) | TradeOps acceptance P0/P1 design | P1 effect ledger; P3 shipment |
| [#4](https://github.com/eltokhey1/hermes-agent/pull/4) | Owner readiness gates & design backlog | **This PR**: central governance and ownership |
| [#5](https://github.com/eltokhey1/hermes-agent/pull/5) | Offline read-only evidence contract validator | P1-05/06 candidate; cannot replace independent runtime testing |
| [#6](https://github.com/eltokhey1/hermes-agent/pull/6) | Portfolio radar + MCP/iFixAi design backlog | P3 radar, P2 tooling |
| [#7](https://github.com/eltokhey1/hermes-agent/pull/7) | Sanitized P0 Windows preflight candidate | P0-01 only; not yet host verified |
| [#9](https://github.com/eltokhey1/hermes-agent/pull/9) | Portfolio evidence/acceptance reference | P1 and P3 decision evidence |
| #2, #3, #8 | Installer, APK audit, cloud deployment candidates | **On hold** until P0/P1 acceptance |

## Rules for updating a row

1. Set real owner, source snapshot/commit, acceptance criterion and dependencies first.
2. Transition to `PASS` **only** after storing timestamped and independently reviewable run evidence (environment, exact command, exit code, artifact digest, test case IDs, redacted source, reviewer).
3. If test not run, label `UNVERIFIED`; if rejected, `FAIL`. Never infer `PASS` from another platform's mock run.
4. Preserve failing evidence and maintain owner approval separately from technical PASS.
5. Do not automatically backfill due dates, spend or claims about a local Windows environment.

## Immediate handoff

Use Draft PR #7 for **read-only** redacted local inventory when the operator's Windows environment is available. Compare to approved fork SHA, preserve dirty local files, make restricted backup, and demonstrate actual isolated restore before executing application tests or modifying the host. Until then: `PRODUCTION_READY=NO`, `PRODUCTION_APPROVED=NO`.
