# Portfolio reconciliation checkpoint — 2026-10-18

**REVIEW-ONLY / NOT PRODUCTION APPROVED.** This adds no executable code, credentials, dependencies, new runtime tool or production authority.

## One hierarchy, not three competing task queues

- **Private owner portfolio:** 45 canonical work packages across 16 workstreams. A verified, locally held register maps 120 unique historical task identifiers onto those 45 packages. No dangling references; sum of per-package link counts equals 120. The complete register is intentionally **not** committed to this public repository.
- **Hermes engineering:** This PR's [32 engineering acceptance-gate rows](./MASTER_IMPLEMENTATION_MATRIX.csv) are subordinate acceptance criteria, **not 32 extra portfolio work packages**. Qualify ambiguous IDs as `engineering_gate_id` versus `portfolio_package_id`.
- **Source and tool lists:** new repositories, agent skills, UI tools and images become research references to existing work packages, not automatically installed dependencies or new permanent agents.
- **Evidence:** a draft PR, owner-reported test, ZIP validation or isolated fixture test cannot establish Windows runtime readiness, actual restoration, or production approval.

## Nine draft PRs — reconciliation plan

At verification time, PRs [#1](https://github.com/eltokhey1/hermes-agent/pull/1) through [#9](https://github.com/eltokhey1/hermes-agent/pull/9) were all **open drafts**. These remain separate review candidates, not nine deployed capabilities.

| Draft | Relationship to portfolio | Next decision |
|---|---|---|
| #1 | TradeOps acceptance | Retain separate; no real data until approval |
| #2 | Installer experiment | Defer installation |
| #3 | Optional Android audit | Defer optional skill |
| #4 | Owner readiness + 32 engineering subgates | **Canonical engineering plan** |
| #5 | Evidence contract validator | Isolated candidate; requires true integration evidence |
| #6 | Research backlog | **Overlaps this PR in `ops/DESIGN_BACKLOG.md`**; compare unique content before any merge |
| #7 | Sanitized P0 inventory | Host/Windows unverified |
| #8 | Cloud security design | Defer cloud deployment and costs |
| #9 | Portfolio evidence/radar | Cross-reference in this plan; avoid second task queue |

Fork `main` remained at `251e5f7c0a067239655f3421812ab7492a206065`, with branch protection reported **off**, and zero Actions runs returned for this fork at the time checked. Do not force-sync, batch-merge, or assume CI is green.

## Single critical path

`P0 identity + redacted inventory → restricted encrypted backup + independently runnable isolated restore → fail-closed/secret-canary/hard cost-stop tests → P1 durable intent and UNKNOWN reconciliation → acceptance evidence and independent go/no-go → separate release approval`.

Other projects (shipping, CRM, commercial, content, bridge, UI/skills) use the same evidence and approval contract but maintain independent work-package IDs and release gates. No unapproved outward communication, expenditures, destructive operations, or production deployment.

## Intake / review rule

For each idea: problem + counterevidence → measured gap vs built-in capability → mapped package → source rights/risk/cost → minimal isolated test → reviewer evidence → explicit scoped authorization. Missing evidence means HOLD; ambiguous external effect means UNKNOWN/STOP (never blind retry).

**Privacy:** no booking numbers, customer records, private paths, backup manifests, API credentials or internal portfolio data may be published in this public fork.
