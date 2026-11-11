# PR #10 — independent adversarial acceptance receipt (non-production)

Date: 2026-11-11 UTC
Repository: eltokhey1/hermes-agent
PR: https://github.com/eltokhey1/hermes-agent/pull/10
Original code HEAD SHA: `7eff2a5723303f20aff3dbb91380fb5a09328368`
Research branch: `research/pr10-sha-7eff2a5-20261111`
Independent audit test+workflow SHA: `9d392045eec24ab67beba8e1088377bbbf65485e`

## Evidence

- Earlier original focused tests: **32 passed**, run https://github.com/eltokhey1/hermes-agent/actions/runs/43108491935
- New, independently written adversarial tests: **5 passed, 3 failed, 0 skipped**, run https://github.com/eltokhey1/hermes-agent/actions/runs/43109896916
- GitHub-hosted Ubuntu runner, Python 3.13 and pytest 9.0.2. Source checkout was PINNED to original PR HEAD and `git rev-parse HEAD` + `git hash-object` checks succeeded before tests.
- The independent tests lived in the research branch, not in the original PR code.
- Exact independent command: `python -m pytest -v -ra audit/verification/test_pr10_independent_acceptance.py`

## Independent tests, results

1. `test_control_baseline_has_expected_synthetic_status` — PASS
2. `test_replay_same_provider_record_is_idempotent` — PASS
3. `test_conflicting_native_event_id_is_fail_closed` — PASS
4. `test_a_vessel_position_cannot_prove_container_status` — PASS
5. `test_native_provider_id_is_mandatory` — PASS
6. `test_changed_persisted_event_code_must_not_be_trusted` — **FAIL**
7. `test_changed_persisted_payload_must_not_be_trusted` — **FAIL**
8. `test_boolean_coordinates_are_not_valid_ais_evidence` — **FAIL**

## Raw log summary

```text
VERIFIED_ORIGINAL_PR10_SHA=7eff2a5723303f20aff3dbb91380fb5a09328368
INDEPENDENT_AUDIT_SHA=9d392045eec24ab67beba8e1088377bbbf65485e
FAILED ...test_changed_persisted_event_code_must_not_be_trusted
  AssertionError: Unsafe: an edited SQLite event code was accepted as verified CURRENT_ACTUAL
FAILED ...test_changed_persisted_payload_must_not_be_trusted
  AssertionError: Unsafe: altered evidence payload was accepted without validating record_sha256
FAILED ...test_boolean_coordinates_are_not_valid_ais_evidence
  Failed: DID NOT RAISE <class 'ValueError'>
========================= 3 failed, 5 passed in 0.12s ==========================
PRODUCTION=HOLD
HITL=REQUIRED
OWNER_WINDOWS_P0_P1=NOT_TESTED
```

## Findings and engineering conclusion

- **HIGH / data integrity:** A previously saved SQLite row could be altered, without updating `record_sha256`, yet `evidence_report` returned `CURRENT_ACTUAL`. Neither row-code nor payload-only tampering was caught when generating the status. The independent tests demonstrate the missing read-side integrity check in an offline local database, **not** a demonstrated external compromise.
- **MEDIUM / input typing:** AIS coordinate `True` was accepted as latitude (numeric conversion of Python boolean); reject booleans explicitly before converting and range checking.
- **Additional limit / provenance:** Valid `record_sha256` is only an unkeyed digest, not a cryptographically trusted carrier signature or remote authentication; even a read-side check alone cannot prevent a malicious actor rewriting both row and digest. Real provider authentication, provenance, permissions, trusted anchoring and external sources remain unverified.

## Smallest safe remediation and re-gate

1. At report/read time, reconstruct canonical persisted evidence, verify `record_sha256` before deriving any `CURRENT_ACTUAL` or vessel positions; fail closed on malformed or mismatched rows. Evaluate immutable append-only evidence / trusted anchors separately.
2. Reject `bool` and invalid coordinate types in AIS adapter before numeric conversion.
3. On a **new pinned patch SHA**, rerun both original 32 focused tests and eight independent cases. Keep independent tests separate from patch authoring.
4. Separate review of authentic licensed DCSA/carrier exports, Windows/P0/P1 recovery, independent approval identity and security policy is still mandatory before any production consideration.

## Decision

`PRODUCTION=HOLD`; `HITL=REQUIRED`; `G0/G-CODE/G1=NO-GO`. PR #10 stays DRAFT. No changes to PR #10 or main, and no merge/deployment/publication to production. This is **adversarial test evidence**, not sign-off by an independent human reviewer.
