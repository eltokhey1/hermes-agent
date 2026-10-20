# Research → Improvement Loop — design-only contract (2026-10-19)

> Non-runtime reference. The active Hermes Windows instance, independent ACL/evidence engine, backup restore and P0/P1 are **UNVERIFIED**. Do not install, deploy, merge or enable any discovered tool automatically.

## One canonical portfolio
- Source of truth remains the private owner-owned Hermes command center: **16 streams / 45 packages / 120 legacy task identifiers**.
- 32 engineering subgates, 34 external task-register rows, 44 V1 crosswalk items and 26 action checkpoints are **children/aliases**, never added to the 45-package count.
- Research comparables: 20 market case studies; internal product ideas: 3, still research/validation. No claim of 23 production applications.
- Per week keep active WIP <= 3 (security/recovery, no-spend commercial validation, shipment evidence).

## Recurring loop
`Observe → Source verify → Canonical-ID de-duplicate → Risk & economic score → 3 offline experiments → Independent acceptance gate → Approved action → Actual measured result → Error/lesson → Next cycle`.

For each candidate record an immutable source link, observed_at versus event_at, licence/terms, freshness, source type, raw data hash, contradicting evidence, parent package ID, expected outcome, synthetic negative tests, zero-dollar cost cap, reviewer, and human approval boundary.

## Current implementation boundary
- The reusable existing ChatGPT weekly radar has been extended with this cycle; **no duplicate schedule is required**. Its result is a report, not a background integration to the owner's Windows host.
- A separate **offline Python standard-library-only prototype** reads validated JSON observation snapshots and simulates official MCP Registry paginated differences. It is not deployed to Hermes.
- Official MCP Registry `GET /v0.1/servers` supports cursor and `updated_since`; a missing entry on a partial page must not be interpreted as deletion. Changed registry metadata is not authority to install code.
- TrustMRR offers a documented MCP with separate public discovery and authenticated tools; Startups.RIP Pro requires payment/credentials. Product Hunt API commercial use needs terms and permission review.
- A local experimental read-only stdio MCP subset and synthetic tests do **not** demonstrate successful live client/model interoperability (GPT/Claude/Gemini/Ollama each require host/version/schema/tool/auth tests).
- Neither vendor-reported revenue nor a listing price is independently verified net profit.

## Current decision
The offline research-loop prototype tests are synthetic and its result is **OFFLINE_TESTED_DESIGN_ONLY**. They do **not** close Windows P0/P1 or prove any actual external benefit. Real P0 requires read-only Windows inventory, protected backup plus *isolated functional restore*, least-privilege identity and secret-exposure evidence; real P1 requires durable intent, no blind UNKNOWN retry, independently protected acceptance store and reviewed recovery tests.

Draft documentation for review only. No source data from private shipments, customers, accounts, or laptop is included.

## Offline v3 acceptance note — 2026-10-19

An independent local regression check found a cross-source ID collision risk: the initial v2 recorder keyed change detection by `(source_id,id)` but shortlisted and formatted candidates by raw `id`, risking evidence/metric misattribution. Offline v3 adds `qualified_id=SOURCE::ID`, fails closed on ambiguous bare outcome IDs and MCP lookups, and validates malformed identifier types. **69/69 synthetic local tests passed** (58 prior + 11 new). A separate private `CURRENT.xlsx` copy retains all 26 original worksheets; four intentional existing-cell updates and two expanded research ranges are documented in a local receipt. No real API, models, Windows instance, P0/P1 acceptance, or independent business outcome has been tested. **Keep this PR draft, no merge.**


## Offline v4 local report-integrity enhancement (2026-10-19)

- Scoped to existing `RAD-02` (discovery) and `GOV-03` (evidence templates); adds **zero** canonical work packages.
- The previous offline writer could leave one of two report files in a folder after interrupted I/O with no completion evidence. The separate v4 research prototype adds `cycle_ledger.py`: a completion receipt written last with input-and-report SHA-256s, two-pass input change detection, exclusive output-folder creation, explicit parent-receipt lineage, and rejection of partial, tampered, symlinked or unexpected files.
- **89/89 isolated stdlib Python tests passed** (69 previous + 20 new); the packaged release also passed the same tests after clean ZIP extraction and matched 27 manifest entries. A synthetic three-cycle chain checked complete.
- This is **offline report integrity**, not a durable production effect ledger, digital signature, official-data verification, or independent security acceptance. It does **not** test the Windows host, licensed external connectors, MCP model interoperability, or financial value. P0/P1 remain OPEN and production HOLD.
- The release bundle is stored in the owner's **private** Hermes command-center library folder as `Hermes_Research_Improvement_Loop_v4_2026-10-19.zip`, **not committed to this public fork**. The owner-private `CURRENT.xlsx` was not replaced by this release (a newer Library version was observed). The existing weekly radar remains the only recurring discovery task; no new automation was created.
- Keep this PR **Draft** and **unmerged**. A SHA-256 manifest is not a cryptographic signature, and no untrusted MCP server should be installed or executed from discovery.
