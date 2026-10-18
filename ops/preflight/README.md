# Hermes owner P0: read-only local inventory

**State: CANDIDATE — NOT DEPLOYED or tested on Windows.**

This stdlib-only Python script produces a metadata-only, sanitized JSON report in the terminal. It **does not run Hermes, read project source contents, read .env files, scan credentials, call the network, install dependencies, change Git, or save reports.** No filenames, directory paths or remote URLs are output.

## Requirements and command

- Python 3.11+ and Git.
- From the actual Hermes repository root on Windows PowerShell:

    python .\ops\preflight\read_only_inventory.py --repo .

If the script was downloaded separately, specify the absolute script path and --repo pointing at the actual local checkout. Do not pipe installer code from the internet to PowerShell.

## Gate interpretation

- A nonzero exit or error_code means **UNKNOWN/BLOCKED**.
- working_tree_dirty=true means STOP: preserve and inspect local changes prior to upgrades.
- If head_sha differs from the reviewed fork, STOP: reconcile the checkout with GitHub first.
- project_markers and docker_cli_on_path indicate presence only, **not readiness**.
- A clean Git tree does not prove absence of secrets, successful recovery, service health, security or functional correctness.

## Tests for this tool only

From the repository root:

    python -m unittest discover -s .\ops\preflight -p test_read_only_inventory.py -v

Tests create and commit in temporary throwaway Git repositories. The inventory command itself is read-only. Local sandbox validation on Python 3.13/Linux: 6/6 passing. This is **not** an application acceptance test and **not** a Windows test.

## Security / limits

The script disables optional Git locks, fsmonitor and recursive submodules, but Git and the host are not sandboxed. Review before running. Do not share other local logs or environment-variable dumps. Only independently verified backups restored in isolation pass the P0 recovery gate.

See ops/OWNER_READINESS_GATES.md in draft PR #4 for the complete acceptance matrix.