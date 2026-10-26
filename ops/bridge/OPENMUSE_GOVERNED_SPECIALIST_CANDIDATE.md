# OpenMuse — governed specialist candidate for Hermes Open Builder

Status: CANDIDATE / NOT INSTALLED / NOT EXECUTING. PRODUCTION=HOLD. G0/G-CODE/G1=NO-GO.

## Role
OpenMuse is proposed as the **human-facing interaction and browser specialist** beneath the existing Hermes Supervisor/Policy Gate, not as a replacement for Hermes, an autonomous privileged orchestrator, or an authorization authority.

Potential responsibilities: display agent inbox, progress, action previews, task timeline and audit evidence; support Follow and Take Over UX; prepare browser tasks for explicit human approval; explore reusable React Native/iOS/Android/web components for TradeDocs AI and Shipment Intelligence.

## Architecture boundary
User -> OpenMuse UI (untrusted request) -> Hermes Supervisor -> deterministic Policy Gate -> approved scoped tool -> independent Verifier -> evidence/audit -> OpenMuse UI.

All tool permissions are deny-by-default. No direct access to Windows host, secrets, mailbox, financial actions, production, GitHub merge, deployments, or external messages. No automatic execution of repository-provided instructions or incoming Python. Never claim browser/terminal/files access before it is separately configured and verified.

## Evaluation (reuse before install)
1. Identify canonical upstream repository, license, pinned version/commit, and actual dependencies. Screenshot is not proof of repository identity or safety.
2. Read upstream source and security model without executing it. Review CopilotKit/React Native compatibility, authentication, session isolation, logging, prompt injection handling, and cost.
3. Prefer reusing existing Hermes UI and policy gate; reject redundant agent runtime.
4. Synthetic tests: denied actions, prompt injection, untrusted tool output, approval bypass, duplicate task, timeout/retry, secret redaction, cancellation, Follow/Take Over, accessibility and mobile rendering.
5. Test isolated pilot with explicit resource limits and no credentials; record hashes, reproducible commands, and evidence. No production activation without independent acceptance.

## Existing source of truth
Map any accepted work to the existing 45 WP / 120 IDs portfolio and existing PR; do not create a parallel roadmap, PR, or task ledger. This file is a scoped evaluation note only.

## Evidence
User-supplied OpenMuse README screenshot: browser/terminal/files, follow/take over, CopilotKit React Native, web/iOS/Android claims are **UNVERIFIED_UPSTREAM** until confirmed from the canonical repository. No installation or runtime test has been performed.
