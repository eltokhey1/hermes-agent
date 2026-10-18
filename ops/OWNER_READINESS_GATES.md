# Hermes owner readiness gates — design / audit only

Status: **NOT IMPLEMENTED / NOT PRODUCTION APPROVED**  
Scope: owner-specific fork `eltokhey1/hermes-agent`, reference `main` observed at `251e5f7c0a067239655f3421812ab7492a206065` (2026-10-18 review).  
This is **not** a claim about the owner's Windows installation. This document defines acceptance criteria and safe sequencing, not enabled functionality.

## Current evidence (GitHub API, 2026-10-18)

- The repository is a **public fork** of `NousResearch/hermes-agent`.
- The fork's `main` resolved to commit `251e5f7c0a067239655f3421812ab7492a206065`, authored/committed 2026-09-17.
- Its `main` reports `protected=false`. **Do not push to or merge into main** as part of this preparation.
- The public API reported zero GitHub Actions workflow runs on this fork. This does **not** establish whether any tests were run elsewhere.
- The upstream main moved in October 2026; upstream and fork must be reconciled with a **reviewed diff**, not a blind update.
- The repository already ships skills, plugins, cron, multiple backends, native Windows support documentation, and a project test runner. Reuse these before adding components.
- The local Windows working tree, Git status, installed version, Docker state, existing credentials, and recovery feasibility remain **unverified**.

## P0: read-only inventory — stop before execution

1. Get owner-provided *redacted* outputs for working tree identity (`git rev-parse --show-toplevel`, HEAD SHA, `git status --porcelain=v1`) and Windows runtime capabilities. Do **not** assume this remote fork equals the local checkout.
2. Confirm whether there are local changes before fetching, updating, installing, running tests, or changing configuration.
3. Produce inventory of existing cron/skills/plugins/integrations **without loading executable modules**.
4. Treat all remote content and skills as untrusted until inspected. Never paste or upload secrets/logs containing secrets.
5. Interpret `hermes update --help` before running `hermes update`; help queries only for discovery.
6. Review upstream differences in a throwaway read-only analysis checkout; no auto-merge or forced reset.

**P0 required evidence:** manifest of observed paths and versions; timestamped redacted command outputs; no unintended working-tree changes.

## P0: backup / restore gate — no upgrades before green

- Determine backup scope, including configurations, encryption/secret references, state databases, skills/plugins, schedules and evidence, while *excluding plaintext secrets from public artifacts*.
- Store backups in an access-restricted, preferably encrypted location away from the live tree.
- Verify hashes and perform an **actual restore into a separate isolated location**; prove recoverability, do not count "ZIP created" as success.
- Keep recovery steps and rollback decision documented.

**PASS:** independently restorable backup; hashes confirmed; isolated restore test evidence; the original working tree is unchanged.  
**FAIL/UNKNOWN:** stop all mutating upgrades.

## P1: security invariants (negative-test driven)

| Gate | Required acceptance evidence |
|---|---|
| Fail-closed tool guard | Timeout, empty, malformed and network-error responses each produce **DENY** with no tool side effect. |
| Secrets | Test with synthetic canary keys; no key in logs, reports or Git; production secrets never used for the canary test. |
| Least privilege | Per-agent identity/scope, tool guards, field masking, environment/credential isolation; high-risk and irreversible actions demand human approval. |
| Runtime policy | Changes do not widen access silently; decisions auditable, policy-versioned and rollback-capable. |
| Hard budget cap | Executions stop when the configured spend limit is reached, rather than warning only. |
| Durable intent and recovery | Before any effect, persist task ID/idempotency key + allowed action and status `PENDING`; transition `RUNNING/SUCCEEDED/FAILED/UNKNOWN`. |
| Ambiguous external effects | `UNKNOWN` stops, reconciles, and **never automatically retries** messages, purchases, publishing, payments or destructive changes. |
| Watchdog | Observes useful progress/resources/child-tool state, not merely process liveness; bounded restarts only for demonstrably safe operations. |
| Acceptance/evidence engine | Every consequential claim has independent observable evidence, source/provenance, timestamp, confidence and a reviewer decision. |

Use the project's **documented test wrapper** `scripts/run_tests.sh` only inside an explicitly approved *isolated* workspace after P0 backup/restore. Tests execute code and are **not** read-only.

## Progress / approval matrix

- `DESIGN_ONLY`: documentation, source review, candidate shortlist, test fixtures, no installation.
- `SANDBOX_TESTED`: isolated validation with no real credentials and explicit cost ceiling.
- `STAGING_APPROVED`: scoped human approval, rollback plan, acceptance report.
- `PRODUCTION_APPROVED`: separate human authorization **only** after all mandatory gates pass.

## Explicitly not done on 2026-10-18

No Windows inspection; no restore test; no runtime tests; no deployment; no secret scans of the local machine; no production change; no claim that Hermes is "ready".

## External links used for codebase context

- Fork: https://github.com/eltokhey1/hermes-agent
- Project instructions: https://github.com/eltokhey1/hermes-agent/blob/main/AGENTS.md
- Original: https://github.com/NousResearch/hermes-agent
