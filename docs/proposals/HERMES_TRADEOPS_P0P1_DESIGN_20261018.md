# Hermes TradeOps v2 — Design-only integration proposal
Date: 2026-10-18
Status: **DRAFT / NOT MERGED / NOT PRODUCTION READY**

This proposal is for a local, read-only TradeOps workflow. It must **not** be
considered an authorization to change the Hermes runtime, send messages, pay,
publish, or alter files outside a deliberately isolated test workspace.

## Proven scope
An independently packaged Python standard-library prototype was tested in an
isolated workspace: 46/46 unit tests pass on synthetic fixtures. Tests cover:
- Invoice, packing-list, bill of lading and LC field comparison with a
  document/source reference for each extracted or manually entered value.
- Explicit weight units; packaging-level differences are marked
  INCOMPARABLE rather than silently compared.
- SQLite append-only ETA *evidence* journal: BL and container identifiers
  retained as strings, changes attributed to source and observation time,
  older observations retained, duplicates and contradictory sources flagged.
- Pure-policy precheck: no caller-supplied boolean is treated as an
  authenticated human approval. External effects are outside the prototype.
- Optional MCP registration with a stub server. Real MCP transport/client
  interoperability has **not** been tested.

The package is not checked into this repository by this documentation-only
branch. It is preserved separately for security and licensing review.

## Required gates before any code is wired into Hermes
### P0 security
1. Verify which Hermes codebase and Python interpreter are running on Windows.
   The repository's pyproject.toml currently requires Python >=3.11,<3.14.
2. Read-only inventory and secret scan; backup and **restore test**.
3. Strict permission/credential boundaries; no uploading confidential trade
   documents to third-party tools by default.
4. If a future connector fetches URLs, apply deny-by-default egress and full
   DNS/redirect/private-IP/SSRF checks **at the fetch layer**. Lexical URL
   triage is NOT SSRF protection.
5. Record a tamper-evident evidence receipt with independent anchor; a
   self-contained SQLite hash chain alone is not tamper-proof.
6. Document source terms and API limits. TrustMRR API data must not be used
   for AI training, grounding, or recommendation datasets without the
   permissions its terms require.

### P1 reliability and acceptance
1. Durable intent before any external side effect; state machine
   PENDING, RUNNING, SUCCEEDED, FAILED, UNKNOWN.
2. If an effect may have occurred but cannot be confirmed, stop at UNKNOWN;
   do not retry payment, message, document release, or write automatically.
3. Verify explicit, per-operation human approval using trusted identity and
   server-side enforcement—not model-supplied approval flags.
4. Acceptance fixtures must include inconsistent LC beneficiary, weight-unit
   mismatch, cargo vs package hierarchy, multiple bills of lading, document
   duplicates, stale ETA, contradictory carriers and prompt injection within
   document text.
5. Independent integration tests with the real runtime, MCP client and
   permitted synthetic carrier/API fixtures. No production credentials.

## Proposed ownership
- Hermes core P0/P1: baseline protection and durable operations.
- TradeOps: domain checking and evidence generation (read-only).
- Research & Solution Intelligence Hub: approved public primary sources,
  licensing/terms register, evidence level classification and comparison.
- External effect executor: separate; disabled until P0/P1 evidence accepted.

## Next action
Review this design, run repository-specific compatibility tests on an
isolated branch, and only then open a code-integration PR. Keep this
documentation proposal unmerged until the acceptance criteria have evidence.

## 2026-10-18: v4 regression findings (standalone package, **not in this PR**)
- Offline, synthetic-input tests: **106/106 pass** (v4); earlier isolated hardening regression **58/58 pass**. These are unit tests, not security certification.
- Critical review checks added: LC number from the LC document must match LC payment details; ETA BL identifier and container must be traceable to BL document fields; low-confidence identity evidence blocks ready state.
- Every externally supplied ETA in this prototype receives `ETA_SOURCE_UNVERIFIED`, including records that self-label `source_type=CARRIER`; an upstream connector must independently authenticate the source before claiming confirmation.
- Read-only Maersk tracking lookups matched 26 booking/BL records to 59 containers and 26 corresponding rows/counts in the user's Arrival workbook. These are historical source events, **not guaranteed current delivery ETAs**, and were not committed to this public repository.
- The original Arrival workbook was NOT modified; a separate verification workbook was created in the offline deliverable.
- The full v4 code remains an isolated artifact for review. The code in this PR is a narrowly scoped acceptance-contract example; no Hermes integration, bank integration, production deployment, or user-facing network actions have been tested.

- Four separate Python-process CLI smoke tests now pass for safe advisory output, LC mismatch, foreign shipment ETA, and duplicate JSON rejection. These remain sandbox evidence only.
