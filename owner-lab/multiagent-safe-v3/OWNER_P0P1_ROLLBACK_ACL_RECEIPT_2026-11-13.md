# Hermes Owner Lab — P0/P1 blockers, rollback floor & hosted Windows ACL receipt

Date (Tripoli): 2026-11-13. GitHub run timestamp: 2026-11-13 UTC.
Mode: **R1 research-only / NO-GO / no real external effects**.
Repository: `eltokhey1/hermes-agent`, research branch `research/owner-p0p1-rollback-guard-20261113`.
Source tests pinned SHA: `32bd651531e1d136a37f46ae1752df08ba43884a`.
Workflow commit SHA: `50b0f758a6ed1a88f947a421f2dd64d68e51f03d`.
Evidence: [GitHub Actions Run #43334654885](https://github.com/eltokhey1/hermes-agent/actions/runs/43334654885), attempt 1, **completed / success**.

## Tests that were actually executed

| Environment | Job ID | Evidence | Verdict |
| --- | ---: | --- | --- |
| GitHub hosted Ubuntu / Python 3.13 | `131587667960` | `Ran 129 tests in 5.897s; OK` | 129 PASS |
| GitHub hosted Windows / Python 3.13 | `131587667509` | `Ran 129 tests in 15.716s; OK` | 129 PASS |
| Separate disposable Windows hosted ACL job | `131587667216` | `WINDOWS_DISPOSABLE_DISTINCT_PRINCIPAL_ACL_WRITE_DENY=PASS` | PASS |
| **Total synthetic Python tests** | | 258 | **258 PASS, 0 FAIL, 0 unittest SKIP** |

Windows ACL test: created a *temporary non-admin local test principal on the disposable GitHub-hosted runner*, applied restrictive NTFS DACL to a synthetic checkpoint directory and a child file, attempted an actual write with the restricted principal, validated write denial and unchanged SHA-256, and attempted cleanup of the test principal and scratch directory. No named Hermes host, production file, real account, or user data was accessed or changed. A log-level PASS is **not** a substitute for inspecting and enforcing ACLs on the owner device.

CI commands:
```bash
python -m compileall -q approvals.py orchestrator.py durable_anchor_research.py isolated_authority_research.py tests
python -W error -m unittest discover -s tests -v
```
Windows ACL job:
```powershell
.\WINDOWS_HOSTED_ACL_RESEARCH.ps1
```

## What changed (research branch only)

- `durable_anchor_research.py` now accepts optional `minimum_expected_epoch` supplied from a **separate trusted monotonic source**, rejecting signed but older checkpoint receipts with `ANCHOR_ROLLBACK_DETECTED`.
- `isolated_authority_research.py` forwards `minimum_expected_epoch` to the protected checkpoint verifier on startup. It does not mint an independent trusted epoch.
- `tests/test_monotonic_epoch_recovery_research.py` adds seven checks: isolated SQLite restoration, proof that *both DB+checkpoint can be rolled back together without an external floor*, rejection with a trusted floor, prevention of stale ESTOP by that floor, fail-closed handling of a DB commit before checkpoint advance, malformed floor types, and absence of real human identity attestation.
- `WINDOWS_HOSTED_ACL_RESEARCH.ps1` is guarded to run only in GitHub Actions' hosted Windows environment and touches **only temporary runner objects**. It does not install or configure the user's hardware.

Relevant pinned blob SHAs:
- `durable_anchor_research.py`: `44a6856ba8c70275446cac6bee7dee584d5b80bf`
- `isolated_authority_research.py`: `05a48a5d6fbb6338e18fabad065aa56d22cd66d5`
- `tests/test_monotonic_epoch_recovery_research.py`: `975fe8c19379f9a65ae0c1911e663a3e2876903d`
- `WINDOWS_HOSTED_ACL_RESEARCH.ps1`: `91b6f42a000221b79bccb9051b6f575a3fffc4bd`

## Exact remaining gates — do not promote

1. **Actual Hermes Windows host: BLOCKED / UNKNOWN.** ruOS `fleet_status` returned `machines: []` and `peer_telemetry: unavailable`; `desktop_status` returned `desktops: []`, with only a separate saved Lite browser. This does not prove the host is offline; only that no verifiable host access was available. Owner-hardware P0/P1 were **NOT_TESTED**.
2. **Real protected monotonic counter: NOT_IMPLEMENTED.** The new *floor interface* is conditional; the harness supplies an external value, but no privileged signer, independent counter service, TPM-backed key, or remote append-only epoch authority was deployed. Without a separately protected latest epoch, two-file rollback can *still* re-enable a previously cleared ESTOP. This was explicitly reproduced in the test suite.
3. **Windows host account/service isolation: NOT_TESTED.** Hosted Windows scratch ACL proof is not equivalent to the target Windows 11 machine's filesystem ACL, service identities, policy or hardening.
4. **Human owner authentication: NOT_TESTED.** The existing Owner Lab authority operates with synthetic HMAC capability tokens. A trusted human identity provider, a dedicated CSRF-protected channel inaccessible to agent tools, action-bound approvals and key custody remain to be implemented independently and assessed.
5. **P0 on the actual hardware: NOT_TESTED.** Run the existing `WINDOWS_READONLY_PREFLIGHT.ps1` only when the owner device is available; then, after human review, use a *consistent* verified backup of the real SQLite+WAL under protected ACLs and restore into a disposable isolated directory/VM, never over the existing DB.
6. **P1 real in-flight effects and independent ESTOP: NOT_TESTED.** The demo uses inert `demo.echo`/`demo.review`; no real tool dispatch, suspended operation, crash while in-flight, independent watchdog or external side effect was exercised. Uncertain external effects must remain `UNKNOWN` and never blindly retry.

## Evidence interpretation and next limited step

**VERIFIED:** a portable research interface that fails closed if a genuinely trusted epoch floor is supplied; actual hosted Linux/Windows 129-test suites; actual scratch-identity NTFS write denial on GitHub-hosted Windows; isolated synthetic backup/restore and crash-gap test.

**NOT VERIFIED:** production signer/counter, protected OS identity on the owner device, human authentication, real Windows P0 restore, real P1 ESTOP and external effect safety, independent human review.

Smallest next viable acceptance action: when host connectivity is independently verified, run the repository's existing **read-only** Windows P0 inventory, confirm disk space and backup target, and produce a specific, human-approved plan for P0 protected copy and isolated restore; do not execute a write or restart automatically.

`PRODUCTION=HOLD` · `HITL=REQUIRED` · `G0/G-CODE/G1=NO-GO`.
