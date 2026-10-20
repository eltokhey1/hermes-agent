# Hermes P0 — Legacy audit safety regression (19 October 2026)

**Decision: HOLD / DO NOT RUN legacy V4 on the owner's Windows host without remediation.**

This note refers only to the optional helper `Hermes_P0_Evidence_Audit.py` embedded in the private **Hermes_Current_Canonical_2026-10-18.zip** package. It does **not** establish that Hermes core, GitHub main, or production credentials have been compromised. No actual Windows files, secrets or accounts were accessed.

## Observed adversarial results (local isolated Linux + synthetic fixture)

A throwaway Git repository and backup folder were created under an ephemeral temporary directory, with an explicitly fake marker `SECRET_CANARY_FAKE_1234`.

| Test | Synthetic result | Why this matters |
|---|---|---|
| Branch label includes fake canary | **LEAK reproduced**: `inventory_repo()` includes unsanitized `branch` in its JSON | Branch names can expose private identifiers in published reports |
| Backup folder name includes fake canary | **LEAK reproduced**: `inventory_backup()` emits `folder_name` verbatim | Local paths/secret-like user labels may be disclosed |
| `GIT_TRACE` inherited by helper | **WRITE reproduced**: test created trace file | The helper invokes `git` without filtering inherited `GIT_*` variables and optional locks, so its blanket read-only claim is unsupported |

**Regression outcome: three of three adversarial checks reproduced the suspected problem.** No real secret was used. This is not a Windows execution test.

## Ownership and non-duplication

- P0-01: repository/installed-runtime inventory: prefer the **sanitized candidate in draft PR #7**, whose code removes inherited `GIT_*`, disables optional Git locks/fsmonitor, and does not emit branch names, paths or remote URLs. It is still a *candidate* and requires independent Windows verification.
- P0-03/P0-04: backup integrity and functional restore: **do not substitute PR #7** for these tests. The legacy backup-manifest helper must be patched and independently reviewed, or use a different safely isolated, redacted verifier. Manifest hash equality never proves a usable recovery.
- Keep the original canonical ZIP immutable as historical evidence; do not propagate the outdated V4 helper to Windows as an approved procedure.
- All P0/P1 acceptance gates remain UNVERIFIED/HOLD. **Do not merge or deploy** from this report.

## Minimum fix-and-test acceptance

1. Filter inherited `GIT_*` and Git trace/config overrides, run built-in Git commands without optional locks or network, and prove no filesystem writes under adversarial synthetic trace settings.
2. Never emit full paths, branch names, backup directory names, remote URLs, secret-bearing filenames or environment variables. Emit only typed location labels, counts, boolean flags, and safe error codes.
3. Reject symlinked/reparse paths and non-canonical repo roots; enforce manifest size/entry constraints and fail closed for malformed/duplicate/unsafe entries.
4. Rerun positive and negative tests in a throwaway repo, then perform authorized **read-only Windows** inventory and **actual isolated functional restore** with independent evidence.
5. Create no new portfolio work package: link each remediation to existing P0-01/P0-03/P0-04 source IDs.

**Scope:** synthetic regression only; production readiness = NO, spending = $0, credential exposure to the test = none.
