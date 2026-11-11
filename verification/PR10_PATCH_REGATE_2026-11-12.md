# Hermes Shipment Intelligence PR #10 — fail-closed patch and cloud re-gate

**Report generated:** 2026-11-12 (local Tripoli; GitHub execution 2026-11-11 UTC).
**Production:** HOLD; **HITL:** REQUIRED; **G0/G-CODE/G1:** NO-GO.
**Target PR:** https://github.com/eltokhey1/hermes-agent/pull/10
**PR original HEAD (unchanged):** `7eff2a5723303f20aff3dbb91380fb5a09328368`
**Isolated patch branch:** `fix/pr10-sqlite-ais-failclosed-20261112`
**Exact patch commit SHA:** `a06c67115ebfe86895d43038dc1fcdf4589fd0ff`
**Patched source Git blob SHA:** `e91321927da1d3ac8f5281a896f8cba7b310b1f7`
**Unchanged original tests blob SHA:** `8866387ed61c9bb8105225a2187d97b149b50661`
**Independent negative-test v2 SHA:** `ed56c5d64c312a2bea7aceb5911211d768c08fda`
**Workflow commit SHA:** `3877e9c8ad68882e9a1c1e8a4db14aabe8ce9863`

## Exact evidence

GitHub Actions [Run #43112953664](https://github.com/eltokhey1/hermes-agent/actions/runs/43112953664), attempt 1, `completed/success`, triggered by a push of research-only workflow file. The job checks out **source from the patched SHA** and tests from the independent audit SHA, in separate directories, with credentials not persisted.

| GitHub job | Job ID | Original tests | Independent negative tests | Job conclusion |
| --- | ---: | ---: | ---: | --- |
| ubuntu-latest / Python 3.13 | 130833507961 | 32 PASS | 13 PASS | success |
| windows-latest / Python 3.13 | 130833508132 | 32 PASS | 13 PASS | success |
| **Total** | | **64 PASS** | **26 PASS** | **90 PASS, 0 FAIL** |

Two exact commands executed in each job:

```bash
python -m pytest -q src/tests/skills/test_shipment_intelligence_skill.py
python -m pytest -q -ra audit/verification/test_pr10_independent_acceptance_v2.py
```

Log excerpts:

```text
VERIFIED_PATCH_SHA=a06c67115ebfe86895d43038dc1fcdf4589fd0ff
VERIFIED_AUDIT_V2_SHA=ed56c5d64c312a2bea7aceb5911211d768c08fda
Ubuntu:  32 passed in 0.15s; 13 passed in 0.10s
Windows: 32 passed in 4.84s; 13 passed in 1.35s
PRODUCTION=HOLD
OWNER_WINDOWS_P0_P1=NOT_TESTED
HASH_IS_NOT_PROVIDER_AUTHENTICATION=true
```

## Code change scope

One **source file only** changed relative to the original PR head: `optional-skills/research/shipment-intelligence/scripts/shipment_intelligence.py` (46 additions, 9 deletions).

- Introduced `_load_verified_events` to verify stored `record_sha256` by reconstructing the same canonical event and payload (excluding ingestion timestamp as in the original hash), before rendering container and linked-vessel observations. A damaged or mismatched row raises `ValueError('EVIDENCE_INTEGRITY: ...')` — not a superficially valid current status.
- `adapt_ais` rejects Python booleans in latitude/longitude fields before `float()` conversion.
- The CLI maps `ValueError` to `FAIL_CLOSED` and exit code 2. A new negative test confirms it.

## Explicitly preserved failed evidence

- [Unpatched independent red run #43109896916](https://github.com/eltokhey1/hermes-agent/actions/runs/43109896916): 5 PASS, 3 FAIL, revealing two content-integrity violations and acceptance of boolean AIS coordinates.
- [First patched run #43112553584](https://github.com/eltokhey1/hermes-agent/actions/runs/43112553584): original 32 PASS on both systems, but two old independent tests required a returned non-current status; the patch **raised an integrity exception** instead, which is the stricter fail-closed contract. The old tests and their failure logs remain unchanged.
- Independent test v2 **explicitly requires** the integrity exception; it also adds checks for corrupt JSON, modified AIS location, modified source_url, boolean False, and non-zero CLI exit. The v2 run is green on both operating systems. This is a contract clarification, not a change to the original production module or a suppression of its logged failures.

## What this proves, and does not

**VERIFIED (bounded synthetic):** exact patched source/tree, git blob identity, tests on GitHub-hosted Ubuntu and Windows, the 3 observed security defects addressed for the tested conditions.

**NOT VERIFIED / NOT TESTED:**
- Authenticated carrier events, licensed DCSA/AIS feeds, provider-specific schemas, container check digit validation and provenance trust.
- Full ledger integrity against deletion, reordering, replacement **with recomputed SHA**, or a malicious actor controlling both data and hash. The SHA is an **unkeyed checksum**, not a MAC/signature or independently anchored append-only log.
- Owner's Windows hardware, protected backup and isolated restore P0, P1 real crash recovery, actual HITL identity/approval isolation, production runtime integration, security review by an independent human.
- Any promotion of PR #10 or the main Hermes system.

## Safest next step

Request independent code review of the isolated patch SHA and the full run logs. For stronger assurance, design independently anchored append-only provenance with signatures or HMAC where appropriate and verify real licensed provider payloads with permission. Hold production and any PR merge for separate human authorization. No deploy, merge, CI rerun, or modification to `main`/PR #10 performed.
