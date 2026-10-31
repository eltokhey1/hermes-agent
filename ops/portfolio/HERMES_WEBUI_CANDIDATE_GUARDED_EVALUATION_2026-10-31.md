# Hermes WebUI — candidate assessment and guarded integration gate (2026-10-31)

**Status:** SOURCE_REVIEWED / CANDIDATE_TIER_2 / DESIGN_ONLY / NOT_INSTALLED / HOST_UNVERIFIED / PRODUCTION=HOLD. This is a research entry in the existing RAD-01/Designer backlog, **not** a new work package, approval, deployment, or evidence of Windows acceptance.

## Source and scope
- Upstream: https://github.com/nesquena/hermes-webui (MIT; verify exact LICENSE and dependency licenses at the pinned candidate SHA before reuse).
- README and architecture: https://github.com/nesquena/hermes-webui/blob/master/README.md and https://github.com/nesquena/hermes-webui/blob/master/ARCHITECTURE.md .
- Upstream advertises a Python/vanilla-JS browser UI with chat, sessions, workspace browser, voice input, profiles, cron, memory and agent delegation; these are **claims/features to test**, not proof of security.
- README explicitly says bootstrap does **not** support native Windows; Linux/macOS/WSL2 are supported, with a community native Windows guide and known POSIX-path/tool limitations. Its ~330 MB native RAM claim is a community measurement, not a verified benchmark on the owner's Surface Pro 7 Plus.
- Important: default WebUI chat runs Hermes in-process, reading HERMES_HOME, not through a separately governed API. Gateway-backed chat has limitations. This is a **critical integration boundary**, not a drop-in safe front end.

## Decision
**Reuse UI patterns/components only after isolated source/security evaluation; do not replace the existing Hermes Core/Harness.** Prefer an adapter through an existing server-enforced authenticated policy gate, not direct in-process agent execution. Do not connect WebUI to live Hermes home, credentials, real LC/customer files, schedulers or Ollama until independent gate testing passes.

## Non-negotiable admission criteria
1. Pin and review exact upstream commit, dependencies, license, SBOM and update path; no bootstrap/install script execution during review. Assess the default auto-install behavior and any egress/telemetry.
2. Verify server-side identity and authorization per action, deny-by-default on every API route; session ownership, CSRF, path traversal/reparse-point and symlink/junction checks; safe preview, attachment and file edit/delete restrictions.
3. Route all tool calls, shell, subprocesses, cron, delegated agents, memory/skills writes, provider calls and workspace mutations through the **existing** Mercury-style guarded dispatcher. ESTOP and PRODUCTION=HOLD outrank UI approvals. Disable 'allow always', uncontrolled shell and self-modifying skills; the Loop may not edit Harness policies, approval gates, budgets or independent evidence.
4. Bind WebUI to loopback only for initial synthetic tests; require separate approval and threat review for remote/mobile/Tailscale, reverse proxy, public share links or any network exposure. Do not rely on optional password being enabled by default.
5. Keep TradeDocs AI and Shipment Intelligence business modules separate and least-privileged; do not copy production bank/LC data into WebUI storage or logs.
6. Establish native Windows evidence on the actual device (P0-01 read-only inventory, original evidence ZIP + SHA-256, isolated restore and gate tests) before claiming compatibility or moving HOLD/NO-GO. Hosted Windows CI and community claims are TESTED_SYNTHETIC/UNKNOWN, not host acceptance.
7. Measure startup RAM, idle RAM, peak RAM, CPU, disk usage, latency, cost per successful task, crash recovery, permission bypass attempts and accessibility on the target host; report test setup and provenance.

## Minimal safe evaluation order
- E0: READ_ONLY upstream file inventory, license, dependency and threat review; record exact SHA and unresolved findings.
- E1: source-only compatibility map against Hermes repo and P0/P1 gates, no runtime changes.
- E2: isolated synthetic offline UI smoke tests and adversarial gate tests only after approval and disk-space check; no real secrets/data.
- E3: independent verifier reviews original Windows evidence and security receipts; decision HOLD until all acceptance gates independently pass.
- E4: optional small adapter on a **draft** branch after E0-E3; no merge/deploy without explicit approvals.

**Hard stop:** insufficient C: free space, missing native evidence, unverified gate coverage, unknown dependencies or uncontrolled in-process tool execution => no install/integration.

References: existing `ops/portfolio/MERCURY_STYLE_GUARDED_RUNTIME_2026-10-27.md`, existing canonical RAD-01/Designer register, and the owner P0/P1 acceptance policy. No new canonical IDs or independent agent created.
