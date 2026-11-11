# PR10 Shipment Intelligence — follow-up acceptance-gate evidence

**Research report date:** 2026-11-12 (Tripoli). **Cloud tests actually ran:** 2026-11-11 UTC.
**Status:** `PRODUCTION=HOLD` · `HITL=REQUIRED` · `G0/G-CODE/G1=NO-GO`.
**Target PR:** https://github.com/eltokhey1/hermes-agent/pull/10
**Original PR head (not changed):** `7eff2a5723303f20aff3dbb91380fb5a09328368`
**Earlier isolated patch SHA:** `a06c67115ebfe86895d43038dc1fcdf4589fd0ff`
**SHA-pinned source blob:** `e91321927da1d3ac8f5281a896f8cba7b310b1f7`
**This research branch:** `research/pr10-resilience-gates-20261112`

## Evidence ledger

| Gate | Evidence | Verdict | Meaning |
| --- | --- | --- | --- |
| Previous targeted PR10 patched suite | [Run 43112953664](https://github.com/eltokhey1/hermes-agent/actions/runs/43112953664) | VERIFIED / 45 PASS on Ubuntu + 45 PASS on hosted Windows | 32 original + 13 independent in each OS; synthetic only |
| SQLite untouched/backup/WAL interrupted-transaction simulations | [Run 43114167097](https://github.com/eltokhey1/hermes-agent/actions/runs/43114167097) | VERIFIED / 4 PASS on Ubuntu + 4 PASS on hosted Windows | Read-side checksum refusal, isolated SQLite backup, crash in child process; **not real Hermes P0/P1** |
| Ledger event deletion | Same run | VERIFIED GAP / FAIL on Ubuntu and Windows | Deletion of last event becomes `UNKNOWN` without independent evidence that a record existed (does not claim a false CURRENT status, but loses audit continuity) |
| Row rewrite + recomputed unkeyed SHA | Same run | VERIFIED GAP / FAIL on Ubuntu and Windows | DB-only attacker can modify evidence and its hash and still yield `CURRENT_ACTUAL` |
| Unknown DCSA code promoted to actual | Same run | VERIFIED GAP / FAIL on Ubuntu and Windows | Unknown token is accepted and promoted to `CURRENT_ACTUAL`. Desired policy is quarantine/UNKNOWN/review for **unrecognized semantics**, not necessarily rejecting extensible codes |
| Off-DB HMAC signed checkpoint + independently monotonic epoch, *prototype only* | [Run 43114689189](https://github.com/eltokhey1/hermes-agent/actions/runs/43114689189) | VERIFIED RESEARCH / 7 PASS on Ubuntu + 7 PASS on hosted Windows | Detects DB deletion, rehash, forged receipt, wrong key, and prior-epoch rollback if external trust key and epoch are genuinely independent |
| Actual trust-boundary isolation of signer/root, key lifecycle, anti-rollback policy | No run | NOT_TESTED | Prototype's test key is fake; real independent signer/epoch authority are not implemented |
| Real licensed carrier feed/DCSA conformance | Official docs only | NOT_TESTED | No provider account, licensed source payloads, API credentials or provider consent used |
| Owner Windows P0 protected backup/restore/ACL + production runtime P1 crash+ESTOP | Hosted simulation only | NOT_TESTED | The GitHub `windows-latest` runner is not the owner's PC or runtime and cannot prove physical restoration/in-flight action safety |
| Independent human reviewer approval | This is an automated review package | NOT_TESTED | No named independent human has reviewed or signed off |

## Raw command and proof boundaries

The red/positive resilience suite checked out `a06c67115ebfe86895d43038dc1fcdf4589fd0ff` and the immutable research tests `83864847f8a4c56c897dc38eee1234a4d9d78fb4`. The GitHub-hosted jobs ran:

```bash
python -m pytest -v -ra audit/verification/test_pr10_resilience_gates.py -k "not deleted and not recomputed and not nonstandard"
python -m pytest -v -ra audit/verification/test_pr10_resilience_gates.py -k "deleted or recomputed or nonstandard"
```

Results on **each** OS: `4 passed, 3 deselected`; then `3 failed, 4 deselected`. Three failures are real unmet security/conformance expectations, **not** accidental infrastructure failures. The separate invalid-YAML run [43114037714](https://github.com/eltokhey1/hermes-agent/actions/runs/43114037714) was an authoring issue (no jobs); it was corrected before the evidenced red run.

The stand-alone HMAC anchor proof checked out the source SHA above and test SHA `ad51295cc1c9b4e3cd70878c81caf40b581e5126`, ran:

```bash
python -m pytest -v -ra audit/verification/test_pr10_external_anchor_prototype.py
```

Results: `7 passed` on Ubuntu and `7 passed` on hosted Windows. Workflow commit `392b5fb7affc622cf8766cfb49127122d23f6093`. The original PR code and patch source were unchanged during this research-only proof.

## What is and isn't a safe remediation

- Treat the SQLite row-level SHA as accidental-corruption detection **only**. A legitimate audit trail needs authoritative event identities, unforgeable journal/receipts, a signer holding HMAC/signature keys inaccessible to Hermes's DB and model processes, a trusted monotonic checkpoint/sequence, backup and truncation alerts, and recoverable fail-closed enforcement at read and dispatch.
- The isolated `verification/pr10_external_anchor_prototype.py` demonstrates DB-only tampering detection under the **assumption** of a separately managed secret and trusted latest epoch. It is **not integrated** into production, does not authenticate the carrier, and is not an approved trust-root design.
- For a versioned DCSA event adapter, validate the producer schema and semantics, and keep unknown/extended pseudo-enums as `UNKNOWN`/`REVIEW_REQUIRED` without promoting them to actual movement events. DCSA's implementation guide and design guidelines explicitly address TNT 2.2 and extensible pseudo-enums:
  - https://reference.dcsa.org/content/standards/guidelines/implementation-guides/implementing-track-and-trace
  - https://reference.dcsa.org/content/standards/guidelines/api-design-and-implementation-guidelines
  - https://models.dcsa.org/2024Q4/EARoot/EA5/EA2/EA6/EA7/EA1/EA1/EA2573.htm
- DCSA's public reference implementation warns against deploying it without authz/authn; neither its code nor public examples are a substitute for an authorized carrier account:
  - https://github.com/dcsaorg/DCSA-TNT

## Exact human acceptance gates

1. **Independent verifier review:** reviewer and timestamp, patch SHA, current upstream schema, negative tests and design of trust-root isolation, with explicit sign-off on action hash binding and unknown outcomes.
2. **Real carrier sandbox:** authorization/consent/license, actual provider export with identifying data redacted, validated schema version and immutable provider IDs; read-only and no credentials in repo.
3. **Owner Windows P0:** fresh hardware/disk/edition/virtualization preflight, protected backup including SQLite/WAL, isolated restore, ACL verification, exact SHA, raw command output and restore integrity.
4. **P1 runtime:** simulate actual tool-call crash and ESTOP midflight with independently authenticated approvals, no blind retries, journal/replay and recovery proof; never equate SQLite child process crash with runtime crash.
5. **GO/NO-GO:** remain NO-GO until separate explicit owner decision based on the entire evidence set.

**No merges, deployments, production writes, new paid services, private credentials or customer documents were used in this research cycle.**
