# Hermes — actual Windows access + independent trusted approval gate

Date: 2026-11-13 (Tripoli). **Research/handoff only**.
Source: `eltokhey1/hermes-agent`, branch `research/owner-p0p1-rollback-guard-20261113`.
Do not merge, deploy, pay for services, install software, or execute on the owner's Windows host from this file.

## Blocker A: verifiable access to owner's actual Windows device

**OBSERVED / UNKNOWN as of this check:**
- ruOS `fleet_status` returned `machines=[]` and `peer_telemetry=unavailable` (`hbbs_db_available=false`); an empty array is **not proof the user's device is offline**.
- ruOS `desktop_status` returned `desktops=[]`; one **saved ruOS Lite browser** is present, but a cloud browser is **not** the owner's Windows PC.
- No known owner-machine heartbeat, OS identity, host filesystem, or real Hermes/SQLite backup could be inspected.
- Owner Windows P0 backup and restore: **NOT_TESTED**. P1 real tool crash/ESTOP: **NOT_TESTED**.

**Next human-required activation (no passwords or authentication codes in chat):**
1. On the actual owner Windows PC, sign in to the ruOS dashboard with the same authorized account and follow ruOS's device-enrollment instructions to make that particular Windows endpoint available. This is **user action**, not performed here.
2. From the ruOS control plane, confirm a **real machine_id** for that physical endpoint and a **fresh heartbeat/independent host identity**, rather than assuming `ready` means connected. Never infer host accessibility from the ruOS Lite browser.
3. For P0 first run the **existing read-only** `owner-lab/multiagent-safe-v3/WINDOWS_READONLY_PREFLIGHT.ps1` in an explicitly trusted session on the owner PC. Do not output user paths, hostname, secrets, usernames or documents. Save redacted JSON and exact script SHA.
4. **Do not** touch owner SQLite/WAL/SHM/backup until free space, backup target, ACLs, and restore plan receive explicit owner approval. Preserve existing ESTOP locks and logs.

Expected read-only evidence: host identity claim source, machine id (redacted if necessary), observed heartbeat timestamp, OS/available disk, Hermes state DB and backup presence, script SHA, raw exit status, no private data. Any missing field => `UNKNOWN`, not `PASS`.

## Blocker B: trusted protected epoch + actual human owner identity

What **exists**:
- Owner Lab's `approvals.py` verifies synthetic HMAC assertions (task, spec hash, TTL, nonce) and `orchestrator.py` applies deterministic preview-only policy.
- `isolated_authority_research.py` shows separate OS process + synthetic agent vs owner IPC capability.
- `durable_anchor_research.py` stores a research-only HMAC checkpoint/ESTOP latch; its optional `minimum_expected_epoch` refuses replay of both DB and checkpoint **only when the floor is from a genuinely independent protected source**.
- GitHub run [#43334654885](https://github.com/eltokhey1/hermes-agent/actions/runs/43334654885): 129/129 on Ubuntu and Windows + hosted Windows scratch NTFS write-denial PASS.
- The **same-user hosted CI environment is not an independent authority** for actual Hermes. Authentication to an IPC listener does **not** authenticate a human being.

Required production boundary (NOT deployed):
1. Owner authentication: supported independent identity provider with phishing-resistant owner login (e.g., passkey/WebAuthn), server-side session integrity and CSRF protection; owner approver identity obtained from the verified provider, never free text/model output.
2. Separate privileged approval service/account/VM not addressable from agent sandbox/tools. Model can submit an intent for review, **never issue, redeem or forge an owner approval**. Bind signed approval to `exact_action_hash`, authorized human, task ID, allowed effect, expiry, one-use nonce, and explicit decision.
3. Dedicated signer/epoch authority with key not readable by the model, agent tools, or DB process. The latest monotonic epoch and sealed journal head must be stored in a **separately protected non-rollbackable store**; do not treat a second file on the same disk or an in-process value as sufficient.
4. Independent ESTOP watchdog able to stop dispatch when the agent crashes or the signer/counter/identity provider is unavailable. Unknown action result => `UNKNOWN`, **no automatic retry**.
5. API/IPC authorization is enforced at a single deterministic Core policy gate at the moment of dispatch; fail closed on stale/missing signed epoch, mismatched SHA, expired token, replay, changed tool list, policy change, or cancelled task.
6. Validate through independent red-team tests: model calls owner endpoint, forged human identity, forged/mismatched hash, replay/expiry, wrong nonce, altered signed checkpoint, DB+checkpoint rollback, signer outage, ESTOP race, protected-account ACL denial, Windows crash/restore and ambiguous external result.

**No paid cloud service, new account, external identity integration, secret provisioning, separate protected signer or durable monotonic service has been authorized or created.** Real owner login requires an explicit secure UI interaction and cannot be inferred from permission to work on research branches.

## Verified, unverified, and GO boundaries

| Gate | Verdict as of 2026-11-13 | Evidence |
| --- | --- | --- |
| Research unit suite (Linux + hosted Windows) | VERIFIED synthetic-only | [CI #43334654885](https://github.com/eltokhey1/hermes-agent/actions/runs/43334654885), 258 PASS total |
| Temporary hosted Windows NTFS denied write | VERIFIED hosted-only | Same run, separate scratch user/job |
| Genuine Windows PC registered and heartbeat verified | BLOCKED/UNKNOWN | ruOS fleet telemetry unavailable, no machine listed |
| Actual Windows P0 protected backup + isolated restore | NOT_TESTED | Requires owner-device access and approved write |
| Actual P1 watchdog/ESTOP tool-call failure recovery | NOT_TESTED | No real isolated runtime |
| Real owner passkey/OIDC authentication channel | NOT_IMPLEMENTED | Synthetic channel capability only |
| Independently protected counter + signer | NOT_IMPLEMENTED | Conditional `minimum_expected_epoch` argument only |
| Human-signed exact-SHA acceptance and decision | NOT_TESTED | Not authorized by this research document |

**Decision remains** `PRODUCTION=HOLD`, `G0/G-CODE/G1=NO-GO`, `HITL=REQUIRED`, cloud/API spend `$0` unless separately bounded and approved.

## Smallest next action when PC becomes available

Do **not** immediately install/start a server. First detect the real ruOS endpoint and verify a fresh heartbeat, then run the existing read-only P0 inventory. Only after that can a separate-action human authorization cover a protected backup, scratch restore, identity provider integration or durable epoch service. All other statuses remain `UNKNOWN/NOT_TESTED`.
