# P0/P1 readiness and evidence ledger — review-only

**Status:** NOT READY / NOT PRODUCTION APPROVED  
**Review reference:** draft PR #5.  
**Local machine coverage:** NOT OBSERVED. This file is a task ledger, not a log from the owner's host.

## Source and trust boundaries

- Source of this ledger: GitHub fork inspection + isolated validator tests.
- Never put API keys, password values, full environment dumps, origin URLs containing credentials, tokens, customer PII, internal hostnames or real shipping records here.
- Stop before running untrusted project tests, unknown `hermes update` flags, network commands or executable setup scripts on the host.
- A green repository check does not establish equivalence with a separate Windows installation.

## Gate 0: inventory and recoverability — UNKNOWN

| ID | Acceptance requirement | Proof required | Status |
| --- | --- | --- | --- |
| P0-01 | Identify exact deployed commit/profile without leaking secrets | redacted read-only inventory + SHA | UNKNOWN |
| P0-02 | Show backup and actual isolated restoration | restoration command log, exit code, digest, functioning restored runtime | UNKNOWN |
| P0-03 | Deny on timeout/empty/malformed/network error | four negative tests, all rejection | UNKNOWN |
| P0-04 | Verify scoped credentials and field masking | non-secret test token injection + scrub checks | UNKNOWN |
| P0-05 | Verify cost cap that stops work automatically | isolated hard-stop test | UNKNOWN |
| P0-06 | Preserve original project and uncommitted work | redacted git status before any mutation | UNKNOWN |

**P0 exit:** each proof is real, independently reviewed and recorded; any missing artifact is a stop.

## Gate 1: durable intents, reconciliation and acceptance — UNKNOWN

| ID | Acceptance requirement | Proof required | Status |
| --- | --- | --- | --- |
| P1-01 | Persist intent before outward action | state transition audit | UNKNOWN |
| P1-02 | Support PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN | state-machine behavior tests | UNKNOWN |
| P1-03 | Ambiguous external effect stays UNKNOWN, not blindly retried | crash and injected timeout tests | UNKNOWN |
| P1-04 | Bounded recovery/watchdog and no duplicate side effects | isolated restart/reconciliation logs | UNKNOWN |
| P1-05 | Evidence gates security/recovery/idempotency/privacy/quality | receipt + independently examined artifacts | UNKNOWN |
| P1-06 | Hash checks and timestamp/command correspondence | file digest verification + independent reviewer | UNKNOWN |
| P1-07 | Exact-commit CI and host-relevant tests | CI run and platform-specific evidence | UNKNOWN |

**P1 exit:** all relevant gates PASS with independently verified proofs. The receipt validator alone cannot pass this gate.

## Pending integration candidates, NOT INSTALLED

- Observability: OpenTelemetry-compatible structure after current logging is mapped; one provider only after benchmark.
- Data sources: read-only MCP integrations after source-contract, egress and prompt-injection review.
- Deployment: Docker or Actions only when host readiness and release approvals are independently verified.
- Commercial features: no real-customer outreach, carrier/API actions, invoices or spend from this ledger.

## Operator checklist

1. Confirm the local host is available and choose a safe evidence destination **outside Git**.
2. Run only explicit, reviewed inventory commands without credentials or remote destinations.
3. Verify isolated backup restoration before any project tests, dependency installs or update checks.
4. Create sanitized receipts. Run the local SHA-256 verifier with `--evidence-root`; do not treat its zero exit code as provenance proof.
5. Obtain separate human review for consequential, outward-facing or financial actions.

**Hard stop:** any missing credential boundary, secret leak, test mutation outside the sandbox, uncontrolled retry, missing backup proof, `UNKNOWN` external effect, or unapproved cost.
