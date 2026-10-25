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
