# Hermes Independent Owner Approval and Protected Root — Cloud Test Receipt

**Verified:** 2026-11-13 UTC  
**Mode:** research-only, synthetic test authority, inert previews only  
**Repo:** `eltokhey1/hermes-agent` (public), branch `research/owner-independent-authority-service-20261113`  
**Pinned source SHA:** `a32758ff44fea2375baf2d98cb160e48601ea51a`  
**Workflow-only SHA:** `f2eff0993e0d34f82ccb4fde8633f330e5bc4494`  
**GitHub Actions evidence:** [Run #43457579658](https://github.com/eltokhey1/hermes-agent/actions/runs/43457579658), attempt 1, **completed / success**.

## Run evidence and exact commands

| Hosted runner | Job ID | Python unit tests | Demo |
| --- | ---: | --- | --- |
| Ubuntu / Python 3.13 | `131995674595` | `Ran 21 tests in 4.040s; OK` | PASS |
| Windows / Python 3.13 | `131995675009` | `Ran 21 tests in 19.124s; OK` | PASS |
| Total | | **42 PASS / 0 FAIL / 0 unittest SKIP** | **2 PASS** |

```bash
python -m compileall -q authority.py ipc_service.py test_identity_research.py demo_run.py test_authority.py
python -W error -m unittest -q test_authority
python -W error demo_run.py
```

Both raw job logs include:

```text
VERIFIED_OWNER_AUTHORITY_SHA=a32758ff44fea2375baf2d98cb160e48601ea51a
DEMO_PROCESSES=2
OWNER_CHANNEL_ISOLATION=PASS
EXACT_ACTION_HASH=PASS
SINGLE_USE=PASS
SYNTHETIC_OWNER_PROOF_ONLY=true
EXTERNAL_EFFECTS=false
PRODUCTION=HOLD
```

The checkout was of pinned research source, separate from the workflow's own new commit, with `persist-credentials: false` and `permissions: contents: read`. Standard GitHub-hosted runners ran without production credentials, network integrations, test package installation, merge or deployment. The public-repo billing details were not independently inspected; no paid API/cloud service was configured.

## Actual code changes

- `authority.py`: inert action allowlist, canonical SHA action contract, synthetic signed owner identity proof verification, owner-session challenge with one-use acknowledgment, explicit decision, time-bound approval, consumed-once preview, append-only hash chain, DB consistency checkpoint, persistent research ESTOP, and strict outage handling.
- `ipc_service.py`: two **separate OS processes** in the test. Root signer key is held in the root process, not the owner authority process. Owner and agent have distinct HMAC-authenticated loopback capabilities; requests use bounded JSON byte payloads rather than unsafe object deserialization.
- `test_identity_research.py`: synthetic identity issuer, fake test key generated at runtime.
- `test_authority.py`: 21 automated negative and positive unit/process tests, including wrong owner key/subject, CSRF challenge mismatch and replay, exact action hash, approval expiry and replay, unauthorized agent approval, root process failure, two-store rollback and externally supplied epoch floor, manual DB mutation, and ESTOP persistence on restart.
- `demo_run.py`: self-cleaning inert two-process demonstration, no real side effects.
- `README_AR.md`, `TEST_RECEIPT.json`: architecture and local evidence. `CI_WORKFLOW_TEMPLATE_NOT_ENABLED.yml` is documentation **only**, not an enabled workflow.

## Important security boundaries — NOT production complete

1. **No authenticated real human owner.** Owner proof is deliberately a synthetic HMAC claim; it is not real passkey/WebAuthn/OIDC login. The test authority has the symmetric *verification* key and cannot be considered an independently authenticated user. No browser-grade CSRF session, owner identity provider, or independent authorization sign-off exists.
2. **No actual OS security-domain split.** Root process and authority process are separate PIDs but run under the **same hosted runner OS identity**. An OS-account-level compromise can potentially read keys/modify both SQLite stores. The code is not a security-reviewed service or exposed TLS endpoint.
3. **No nonrollbackable external epoch authority.** Root store and authority state use separate SQLite files; rolling back *both* can be undetected without a genuinely protected `trusted_min_epoch` obtained from outside both files. The test proves this limitation and the conditional check; no protected external counter has been provisioned.
4. **No actual owner Windows P0/P1.** No confirmed ruOS host heartbeat, no real Hermes database restoration, independent in-flight watchdog or genuine tool effects. Tests are only on hosted GitHub runners and local container fixtures.
5. **No actual production-effect approval.** `demo.echo` and `demo.review` only. Unsupported effects, deployment, network-enabled jobs, payments, emails, external tool dispatch and cost-bearing actions are denied. Any crash gap between primary DB and root checkpoint fails closed and must be reconciled by a human (no automatic retry).

## Safe next mandatory gates

- Add a genuine independent owner passkey/OIDC service through a secure human-authenticated UI, with issuer/audience/public-key validation, CSRF-protected session, exact-action hash and one-use approval.
- Deploy signer + monotonic epoch in **a truly separate security principal / external trusted store** with ACL/key-protection and an independent ESTOP watchdog, then adversarially test lost root, rollback of both stores, signer compromise, expiry, nonce replay and agent-side prompt injection.
- Check the owner's actual Windows machine once available and perform the protected P0 backup and isolated restore, then real P1 crash/ESTOP verification inside a disposable runtime.
- Require an independent human GO/NO-GO at an exact reviewed SHA before any R2 or production action.

**Final:** `PRODUCTION=HOLD` · `HITL=REQUIRED` · `G0/G-CODE/G1=NO-GO`. No owner identity or paid system was set up.
