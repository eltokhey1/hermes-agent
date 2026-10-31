# Hermes Radar — Executed Source Audit and Synthetic Candidate-Gate Test (2026-10-27)

**Status:** SOURCE_AUDIT_COMPLETED / EXACT_URL_DEDUP_COMPLETED / SYNTHETIC_POLICY_25_OF_25_PASS (ISOLATED LINUX NODE) / REAL_TOOL_BENCHMARK_NOT_RUN / WINDOWS_NATIVE_NOT_VERIFIED / PRODUCTION=HOLD.
**Owner workflow:** Existing Hermes RAD-01/MKT-01. Follows [200-entry inventory](./AI_200_SOURCE_TOOL_INVENTORY_AND_SCREENING_2026-10-27.md), [50×50 inventory](./PRODUCT_DISCOVERY_VIBE_CODING_50X50_RADAR_2026-10-27.md), and [governed agent orchestration](./SUPERVISOR_SPECIALISTS_HITL_OBSERVABILITY_REFERENCE_2026-10-27.md).
**Scope:** Check dated current primary documentation, prune unsafe or unmaintained new adoption candidates, calculate bounded exact-URL overlap, execute a reversible offline *policy-only* test suite, and identify next measurable A/B target. This is **not** a live model, GUI, cloud service, Windows host or production test.
**Assets:** [Reproducible Node.js standard-library-only synthetic test suite](./evals/candidate_gate.test.mjs). Run: `node --test ops/portfolio/evals/candidate_gate.test.mjs`. This is not imported by any Hermes runtime module.

## Verified documentation / decision table (no generated scores)

| Tool / candidate | Findings supported by vendor or maintainer | Provisional local Hermes disposition | What remains UNTESTED |
|---|---|---|---|
| Existing Aider + Ollama | [Aider official Ollama guide](https://aider.chat/docs/llms/ollama.html) supports local API; prior Hermes records report Aider/Ollama existing on Windows | **RETAIN_EXISTING_HOLD**; measure before replacing; no new install | Native Oct 27 exact executable versions, current functionality, task accuracy, cost/task, p95 latency |
| Continue | [Maintainer repository README](https://github.com/continuedev/continue) says no longer actively maintained and read-only; final release noted | **REJECT_NEW_ADOPTION**; remove from active candidate list, keep source as legacy | No need to install; security suitability of abandoned versions |
| Langfuse self-host v4 | [Official architecture](https://langfuse.com/self-hosting) needs web/worker plus PostgreSQL, ClickHouse, Redis and object store; [official minimum infrastructure](https://langfuse.com/self-hosting/configuration/scaling) quotes substantial separate resource floors | **DEFER_LOCAL_INSTALL** on i5/16GB host; prefer existing logs/SQLite; not a hard universal claim about minimal hardware | No actual memory measurement on Surface Pro; no measured Hermes benefit |
| MLflow | [Official tracking guide](https://mlflow.org/docs/latest/ml/tracking) and [server guide](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/) support local SQLite for metadata | **REFERENCE_ONLY / LOWER-INFRASTRUCTURE ALTERNATIVE** to evaluate only if stdlib traces are inadequate | Not installed here; no measured memory/latency/maintenance cost; not asserting MLflow and Langfuse feature parity |
| n8n Community | [Official Oct 6 2026 license FAQ](https://support.n8n.io/article/can-i-use-your-license-for-my-use-case) allows free self-host internal workflows but needs commercial license if external clients can build/configure workflows or platform is hosted as service | **KEEP_INTERNAL_ONLY** if already present, no new activation; **LICENSE_REVIEW_REQUIRED** for customer-facing editor/MCP configuration | No new workflow run; actual intended SaaS licensing determination requires vendor-specific interpretation |
| Activepieces Community | [Official license](https://www.activepieces.com/docs/about/license) says MIT core, commercial licensing for enterprise-specific portions | **SANDBOX_RESEARCH_CANDIDATE** as alternative to n8n if a real workflow gap appears | Integration reliability, required RAM, network security, total cost, support, Windows performance |
| Recraft Free | [Official terms](https://www.recraft.ai/legal/terms) and [official pricing](https://www.recraft.ai/pricing) say free-plan generated work is not licensed for commercial use and is owned by Recraft | **REJECT_FREE_COMMERCIAL_CREATIVE_USE**; may research references under terms | Paid-plan licensing and any chosen asset workflow must be separately reviewed |
| ComfyUI | [Official repository README](https://github.com/Comfy-Org/ComfyUI) describes Windows CPU-only portable execution option | **DEFER_RESOURCE_TEST**; Intel i5 integrated-GPU efficiency unmeasured | Actual throughput, memory and image quality for intended tasks |
| Legacy standard library logger | No new external service needed to record run ID, timestamps, evidence and costs | **PREFERRED P0/P1 BASELINE** where existing Hermes logs/checkpoints already meet requirements | Verify repository runtime behavior and acceptance with true Windows evidence |

### Why these decisions matter

- A discontinued coding assistant and a license-incompatible free designer can **fail eligibility without a head-to-head speed benchmark**; these are verified constraints, not opinions about generated output quality.
- Langfuse's official minimum service footprints are individually listed as web 4GiB, worker 4GiB, PostgreSQL 4GiB, Redis/Valkey 1.5GiB, ClickHouse 8GiB and optional self-host storage 4GiB. These **illustrate operational complexity**, not a universally measured RAM total or an exact Surface Pro installation requirement. A dependency-heavy evaluation without current need violates lean-first.
- Open-source status alone does not determine SaaS rehosting, white-label rights or commercial asset ownership. Explicit license assessment is a veto before pricing scores.
- No point assigning arbitrary numerical "performance scores" without running *the same real workload on the same host*.

## Inventory dedup — independently executed parsing

- First [50×50 list](./PRODUCT_DISCOVERY_VIBE_CODING_50X50_RADAR_2026-10-27.md) contains **50 URL-bearing discovery/launch directory rows** and **50 coding-candidate names without URL fields**. This particular exact-URL comparison therefore examines the **50 directory URLs only**, NOT all 100 prior entries.
- Owner-supplied [200 list](./AI_200_SOURCE_TOOL_INVENTORY_AND_SCREENING_2026-10-27.md) has **200 URL rows**; within-list no identical URLs were found.
- After normalizing `www.`, case of path, and trailing slashes, **10** URLs overlap the prior 50 launch-directory URLs: #1 There's An AI For That, #2 Futurepedia, #3 FutureTools, #4 Toolify, #7 TopAI.tools, #9 AlternativeTo, #10 SaaSHub, #11 Uneed, #12 Fazier and #14 Indie Hackers.
- Thus the two **URL-bearing** sets contain **240 unique normalized URLs among 250 URL records**. Do not call this 240 unique tools, 300 unique tools, or deduplication of the 50 previous **name-only** coding candidates. More canonical-vendor / service-level entity resolution remains unrun.

## Offline automated rule checks — executed

**Test executable:** Node.js v22.16.0 in an isolated Linux sandbox, no installs/APIs/credentials/Windows access, 2026-10-27.
**Command:** `node --test /mnt/data/hermes_radar_eval/candidate_gate.test.mjs`
**Observed TAP summary:** `1..25`, `# tests 25`, `# pass 25`, `# fail 0`, `# cancelled 0`, `# skipped 0`; duration **171.636133 ms** on that sandbox run (not comparable to Windows).
**Local source SHA256:** `09b5a1a4b7f0841305a6c46a5508357013c65c2d91085d206e64cdd477bc1337`. One-file suite is committed here in GitHub and replayable with Node.js. Output is only a controlled test record; not network or agent execution.

25 scenarios checked input validation, type-injection, incompatible contexts, retention vs promotion, abandoned tools, commercial license veto, RAM mismatch, unknown license/free tier/maintenance, unproven new dependency gap, missing synthetic evidence, installation/spend/external-data/secret HITL gating, and that the maximum outcome is **SANDBOX_ELIGIBLE_ONLY**. Other proposed agent/robot safety adversarial tests in the architecture annex remain **PLANNED / NOT_RUN**. Passing these synthetic predicates **does not imply any real candidate passed QA or is safe to deploy**.

## Real tool benchmark schema (not executed — requires authenticated Windows evidence)

For a prospective code-agent replacement, compare the currently installed Aider+Ollama baseline to **only one maintained, license-suitable challenger at a time**, holding model, task, task fixture, machine load and budget constant:

| Metric | Measurement | This-turn verified observation |
|---|---|---|
| Solved real test cases | Passing golden tasks / all tasks, three bounded runs if feasible | **UNKNOWN — no head-to-head tool run** |
| Security-block success | Denied risky requests / attempted risky actions | **UNKNOWN (25 policy *simulation* checks are different)** |
| Time / p50 / p95 | Per-task wall-clock in seconds | **UNKNOWN** |
| Cost per successful task | (model usage + services + resource cost estimate + human review) / accepted completed tasks | **UNKNOWN — no billed API call** |
| Recovery | checkpoint and interrupted-run correctness | **UNKNOWN** |
| CPU / memory | Peak working set, pressure and exact model tag on Surface Pro 7 Plus | **UNKNOWN — Windows not accessed** |
| Rights | Contractual free/commercial use, telemetry and data handling | **CHECKED for named candidates above only** |

**Safe-native follow-up commands (not run):** `node --test ops/portfolio/evals/candidate_gate.test.mjs`, `Get-Command aider,ollama,kilo -ErrorAction SilentlyContinue`, `ollama list`, `git status --short`. Commands require user's authenticated local host and must not be represented as completed. Real source repositories/models need supply-chain and provenance review before downloading/updating.

## Decision / promotion gate

1. **Keep current existing Hermes + Aider + Ollama as the comparison baseline**; no measured evidence in this turn justifies replacing them. Continue and Recraft Free (commercial design) leave *active* shortlist.
2. **Prefer stdlib tracing/SQLite**, not Langfuse self-host on 16GB; MLflow is a conditional *research candidate*, not a required addition.
3. **n8n internal** remains conditional under SUL; Activepieces community is only a future sandbox alternative with core MIT, not proven superior in tasks.
4. **No new production change / install / spending / Windows modification.** Production HOLD; G0/G-CODE/G1 remain NO-GO pending real independent Windows-native acceptance. Repo changes are restricted to a prior open Draft PR #6.
5. Supervisor/Designer/TradeDocs/Shipment/Commercial Radar may read this file as evidence. Writing it does not actively synchronize remote agents or train models.

**Known limits:** Vendor policies change; every vendor-term result here is a dated 2026-10-27 snapshot. Exact URL overlap is a technical normalization exercise, not business equivalence. No approval token, external account or tool execution was implied by the user's instruction "execute".
