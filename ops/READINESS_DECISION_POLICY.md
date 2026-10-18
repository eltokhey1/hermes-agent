# Hermes readiness decision policy (review-only)

Scope: all AI delivery streams and Hermes P0–P4. Initial status: **HOLD**. This document is a candidate gate specification, not deployed policy.

## Definitions
- `UNVERIFIED`: no admissible evidence from the target runtime.
- `DESIGN_ONLY`: unimplemented and intentionally deferred.
- `PASS`: criterion passed on the identified target with evidence, digest, timestamp and independent reviewer.
- `FAIL`: observed negative result; blocked.
- `BLOCKED`: prerequisite not met.
- `HOLD`: no consequential work permitted.
- `UNKNOWN`: ambiguous **runtime effect**; never automatically retry, reconcile before resolution.

## Required proof before production review
1. **Every P0 gate P0-01…P0-09:** actual read-only host identity, restricted/encrypted backup with independent off-device custody, **real restored Hermes startup** in an isolated synthetic-credential environment, four deny-by-default negative cases, canary leakage scan, aggregate $0 default cost cap, upstream/PR reconciliation and a reviewed branch protection/rollback decision. The dependency graph cannot substitute for proof of a complete P0 sign-off.
2. **Every P1 gate P1-01…P1-08:** pre-action durable effect journal, post-crash `UNKNOWN` reconciliation (never retry an ambiguous external effect), identity/action-bound expiring approval, bounded progress watchdog, independent tamper-resistant evidence ACL, positive/negative security and accuracy evaluations, and **recovery/incident tabletop proof**. P1-04 and P1-08 are mandatory for P1-09; their omission would be a stop condition.
3. **P1-09 independent go/no-go:** verify admissible evidence for every required P0/P1 gate with reviewer independence, environment, commit SHA, timestamps, expected vs observed, negative-case receipts and rollback rehearsal; maintain a **separate action-bound human release authorization**. Code review, documents, SHA equality or isolated mock tests cannot establish Windows production readiness.

## Deterministic verdict
- Any mandatory `FAIL` → `REJECT`.
- Any mandatory `BLOCKED`, `UNVERIFIED`, `DESIGN_ONLY`, or missing evidence → `HOLD`.
- All mandatory `PASS` + valid evidence + separate human approval + no unsafe `UNKNOWN` outcomes → **eligible for go/no-go meeting**, not automatic deployment.
- Any `UNKNOWN` real-world side effect forces immediate `HOLD` and supervised reconciliation.
- Any budget overrun / credential leak / unsigned permission upgrade is a stop condition.

## Deterministic acceptance cross-checks (design specification)

The following are **design-level negative cases**, not executed tests of the user's Hermes installation. The acceptance decision for any P0/P1 release must satisfy all rows.

| Scenario | Expected readiness verdict |
|---|---|
| All evidence missing, or only a GitHub PR exists | `HOLD` |
| Backup ZIP hash/CRC and extracted SQLite checks succeed, but restored Hermes never starts | `HOLD` |
| Encrypted backup unavailable off-device or ciphertext cannot be decrypted to matching SHA | `HOLD` |
| Permission service: timeout, empty response, malformed response or network failure; any action proceeds | `REJECT` |
| Test canary appears in logs, Git-tracked secrets or report artifacts | `REJECT` |
| Aggregate budget is only a warning, or unknown-price tool calls can charge | `HOLD` until demonstrated hard stop; `REJECT` on observed unauthorized charge |
| Evidence DB or its parent directory writable/deletable by the executing agent | `REJECT` |
| Watchdog or incident recovery drill (`P1-04`, `P1-08`) omitted | `HOLD` |
| External effect outcome ambiguous (`UNKNOWN`) and automatically retried | `REJECT` |
| All gate proofs pass but no independent reviewer or human release approval | `HOLD` |
| All gate proofs pass, reviewed in the **target environment**, with separate human approval | Eligible for a **human go/no-go** decision; never auto-deploy |

Never infer `PASS` from documentation metadata, CI green on an unrelated commit, a scheduled automation, or a synthetic policy unit test. There is no inferred approval. The **source of truth for task dependencies is [`MASTER_IMPLEMENTATION_MATRIX.csv`](./MASTER_IMPLEMENTATION_MATRIX.csv)** and its IDs must be resolved against any historical PR #9 references before acting. This is proposed policy pending implementation and host verification.

## Evidence record fields
`task_id, gate_id, project, environment, commit_sha, command_id, run_timestamp_utc, exit_code, expected_result, observed_result, artifact_sha256, provenance, reviewer, reviewer_decision, approval_reference, expires_at`

No production secrets, tokens, customer records, credentials or private paths may appear in a public PR. No deployment and no change to fork `main` is authorized by this document.
