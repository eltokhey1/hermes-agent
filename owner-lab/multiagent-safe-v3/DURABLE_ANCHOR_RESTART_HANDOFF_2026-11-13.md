# Hermes Owner Authority — durable research checkpoint across restart

**Receipt date:** 2026-11-13 (Tripoli; CI executed 2026-11-12 UTC)
**Repo:** `eltokhey1/hermes-agent`
**Status:** `PRODUCTION=HOLD`, `HITL=REQUIRED`, `G0/G-CODE/G1=NO-GO`.
**Base reused:** Owner Lab PR [#14](https://github.com/eltokhey1/hermes-agent/pull/14) plus earlier independent process-boundary research at `cde28e94e920b339c93871ab728a5050ae2fda93`.
**Research-only branch:** `research/owner-durable-anchor-restart-20261113`.

## What was actually added

- `durable_anchor_research.py`: HMAC-SHA256-protected JSON checkpoint **outside the Owner Lab SQLite database**; explicit empty-ledger-only bootstrap, atomic local replacement after fsync, increasing synthetic epoch, no silent reinitialization on missing/corrupt data. It includes the agent-visible ledger sequence/head and a synthetic ESTOP latch. **Not** a trusted monotonic epoch or protected production signer.
- `isolated_authority_research.py`: reuses existing `approvals.py`, `orchestrator.py` and separate-process agent/owner authenticated demo channels. When optional `checkpoint_path` and `signing_key` are supplied by a harness, it loads and verifies the checkpoint before accepting commands, persists updates after simulated task transitions, and rechecks against a DB ledger head on every operation. Without optional arguments the old in-memory research behavior remains unchanged.
- `tests/test_durable_anchor_restart_research.py`: seven new synthetic acceptance tests for explicit first boot, approved preview after authority-process restart, persistent ESTOP after authority crash/restart, tampered checkpoint MAC, refused re-bootstrap after checkpoint deletion with nonempty ledger, SQLite event deletion refused at restart, and wrong authority signing key. These run in the same harness as previous Owner Lab tests (no live tools).
- No changes to original PR #14, PR #10, `main`, paid APIs, customer data or local owner PC.

## Exact evidence

**Code and seven new tests pinned SHA:** `bb7cec1ea768ae15b4141cc9609ccff94707da6e`
**Workflow commit SHA:** `ed694bc272ac52477d90acf3836f5fdf74fc399e`
**Source blob SHA:** `354898f17bb1c682e2b3950bbc66225bbd4983b8`
**Integrated process wrapper blob SHA:** `e2d3fd0e3eed9a3e2bfec170bc35e405ae3a6fd8`
**New tests blob SHA:** `0e63d14afdc72e86a90f50c86a66828dc96807c3`

**GitHub Actions:** [Run #43331936900](https://github.com/eltokhey1/hermes-agent/actions/runs/43331936900), attempt 1, status `completed`, conclusion `success`.

| GitHub-hosted job | Job ID | Tests | Result |
| --- | --- | ---: | --- |
| Ubuntu latest / Python 3.13 | 131578510493 | 122 | PASS |
| Windows latest / Python 3.13 | 131578510819 | 122 | PASS |
| **Total** | | **244** | **244 PASS, 0 FAIL, 0 unittest SKIP** |

Expected skipped *workflow step*: Windows-only inventory assertion intentionally skipped on Ubuntu; it **passed** on hosted Windows.

Executed command:

```bash
python -m compileall -q approvals.py orchestrator.py isolated_authority_research.py durable_anchor_research.py tests
python -W error -m unittest discover -s tests -v
```

Raw summary:

```text
VERIFIED_DURABLE_ANCHOR_SHA=bb7cec1ea768ae15b4141cc9609ccff94707da6e
Ubuntu:  Ran 122 tests in 8.207s; OK
Windows: Ran 122 tests in 26.295s; OK
HOSTED_WINDOWS_PREFLIGHT_CONTRACT=PASS
OWNER_WINDOWS_P0_P1=UNVERIFIED
PRODUCTION=HOLD
HITL=REQUIRED
INDEPENDENT_OS_ACCOUNT_ACL=NOT_TESTED
AUTHENTICATED_HUMAN_OWNER=NOT_TESTED
MONOTONIC_EXTERNAL_COUNTER=NOT_TESTED
REAL_TOOL_SIDE_EFFECTS=DISABLED
```

## Explicit limits and nonacceptance

1. **No owner hardware access.** The read-only ruOS tenant view returned `machines: []` and `desktops: []`; rendezvous telemetry `unavailable` means it cannot positively establish the real Windows host offline. The separate ruOS Lite web browser is NOT the host. P0/P1 on the Windows machine remains `NOT_TESTED`.
2. **No separate OS identity/ACL.** Research checkpoint and SQLite share a hosted CI OS account; file permissions, signer-key custody, separate Windows service account, dedicated independent ESTOP/watchdog and protected human authorization endpoint are **NOT PROVEN**.
3. **No true monotonic anti-rollback.** Although a synthetic checkpoint epoch increases, an actor who rolls back BOTH the old signed checkpoint and the old DB could escape detection. A real protected external monotonic counter / hardware anchor or independently audited remote service is still required.
4. **Partial-commit crash gap.** DB changes and checkpoint writes are not one atomic transaction. A process crash between them yields a mismatch on next start, which must be held for manual reconciliation; it must **not** be blindly auto-repaired, re-bootstrapped, or retried. No complete real P1 crash/drain proof exists.
5. **Synthetic human identity.** HMAC-authenticated test IPC capability and test harness signer key do not prove the owner logged in, gave action-specific consent, or was protected by CSRF, hardware credentials or a separate privileged service. The test harness itself supplies the synthetic signer secret.
6. **ESTOP limitation.** The demonstration persists a latch after handling the owner's synthetic stop request; independent emergency stopping of a hung signer, mid-flight tool call or physical action is NOT TESTED.
7. **No production dispatch.** Only deterministic `demo.review`/`demo.echo` inert previews are permitted; `external_effects_enabled=false`. Passing the test is not authorization to merge, deploy, send, or run external effects.

## Next owner-hardware gate (NOT EXECUTED)

1. First use the **existing** `owner-lab/multiagent-safe-v3/WINDOWS_READONLY_PREFLIGHT.ps1` on the actual Windows device, only when the owner has it available, and redact its receipt. Confirm current disk/CPU/RAM/build, state DB existence and backup target. Hosted Windows inventory is not a substitute.
2. For P0, obtain independently protected, consistent SQLite+WAL backup (without deleting or overwriting original data); restore into disposable isolated directory/VM and verify DB integrity, row count, event ledger root and Hermes functional recovery with raw outputs and exact SHA. Verify file ACL-deny tests and signer separation.
3. For P1, conduct controlled crash/ESTOP tests inside the disposable instance with real owner-authenticated approval (action hash, nonce and expiry), independent watchdog, no blind retry for ambiguous external effects and separately protected audit anchor.
4. Human review and explicit one-time, SHA-bound GO/NO-GO decision required after the above results. Production remains HOLD.

**No writes to owner Windows, no merge, no deployment, no main/PR modification.**
