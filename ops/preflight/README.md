# Hermes owner P0: read-only local inventory

**State: CANDIDATE — NOT DEPLOYED or tested on Windows.**

This stdlib-only Python script produces a metadata-only, sanitized JSON report in the terminal. It **does not run Hermes, read project source contents, read .env files, scan credentials, call the network, install dependencies, change Git, or save reports.** No filenames, directory paths or remote URLs are output.

## Requirements and command

- Python 3.11+ and Git.
- `--repo` must point to the **exact Git repository root**. A child folder that inherits a parent Git repository is rejected with `REPOSITORY_ROOT_MISMATCH` (nonzero exit).
- From the actual Hermes repository root on Windows PowerShell:

    python .\ops\preflight\read_only_inventory.py --repo .

If the script was downloaded separately, specify the absolute script path and --repo pointing at the actual local checkout. Do not pipe installer code from the internet to PowerShell.

## Installed Windows Hermes is not necessarily a Git checkout

The operator-reported Hermes installation is an **installed runtime/data directory** that did **not** contain a `.git` directory when inspected. This preflight intentionally audits a *Git checkout*, not the installed binary and not `HERMES_HOME`. Therefore **do not point `--repo` at the installed Hermes home and treat `NOT_A_GIT_REPOSITORY` as a corrupted installation**. That result only means this tool cannot prove the installed build's source commit.

The required P0-01 identity work has two distinct receipts: (a) read-only installed-binary/version/digest and active-home metadata, with no secret content; (b) independently inspected Git checkout HEAD/dirty state where a checkout actually exists. Compare code provenance explicitly; a SHA-256 digest of the installed executable does **not** establish a Git commit. No auto-fetch, reinstall, forced sync or credential inspection should be performed to bridge this gap. Owner-reported host facts are partial evidence only.

## Gate interpretation

- A nonzero exit or error_code means **UNKNOWN/BLOCKED**.
- working_tree_dirty=true means STOP: preserve and inspect local changes prior to upgrades.
- If head_sha differs from the reviewed fork, STOP: reconcile the checkout with GitHub first.
- project_markers and docker_cli_on_path indicate presence only, **not readiness**.
- A clean Git tree does not prove absence of secrets, successful recovery, service health, security or functional correctness.

## Tests for this tool only

From the repository root:

    python -m unittest discover -s .\ops\preflight -p test_read_only_inventory.py -v

Tests create and commit in temporary throwaway Git repositories. The inventory command itself is read-only. The source contains 15 inventory tests, including a regression for a Unicode line-separator filename when `core.quotePath=false`. The current commit's GitHub-hosted synthetic CI result must be checked separately; hosted Windows is **not** the owner's Windows machine or application acceptance.

## LOCALAPPDATA identity guard — 2026-10-19

On Windows, `hermes_windows_install_directory_present` is now `null` if `LOCALAPPDATA` is missing or relative. This prevents accidental detection of an unrelated relative `hermes` directory. A true value only proves that the directory exists, **not** that it contains a working Hermes installation or that the installed binary matches GitHub.

Three additional test methods cover missing, relative and absolute `LOCALAPPDATA` cases. The inventory suite now has **15** test methods. The earlier `9/9` Linux result is historical; only GitHub-hosted test results for the **exact** commit SHA count as synthetic CI evidence, never as owner-machine acceptance.

## Security / limits

The script disables optional Git locks, fsmonitor and recursive submodules, and filters inherited `GIT_*` environment variables before running Git (preventing unexpected `GIT_TRACE` output and repository-override variables). Git and the host are still not sandboxed. Review before running. Do not share other local logs or environment-variable dumps. Only independently verified backups restored in isolation pass the P0 recovery gate.

See ops/OWNER_READINESS_GATES.md in draft PR #4 for the complete acceptance matrix.
## Read-only SQLite backup preflight (2026-10-24)

Added `verify_sqlite_snapshot.py`, an offline **preflight only** for an operator-created stable SQLite backup (not the active Hermes database). It opens the snapshot in SQLite immutable mode, reconstructs it *in memory*, runs `PRAGMA integrity_check` and `PRAGMA foreign_key_check`, confirms tables exist, and checks the source SHA-256 has not changed. It prints only sanitized counts, digest and gate labels, not row contents or paths. It refuses a source with separate WAL/journal sidecars or a snapshot over 512 MiB; it never overwrites the live database or writes a restored copy to disk.

From the **actual checkout** with an independently prepared offline backup, Windows PowerShell usage:

```powershell
python .\ops\preflight\verify_sqlite_snapshot.py --snapshot 'C:\PATH\TO\OFFLINE\BACKUP\state.db'
```

**Never pass a live, actively changing `state.db` as the snapshot.** This validates SQLite file consistency only. It does **not** demonstrate protected/off-device backup, full Hermes application startup, ACL, secrets isolation, ESTOP, authenticated approvals, independent audit anchor or P0/P1 acceptance. Synthetic CI runs on GitHub-hosted Windows/Ubuntu with throwaway fixtures, and must not be treated as owner-machine evidence. `PRODUCTION=HOLD`.

The preflight also rejects snapshots whose **parent directories** are symlinks or Windows junctions, to avoid silently following an alias into a live Hermes database. A normal snapshot path with a redirected parent must be copied to an independently prepared, stable, non-redirected location by the owner before preflight. This is a fail-closed path guard, **not** proof that the backup is offline or protected.
