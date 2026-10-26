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
The PowerShell launcher downloads four pinned sources, validates exact SHA-256, runs the 38 + 25 offline tests, performs a **single** initial scan, and optionally starts a local polling process if `-Poll` is supplied. The supervisor keeps local `status.json`, verifies the pinned worker before each scan, refuses unknown worker output (including spoofed or non-final success markers), a missing inbox, and unexpected worker stderr, and stops after five consecutive failures. A missing inbox is a DEGRADED scan, never a healthy acknowledgment. On Windows it uses a one-instance file lock. Startup on device boot is not configured.

Published SHA-256:
- `hermes_bridge_v1.py`: `f85bf5021fa2e05fc06abb52502932d09952a19fb0c1fcf6f83106158ac4278f`
- `hermes_bridge_supervisor_v1.py`: `edd4ccb304d18089fc7d8d317bf2f1e44358e8b12e5864cb76b9286e1adc8f61`
- `test_bridge_v1.py`: `2a200312893d19d74cd19def74ecc8e652b4ade9600e93321376235e6e1e9ac3`
- `test_supervisor_v1.py`: `a36794f0efa09a646c9ec0467c2ea7b2ec41aa5804cc8bbd7314d47d59421128`

Manual launch on Windows after obtaining and reviewing the PowerShell launcher:
`powershell -NoProfile -File .\start_bridge_pilot.ps1 -Poll`
Only if the local operator executes this will the supervisor start. **No unattended Windows run of the supervisor or 63 tests has yet been verified.**

## Observed GitHub round-trip

`outbox/job-20261025-01.json` is Windows-generated and was independently fetched through the GitHub connector: `status=PASS`, `executed=false`, `function_names=['sum_range']`. Follow-up receipts for jobs 02 and 03 are now independently present and matched to their requests; job 02 returned `PASS` and the deliberately invalid job 03 returned `SYNTAX_ERROR`. See `ACCEPTANCE_SNAPSHOT_20261025.md`. These receipts do **not** establish current Windows process continuity. The status snapshot in `ACCEPTANCE_SNAPSHOT_20261025.md` governs acceptance. No claim of Hermes agent readiness.

## Verified launcher artifact

`start_bridge_pilot.ps1` SHA-256: `6a581bf48b0246f743e0f8e48c916b8b09d67fab72e54bdfde19343790b28d5f` (verified by independent GitHub fetch + digest calculation). The launcher itself has NOT been executed on Windows. The Windows operator must obtain and verify the exact file before running it with `-Poll`. This script does not install a scheduled task or service and will stop if its offline tests fail. A sleeping/suspended PC cannot be assumed to continue polling.

## Bridge diagnostics and opt-in recovery (2026-10-25)

The Windows bridge has supplied AST receipts for jobs 01, 02 and 03; both follow-up receipts were independently verified for IDs, source digests, `executed=false`, `production=HOLD` and expected AST outcomes. **Do not infer local poller health from historical receipts.** GitHub alone cannot inspect Windows processes, sleep state, authenticated gh CLI health, or local stderr.

[recover_bridge_pilot.ps1](recover_bridge_pilot.ps1) is **read-only by default**. It reads the local supervisor status, process list and tail of local logs. Add the explicit `-Recover` switch to start **only** the previously downloaded, SHA256-pinned, AST-only supervisor when no matching bridge process exists. It never installs a Windows service or scheduled task, stops existing processes, executes received code, invokes Aider, or changes production settings.

Recovery script SHA-256: `37612c3a4cde22754db233960d72682aef4cdd9a05c9165ac37d2fa613545454` (Git blob `e68fe5928962b33d37bb87c23acf33bd4d15940a`). The source was checked for balanced delimiters and its Git blob was independently recomputed; **Windows PowerShell runtime acceptance is still UNKNOWN**.

The helper requires pinned files in `$env:LOCALAPPDATA\HermesBridgePilot`; if they are missing, use the existing verified `start_bridge_pilot.ps1` rather than bypassing verification.

**Read-only Windows path check:** `Test-Path -LiteralPath (Join-Path $env:LOCALAPPDATA 'HermesBridgePilot') -PathType Container`. A failed check under `Downloads\HermesBridgePilot` does **not** establish that the actual local state directory is absent. Inspect `status.json` under the `LOCALAPPDATA` path; do not interpret a missing status as proof of a running or stopped process. A started PID is not a completed scan. The actual response must appear in the GitHub outbox and pass `verify_receipts.py` before it is called VERIFIED.

A sleeping/suspended Windows device cannot keep polling. The repository launcher does not configure boot/wake startup; actual Windows scheduled-task persistence and post-reboot behavior remain unverified by GitHub.

## Windows scheduled launcher — 2026-10-26 diagnosis

Operator evidence: Task Scheduler returned `LastTaskResult=0` and `Queued` after launching local `start_supervisor.ps1`, but no `hermes_bridge_supervisor_v1.py` process remained. The latest `status.json` was stale (`2026-10-25T20:40:21Z`, `DEGRADED`, `WORKER_EXIT_NONZERO`, exit code 1); older stdout contained one `SCAN_OK`. These facts do not prove current Windows liveness or the root cause of Python's exit.

The operator-supplied launcher uses `Start-Process -PassThru` and checks only that a process object was returned. This proves spawning, **not** sustained health. Recommended minimal, fail-closed repair: a bounded post-spawn liveness check plus fresh supervisor status heartbeat, without unbounded restart; independently test synthetic success, immediate child exit, stale heartbeat, and concurrent instance. Review `scheduled.stderr.log` locally before assigning root cause. Do not change host services or enable execution of incoming code. `PRODUCTION=HOLD`; `G0/G-CODE/G1=NO-GO`. Keep this within the existing 45 WP / 120 IDs portfolio.
