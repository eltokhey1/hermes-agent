# Hermes Research & Solution Intelligence Hub — Cross-project roadmap
Date: 2026-10-18 · status: planning only

## One shared engine, not 100 competing agents
Research and evidence support: Hermes core, TradeOps/document audit,
shipment tracking, supplier verification, quotations, Crystal Agro Egypt,
CRM/Homi, SEO/GEO, SaaS opportunity validation and device interoperability.

## Single intake schema
project_id | question | candidate | original_source_url | source_date |
checked_at | license/terms | estimated_cost | data_sensitivity |
API/MCP availability | risks | corroboration_level | test_evidence |
approval_state | acceptance_criteria | last_status_change.

Levels must distinguish DISCOVERY from FIRST_PARTY_REVIEWED,
INDEPENDENTLY_CORROBORATED, SANDBOX_TESTED and PRODUCTION_VERIFIED.
Unknown data stays UNKNOWN; no claimed "verified profit" from directory MRR.

## Order of work
P0: audit local/remote security posture, restore-test backups, secrets,
fail-closed, non-production isolation.
P1: reliable intent/execution states, evidence of completion, human approvals.
P2: read-only connectors and tool/model routing with source policy registry.
P3: evidence-based commercial radar and user-approved MVPs.
P4: controlled improvement proposals and regression tests, with human
approval before any persistent self-modification.

## Commercial candidates (hypotheses, not revenue forecasts)
1. Trade Document Auditor — importer-facing structured discrepancy review.
2. Shipping & LC Intelligence — trustworthy ETA and bank document status.
3. Human-approved Quotation Assistant — draft/export quotations, no send.
Each is gated on buyer interviews, willingness-to-pay evidence and a
measured pilot. No guaranteed income is asserted.

## Tool/provider gate
- GitHub: official API docs, minimum scopes, authenticated quotas and rate
  limit responses; no blind retries.
- TrustMRR: terms restrict AI grounding/republication and wholesale data
  acquisition; **do not ingest API data into an AI recommendation system
  without written authorization**.
- MCP: tool metadata/annotations are descriptions, NOT trust boundaries.
  Enforce read-only behavior and permission checks in executable code.
- SEO: Google's multilingual guidance requires complete alternate URL sets
  for hreflang deployments. llms.txt alone is not an established
  Google ranking requirement.
- OSINT: passive supplier/company verification only, provenance and privacy;
  no invasive individual profiling, no confidential file uploads to public
  scanners, no unauthorized asset probing.

## Exit evidence
For every item marked DONE record a test, URL or artifact digest and date.
Documentation/design-only items must never appear as deployed or complete.
Do not merge these proposals into production on the strength of local unit
tests alone.
