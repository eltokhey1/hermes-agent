# Hermes Master Implementation Matrix — 2026-10-18

**Status: REVIEW-ONLY / NOT PRODUCTION READY.** This ledger is a proposal built from the AI implementation mindmap and nine existing Draft PRs. It is **not** an observed Windows status report. No core code, credentials, dependencies, CI, budget, or production settings are changed here.

## Single source of truth

- Machine-readable work queue: [MASTER_IMPLEMENTATION_MATRIX.csv](./MASTER_IMPLEMENTATION_MATRIX.csv)
- Unified portfolio program overlay: [PORTFOLIO_CONTROL_TOWER.md](./PORTFOLIO_CONTROL_TOWER.md) — no duplicate engineering task queue.
- Gate policy: [READINESS_DECISION_POLICY.md](./READINESS_DECISION_POLICY.md)
- Existing P0/P1 requirements: [OWNER_READINESS_GATES.md](./OWNER_READINESS_GATES.md)
- Existing deferred design: [DESIGN_BACKLOG.md](./DESIGN_BACKLOG.md)
- **Rows:** 32 (P0: 9, P1: 9, P2: 6, P3: 5, P4: 3).
- **Baseline observation:** All P0/P1 gates marked UNVERIFIED until independently tested on the target Windows instance. P2–P4 are DESIGN_ONLY. A draft PR or synthetic local test is not proof of working integration.

## Operator checkpoint (2026-10-18)

[CONSOLIDATED_OWNER_CHECKPOINT_2026-10-18.md](./CONSOLIDATED_OWNER_CHECKPOINT_2026-10-18.md) is the single public-safe summary of **owner-reported** Windows P0 progress. It records local ZIP/SQLite/file-level restore and infrastructure sandbox observations, while retaining formal P0/P1 gate status **UNVERIFIED/HOLD** pending encrypted/off-device custody, actual application recovery and independent evidence. The original 32 task IDs remain unchanged; do not create a competing queue or promote the matrix to PASS on chat output alone.

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

## Unified execution order / dependency verification — 2026-10-18

**Source-of-truth hierarchy — counts have different meanings (do not add them):**

1. **32 gate-oriented engineering tasks** (P0:9, P1:9, P2:6, P3:5, P4:3) in [`MASTER_IMPLEMENTATION_MATRIX.csv`](./MASTER_IMPLEMENTATION_MATRIX.csv): the canonical **technical acceptance and dependency register** for Hermes Core. These IDs never change during research intake.
2. **120 historical project task IDs → 45 work packages → 16 operational streams:** mapping reported in the existing [Draft PR #9 commercial/portfolio register](https://github.com/eltokhey1/hermes-agent/pull/9) and owner Library workbook `Hermes_Unified_Portfolio_2026-10-18.xlsx`. This is the **portfolio traceability layer**, not 45 additional P0/P1 gates. Preserve original IDs in private owner records. Verify the latest spreadsheet mapping before promotion; it has not been independently re-audited in this change.
3. **7 executive programs** in [`PORTFOLIO_CONTROL_TOWER.md`](./PORTFOLIO_CONTROL_TOWER.md) group decision ownership only; no duplicate databases/queues.
4. **23 research tracks** in [Draft PR #9](https://github.com/eltokhey1/hermes-agent/pull/9) = 20 competitor case studies + 3 original product ideas, **not** active builds. Product Hunt monthly/year-to-date/category signals are source leads attached to P3-02, not tickets.
5. **9 Draft PRs** are staged artifacts linked from this document, not deployed work. #4 governs scope; #7 local inventory proposal; #5 evidence validator candidate; #9 historical portfolio mapping. Keep all Draft until evidence gates and owner review.

**Dependency audit (static validation on canonical CSV):** 32 rows, 32 unique task IDs, 11 columns, zero missing dependency references and zero cycles. Corrected **six dependency cells**: `P0-05/06/07` require `P0-04` functional isolated restore; `P1-01` now requires P0 identity/secrets/restore/fail-closed/canary/hard-spend/branch-decision evidence; `P2-04` requires the independent `P1-09` gate; and **`P1-09` now requires `P1-04` bounded watchdog and `P1-08` recovery/incident tabletop**. Graph traversal verified all 9 P0 and all 8 preceding P1 task IDs are required before `P1-09` can pass (17 of 17). **18 UNVERIFIED and 14 DESIGN_ONLY statuses remain unchanged.** Graph checks do not establish Hermes functional readiness.

**One physical execution path, with allowed non-mutating parallel research:**

- **Gate A:** `P0-01` read-only local identity / worktree / ACL inventory; preserve uncommitted files and user-owned secrets.
- **Gate B:** `P0-03` protected encrypted archive + separate protected off-device copy; prove ciphertext decrypts back to the expected file SHA. An operator report of ZIP CRC / SHA is useful but not proof of custody.
- **Gate C:** `P0-04` actual restored application smoke-test in a new offline, synthetic-credential, no-production-network location; test executable, persistence, config, rollback and evidence. **No application tests are allowed on the owner host before B and C pass.**
- **Gate D:** `P0-05/06/07` four explicit fail-closed conditions → DENY and zero side effects; synthetic-secret redaction with zero matches; hard shared spend gate with $0 default and concurrency safety. Validate the *real guard interface*, not only a stub.
- **Gate E:** `P0-08/09` reconcile draft changes/upstream and decide reviewed protected-main rules; `P1-01…09` continue only after accepted P0 and independent review. `UNKNOWN` external effects stop for reconciliation; no auto-retry.
- **Gate F:** P2 safe adapters → P3 market and shipping experiments → P4 advanced cloud/autonomy. This is a permission and acceptance dependency, not a block on safe public-source *research*.

**Current work-in-progress cap: no more than three tracks:**
1. P0 custody/restore/evidence (**critical path**, blocked on host actions).
2. Read-only research/business hypothesis validation (**no spend, outreach or customer data**).
3. Shipment source-evidence review when necessary (**read-only; event time/source/confidence; AIS never proves container discharge**).
All voice/dictation, workflow automation, vibe-coding, marketplace, cloud hosting, experimental libraries and historical PRs are queued to their existing task IDs and cannot create a fourth active implementation stream.

**Gate invariants:** `PRODUCTION_READY=NO` and `PRODUCTION_APPROVED=NO`. Planning states (`UNVERIFIED/DESIGN_ONLY/PARTIAL_OWNER_REPORTED`) must not be confused with runtime operation states (`PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN`). No secret-bearing backups, tokens, private paths or third-party personal data in GitHub evidence.

**P0 legacy-ID collision crosswalk:** [Draft PR #9 — `NEXT_ACTIONS_AR.md`](https://github.com/eltokhey1/hermes-agent/blob/docs/hermes-portfolio-v4-evidence-20261018/ops/portfolio/NEXT_ACTIONS_AR.md) explicitly maps its historical `NEXT-004…NEXT-009` task references to the engineering IDs. For example, `P0-04` denotes denial tests in the older NEXT register, but **restoration** in the authoritative engineering matrix; the actual denial tests are `P0-05`. Always resolve `register + task ID + description` before running host commands. Do not rename or erase historical IDs.

**Cross-PR path collision audit:** inspected changed-file lists of all **nine Draft PRs**: 39 path occurrences, **38 unique file paths**, and exactly **one overlapping path**: `ops/DESIGN_BACKLOG.md` in PR [#4](https://github.com/eltokhey1/hermes-agent/pull/4) and [#6](https://github.com/eltokhey1/hermes-agent/pull/6). Their contents differ materially. **STOP any blind merge/overwrite.** Preserve #4 generic project gates and manually reconcile unique commercial research/MCP/iFixAi notes from #6 with #9's commercial source records; do not close or merge either PR automatically. Review note: [PR #6 discussion](https://github.com/eltokhey1/hermes-agent/pull/6#issuecomment-6255459276).

**Acceptance detail reconciled in matrix:** P0-06 now explicitly requires canary absence in logs/reports/artifacts and `.env`/runtime logs untracked; P0-07 requires a hard, concurrent **aggregate** spend reservation with **unknown-price DENY**; P1-05 requires an independent evidence store whose DB **and parent directory** are OS-ACL-protected against Executor write/delete. These are **future acceptance criteria, not passed tests**.

**Readiness decision truth table:** [Policy test cases](./READINESS_DECISION_POLICY.md#deterministic-acceptance-cross-checks-design-specification) define how partial ZIP evidence, permission failures, lost backup custody, budget overrun, evidence tampering, crash recovery and missing reviewer/owner approval yield `HOLD` or `REJECT`. These are design/test specifications, not production test results.

**Owner handoff / next real blocker:** obtain a redacted proof of *encrypted local backup custody and decrypt-to-hash* plus separate off-device copy, then safe restore/start evidence. Remote GitHub commits cannot certify those tasks. Do not create another orchestration system or close Draft PRs on this documentation alone.
