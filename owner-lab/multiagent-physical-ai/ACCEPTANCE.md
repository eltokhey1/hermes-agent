# Owner Lab acceptance mapping (not a new portfolio track)

| Gate | Stage | Status | Proof still needed |
|---|---|---|---|
| Read-only inventory + backup/restore | P0 | UNKNOWN / NO GO | Owner Windows trusted restore and ACL negative tests |
| Durable intent and crash recovery | P1 | REFERENCE TESTED ONLY | Real runner restart without duplicated external effects |
| Independent evidence/verifier | P1 | REFERENCE TESTED ONLY | Real proof per field, staleness and tamper anchoring |
| Agent task routing / tool connectors | P2 | NOT INTEGRATED | Consumer adapter + least-privilege allowlist + E2E |
| Model cost fallback | P2 | NOT INTEGRATED | Free quota exhaustion, default-deny paid model |
| Observatory / ledger privacy | P1/P2 | REFERENCE TESTED ONLY | Protected independent anchor + redaction and tracing review |
| Physical AI virtual safety demonstration | Future research | REFERENCE TESTED ONLY | Dedicated simulator benchmark, actual safety-case (future) |
| Physical AI real motors/robot | Future research | DENIED | Physical-world approval and independent certified controls |

Acceptance rule: Missing evidence means UNKNOWN; never report PASS from isolated synthetic tests. A verdict-affecting change restarts the shadow observation window. Do not bypass owner approvals.
