# Hermes HX P1 — Real-turn fake-provider E2E handoff

**UTC date:** 2026-11-24  
**Decision:** RESEARCH=PARTIAL_PASS; PRODUCTION=HOLD; HITL=REQUIRED; G0/G-CODE/G1=NO-GO.  
**Paid spend policy:** $0 (no paid provider was invoked; actual provider billing not audited).

## Exact source-backed evidence

- Repository: https://github.com/eltokhey1/hermes-agent
- Research branch: `research/hx-p1-real-turn-fake-provider-20261124`.
- Research base SHA: `5163296ead8df9c24c20ceca53de49ce6aa8821d`.
- **Exactly CI-tested SHA:** `08df4ccbf9678dc0794d403489646a81b28a2433`.
- GitHub Actions: https://github.com/eltokhey1/hermes-agent/actions/runs/45469979159
- Job `138714993938`: `completed/success`, attempt 1.
- Source file: `tests/agent/test_hx_p1_fake_provider_write_denial.py`.
- Workflow: `.github/workflows/hx-p1-real-turn-fake-provider.yml`.
- GitHub log: `TESTENV_PY314=VERIFIED 3.14.7 PYTEST 9.1.1`.
- GitHub log: `HX_OS_BOUNDARY=VERIFIED_PARTIAL network_isolated+readonly_repo+zero_caps+no_new_privs`.
- GitHub log: `1 files, 1 tests passed, 0 failed` and `HX_REAL_FAKE_TURN_E2E=PASS`.
- Outside-worker source witness: `SOURCE_UNCHANGED_SHA256=a8948f7bf162528ec9f2a9ca5f007e77f0c5f0901a428c92d0f77ef1185cfb38` for `AGENTS.md`.
- Relative to the research base, the CI-tested commit adds exactly two files: one test and one workflow. No original production source file was modified.
- Observed `main` SHA: `54455f3ec177395aad4bbb6770925e198cad216a`. No merge, deploy, PR or production change.

## Test contract

A real `run_agent.AIAgent` opens an OpenAI-compatible HTTP conversation with the repository's `tests.fakes.fake_llm_provider.FakeLLMServer` over localhost. The model script requests a `write_file` tool call targeting the source root `AGENTS.md`, followed by a final answer. The test asserts:

1. The real first model request advertises `write_file`.
2. The fake provider receives two or more real HTTP model requests.
3. The second request contains the actual assistant tool-call with its unique `tool_call_id`.
4. Exactly one tool result with the matching ID reports an error, denial, permission problem, read-only filesystem, or equivalent block.
5. The checkout's `AGENTS.md` bytes remain unchanged; the synthetic injection does not persist.
6. The same AIAgent turn returns the scripted final response after the denied tool.
7. The outer OS namespace preflight verifies no external egress, checkout read-only, zero capabilities, and `no_new_privs`.

The enclosing GitHub job uses `ubuntu-latest`, `contents: read`, non-persistent checkout credentials, no app secrets, pinned Python 3.14 from the project lock, `scripts/run_tests.sh`, and a single writable bind mount to an ephemeral test-duration metadata file.

## Strict limitations

- VERIFIED: real model-protocol loop to a **fake localhost LLM**, real AIAgent turn handling, tool-result correlation and protected-file denial within this one scenario, job success at exact SHA.
- VERIFIED_PARTIAL: whole-process Linux namespace egress/source protection and same-runner outside-worker SHA256 witness. This is **not** a full system filesystem sandbox or independent offhost witness.
- UNKNOWN / NOT_VERIFIED: real paid or external model, full Browser/MCP/Inline end-to-end with effects, owner signatures bound to action+SHA+nonce, approval across processes, independent offhost signed evidence, recovery/rollback and hard in-flight ESTOP.
- **No production rating >=9.8/10 can be claimed.** A successful CI test is not an authorization or score.
- The future handoff commit (this document) is intentionally **not** claimed as CI-tested; the exact passed SHA is the one above.

## Earlier pinned evidence (different SHA)

- Component regression `63/63` at `41bddbb70850f89779b78aa395ecb6b4a6c5686d`:
  https://github.com/eltokhey1/hermes-agent/actions/runs/45348171650
- Do NOT transfer that check's green status to this new branch's SHA or vice versa.

## Next smallest safe action

Build an **independent offhost signed witness** for the same bounded fake-provider turn (including nonce, exact SHA and tool-result correlation), then an approval authorization gate where action executes only after separately authenticated owner approval. Do not merge, deploy, provision paid services, create keys, widen outbound network or waive HITL without exact-scoped approval.
