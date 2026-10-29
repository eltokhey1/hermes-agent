# Web + iOS + Android implementation backlog

**Current release:** offline localhost pilot only. A connected website and mobile apps are **not yet deployed**.

## P0 — verify current pilot
- [ ] GitHub CI for the exact commit is green; review all failed checks.
- [ ] Run browser smoke test for review, error handling, and four languages.
- [ ] Validate loopback Host/Origin restrictions and no real-data leakage.
- [ ] Record manual pilot acceptance evidence.

## P1 — shared secure backend
- [ ] Define OpenAPI contracts for shipments, documents, LC balances and review outcomes.
- [ ] Add authentication, tenant isolation, RBAC, idempotency, and append-only audit events.
- [ ] Add PostgreSQL migrations and backups; encrypted object storage.
- [ ] Integrate Microsoft Graph Mail.Read **read-only** with mailbox scoping and explicit authorization.
- [ ] Add provider adapters for shipping lines with rate limits and provenance; mark ETA unconfirmed until corroborated.

## P2 — connected clients
- [ ] Responsive accessible web dashboard with installable PWA support.
- [ ] Expo/React Native iOS and Android app using the same backend.
- [ ] Camera capture, document upload and review with explicit consent.
- [ ] Verify updates synchronize across all three clients and tenant boundaries cannot be crossed.

## P3 — staging / distribution
- [ ] Deploy isolated staging backend with secret management and access controls.
- [ ] Publish staging web URL only after security verification and publish approval.
- [ ] Produce internal iOS/Android test builds; store releases require compliance and approval.
- [ ] Measure cost per successful review, error rate, latency and pilot customer feedback.

**Stop conditions:** no automatic financial execution, bank approvals, production rollout, public document access, or unapproved external messages. Do not expose the existing loopback API to the Internet.
