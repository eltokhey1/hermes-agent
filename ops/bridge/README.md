# Hermes GitHub Code Transport — v1 Pilot

**Status:** read-only code review transport; NOT a Hermes agent deployment. `PRODUCTION=HOLD`, `G0/G-CODE/G1=NO-GO`.

Only on isolated branch `sandbox/hermes-transport-smoke-20261025`; no merge into `main`.

## Operation

1. ChatGPT writes a JSON job named `job-YYYYMMDD-NN.json` under `ops/bridge/inbox/`.
2. A manually started Windows Python bridge uses authenticated `gh api` to fetch jobs.
3. It validates schema, job ID, read-only approval, and source SHA-256, then checks Python syntax using `ast.parse()` without executing the submitted code.
4. It posts a receipt under `ops/bridge/outbox/` (idempotent; no overwrite).
5. Optional `--poll --interval 30` repeats while the operator keeps the bridge process running. No boot startup or service is installed.

**Not supported:** untrusted code execution, unattended Aider edits, arbitrary commands, production deploy, secrets, finance, automatic merge, external messages.

## Job schema

See `inbox/job-20261025-01.json`. Required: `schema=hermes.bridge.job.v1`, filename-matching `job_id`, `operation=python_ast_check`, `approval=read_only`, `source` (<=8192 UTF-8 bytes), `source_sha256`.

## Windows usage

Requires Python, GitHub CLI `gh`, and an authenticated GitHub session.
Download the exact `hermes_bridge_v1.py` from this branch and compare SHA-256 before executing.
SHA-256: `fb8706ac8ae5ecebd9de06e97c23ae4639b09733ad1984f2e097bb38054a046a`.
Run `python -I -B -S hermes_bridge_v1.py` once, or add `--poll --interval 30` for manually opted-in polling.
Stop a foreground poll with Ctrl+C. Do not run multiple bridge copies concurrently.

## Tests and security

`python -m unittest -v test_bridge_v1.py` passes 35 synthetic/adversarial cases on the authoring machine.
Windows-local acceptance is NOT proven until a receipt arrives and is checked here.
`status=PASS` means Python syntax parsed, **not** that the code executed or passed behavioral tests.
Every response explicitly includes `executed=false` and `production=HOLD`.
The repository is public: do not send secrets, customer data, or confidential code.
Network/OS isolation is not proven; GitHub write access is not cryptographic job signing.
Never allow code execution without a separate, independently accepted policy gate.

## Resilient pilot supervisor (separate from live v1)

Files: `hermes_bridge_supervisor_v1.py`, `test_supervisor_v1.py`, and `start_bridge_pilot.ps1`.
The PowerShell launcher downloads four pinned sources, validates exact SHA-256, runs the 35 + 20 offline tests, performs a **single** initial scan, and optionally starts a local polling process if `-Poll` is supplied. The supervisor keeps local `status.json`, verifies the pinned worker before each scan, refuses unknown worker output, and stops after five consecutive failures. On Windows it uses a one-instance file lock. Startup on device boot is not configured.

Published SHA-256:
- `hermes_bridge_v1.py`: `fb8706ac8ae5ecebd9de06e97c23ae4639b09733ad1984f2e097bb38054a046a`
- `hermes_bridge_supervisor_v1.py`: `cf7a9f38aa2f2da613b981f856f066c06602c329287f5b35925f40ac3691644b`
- `test_bridge_v1.py`: `3225029266f7ed9a874c8950bf36139ecc10da7f255690364fa6e9c7f6814462`
- `test_supervisor_v1.py`: `2c2475723cd10965230afb68a58d8acb62eb83c37ad5a6ddc4945b535b3af3fe`

Manual launch on Windows after obtaining and reviewing the PowerShell launcher:
`powershell -NoProfile -File .\start_bridge_pilot.ps1 -Poll`
Only if the local operator executes this will the supervisor start. **No unattended Windows run of the supervisor or 55 tests has yet been verified.**

## Observed GitHub round-trip

`outbox/job-20261025-01.json` is Windows-generated and was independently fetched through the GitHub connector: `status=PASS`, `executed=false`, `function_names=['sum_range']`. The follow-up request `inbox/job-20261025-02.json` is published but its reply was not yet found; the original background process may be stopped. The status snapshot in `ACCEPTANCE_SNAPSHOT_20261025.md` governs acceptance. No claim of Hermes agent readiness.

## Verified launcher artifact

`start_bridge_pilot.ps1` SHA-256: `745c771bb8692914b61b992df79993286690b44ee7a12d45c441c795edf11a8e` (verified by independent GitHub fetch + digest calculation). The launcher itself has NOT been executed on Windows. The Windows operator must obtain and verify the exact file before running it with `-Poll`. This script does not install a scheduled task or service and will stop if its offline tests fail. A sleeping/suspended PC cannot be assumed to continue polling.
