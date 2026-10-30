# ADR-0001: Harness and Loop portfolio boundary

- Status: Accepted for classification and authority boundaries
- Date: 2026-10-31
- Scope: Owner portfolio governance only; no production or deployment effect
- Evidence state: `MAPPING_HOST_UNVERIFIED`

## Context

The owner readiness plan defines one portfolio of 45 work packages associated with
120 legacy IDs. The authoritative row-level portfolio register is private and is
not present in this public repository. This ADR therefore records the approved
classification totals and authority boundary without reproducing, renaming, or
reprioritizing private register entries.

The classification is:

- Harness: 23 work packages.
- Loop: 22 work packages.
- Total: 45 work packages.

Every existing portfolio package ID, all 120 legacy IDs, and every recorded
priority remain unchanged. Classification adds an ownership boundary; it is not
an ID migration, reprioritization, acceptance decision, or production approval.
Row-level correspondence to the private register remains
`MAPPING_HOST_UNVERIFIED` until the owner supplies an independently reviewable
register receipt or digest.

## Decision

Harness owns the controls that constrain, authorize, observe, and accept Loop
activity. Loop may propose or execute improvements only inside those controls.
This classification does not independently authorize any Loop execution.

Loop MUST NOT directly or indirectly modify, bypass, weaken, reinterpret, or
self-approve any of the following Harness-owned controls:

1. Harness policies and enforcement rules.
2. Human or automated approval gates, approver identity, or separation of duties.
3. Budgets, spending limits, resource caps, or accounting controls.
4. Acceptance criteria, evidence requirements, evidence sources, evidence
   retention, or evidence status.
5. Production promotion gates or the recorded readiness state.

Loop output is candidate evidence only. Loop cannot promote its own output to
accepted, verified, approved, or production-ready evidence. Any exception
requires explicit human approval and a superseding ADR; a Loop action alone can
never create an exception.

## Preserved gate state

This ADR does not change the current gates:

- `PRODUCTION=HOLD`
- `G0=NO-GO`
- `G-CODE=NO-GO`
- `G1=NO-GO`

It authorizes no merge, deployment, publication, production configuration
change, package installation, host mutation, or workflow execution.

## Verification and evidence limits

The arithmetic invariant is `23 + 22 = 45`. The 45-package/120-ID register must
be compared separately in its protected location to prove that each row was
classified exactly once and that no ID or priority changed. Until that comparison
is independently reviewed, the numeric classification is accepted but the
row-level mapping remains `MAPPING_HOST_UNVERIFIED`.

P0-01 Windows inventory evidence is also separate. GitHub-hosted Windows results
and repository metadata do not establish the identity, active home, health, or
acceptance of the owner's installed Windows Hermes runtime. Those claims remain
`HOST_UNVERIFIED` until owner-host receipts are captured and independently
reviewed.

## Consequences

- Future portfolio work must preserve the 23/22 totals unless a superseding ADR
  explicitly changes the classification.
- The private register remains authoritative for package IDs, legacy IDs, and
  priorities; this ADR cannot be used to reconstruct or alter it.
- Harness controls prevail over conflicting Loop proposals or outputs.
- Missing or ambiguous evidence fails closed and cannot advance any production
  gate.
