# Hermes HX P1 — Boundary Component Regression Handoff

**Date:** 2026-11-24 (UTC).
**Scope:** R1 isolated research branch; no production code, merge, deploy, or external service connection.

## Pinned hosted evidence

- Repository: `eltokhey1/hermes-agent`.
- Branch: `research/p1-python314-shadow-20261123`.
- Exact CI-tested SHA: `41bddbb70850f89779b78aa395ecb6b4a6c5686d`.
- Workflow: `.github/workflows/hx-p1-boundary-component-regression.yml`.
- GitHub Actions: https://github.com/eltokhey1/hermes-agent/actions/runs/45348171650
- Job: `138287726237`, final `completed/success`.
- Hosted log: `TESTENV_PY314=VERIFIED 3.14.7 PYTEST 9.1.1`.
- Hosted log: `HX_OS_BOUNDARY=VERIFIED_PARTIAL network_isolated+readonly_repo+zero_caps+no_new_privs`.
- Hosted log: `6 files, 63 tests passed, 0 failed` followed by `HX_BOUNDARY_TESTS=PASS`.
- Hosted log: `SOURCE_UNCHANGED_SHA256=a8948f7bf162528ec9f2a9ca5f007e77f0c5f0901a428c92d0f77ef1185cfb38` for `AGENTS.md`.
- Source tree readonly except a **single writable bind mount** for synthetic test-runner metadata `test_durations.json`, mapped to an ephemeral runner-temp file. No code-writing exceptions.
- Runner: `ubuntu-latest`, `contents: read`, checkout credentials not persisted; no paid integration invoked.

## Six source-backed test files

1. `tests/hermes_cli/test_mcp_security.py` — hardening for malicious configured MCP server commands.
2. `tests/tools/test_browser_secret_exfil.py` — browser/web secret-exfil prevention.
3. `tests/tools/test_browser_private_page_action_guard.py` — disallowed private-page interactions.
4. `tests/agent/test_inline_tool_executors_memory_args.py` — real inline memory executor test contract.
5. `tests/cron/test_estop.py` — ESTOP sentinel behavior, which pauses **new** work only.
6. `tests/hermes_cli/test_approval_transport.py` — approval transport and fail-closed host routing, including rejection of stale decisions.

## Failure history and correction

- Run #45347454657 at SHA `43c6472537405ff03c83b84924909dc1f15b8c2a`: workflow YAML invalid; zero jobs.
- Run #45347699234 at SHA `7a0dd66477e2d9cbfd61f58adaa692167015ccba`: all 63 component tests passed; runner exited with EROFS writing `test_durations.json`. This was not a Hermes test failure.
- Run #45348171650 at SHA `41bddbb70850f89779b78aa395ecb6b4a6c5686d`: **success**, controlled temporary metadata bind mount maintained source readonly.

Earlier independently spawned *same-runner* witness:
https://github.com/eltokhey1/hermes-agent/actions/runs/45343699830
at SHA `d5175d9cea2654e81b2bdd1c072defe417e09f18`. Same-runner subprocess is **not** external independent witness.

## Strict evidence classification

- VERIFIED: six actual original-source test files, 63/63 tests green, Python 3.14.7, pytest 9.1.1, network namespace, readonly source, no_new_privs and zero caps in this research job.
- VERIFIED_PARTIAL: browser/mcp/inline/approval/ESTOP behavior exercised through selected unit/integration tests. Not full unified actual-session E2E.
- UNKNOWN: full Browser navigation, MCP transport lifecycle, external effects from inline executor in a real LLM conversation; independent OS broker attestation; offhost signed witness.
- NOT_VERIFIED: owner signature cryptographic binding to request/task/source SHA; owner decision enforcement across boundaries; hard in-flight kill (not the existing ESTOP contract); recovery and rollback.
- NO-GO: production acceptance, G0/G-CODE/G1 gates and any `9.8/10` production score. `PRODUCTION=HOLD`, `HITL=REQUIRED`, paid spend default $0; invoice total not independently audited.

## Smallest next safe step

Use a fake local LLM provider and a confined terminal/browser/MCP fake transport in one policy-gated end-to-end test on a separate research workflow; demonstrate rejection of an unauthorized sensitive operation, correlate event IDs, and verify an external **separately authorized** witness. Do not weaken source readonly, permit real external network, introduce secrets, or claim full production readiness from component tests alone.
