# TradeDocs / Shipment Intelligence — Multi-platform product target

Status: **architecture decision / not yet implemented**.

## Product contract

Deliver three connected clients: responsive web (installable PWA where supported), iOS, and Android. All clients must use the same authenticated backend API, authorization policy, shipment and LC records, document store, and audit trail. A change from any client must be visible to the others after synchronization. Do not implement separate client-side authoritative databases.

## Lean staged rollout

1. **Web pilot:** extend the existing offline TradeDocs review into a responsive, accessible web workflow. Existing localhost API is **not** an Internet-facing backend; preserve its loopback-only guard.
2. **Shared backend:** implement authenticated versioned API, tenant isolation, RBAC, server-side validation, audit log, idempotent mutations, and object storage for sensitive documents. Use PostgreSQL for production data; migrations and backups required.
3. **Mobile:** build iOS and Android clients with Expo/React Native, reusing shared TypeScript API contracts where practical. Mobile sessions must use platform secure credential storage. Camera document capture and upload require explicit consent.
4. **Release:** web staging + mobile test builds first; App Store / Google Play publication only after platform compliance, privacy/security review, and explicit publish approval.

## Release gates

- No financial, bank, production, publishing, external messaging, or secrets action without HITL approval.
- No public exposure of the existing `local_api.py` or real bank/customer data in the synthetic pilot.
- CI unit/integration/security checks, cross-device synchronization tests, tenant isolation tests, and iOS/Android device smoke tests must pass before any production-ready claim.
- Monitor cost per successful task, latency, failure rate, and user conversion in pilot.
- Keep Hermes core production HOLD until its own gates pass independently of TradeDocs.

## Explicit non-goals for current offline pilot

No live Outlook/Graph integration, shipping-line API, real bank reconciliation, automatic regulatory compliance certification, production hosting, or app store publication is implemented by this document.
