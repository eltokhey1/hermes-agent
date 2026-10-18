# Hermes FDE engineering pilot — proposal (not deployed)

**Status 2026-10-18:** proposed workflow and an offline evidence-receipt validator. No new integrations, hosted services, live data access, workflow execution, CI results, production credentials, or production approval are claimed. This is a user-specific planning addition to the existing Hermes agent; it does not replace its core.

## Why / concrete consumer

The first pilot is **shipment ETA and export-document audit**: given user-approved, non-sensitive offline samples, compare cited vessel/shipment events against a structured shipment state and produce a human-reviewable discrepancies report. Never claim real-time AIS, carrier access, or verified ETA without observed source evidence. The second candidate, human-reviewed WhatsApp quotations, remains backlog only.

## Six work phases and the lightest tool choice

1. Discovery: written problem statement, workflow map, success criteria and scope boundaries. Use Markdown/Excalidraw first; Notion/Figma only if needed for collaboration.
2. Data integration: immutable raw files with provenance and verification time; use existing SQLite first. PostgreSQL/pgvector or Unstructured only when a measured requirement justifies them.
3. Agent & application: deterministic code for arithmetic, verification and policies; reuse Hermes tools/skills and read-only MCP integrations only after threat review. LangGraph/agent SDK are optional, not prerequisites.
4. Deployment: isolated fixture run before any cloud/desktop action. No Docker, CI or hosting install is authorized by this document.
5. Evals & observability: create repeatable fixtures (genuine, negative, missing-data, spoofed-source and adversarial inputs). Prefer existing Hermes test infrastructure; only add Promptfoo and one tracing service after an A/B trial. OpenTelemetry is a future interoperability target, not an existing integration claim.
6. Security & governance: least privilege, per-agent identity, deny-by-default, sensitive-field masking, prompt-injection isolation, bounded tools, network egress controls, human approval for externally visible or irreversible actions.

## Delivery contract / gates

The receipt is structured JSON (sample: `examples/shipment-eta-audit.sample.json`). Its required gates are `security`, `recovery`, `idempotency`, `privacy`, and `quality`. Each gate is `PASS`, `FAIL`, or `UNKNOWN`. A PASS must include a reproducible non-sensitive command, an observed exit code 0, timezone-aware observation timestamp, and a SHA-256 digest of the reviewable artifact. A reviewer must independently verify the referenced artifact and confirm the command actually corresponds to that gate. **Never put tokens, passwords, customer PII or sensitive paths into receipts or PR logs.**

Offline check (reads a local JSON file only; never executes receipt commands):

```bash
python scripts/fde_contract_validate.py docs/fde/examples/shipment-eta-audit.sample.json
```

The sample intentionally returns nonzero (`VERDICT=NOT_READY`) because all tests remain `UNKNOWN` until executed and reviewed. Unit tests for the validator:

```bash
python -m unittest discover -s tests/scripts -p 'test_fde_contract_validate.py' -v
```

A zero validator exit code would only mean **receipt syntax and required gate assertions have the expected shape**, not that evidence is authentic, that a security review happened, or that production release is approved. The utility intentionally rejects `production_approved: true` and any release intent other than `review_only`.

## Work order and explicit stop conditions

- **P0**: confirm deployment ownership, read-only inventory, secrets scope, current exact code SHA; design offline backup and restoration proof. Stop if evidence or authority is missing.
- **P1**: run crash/recovery and idempotency fixtures against the actual intended target; collect signed/anchored audit artifacts if available. Stop on `UNKNOWN`, critical leaks, failed policy gates, uncontrolled retries or incomplete provenance.
- **P2**: evaluate one concrete read-only pilot under isolated fixtures; ensure model cost budgets, repeatable observability and failure handling. Keep core tool list unchanged.
- **P3**: request customer/problem validation before any SaaS commitments; track measured time saved, evidence quality and unit economics.
- **P4**: compare new tools only after duplications, licenses and total cost are reviewed; stage changes behind approval gates.

## Reuse-before-build and evidence boundaries

Hermes already has extensive tests, evaluations, gateway and tool integration code. This patch deliberately does not introduce a second scheduler, approval engine, agent registry, auth layer or persistent-state system. The actual machine's Hermes version, its backup state, secrets, Windows/Docker availability and deployment status are **not observable from the GitHub fork**. Do not assert production readiness based on this repository or these documents.

**Merge condition:** owner reviews this scope and tests on the relevant branch. **Deployment condition:** separately documented operator approval with actual-environment evidence; there is no implicit permission to deploy from this PR.
