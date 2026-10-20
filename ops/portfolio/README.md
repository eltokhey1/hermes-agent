# Hermes Commercial Opportunity Radar — design-only portfolio (2026-10-18)

> This folder is a proposed, non-runtime planning record. No AI agent, network connector, model, subscription, payment, migration, or live customer data use is authorized by its presence.

## Scope
- 20 independent **competitor/source research dossiers**: HERMES-001 through HERMES-020.
- 3 proposed **original internal product tracks**: TradeDocs AI, ExportLead AI, Shipment Intelligence.
- Shared candidates: iFixAi for independent agent assessment; TrustMRR official MCP for startup discovery; Startups.RIP public case research (Pro CLI is not approved).

## Project status policy
- Research references: `UNDER_RESEARCH`; not 20 products actively being coded.
- Internal opportunities: `VALIDATION_BACKLOG`; interviews, legal/technical evidence and paid-intent research before MVP.
- Source/integration adapter design: `DESIGN_ONLY`.
- Live Hermes readiness: **UNVERIFIED**, until Windows P0/P1 evidence is collected and independently checked.

## P0/P1 first
1. Read-only inspect actual local Windows runtime and working tree; redact remote tokens. Never run project tests before isolation.
2. Create a secure backup and **restore it successfully in a separate environment**, then test the restored copy.
3. Verify fail-closed denial for timeout, empty, malformed, and network failures; real synthetic-secret leakage scans and Git exclusions.
4. Default spend hard cap = $0; preserve human approvals for financial, destructive or external effects.
5. Before any effect, durably record intent; classify outcomes PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN; do not retry UNKNOWN automatically.
6. Independent acceptance evidence and watchdog should be separately tested; iFixAi is a candidate, not a security guarantee.

## MCP interoperability
Use a shared, scoped MCP gateway instead of installing one unsafe server per researched company. Product-specific schema/namespace and per-agent identity are essential. Stdio prototype is read-only/advisory and not security enforcement. OpenAI, Claude, Gemini and local models need host-by-host actual integration tests. JSON-RPC mock tests alone do not prove compatibility.

## Source endpoints
- TrustMRR official MCP: https://trustmrr.com/mcp ; public discovery and authenticated tools have different permissions.
- Startups.RIP CLI: https://startups.rip/cli ; Pro token and subscription required for premium CLI use.
- iFixAi: https://github.com/ifixai-ai/iFixAi ; pin and audit release, disable telemetry during synthetic offline tests, treat scorecards as potentially sensitive.
- Model Context Protocol: https://modelcontextprotocol.io/specification ; use a pinned official SDK and negotiate versions.

## Local evidence
A separately generated v4 offline artifact contains the 20 source dossiers, 23 zero-spend MCP profiles, integrity checker, negative tests and an in-memory UNKNOWN non-retry illustration. **Neither the ZIP nor any offline tests are evidence that the Windows Hermes production instance is ready.**

## Decision
Keep this draft separate from the project runtime. No merger into main or deployment before explicit review and P0/P1 verification.
