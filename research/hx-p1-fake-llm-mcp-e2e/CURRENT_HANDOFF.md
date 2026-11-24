# Hermes HX P1 — Local fake-provider MCP STDIO E2E evidence handoff

**Observed UTC date:** 2026-11-24  
**Source repository:** `eltokhey1/hermes-agent`  
**Research branch:** `research/p1-fake-llm-mcp-e2e-20261124`  
**Exact tested source SHA:** `c4a5ef9e0aa96d4f36cab9648793d6243e07e11c`  
**Workflow:** `.github/workflows/hx-p1-fake-llm-mcp-e2e.yml`  
**Source of truth:** https://github.com/eltokhey1/hermes-agent/actions/runs/45460738200  
**Job:** `138682285981` — GitHub Actions `completed/success`, attempt 1.

## What was executed

1. Python 3.14.7, pytest 9.1.1 and project pinned test environment on standard `ubuntu-latest`.
2. Actual Hermes E2E suite against a **local fake LLM provider** and a **real MCP 2.x stdio fixture**:
   - `tests/e2e/core/mcp_plugins/test_mcp_stdio_conformance.py`
   - `tests/e2e/core/parity/test_mcp_lifecycle.py`
3. Mount/Network/PID namespaces, **new PID namespace-local procfs** via `unshare --mount-proc`, read-only repository, restricted writable temp metadata only, drop to unprivileged runner UID, all capabilities zero and `no_new_privs`. No external network, secrets or paid provider.
4. Source-identity checks: checkout at exact source SHA; `HX_PROC_PID_NAMESPACE=VERIFIED`, `HX_OS_BOUNDARY=VERIFIED_PARTIAL` and unchanged `AGENTS.md` SHA256: `a8948f7bf162528ec9f2a9ca5f007e77f0c5f0901a428c92d0f77ef1185cfb38`.

## Actual GitHub log verdict

- `8 tests passed, 0 failed` over 2 files, with **5 additional xfail** in the MCP conformance file. 5 xfail must **NOT** be called PASSED; they are pre-existing known gaps, including `#120227` for unsupported MCP image formats. The source uses a runtime `known_gate` that xfails **only for recognized active symptoms**.
- Lifecycle test file: `2 passed` (fast server death / host crash process-tree reaping).
- MCP stdio conformance file: `6 passed, 5 xfail`.
- `HX_MCP_E2E_TESTS=PASS` and `SOURCE_UNCHANGED_SHA256=...`.
- Prior initial run https://github.com/eltokhey1/hermes-agent/actions/runs/45459802453 at SHA `1db69fd230dd4a23cd93d89dc1ada7dd5e64d04c`: `6 passed, 2 failed` lifecycle checks. It was followed by a **harness-only** `--mount-proc` correction, not source test modifications. Do not reinterpret the first failure as a proven production security vulnerability.

## Other already-hosted evidence (distinct SHA)

- Component regression: https://github.com/eltokhey1/hermes-agent/actions/runs/45348171650
- Exact tested SHA: `41bddbb70850f89779b78aa395ecb6b4a6c5686d`.
- 6 actual source test files; 63 passed, 0 failed; MCP/Browser/Inline/approval/ESTOP components. Not the same SHA as the 8 E2E test run. **Do not sum these as 71 tests at a single SHA.**

## NO-GO boundaries

- `PRODUCTION=HOLD`, `HITL=REQUIRED`, `G0/G-CODE/G1=NO-GO`, default paid spend `$0`.
- No true remote LLM, browser navigation with real external website, inline external effects, externally authenticated owner sign-off, independently controlled OS broker, offhost signed witness, or hard in-flight ESTOP tested here.
- XFAIL=5 means several known E2E contract gaps are **not closed**.
- GitHub Action success is **research evidence**, not a 9.8/10 acceptance score or independent billing audit.
- No changes to production code, no merge, no deploy, no secrets used. This documentation commit is **not** the SHA tested in CI; the evidence SHA above is authoritative.

## Smallest next test

First target the 5 known MCP image-format xfails in a separate research-only CI with strict acceptance mode and a pinned source SHA (expect FAIL until the source behavior is fixed). For any future source fix, require independent review and an explicit approval before merge. Keep a signed offhost witness and owner approval as separate gates.
