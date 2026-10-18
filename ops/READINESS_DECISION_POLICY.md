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
1. P0-01 through P0-07: actual read-only identity check, restricted backup with real isolated restore, four deny-by-default negative cases, synthetic canary leak scan, and hard $0 default cost control.
2. P1-01, P1-02, P1-03, P1-05, P1-06, P1-07 and P1-09: durable effect journal, post-crash UNKNOWN reconciliation, cryptographically bound approvals, independent evidence, positive/negative safety and quality evaluations.
3. Independent reviewer, rollback rehearsal, bounded scope and explicit separate **human production approval**. Code review, doc completion, SHA matching or isolated mock test alone never imply production readiness.

## Deterministic verdict
- Any mandatory `FAIL` → `REJECT`.
- Any mandatory `BLOCKED`, `UNVERIFIED`, `DESIGN_ONLY`, or missing evidence → `HOLD`.
- All mandatory `PASS` + valid evidence + separate human approval + no unsafe `UNKNOWN` outcomes → **eligible for go/no-go meeting**, not automatic deployment.
- Any `UNKNOWN` real-world side effect forces immediate `HOLD` and supervised reconciliation.
- Any budget overrun / credential leak / unsigned permission upgrade is a stop condition.

## Evidence record fields
`task_id, gate_id, project, environment, commit_sha, command_id, run_timestamp_utc, exit_code, expected_result, observed_result, artifact_sha256, provenance, reviewer, reviewer_decision, approval_reference, expires_at`

No production secrets, tokens, customer records, credentials or private paths may appear in a public PR. No deployment and no change to fork `main` is authorized by this document.
