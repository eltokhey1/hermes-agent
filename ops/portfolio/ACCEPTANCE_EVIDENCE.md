# P0/P1 acceptance gates and evidence requirements

**Gate status on 2026-10-18: P0=UNVERIFIED, P1=UNVERIFIED, production_ready=NO.**

| Gate | Minimal evidence, in real isolated Hermes environment | Current state |
|---|---|---|
| P0-1 | Read-only inventory of current Windows runtime commit/version/config, no token leakage | UNVERIFIED |
| P0-2 | Timestamped backup checksum and *actual isolated restore* with smoke-test logs | UNVERIFIED |
| P0-3 | Four denial traces: timeout, empty, malformed, network failure | UNVERIFIED |
| P0-4 | Synthetic key leakage scan against logs, reports, git state; zero matches | UNVERIFIED |
| P0-5 | Fixed spend cap $0 and verified stop before spend | UNVERIFIED |
| P0-6 | Cross-tenant boundaries tested with unauthorized negative cases | UNVERIFIED |
| P1-1 | Durable pre-action intent journal and explicit operation ID before real effects | UNVERIFIED |
| P1-2 | PENDING / RUNNING / SUCCEEDED / FAILED / UNKNOWN transitions with reconciliation | UNVERIFIED |
| P1-3 | UNKNOWN is not auto-retried, including after restart | UNVERIFIED |
| P1-4 | Independent acceptance hashes/receipts and separately verified watchdog bounds | UNVERIFIED |

## Approval boundaries
No payment, messaging, deployment, destructive file operation, external tool invocation or sensitive customer-data processing is authorized by a model output, JSON field, advisory rule, or branch merge. Approvals must originate from a trusted external authorization system with durable evidence.

## Failure evidence integrity
Null/unavailable test evidence is **not** a pass. Keep source timestamp, method, artifact checksum, expected/observed result, executor/reviewer and redaction decision. Avoid attaching credentials, personal documents or raw customer data to Issues/PRs.

## Unverified compatibility
Local mocks may test message shapes, but only a real, version-pinned host + MCP SDK test can establish GPT/Claude/Gemini/Ollama interoperability for a given environment.
