# Hermes HX P1 — research boundary contract (NOT PRODUCTION)

- Date: 2026-11-24.
- Branch forked from commit `5163296ead8df9c24c20ceca53de49ce6aa8821d`.
- Local tested Python prototype (source SHA256): `542439124eb61ae1ac0f1fda3069ddda1bafc0e28aba28799f2ae6cb1c437039`.
- Full local research archive (SHA256): `edeab8aebadf14d6ae3f5cf66537b70f5268c682934e449c89a3846a262f5d8e`.
- **DO NOT claim the local test was hosted.** The checked-in source, pinned hosted workflow and successful hosted job are not yet present on this branch.

## Local execution (unprivileged worker UID 65534)

VERIFIED_LOCAL_SYNTHETIC: 3/3 inert actions `browser.navigate`, `mcp.invoke`, `inline.memory` required an Ed25519 signed owner grant from an independent broker process. Wrong signature, replay, cross-effect substitution, argument substitution, and agent-issued owner approvals were denied.

VERIFIED_LOCAL_SYNTHETIC: Root-owned ESTOP sentinel blocked new operations; unprivileged worker could not clear it; approvals from the previous epoch were denied after resume; 4/4 same-host witness Ed25519 receipts verified with a monotonically increasing sequence and hash chain.

UNKNOWN/NOT_ATTESTED: real Hermes `agent.estop.is_engaged` source import in this **local** lab (the local harness skipped that import), real Browser navigation, MCP transport lifecycle, Inline memory effects as a single agent session, OS broker wired into `agent.tool_executor`, user-authenticated owner identity, offhost/independently protected witness, in-flight emergency kill, protected rollback anchor.

The existing hosted Hermes component-regression evidence is independent of this prototype: [63 source tests at SHA 41bddbb70850f89779b78aa395ecb6b4a6c5686d](https://github.com/eltokhey1/hermes-agent/actions/runs/45348171650).

## Hosted acceptance prerequisites

1. Place exact reviewed human-readable Python source in this research branch; independently compare SHA256 with the local receipt. Do not auto-repair/trust mismatched bytes.
2. Run one strictly scoped GitHub Actions job on Ubuntu with pinned Python 3.14 and `uv.lock`, within an OS-level whole-process wrapper, without network and without any real external actions.
3. Verify no authority secret is reachable by worker UID, independently verify signature and anti-replay, verify actual `agent.estop.is_engaged()`, and preserve job logs at exact SHA.
4. Separate real browser/MCP/inline end-to-end tests and owner human identity/offhost witness into independent acceptance evidence. A same-runner witness is NOT offhost.

`PRODUCTION=HOLD` · `HITL=REQUIRED` · `G0/G-CODE/G1=NO-GO` · paid spend default `$0` · **9.8/10 not verified**.
