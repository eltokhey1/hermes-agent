# Hermes Open Builder — GitHub transport acceptance snapshot

Date: 2026-10-25. Source of work-package truth remains the existing Hermes 45-WP/120-ID portfolio; this file is a **gate evidence snapshot**, not a parallel work backlog.

## Verified using GitHub and Windows reply

- ChatGPT GitHub connector created a SHA256-pinned one-shot smoke task on `sandbox/hermes-transport-smoke-20261025` and fetched it back, exact match.
- A Windows-local process using GitHub CLI executed the *pinned, fixed smoke fixture* and uploaded `ops/smoke_tests/ack_transport_smoke_20261025.json`; GitHub-side fetch confirmed `status=PASS`, `returncode=0`, `production=HOLD`, `isolation=NOT_PROVEN`.
- Read-only code transport job `ops/bridge/inbox/job-20261025-01.json` received Windows-local acknowledgment `ops/bridge/outbox/job-20261025-01.json`, `status=PASS`, `executed=false`, `function_names=['sum_range']`, source SHA256 matched.
- `PASS` here means successful **data transport and Python AST syntax analysis**. It is NOT Hermes runtime integration or successful code execution by Aider.

## Pending independent checks

- Job `ops/bridge/inbox/job-20261025-02.json` (`average`) was submitted. Its reply was **not yet seen** as of this snapshot. Cannot assert the background poller remains alive.
- `hermes_bridge_supervisor_v1.py` was published as an **opt-in** recovery wrapper for the previously verified local bridge file. It pins the worker SHA256, writes a local `status.json`, retries transient failures up to five times, and never runs submitted code.
- Tests: `test_bridge_v1.py` (35 cases), `test_supervisor_v1.py` (20 cases) are published for deterministic offline execution. **Do not mark these suites VERIFIED without a real test-run transcript/CI evidence linked to an exact commit.**
- Windows-side supervisor process, process lifetime across sleep/restart, ESTOP, OS process isolation, offline network isolation, and host backup/functional restore: UNKNOWN / NO-GO.

## Security / policy

- Public GitHub transport is limited to nonsensitive test snippets. No customer data, LC documents, passwords or secrets.
- The current v1 bridge **never executes untrusted code**; only `ast.parse()` is used on validated input. This is a syntax check, not safety certification or behavioral testing.
- Do not treat GH commit/receipt as authorization to run arbitrary model-generated code. A future Aider runner needs independently accepted local sandbox, pinned job permissions, HITL policy gate, bounded retries, allowlisted files, audit log, and replay protection.
- No merges, automated production deploys, external messages, secrets linking, spend, service auto-start, or new accounts.
- `G0=NO-GO; G-CODE=NO-GO; G1=NO-GO; PRODUCTION=HOLD`.

## Suggested next safe milestone

Verify the pending `average` receipt or diagnose Windows supervisor local status. Then run the 35+20 synthetic suites on Windows and capture SHA256 and process exit codes. Only after read-only transport is reliable should a separately authorized, fixed-fixture Aider+Ollama worker be piloted in an isolated non-production workspace.

## 2026-10-25 — independent receipt verifier and second negative-control task

- Job `job-20261025-03` was queued on the isolated branch at commit `a4a1b4ddd3cf82a3d96f3e0461109b3b0a651d1e` as a deliberately **invalid Python syntax** negative control. Its correct eventual receipt is `status=SYNTAX_ERROR`, `error_code=SYNTAX_ERROR`, `executed=false`. Do not report PASS for it.
- At the time of this update the GitHub outbox contains the Windows-confirmed receipt for `job-20261025-01` only; replies for `job-20261025-02` and `job-20261025-03` were not present. **Background Windows bridge health remains UNKNOWN.**
- A standalone read-only verifier `verify_receipts.py` and tests `test_verify_receipts.py` were added on the same isolated branch. The **exact published Git blobs** match the independently tested local copies (blob SHA `88bd0fe025d2b9a06d7b26220aec78f136727029` and `fc8d1a2f6f910362fb87c76fa4f3c3cf21c45682`). SHA-256 of the verifier is `8532ed9be2eb25089a5a61abbc4bfd20bb7ef5f4224a119c9c4f22e4627b11e4`.
- **TESTED_SYNTHETIC:** `python -m unittest -v test_verify_receipts.py`: **12/12 PASS**, exit 0, on the independent Linux Python execution environment. These tests cover request/receipt SHA mismatch, replayed job ID, production/execution markers, missing approvals, timestamp, positive syntax, and negative-control false success. **No Windows/CI run of this new suite has been established.**
- The verifier is read-only (`gh api` GET), and `VERIFIED_TRANSPORT_ONLY` asserts neither Windows process identity nor isolation nor any execution of submitted Python code. No merge, production, Aider auto-run or account/secret change was made.

## 2026-10-25 — bridge-poller recovery preparation

- Independently re-fetched GitHub outbox: `job-20261025-01` is Windows-origin and still matches its request with `status=PASS`, `executed=false`. `job-20261025-02` and `job-20261025-03` have **no receipt** as of this review; therefore `AUTO_POLLING=UNKNOWN`, not HEALTHY.
- Published `ops/bridge/recover_bridge_pilot.ps1` on the same isolated branch (commit `9e9d7fba47a48ea1521deb5480a1067bc95ecbc3`, Git blob `1f6f320e2fc34a239a97832052b1ee1b3c1cda27`, SHA256 `2d453983f9506a19107ea5494078d1d25bec5d0e540050de5d9f4a6e483389fa`). Its default operation is local, read-only process/status/log diagnostics. Explicit `-Recover` first enforces the SHA256 pins on the *existing* worker and supervisor and refuses to start a second process; it never executes GitHub-submitted code or changes production settings.
- **QA classification:** exact source blob match and static delimiter/policy checks `TESTED_SYNTHETIC`; Windows PowerShell parsing, process startup, read/write permissions, live `gh` polling, wake/sleep persistence and actual new receipt `UNKNOWN`. The helper is not installed or launched on Windows from this ChatGPT session.
- `PRODUCTION=HOLD`; `G0/G-CODE/G1=NO-GO`. No `main` changes, merge, cloud deployment, new secret, payment, or Windows service modification.

Blocked next milestone: the Windows-side operator/runtime must recover or keep the read-only bridge process alive; only an independently fetched, valid outbox receipt can promote tasks 02/03 to `VERIFIED_TRANSPORT_ONLY`. Do not forge replies from the cloud side.

## 2026-10-25 — verified follow-up receipts (independent recheck)

- **VERIFIED_TRANSPORT_ONLY:** `inbox/job-20261025-02.json` and `outbox/job-20261025-02.json` independently fetched from GitHub. Matching `job_id=job-20261025-02` and SHA-256 `dddb92dfc192f97e67d36a0b74b647ad9dd6563e58cc465adca146c4a0c4241f`; receipt `status=PASS`, `executed=false`, `production=HOLD`, `isolation=NOT_PROVEN`. Independently parsed the source as Python AST (no execution).
- **VERIFIED_TRANSPORT_ONLY (negative control):** `inbox/job-20261025-03.json` and `outbox/job-20261025-03.json` independently fetched from GitHub. Matching `job_id=job-20261025-03` and SHA-256 `f5359a386641932bec76ad82d3be08ca18a7ee9bd6e5f6b009127aa2b1de3d87`; receipt `status=SYNTAX_ERROR`, `error_code=SYNTAX_ERROR`, `executed=false`, `production=HOLD`, `isolation=NOT_PROVEN`. Independent AST parsing confirmed syntax rejection; **not PASS**.
- **Windows evidence, limited:** operator reported `Ran 63 tests ... OK` with exit code 0, and one supervisor scan `SCAN_OK`. Later local status showed `scans=1`, `polling=true`, and a stale timestamp (`age=132s`). No independent Windows process-liveness, subsequent scan, reboot persistence, OS isolation or functional restore evidence. `CONTINUITY=UNKNOWN`; do not equate a stale `HEALTHY` state with a live poller.
- **PR #16 / CI:** draft and unmerged at head `1fa194d64c055f3af4afca0ecc64893c3013f7b3`. GitHub-hosted `TradeDocs Offline Pilot` run `40146916279` completed successfully; general CI `40146916309` and Docker `40146916238` remained pending, Nix `40146916224` queued at this review. One passing workflow does not prove full CI acceptance.
- **Unchanged gates:** `G0=NO-GO`, `G-CODE=NO-GO`, `G1=NO-GO`, `PRODUCTION=HOLD`. Backup integrity and functional restore, host isolation and independent acceptance remain unverified by this review. No execution of submitted source, Aider invocation, merge, deployment, or Windows process modification.
- Evidence: [job 02 receipt](https://github.com/eltokhey1/hermes-agent/blob/sandbox/hermes-transport-smoke-20261025/ops/bridge/outbox/job-20261025-02.json), [job 03 receipt](https://github.com/eltokhey1/hermes-agent/blob/sandbox/hermes-transport-smoke-20261025/ops/bridge/outbox/job-20261025-03.json), [PR #16](https://github.com/eltokhey1/hermes-agent/pull/16), [passing pilot CI](https://github.com/eltokhey1/hermes-agent/actions/runs/40146916279).

## 2026-10-25 — fail-closed receipt verification regression

- Re-fetched both requests and receipts for `job-20261025-02/03` from the sandbox branch. IDs and SHA256 matched; `executed=false`, `production=HOLD`, `isolation=NOT_PROVEN`. Independent `ast.parse` checks: job 02 `PASS`; negative-control job 03 `SYNTAX_ERROR` (not PASS). **VERIFIED_TRANSPORT_ONLY**, not proof of an active Windows poller.
- Identified a fail-open inconsistency: a syntactically valid source could be accepted with receipt `status=PASS` while carrying `error_code=SYNTAX_ERROR`. Added a one-line rejection (`PASS_WITH_ERROR_CODE`) in `verify_receipts.py` and one regression test in `test_verify_receipts.py` on this sandbox branch only.
- **TESTED_SYNTHETIC (independent Linux Python):** reconstructed exact previous sources with Git blob SHA match; baseline **12/12 PASS**; new regression **FAILED before fix**; patched suite **13/13 PASS**, exit 0. Re-fetched published sources and matched exact independently tested Git blobs: verifier `3369ff310076469e90bf4d3401ca79bbb2616512`, test `d8f312273f1cf031b422d80f3de4550edd214f67`.
- Commits: [guard `56a0a3dfa7450bfee68951e775cd6dfb05696f67`](https://github.com/eltokhey1/hermes-agent/commit/56a0a3dfa7450bfee68951e775cd6dfb05696f67); [test `57eead56865389458a66fcc088ceb06e2b11cc49`](https://github.com/eltokhey1/hermes-agent/commit/57eead56865389458a66fcc088ceb06e2b11cc49).
- PR #16 remains open/draft/unmerged at `1fa194d64c055f3af4afca0ecc64893c3013f7b3`. `TradeDocs Offline Pilot` GitHub run `40146916279` success; general CI `40146916309` and Docker `40146916238` pending, Nix `40146916224` queued at this review. No general CI acceptance. Windows process continuity, OS isolation, functional restore and fresh backup integrity remain UNKNOWN. `G0/G-CODE/G1=NO-GO; PRODUCTION=HOLD`. No merge, deploy, Aider invocation, secret, external message, or Windows service change.


## 2026-10-25 — isolated Python diagnostics import repair (sandbox only)

- Rechecked GitHub inbox/outbox jobs 02/03 independently: matching IDs and source SHA-256; `executed=false`, `production=HOLD`, `isolation=NOT_PROVEN`. Local independent `hashlib.sha256` and `ast.parse` checks matched: job 02 `PASS`, job 03 `SYNTAX_ERROR` (negative control).
- Identified and reproduced an isolated-mode defect: under `python -I -B -S`, a sibling `from worker_exit_diagnostics_v1 import ...` can fail with `ModuleNotFoundError` on the worker nonzero-exit path. Independent isolated Python reproducer confirmed failure before and explicit `runpy.run_path` sibling-file lookup success after, without adding the script directory to `sys.path`.
- Patched only sandbox `hermes_bridge_supervisor_v2_candidate.py` to load the local allowlisted diagnostics via explicit file path; commit `ef3e9a80cf589ae495ff151207597d002928bc56`, Git blob `6c1d05244eb02f6697371eac55b72d7a841f0fc2`. Added a regression test for nonzero worker exit in isolated mode; commit `c012cde1c446f7ec1d1e230839a519cd933e03de`, Git blob `5ea639eb03b91df1c7c64e1ac86e1f21b2617f8f`. Both published files were re-fetched.
- **TESTED_SYNTHETIC:** standalone isolated-mode reproducer passed on independent Linux Python. **UNKNOWN:** complete updated v2 test suite, Windows v2 invocation, actual worker failure-path integration, CI on sandbox branch, Windows continuity, OS isolation, backup functional restore. Do not promote to VERIFIED runtime.
- PR #16 still open/draft/unmerged at `1fa194d64c055f3af4afca0ecc64893c3013f7b3`; TradeDocs Offline Pilot CI successful, general CI/Docker pending and Nix queued. No CI run found for sandbox branch.
- No changes to Windows, main, scheduled tasks, production, secrets, payments or external messaging. `G0=NO-GO; G-CODE=NO-GO; G1=NO-GO; PRODUCTION=HOLD`.
