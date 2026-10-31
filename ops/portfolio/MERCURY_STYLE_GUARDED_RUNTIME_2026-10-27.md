# Shared Mercury-style Guarded Runtime pattern — 2026-10-27

**Canonical placement:** Existing RAD-01/MKT-01 cross-project learning register and Hermes Core/P0-P1 safety work; not a new top-level agent, project ID, schedule, integration, or replacement for existing Hermes safety controls.

**Status:** SOURCE_REVIEWED / DESIGN_REGISTERED / RUNTIME_NOT_INTEGRATED / WINDOWS_NOT_VERIFIED / PRODUCTION=HOLD. This file contains an inert reference policy and admission criteria; it is not an activation order.

## Provenance and tradeoffs

Official upstream: https://github.com/cosmicstack-labs/mercury-agent ; https://github.com/cosmicstack-labs/mercury-agent/blob/main/ARCHITECTURE.md ; https://mercuryagent.sh/docs/reference/completion-architecture .

Mercury documents a permission-aware agent loop, scoped filesystem access, shell blocklist/approval modes, shared CLI/Telegram channels, SQLite-backed memory, persistent scheduler/sub-agents, incremental skills disclosure and token limits. **Source-reviewed feature descriptions are not evidence that upstream is secure or fits this Windows host.** Upstream's `Allow All`, shell blocklist and command auto-approval are explicitly **not approved defaults** for Hermes; command strings alone are not a robust boundary against interpreters, wrappers, aliasing or argument injection. Source also describes auto-continuation across multiple budgets; Hermes will NOT adopt it unbounded.

**Reuse-first decision:** implement or reuse one deterministic *host-controlled* pre-tool authorization gate in the existing Hermes core (once P0/P1 evidence permits), not another agent, proxy, planner, daemon, always-on loop, database engine, or dependency. Preserve current independent Verifier, durable state, human approvals, audit and existing canonical portfolio IDs. An LLM instruction, tool schema, skills metadata or UX approval alone is not a security boundary.

## Architecture / control flow

```text
CLI / Web / Telegram / iOS / Android / API
  -> authenticated principal + channel + request_id (server-verified)
  -> Hermes existing router / bounded agent
  -> deterministic pre-tool gate (ESTOP; allowlist; args; scopes; HITL; budgets)
  -> existing authorized adapter (read-only first)
  -> durable result receipt and independent review
  -> minimal context retrieval (SQLite + FTS5, relevance/time/scope caps)
```

**Decision controls** (server-side, fail closed):
1. Default `DENY`. ESTOP and `PRODUCTION=HOLD` outrank all model prompts, role descriptions, channel messages, workflows, and tool metadata.
2. Classify actions into: read-only allowlisted local reads; controlled writes; shell/process; file deletion; network/provider calls; spend/finance; publication/outbound messages; secrets/credentials; production changes. All categories other than explicitly approved read-only reads are `DENY` until a distinct authoritative policy, independent human authorization and a tested adapter exist.
3. Treat tool arguments as untrusted. Validate exact schema, normalized path containment **plus symlink/junction/reparse and TOCTOU defenses at use**, destination host/IP/redirect/DNS-rebinding controls for HTTP, shell process+argv exact allowlist rather than substring/blocklist, content size, tenant and identity. Do not run a shell at all where a structured API is possible.
4. Approval receipts must bind real authenticated human actor, action, arguments/hash, target/tenant, expiry, nonce, channel and request ID; separately verified, single-use, durable; never self-issued by the LLM or worker. Current synthetic HMAC patterns are not proof of independent human identity.
5. Persist pre-execution reservation and post-execution metering of per-request, task and daily token/cost/steps/concurrency limits in existing durable store with atomic updates; budget exhaustion means pause/deny, not silent reset, fallback spend or recursive fresh budgets.
6. Preserve existing state machine `PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN`; external effects interrupted after dispatch are `UNKNOWN` until independently reconciled (not retried blindly). Idempotency key and receipts are mandatory for permitted side effects.
7. Single memory source initially: existing SQLite FTS5, bounded recent context and filtered snippets by tenant/purpose; no entire history or secrets in prompt, embeddings or logs by default. Cached/retrieved/source text is **data**, not privileged instructions.
8. Every channel enforces equivalent policy and actor-bound permissions; Telegram/web/browser channel commands cannot bypass the gate or raise their own roles.
9. Emit redacted audit records: gate version, policy version, actor pseudonym, tool, safe arguments digest, budget reservation, decision, receipt, verifier status. Independent evidence store/anchor required before high-trust claims.

## Minimal Python reference policy — READ ONLY BY CONSTRUCTION

This *pure* reference function illustrates centralized deny-before-action semantics. The `Usage` object MUST come from a durable, transactionally reserved budget, never from model output or user-supplied text. This snippet does **not** itself provide durable reservations, host filesystem isolation or authenticated human approval and must not be described as production-ready alone.

```python
from dataclasses import dataclass

READ_ONLY = frozenset({"audit.read", "repo.read", "memory.search"})
CHANNELS = frozenset({"cli", "web", "telegram", "api"})
MAX_STEPS, MAX_TOKENS = 8, 12_000  # pilot ceilings; tune from evidence

@dataclass(frozen=True)
class Usage:
    steps: int
    tokens_spent: int
    tokens_reserved: int

def authorize(*, operation: str, channel: str, actor_verified: bool,
              scope_verified: bool, estop: bool, usage: Usage) -> None:
    if estop or not actor_verified or not scope_verified:
        raise PermissionError("DENY: control or identity")
    if operation not in READ_ONLY or channel not in CHANNELS:
        raise PermissionError("DENY: tool or channel")
    if (min(usage.steps, usage.tokens_spent, usage.tokens_reserved) < 0
            or usage.steps >= MAX_STEPS
            or usage.tokens_spent + usage.tokens_reserved > MAX_TOKENS):
        raise PermissionError("DENY: budget")
```

**Adapter contract:** a trusted dispatcher calls the policy **on every tool request**, then separately validates typed args and path/egress boundaries, atomically reserves the next step and worst-case tokens, executes only an allowlisted read adapter, meters actual usage and durably records result. Disallow direct model access to shell, raw filesystem, general HTTP clients, DB write connections, cloud credentials or tool registration. A failed reservation/policy/store means DENY. No downstream adapters may be reachable around the dispatcher.

## Cross-project shared inheritance (not global permission inheritance)

| Existing owner | Reuse | Deny until separately approved |
|---|---|---|
| Hermes Core / Open Builder / Engineering Supervisor | Canonical safety gate, budget meter, bounded tools, recovery receipts | Shell, deployment, auto-merge, new connector credentials |
| TradeDocs AI | Local read+parse for redacted BL/LC/invoices, tenant/field provenance, bounded OCR/model calls | Bank operations, document emailing, external upload, signatures as authority |
| Shipment Intelligence | Bounded read-only reconciliation and event provenance; UNKNOWN state | Mail.Read grant, carrier scraping/API, external ETA claims without licensed data |
| Radar / Commercial / ExportLead / Crystal Agro | Public/licensed source reads and costed research; optional summaries | Automatic marketing, scraping without authorization, emails, spending, publishing |
| Designer / content / website / mobile | Preview/render checks and privacy controls, shared request/approval identity | Auto-publish, app deployment, account or profile changes |
| Additional agents, scripts, MCP, browser/Telegram/CLI channels | Same dispatcher contract where an execution tool is legitimately used | Any global role/permissions transfer between channels |

**Relevance rule:** the guard is shared everywhere that agents can act, but an informational-only task should not spawn extra runtime components. Skills teach practices, never grant permissions.

## Risks, adversarial tests and acceptance gates

| Threat | Required negative control/evidence |
|---|---|
| Prompt injection or forged higher-priority text | Host-enforced denial regardless of tool/skill/LLM response |
| Token explosion, tool recursion, restart reset, fallback cost | Hard step+token+daily ceilings, atomic durable reservations, no unbounded continuation |
| Shell command chaining, aliases, `curl|sh`, obfuscated interpreters | No generic shell in agent path; explicit executable/argv contract if later authorized |
| Path traversal, symlink/junction swap and protected data | Canonical scoped handle validation at execution, TOCTOU/reparse regression tests on Windows |
| SSRF, redirects, DNS rebinding, metadata/private IP | Centralized network egress control, redirect revalidation and integration tests |
| Replayed, forged, cross-tenant or expired approval | Independent actor identity/nonce/single-use hash, scope and expiry enforcement |
| Duplicate side effect after timeout or restart | Durable idempotency/UNKNOWN-on-recovery and reconciliation; no automatic replay |
| Channel privilege escalation or multi-channel race | Same principal and policy per call, atomic updates and concurrent tests |
| Memory poison, PII in context/telemetry | Tenant-bound FTS5, low-context summaries, redacted log, prompt-injection isolation |
| ESTOP racing tool dispatch / corrupted ledger | Check inside atomic dispatch boundary, fail closed on store/ESTOP errors, independent audit |

Before any actual Hermes integration: verify existing gate coverage and code reuse; define threat model; pin upstream reference revision/license and dependency transitive risk; run >=25 adversarial offline tests and hosted CI on exact commit; collect native Windows P0 backup/restore/ACL/ESTOP/secret-isolation evidence and independent acceptance. Compare memory and task performance, cost per successful task, p50/p95 latency, failure rate, context tokens saved. Only proceed to controlled shadow evaluation with human review. Never infer production readiness from docs, isolated tests or GitHub hosted Windows.

## Outcome / governance

- Document/radar registration: allowed on **existing Draft PR #6 only**, no merge to main.
- Proposed adoption: **SHARED_GUARDRAIL_CANDIDATE / TIER_1_PATTERN**, not VERIFIED_RUNTIME nor installed product.
- No new account, schedule, paid API, laptop change, executable connection or autonomous permission expansion.
- **PRODUCTION=HOLD; G0/G-CODE/G1=NO-GO pending authentic Windows evidence and independent review.**
