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
SHA-256: `f85bf5021fa2e05fc06abb52502932d09952a19fb0c1fcf6f83106158ac4278f`.
Run `python -I -B -S hermes_bridge_v1.py` once, or add `--poll --interval 30` for manually opted-in polling.
Stop a foreground poll with Ctrl+C. Do not run multiple bridge copies concurrently.

## Tests and security

`test_bridge_v1.py` now contains 38 synthetic/adversarial cases; the three new base64 validation regressions are published but have **not** been run as the repository suite. Independent standalone validation of the decoding logic passed 4/4 synthetic cases; this is not Windows or CI acceptance.
Windows-local acceptance is NOT proven until a receipt arrives and is checked here.
`status=PASS` means Python syntax parsed, **not** that the code executed or passed behavioral tests.
Every response explicitly includes `executed=false` and `production=HOLD`.
The repository is public: do not send secrets, customer data, or confidential code.
Network/OS isolation is not proven; GitHub write access is not cryptographic job signing.
Never allow code execution without a separate, independently accepted policy gate.

## Resilient pilot supervisor (separate from live v1)

Files: `hermes_bridge_supervisor_v1.py`, `test_supervisor_v1.py`, and `start_bridge_pilot.ps1`.
The PowerShell launcher downloads four pinned sources, validates exact SHA-256, runs the 38 + 25 offline tests, performs a **single** initial scan, and optionally starts a local polling process if `-Poll` is supplied. The supervisor keeps local `status.json`, verifies the pinned worker before each scan, refuses unknown worker output (including spoofed or non-final success markers) and unexpected worker stderr, and stops after five consecutive failures. On Windows it uses a one-instance file lock. Startup on device boot is not configured.

Published SHA-256:
- `hermes_bridge_v1.py`: `f85bf5021fa2e05fc06abb52502932d09952a19fb0c1fcf6f83106158ac4278f`
- `hermes_bridge_supervisor_v1.py`: `e5e861db8a73811f7621706431e58a7e9b5547b90232652235d83811bbdd0d65`
- `test_bridge_v1.py`: `2a200312893d19d74cd19def74ecc8e652b4ade9600e93321376235e6e1e9ac3`
- `test_supervisor_v1.py`: `783e9cd24afb5875d021e3a8d941c5b3f7bd8eeb41dd1daf9f800ccbc2f2039c`

Manual launch on Windows after obtaining and reviewing the PowerShell launcher:
`powershell -NoProfile -File .\start_bridge_pilot.ps1 -Poll`
Only if the local operator executes this will the supervisor start. **No unattended Windows run of the supervisor or 63 tests has yet been verified.**

## Observed GitHub round-trip

`outbox/job-20261025-01.json` is Windows-generated and was independently fetched through the GitHub connector: `status=PASS`, `executed=false`, `function_names=['sum_range']`. The follow-up request `inbox/job-20261025-02.json` is published but its reply was not yet found; the original background process may be stopped. The status snapshot in `ACCEPTANCE_SNAPSHOT_20261025.md` governs acceptance. No claim of Hermes agent readiness.

## Verified launcher artifact

`start_bridge_pilot.ps1` SHA-256: `d6050e3b349af2a4b559254f2074efd26abb743ee07324f9c1c39f8a5e227aa5` (verified by independent GitHub fetch + digest calculation). The launcher itself has NOT been executed on Windows. The Windows operator must obtain and verify the exact file before running it with `-Poll`. This script does not install a scheduled task or service and will stop if its offline tests fail. A sleeping/suspended PC cannot be assumed to continue polling.
