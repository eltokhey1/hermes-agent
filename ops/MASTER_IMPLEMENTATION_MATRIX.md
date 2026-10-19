# Hermes Master Implementation Matrix — 2026-10-18

**Status: REVIEW-ONLY / NOT PRODUCTION READY.** This ledger is a proposal built from the AI implementation mindmap and 10 currently open Draft PRs (including staged shipment PR #10). It is **not** an observed Windows status report. No core code, credentials, dependencies, CI, budget, or production settings are changed here.

## Two-level registry reconciliation — 2026-10-18

**Scope correction:** The 32 rows here are the **Hermes engineering acceptance/gate queue**, **not** a replacement for the owner's separate multi-project command-center portfolio. That private canonical workbook contains **45 work packages**, references **120 historical task identifiers**, and groups them into **16 project streams**. A local, add-only reconciliation overlay maps each of these 32 gate IDs to one or more existing portfolio packages; links are *semantic references*, not 1:1 equivalences or permission to close work. One training/change-management gate has no exact package equivalent and remains a documented mapping gap. Do not duplicate the portfolio here or publish private task-level details.

The owner-reported Windows ZIP, isolated file restore, SQLite checks and disconnected Docker probe are summarized in [CONSOLIDATED_OWNER_CHECKPOINT_2026-10-18.md](./CONSOLIDATED_OWNER_CHECKPOINT_2026-10-18.md). These remain **partial operator-reported evidence**, not independently reviewed Windows application acceptance. Archive encryption and off-device custody, actual Hermes functional restore, and mandatory P0/P1 controls remain open. **Release verdict: HOLD.**

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

## 2026-10-19 ID collision remediation

The FDE pilot's historical P0/P1 checklist uses **different local meanings** for several identical-looking IDs. Its [`READINESS_EVIDENCE.md`](https://github.com/eltokhey1/hermes-agent/blob/docs/fde-evidence-pilot-20261018/docs/fde/READINESS_EVIDENCE.md) has now been amended on **existing Draft PR #5** to namespace all local IDs as `FDE-LEGACY::P0-xx`/`FDE-LEGACY::P1-xx`, with explicit semantic cross-links to this matrix. Do **not** merge the FDE legacy IDs into this 32-row queue or add them to the owner's 45 work packages. The original gate evidence and production **HOLD** remain unchanged.

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
5. **10 Draft PRs** are staged artifacts linked from this document, not deployed work. #4 governs scope; #7 local inventory proposal; #5 evidence validator candidate; #9 historical portfolio mapping; #10 is an offline Shipment Intelligence candidate under SHP-02/VES-01 and engineering P3-03. Keep all Draft until evidence gates and owner review.

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

**Cross-PR changed-path audit — refreshed 2026-10-19:** previously, PR #4 and #6 shared `ops/DESIGN_BACKLOG.md`, but that *historical* filename collision is no longer present. The latest changed-file lists for PRs #1–#10 comprise **46 distinct paths and zero repeated paths** (GitHub file list enumeration on 2026-10-19). PR #6 now changes only `ops/portfolio/BUSINESS_PORTFOLIO_RESEARCH_BACKLOG_2026-10-18.md`. This is **not** a green mergeability, CI, security, or policy decision: #4/#6/#9 still have overlapping portfolio concepts and must be reviewed on their current head SHAs with no automatic merge or state promotion. Older [PR #6 discussion](https://github.com/eltokhey1/hermes-agent/pull/6#issuecomment-6255459276) describes the superseded path snapshot.

**Acceptance detail reconciled in matrix:** P0-06 now explicitly requires canary absence in logs/reports/artifacts and `.env`/runtime logs untracked; P0-07 requires a hard, concurrent **aggregate** spend reservation with **unknown-price DENY**; P1-05 requires an independent evidence store whose DB **and parent directory** are OS-ACL-protected against Executor write/delete. These are **future acceptance criteria, not passed tests**.

**Readiness decision truth table:** [Policy test cases](./READINESS_DECISION_POLICY.md#deterministic-acceptance-cross-checks-design-specification) define how partial ZIP evidence, permission failures, lost backup custody, budget overrun, evidence tampering, crash recovery and missing reviewer/owner approval yield `HOLD` or `REJECT`. These are design/test specifications, not production test results.

**Owner handoff / next real blocker:** obtain a redacted proof of *encrypted local backup custody and decrypt-to-hash* plus separate off-device copy, then safe restore/start evidence. Remote GitHub commits cannot certify those tasks. Do not create another orchestration system or close Draft PRs on this documentation alone.

## Verified library crosswalk parity — 2026-10-19

**Scope:** static **cross-file reconciliation**, not Windows/runtime testing or evidence acceptance. The user Library source files were actually read: `Hermes_Unified_Command_Center_2026-10-18_CURRENT.xlsx` (45 rows in `حزم العمل`) and `HERMES_32_TO_45_CROSSWALK_2026-10-18.csv` (32 gate mappings), then compared against this branch's `MASTER_IMPLEMENTATION_MATRIX.csv` (32 engineering gate IDs).

| Static check | Verified result | Interpretation |
| --- | ---: | --- |
| Canonical historical package IDs present | **45 unique / 45 rows** | Historical source-of-truth retained; **not** 45 new engineering gates |
| Historical legacy IDs counted across 45 packages | **120 entries / 120 unique** | No duplicated historical ID in the CURRENT package view; each package's declared count matches its IDs |
| Operational stream names in CURRENT package view | **16** | These are operational streams, not extra package counts |
| Engineering gate IDs present | **32 / 32** | All 32 engineering rows have crosswalk entries |
| Engineering gate IDs absent in crosswalk | **0** | Full *identifier* coverage only |
| Crosswalk mapping to missing historical package ID | **0** | Every referenced historical package ID exists in the 45 package view |
| Crosswalk review required | **32 / 32** | **NO automatic state or approval transfer** |
| Mapping quality: DIRECT / OVERLAP / RELATED / PARTIAL / GAP | **11 / 10 / 6 / 4 / 1** | A valid pointer **is not** semantic equivalence or completed work |

**High-risk semantic differences:**
- Engineering `P0-04` (**isolated functional restore**) maps to historical package `P0-03` (**backup/restore**), while engineering `P0-05` (**fail-closed negatives**) maps to historical `P0-04`. **Never match these by the raw ID alone**.
- Engineering `P3-05` (role training and redesigned workflows) is explicitly marked **GAP** in the existing crosswalk and points to `GOV-01` only as a provisional governance association: not a directly implemented package.
- V7's separate `TASK_REGISTER_2026-10-18` contains **34 supplemental records** with **14 semantic collisions** in overlapping IDs against the canonical 120; use a source namespace such as `TASK_REGISTER_2026-10-18::H-P0-02` and the V7 collision report, not an unqualified `H-P0-02`. The 34, 44 V1 details, 26 checkpoints, 23 research opportunities and 32 gates **must not be added** to the 45 package count.
- P0-01, P0-03 and P0-04 engineering crosswalk rows contain `PARTIAL_OWNER_REPORTED`, not independent proof. Formal status remains `UNVERIFIED/HOLD`.

**Three work-in-progress lanes, unchanged:** (1) P0/P1 host readiness and protected real recovery, (2) source-verified non-spending commercial research, (3) read-only dated shipment evidence review when needed. Other work remains queued by canonical package and dependent phase, not abandoned. This amendment changes **no** source workbook, runtime code, task states, approvals, merges, or deployment.


**Read-only fork protection and CI fact-check (2026-10-19):** `main` branch read indicated `protected=false`; visible repository Rulesets API returned zero entries. Git commit `251e5f7c0a067239655f3421812ab7492a206065` reported **0 combined legacy statuses** and **0 Check Runs** (API state `pending` is not a successful check), and historical fork Actions runs query returned none. Detailed branch-protection GET was **403 due to connector restrictions**; thus this is a partial control audit, **not a certification that no other controls exist**. P0-09 remains **UNVERIFIED/HOLD**. Propose required PR review, explicit CI checks and default branch ruleset only after the required checks have been proven and rollback/administration paths reviewed; do not apply settings automatically.

**Sources preserved in Library:** `/Hermes/Command_Center_2026-10-18/Hermes_Unified_Command_Center_2026-10-18_CURRENT.xlsx`, `/Hermes/Command_Center_2026-10-18/HERMES_32_TO_45_CROSSWALK_2026-10-18.csv` and `Hermes_Portfolio_Consolidation_V7_README_AR.md`. Historical evidence must stay private/owner-controlled, not copied into this public GitHub repo.

## Static mutation regression — 2026-10-19

**Scope**: The *current exact* `MASTER_IMPLEMENTATION_MATRIX.csv` file at Git blob `643bee3d2a77ac2d76a6c14bdc1302c377d093c1` was read from the connected GitHub repository and parsed as RFC-style quoted CSV into a pure in-memory **structural/dependency verifier**. This did not run Hermes, Python tools from the draft PRs, Windows tests, external effects, cloud tools, or code coverage.

**Result: 20 of 20 expected structural verdicts matched.** There were two allowed/static-preserving scenarios and 18 adversarial changes rejected. The original graph includes **32 rows / 32 unique IDs / 11 columns**. The verifier checked: ID uniqueness, phase identity, expected UNVERIFIED/DESIGN_ONLY states, missing dependencies, cycles and future-phase dependencies, P0 backup→restore→negative-test ordering, P1-09 ancestor coverage of all 17 preceding P0/P1 tasks, and required P1-09 ancestry for later P2–P4 tasks.

Test cases deliberately exercised:
- Duplicate ID, missing dependency, self-cycle and cross-cycle — reject.
- Forged P0/P3 `PASS` states and phase reassignment — reject.
- Fail-closed, canary or cost testing started before isolated restore — reject.
- Remove `P1-08` incident drill or **both** paths to `P1-04` watchdog from `P1-09` — reject.
- Let model routing, market prioritization or shipment fusion bypass `P1-09` — reject.
- Skip backup before restore or allow `P1-01` before aggregate budget — reject.
- Insert dependency on later phase — reject.
- **Non-bypass control:** deleting only the direct `P1-04` link from `P1-09` must remain *structurally safe*, because the `P1-09 → P1-08 → P1-04` chain still enforces the watchdog. This is the second allowed scenario, not a false acceptance.

**Limitation:** This is a static integrity test of the control matrix and its documented statuses, **not a runtime fail-closed test, security review of an executing model or permission to deploy**. The mutation fixture definitions are recorded here; the transient in-memory test harness is not a CI workflow or a persisted code artifact. These test verdicts **must not** be recorded as P0/P1 `PASS` in the portfolio.

**Three tightened acceptance requirements, already updated in the CSV:**
1. `P0-01`: distinguish installed Hermes binary/build identity and active data directory from any Git checkout; independently verify parity or mark runtime provenance `UNKNOWN`. The candidate [read-only Git preflight in PR #7](https://github.com/eltokhey1/hermes-agent/pull/7) **cannot prove an installed Windows runtime is the same checkout**. It must be assessed separately and remain draft.
2. `P0-03`: verify a **crash-consistent** restricted/encrypted backup covering SQLite including relevant WAL/state and scheduling/config metadata, a recorded scope manifest, decrypt-to-SHA match and protected off-device copy. Do not infer an app-consistent backup merely from ZIP CRCs.
3. `P1-05`: evidence database **and containing directory** must resist modification, rename and deletion by the execution principal, demonstrated with **separate OS identities** on the actual target; same-account paperwork does not establish an independent verifier. [PR #5 review note](https://github.com/eltokhey1/hermes-agent/pull/5#issuecomment-6255914367) highlights that its hash/receipt validator is evidence-shaped only.

No runnable files were changed by this owner-readiness documentation review; all ten PRs remain Draft for review, and `main` was not modified. `PRODUCTION_READY=NO / HOLD` until independent host proofs.

## PR #10 shipment staging safety intake — 2026-10-19

**New candidate, not a new portfolio work package.** [Draft #10](https://github.com/eltokhey1/hermes-agent/pull/10) adds an offline DCSA/AIS/SQLite Shipment Intelligence skill under existing historical **SHP-02 / VES-01**; its engineering review maps to **P3-03**, with source provenance to **P2-02** and evidence format to **P1-05**. The current PR head was `6516971786668f2449551d52c7124108c810c3c1` at review. No direct conflicts were found across the 46 paths changed in all ten open draft PRs. Zero overlapping filenames is **not** permission to merge; source semantics and execution authority are separate.

**Read-only code inspection and sandbox comparison:** v0.1.1 code (Git blob `1a0c0ddbf20fa63695c71b0f4f7a0f8086e759d9`) retains pathways associated with three v0.1.0 library findings. The older v0.1.0 code ran **12/12 synthetic unit tests** in an isolated checkout. A malformed JSON import returned exit 2 but created a SQLite file before input rejection; an arbitrary unverified source with a fabricated `ACT` equipment record could produce `CURRENT_ACTUAL`; and Maersk-shaped records without provider-native IDs received locally derived digest identifiers. **The new v0.1.1 PR has not had its test suite executed in this review.** No production or genuine tracking data were used.

**Acceptance before promoting #10:** (1) reject invalid input before creating a DB or side-effecting directories; isolate DB paths and ACL, (2) distinguish `provider_claimed_actual` from independent carrier-origin verification and ensure no counterfeit source URL alone clears trust, (3) label locally derived IDs separate from native carrier IDs and test corrected event versions/duplicates, (4) run and record matching v0.1.1 test suite with exact commit SHA; independent reviewer and no CI green assumptions, (5) retain the AIS/container separation and licensed provider read-only constraints. Review details: [PR #10 comment](https://github.com/eltokhey1/hermes-agent/pull/10#issuecomment-6260572178).

**NO-GO**: PR #10 is not installed, does not fetch live carrier data, cannot authorize shipping/customs actions, and must not be merged/deployed before functional P0 restoration and P1 evidence gates. A GH change in the repo is not a Windows Hermes installation change.
