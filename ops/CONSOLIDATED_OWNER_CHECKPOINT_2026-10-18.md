# Hermes consolidated checkpoint — 2026-10-18 (owner-reported, review-only)

> **PRODUCTION: HOLD.** This file is a documentation checkpoint in Draft PR #4, not a release, deployment, live test, or independent attestation. Public-safe summary only: no user paths, PIDs, credentials, hashes of private archives, logs, or recovered files.

## Canonical task system and anti-duplication

- **Canonical engineering queue:** [MASTER_IMPLEMENTATION_MATRIX.csv](./MASTER_IMPLEMENTATION_MATRIX.csv) (**32 tasks**: P0 9, P1 9, P2 6, P3 5, P4 3). Keep these task IDs stable.
- **Acceptance and authority:** [READINESS_DECISION_POLICY.md](./READINESS_DECISION_POLICY.md), [OWNER_READINESS_GATES.md](./OWNER_READINESS_GATES.md).
- **Design-only backlog and tools:** [DESIGN_BACKLOG.md](./DESIGN_BACKLOG.md). No parallel agent operating system, no duplicate queue or runtime.
- **Candidate implementation:** Draft PR #7 inventory and Draft PR #5 evidence validator. Their Linux tests are not Windows production proof.
- **PR policy:** keep #4/#5/#7 **DRAFT**, no auto-merge, no changes to `main`, and no installs/deployments/credentials/external financial actions.

## Reported Windows progress (not yet independently reviewed)

| Gate | Owner-reported observation | Formal gate |
|---|---|---|
| P0-01 inventory | Installed Windows executable, data root and runtime dependencies identified; local working-tree commit/dirty state not certified | **PARTIAL / UNVERIFIED** |
| P0-03 local backup | Native backup ZIP reported and SHA/CRC verification performed offline. Original secret-bearing ZIP still unencrypted; off-device copy not demonstrated | **PARTIAL / UNVERIFIED** |
| P0-04 isolated file recovery | ZIP extracted to separate directory; 25,433 file-level SHA comparisons and 13 SQLite quick-checks reported PASS; **application not started from restore** | **PARTIAL / UNVERIFIED** |
| Infrastructure sandbox | A no-network, read-only-root, non-root Python container probe reported PASS. **No Hermes data mounted and no Hermes execution** | **INFRASTRUCTURE-ONLY / NOT P0-P1 ACCEPTANCE** |
| Encryption | GPG discovered, encryption/decryption check not yet reported | **BLOCKED / UNVERIFIED** |
| P0-02 / P0-05 / P0-06 / P0-07 | Least privilege, fail-closed 4-case suite, synthetic secret canary, and hard spend guard not demonstrated | **UNVERIFIED** |
| P1-01…P1-09 | Durable intent/UNKNOWN recovery, approvals, watchdog, evidence and independent signoff not demonstrated on target | **UNVERIFIED / HOLD** |

The standalone sandbox passed a narrower infrastructural test, not a comprehensive Docker escape-risk review. Integrity of a ZIP and a restored SQLite file does not prove a runnable Hermes recovery, overall backup scope, or rollback quality. The above observations were supplied in an operator chat; do **not** turn them into formal `PASS` rows until reviewer-admissible evidence is captured.

## One ordered critical path

1. **P0 custody** — confirm installed/local code identity and active profile; securely encrypt the existing verified archive with interactive key entry; verify decrypted SHA; arrange **separate** protected off-device copy; avoid exposing secrets or leaving extra plaintext copies.
2. **P0 functional restore** — run a **disconnected, synthetic-credential** smoke test against a separate restored home. No production network, API keys, messaging, cron side effects, auto-import to the live home, or unsafe path mounts.
3. **P0 security** — fail-closed 4-case tests; synthetic canary redaction; access/scopes review; hard $0 external spend baseline; evidence receipt (time, command, exit code, digest, source, independent reviewer).
4. **P1 control gates** — durable intent, unknown-outcome reconciliation/no automatic retries, approval binding, progress watchdog, and acceptance/evidence suite; require independent go/no-go and **separate human release approval**.
5. **P2–P4 defer** — after P0/P1 gates: MCP and data integration → shipping vertical slice with carrier/AIS provenance and ETA confidence → commercial radar/pilots → bounded resilience and improvement.

## Portfolio lanes: separate data, unified standards

- **Hermes Core:** P0/P1 owner, no new platform layers until acceptance.
- **TradeOps / Shipping Intelligence:** DCSA/carrier events + AIS evidence + ETA confidence; container state must not be inferred from vessel location alone.
- **Viral Kit / CRM & Content:** separate project acceptance, no outbound sends/publishing before action approvals and idempotency.
- **Hermes Bridge:** independently packaged offline proof-of-concept; **not installed or integrated** on owner's Windows host.
- **Commercial Radar & validated SaaS:** source-verified research and demand interviews; TradeDocs AI, ExportLead AI, Procurement Copilot, WhatsApp Sales Agent are candidates, not deployed products.
- **Quant / TradingAgents:** research isolation; no trading or expenditure.

## Status discipline

Engineering plan statuses = `DESIGN_ONLY / UNVERIFIED / PARTIAL_OWNER_REPORTED / VERIFIED_PASS / FAIL / HOLD`. They are distinct from runtime operation states `PENDING / RUNNING / SUCCEEDED / FAILED / UNKNOWN`. Never auto-retry `UNKNOWN` external effects. Preserve any source-controlled and local existing work; no destructive rewrite or forced sync.

**Next authoritative action:** operator returns a **redacted** encryption-and-decryption verification receipt or the blocker. Do not publish encrypted backup itself, credentials, exact private paths, or unredacted diagnostic logs in this public repository.
