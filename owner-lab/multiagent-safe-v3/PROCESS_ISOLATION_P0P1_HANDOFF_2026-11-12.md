# Hermes Owner Lab — isolated approval process / P0-P1 acceptance handoff

**Report date (Tripoli):** 2026-11-12
**Scope:** Owner Lab synthetic-only, non-production. No merge, deploy, secrets, paid services, main edits or physical/local machine actions.
**Production:** `HOLD`; **HITL:** `REQUIRED`; **G0/G-CODE/G1:** `NO-GO`.

## Provenance and reuse

- Reference: `eltokhey1/hermes-agent` PR [#14](https://github.com/eltokhey1/hermes-agent/pull/14), baseline commit `6b0f5e0a957f986017722a734b56992be5f1dd01`.
- Research-only branch: `research/owner-auth-process-boundary-20261112`.
- Do **not** merge or publish this research branch. PR #14 and `main` remain untouched.
- Reuses `approvals.py` (HMAC-signed, task/spec-hash/expiry-bound assertions), `orchestrator.py` (existing deterministic allowlist, SQLite journal, same single reservation boundary), existing tests and the read-only Windows inventory script.
- New research-only `isolated_authority_research.py`: independent spawned **OS process**, two HMAC-authenticated **loopback** listeners (agent/owner), JSON bytes only (no pickle), private server-side approval signing key, fixed synthetic approver name, exact `spec_hash` comparison, bounded TTL, replay resistance via existing orchestrator, in-memory independent ledger head, ESTOP latch. Only inert `demo.echo` and `demo.review`; no external tool dispatch.
- New `tests/test_isolated_authority_research.py`: ten adversarial tests, including wrong-channel owner impersonation, wrong action hash, owner rejection, expired approval, fake model risk, duplicate concurrent dispatch, ESTOP and SQLite event removal.

## Exact evidence

- **Source+tests commit SHA:** `cde28e94e920b339c93871ab728a5050ae2fda93`
- **Workflow-only commit SHA:** `2d9a2f01c2520a84649f1377562dd18785c3bcca`
- **Successful GitHub-hosted run:** [#43122599506](https://github.com/eltokhey1/hermes-agent/actions/runs/43122599506), attempt 1, `completed/success`.
- Jobs: Ubuntu `130866538001`; Windows `130866537780`.
- **Linux:** `Ran 115 tests in 5.226s`, `OK`.
- **Windows runner:** `Ran 115 tests in 21.164s`, `OK`, `HOSTED_WINDOWS_READONLY_INVENTORY=PASS`, `OWNER_WINDOWS_P0_P1=NOT_TESTED`.
- **Pass/Fail/Skip:** 115/0/0 each OS; total 230/0/0. Note that the **Windows-only inventory check is correctly skipped on Ubuntu** and passes on hosted Windows; it is not a unittest skip.
- Exact code-gate command:
  ```sh
  python -m compileall -q approvals.py orchestrator.py isolated_authority_research.py tests
  python -W error -m unittest discover -s tests -v
  ```
- The source snapshot in the workflow is pinned and checked: `VERIFIED_OWNER_BOUNDARY_SHA=cde28e94e920b339c93871ab728a5050ae2fda93`.

### Preserved failed attempt

[Run #43122421807](https://github.com/eltokhey1/hermes-agent/actions/runs/43122421807) was green on Linux, red on Windows because two **test-fixture-owned** SQLite connections used `with sqlite3.connect(...)`, which commits/rolls back but does not close the connection. Windows temp directory cleanup encountered WinError 32. The research tests were corrected to use `contextlib.closing` and rerun at a new exact SHA. No original Owner Lab approval or runtime code was modified.

## Accurate limits (HOLD reasons)

1. **Actual owner authentication is NOT implemented.** Session HMAC authenticates a channel capability in a synthetic ephemeral test; it does not independently authenticate the human owner, prove user consent, prevent CSRF, or protect against theft of the owner capability. It is **not** an approval service for external actions.
2. **OS account isolation is NOT proven.** Both the test harness and the isolated authority process run under a single hosted CI account. A hostile same-user process could inspect secrets or modify SQLite; production requires separate restricted accounts/VM/sandbox, protected key vault and independent watchdog/ESTOP.
3. **Anchor durability is NOT proven.** The ledger head is held in process memory, so a process restart loses it; process memory is not an independently durable signed checkpoint. A deleted/truncated/rehashed ledger after restart remains a risk until a separately protected monotonic checkpoint is engineered and tested. Cross-project PR10 [research HMAC anchor proof](https://github.com/eltokhey1/hermes-agent/actions/runs/43114689189) is also synthetic, not deployable trust isolation.
4. **Only inert demo actions exist.** No external effect, email, shipment update, payment, production connector, cloud API, model tool, or file write outside the isolated SQLite fixture was exercised. ESTOP latching is simulated; actual in-flight cancellation/drain is NOT tested.
5. **Owner Windows restore is NOT tested.** Passing GitHub-hosted Windows tests is not Windows host P0/P1 acceptance, ACL proof, encrypted backup, or recovery on the user's PC.
6. Historical Owner Lab approval issuer uses demo synthetic approvals; no approval token is a real identity proof, and independent human review remains open.

## Precise smallest safe P0/P1 gate for OWNER hardware

1. **Owner preflight only (read-only):** use existing `WINDOWS_READONLY_PREFLIGHT.ps1` **on the owner's Windows host when available**, through a trusted user action. Record Windows edition/build, free disk/RAM, available backup target, virtualization capability, expected Hermes process identity and permissions; script deliberately avoids usernames and secrets. The runner-only PASS cannot substitute.
2. **P0 backup+isolated restore:** once a protected backup is proven, create a known-consistent SQLite backup with WAL/SHM accounted for, copy **only into an isolated disposable VM or new scratch directory** under restricted ACLs; validate SHA manifest, SQLite integrity, schema, functional Hermes recovery and negative write-permission tests. Never overwrite the original DB and never delete WAL/ESTOP artifacts. Require raw outputs, timestamps, exact executable/repo SHA, PASS/FAIL/SKIP count and independent reviewer signature.
3. **P1 real failure/ESTOP:** in the isolated disposable instance (NOT production), create a synthetic high-risk pending task; verify owner identity and exact-action-hash approval cannot be forged from the model/sandbox; simulate crash while an action is in-flight; independently halt dispatch and latch ESTOP; after restart, classify uncertain effects as UNKNOWN, never auto-retry; prove signer/ESTOP/watchdog survive an agent crash and that the signed external anchor detects truncation/reordering/rollback.
4. **Failure gates:** Missing owner-machine access, P0 restore proof, P1 in-flight drain, ACL denial, real owner identity / trust-root separation, paid budget clearance or any policy violation => **NO-GO**.

## Next technical action

Set up an independently protected, restart-durable checkpoint and separate owner identity/authentication boundary under a disposable VM account, then test exact-SHA recovery and ESTOP. This is a **future gate** and no machine changes are authorized or made by this handoff.

**Verified today:** cloud-hosted synthetic separation and regression tests. **Unverified:** production isolation and real P0/P1. `PRODUCTION=HOLD`, `HITL=REQUIRED`.
