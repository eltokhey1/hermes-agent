---
name: shipment-intelligence
description: Reconcile shipment milestones with vessel evidence.
version: 0.1.0
author: eltokhey1, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shipping, logistics, containers, maritime, DCSA, AIS]
    category: research
    related_skills: []
---

# Shipment Intelligence Skill

Normalize carrier milestones and historical vessel AIS into an offline, evidence-first shipment view. This skill does **not** supply live tracking feeds, infer container arrivals from vessel movements, or change carrier systems.

## When to Use

- Comparing Maersk or other carrier container events with historical AIS vessel positions.
- Finding stale, uncertain, duplicate, or conflicting shipment updates.
- Importing a DCSA Track & Trace 2.2-style event export for private local analysis.

## Prerequisites

- Python 3.10+ on Windows/macOS/Linux; stdlib only.
- Event input explicitly exported from authorized providers; do **not** scrape login walls.
- For carrier observations, a source URL and tracking reference. For AIS, the IMO and time of the original position.
- The folder holding this `SKILL.md` is `SKILL_DIR` in the examples.

## How to Run

Install optional skill if published in the official catalog:

```text
hermes skills install official/research/shipment-intelligence
```

Until published, put the skill folder in `~/.hermes/skills/shipment-intelligence/`. From Hermes, use `terminal` to call the bundled Python script; never add a core model tool or edit `run_agent.py`.

```text
python SKILL_DIR/scripts/shipment_intelligence.py --db SHIPMENT_DB import-ais vessel_history.jsonl
python SKILL_DIR/scripts/shipment_intelligence.py --db SHIPMENT_DB import-dcsa carrier_events.json --provider carrier --source-url https://carrier.example/tracking/REFERENCE
python SKILL_DIR/scripts/shipment_intelligence.py --db SHIPMENT_DB import-maersk maersk_ocean_result.json
python SKILL_DIR/scripts/shipment_intelligence.py --db SHIPMENT_DB status ABCD1234567
```

`SHIPMENT_DB` is an absolute path to a private local SQLite file. Omit `--db` to use `~/.hermes/shipment-intelligence.sqlite3`. All commands work in Windows PowerShell too; replace placeholder values with real paths and authorized source URLs.

## Quick Reference

| CLI operation | Effect |
|---|---|
| `import-ais INPUT.jsonl` | Import vessel AIS/port events, with preserved unverified times |
| `import-dcsa INPUT.json --source-url URL` | Import DCSA 2.2-style shipment/transport/equipment event objects |
| `import-maersk INPUT.json` | Import the JSON shape of a Maersk ocean tracking result (offline) |
| `link-vessel CONTAINER IMO --source-url URL --note TEXT` | Record **manual**, traceable container–vessel association; does not verify its contents |
| `status CONTAINER` | Return carrier-only actual status, ETA clues, vessel context, warnings |
| `health` | Check local database and event counts |

The `maersk_ocean_result.json` input must be a structured ocean-tracking result containing `containers` and `url`, saved through an authorized connector/export. This tool does not fetch Maersk results itself.

## Procedure

1. Use Hermes `terminal` or an explicitly authorized provider connector to obtain **container-specific** events. Do not convert vessel arrival into a container arrival, discharge, or gate-out.
2. Record the original provider URL, timestamp, timezone, and identifiers. `time_utc=null` is valid for unknown timezones, and must never be auto-filled from an unlabeled local timestamp.
3. Use `terminal` to import each record set. Imports are idempotent on event ID and fail atomically if an existing event ID changes evidence. Original records are preserved in local SQLite.
4. Use `terminal` `status CONTAINER` to review the current best **carrier equipment** event. Estimated/planned information stays in a separate `latest_estimates` field.
5. Link a vessel only if a real shipping document or carrier voyage result identifies the connection. The supplied evidence note is a **manual assertion**, not machine verification. Vessel AIS appears as supplementary context only.
6. Treat `UNKNOWN`, `STALE`, and `REVIEW_REQUIRED` as non-actionable states. `CURRENT_ACTUAL` depends on a fresh, timezone-grounded carrier equipment event; it is **not** an authorization to arrange customs clearance, deliveries, money transfers or other consequential actions.

## Pitfalls

- AIS says where the ship reported itself; it cannot prove any given container was on board or discharged.
- Two actual equipment events at the same timestamp with different status or port trigger manual review, not automatic selection.
- Provider event timestamps without timezone are not promoted to UTC.
- A vessel's "Moored" status or port arrival may be stale or out of range. Report source time and age, not "currently moored".
- Do not assume DCSA 3.0 interoperability: current implementation is an internal normalized **DCSA 2.2-style** adapter, not a conformance-certified DCSA endpoint. No 3.0 mapping/IoT/reefer support is claimed.
- Do not place private tracking exports, container IDs, authentication tokens, or the SQLite database into a **public** GitHub repository.
- Built-in tracking connectors/APIs, if available, have their own access, terms, costs, limits, and authentication; this skill includes **no network calls**.

## Verification

- Run `pytest -q tests/skills/test_shipment_intelligence_skill.py` in the matching source checkout before publishing.
- Import the same data twice; count must remain unchanged.
- Insert contradictory records with the same immutable event ID; importer must fail closed without overwriting original evidence.
- Check that AIS-only imports and estimated-only equipment events return `shipment_state=UNKNOWN`.
- Time-travel `status` via `--now 2026-10-18T10:00:00Z` to reproduce stale state tests.
- Keep production deployment disabled until the local Hermes P0/P1 safety gates are independently passed.

## References

- DCSA Track & Trace: https://dcsa.org/standards/track-and-trace
- DCSA 2.2 implementation: https://reference.dcsa.org/content/standards/guidelines/implementation-guides/implementing-track-and-trace
- DCSA 3.0 rollout: https://dcsa.org/newsroom/track-and-trace-3-0-0-iot-reefer-visibility