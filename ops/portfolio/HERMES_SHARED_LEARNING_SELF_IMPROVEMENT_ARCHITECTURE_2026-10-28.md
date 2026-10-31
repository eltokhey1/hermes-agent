# Hermes shared learning, architecture selection and self-improvement reference
Date: 2026-10-28
Status: SOURCE_IMAGE_REVIEWED / DESIGN_REGISTERED / IMPLEMENTATION_NOT_VERIFIED
Scope: existing RAD-01/MKT-01 and Hermes P0/P1; **no new agent, schedule, canonical WP or deployment**.

## Intake and evidence
Source: four user-supplied infographics on enterprise AI system selection, AI vs ML engineering, 15 AI terms, and nine AI stack layers. These are **secondary illustrative sources**, not proof of product performance, pricing, security, or production readiness. Register each candidate with original official documentation, license, version/commit, privacy/residency, Windows compatibility, maintenance, test fixture, measured quality/latency/cost, and independent reviewer before promotion. Deduplicate against existing portfolio registry and compare against the currently approved option.

## Decision matrix (start from the business problem)
| Need | Minimum viable approach | Escalate only when |
|---|---|---|
| Answers grounded in internal documents | permission-scoped keyword/FTS5 search with citations | hybrid RAG measurably improves retrieval |
| BL/LC/invoice/packing-list extraction (TradeDocs AI) | deterministic parsing + bounded OCR candidate + field provenance + human review | vision/model challenger beats baseline on representative fixtures |
| Shipment ETA / discrepancy | read-only licensed source adapter + event ledger | trusted source access and event tests exist |
| Cross-system tasks | deterministic workflow, strict schemas and HITL | agentic planning beats bounded workflow |
| Data insights | SQL with allowlisted read-only queries | predictive ML has validated labels and business uplift |
| Customer replies / marketing | approved knowledge and human sign-off | safe and measured workflow is demonstrated |
| Multiple agents | one router with specialist modes and independent verifier | coordination benefit outweighs latency/cost/attack surface |
| Sensitive local data | local model and least-privilege gateway | external processing separately authorized |

## Engineering competency map
AI application engineering: Python, JSON/SQL, APIs, prompt and retrieval evaluation, tool schemas, security, cost/latency tracing, deterministic CI, provenance and human approval.
ML engineering: data quality, splits/leakage, feature engineering, training, validation, calibration, drift and serving.
Do not require custom model training, cloud services, vector databases, agent frameworks or Kubernetes without measured need. Prefer existing SQLite/FTS5 and governed core.

## Shared glossary
LLM: language model; ML: learning from data; hallucination: unsupported generated claim; token: model input/output unit; context window: bounded working context; AGI: speculative general intelligence; MCP: tool interoperability protocol, **not** a security boundary; training: weight updates; inference: using a trained model; fine-tuning: additional task/domain training; reinforcement learning: optimization using feedback; distillation: transferring behavior to a smaller model; RAG: retrieval-grounded generation; chain-of-thought: reasoning-related term, not an audit record; weights: learned parameters; validation loss: metric on held-out data, not a guarantee of business quality.

## Nine-layer coverage checklist, not a mandatory shopping list
0. Inference and deployment: local Ollama candidate first; cloud only with approval.
1. Evaluation: deterministic acceptance fixtures, regression and adversarial tests.
2. Models: compare aliases and measured baselines; no hardcoded provider assumptions.
3. Application framework: reuse existing Hermes routing before introducing frameworks.
4. Search: SQLite FTS5 first; vector retrieval only with demonstrated improvement.
5. Embeddings/runtime: optional; benchmark CPU/RAM and cost.
6. Ingestion/parsing: source-aware, schema-validated and redacted.
7. Memory: durable SQLite state; prevent leakage and stale cross-project propagation.
8. Guardrails/observability: Mercury-style fail-closed policy, ESTOP, allowlists, budget, receipts and independent verification.

## Closed-loop learning and self-improvement (proposal-only)
1. RADAR_INTAKE: record source and candidate with dedup key (canonical URL + version).
2. STUDY: classify problem, license, threat model and alternative.
3. EVALUATE: benchmark on synthetic/offline fixtures; mark VERIFIED only with traceable evidence for the exact artifact/version.
4. PROPOSE: hypothesis, affected project, expected business benefit, minimal diff, acceptance test, rollback plan, cost and owner.
5. VERIFY: independent evaluator reviews failures, security, quality, latency, cost per successful task, and Windows-native evidence when required.
6. TEACH: publish only reviewed lessons to shared registry; never inherit tool permissions across projects.
7. PROMOTE: only after G0/G-CODE/G1 evidence and explicit applicable approvals. UNKNOWN effects are never automatically retried.

Allowed states: CANDIDATE, UNDER_STUDY, TESTED_SYNTHETIC, VERIFIED, REJECTED. Improvement proposals remain PROPOSED_ONLY until independent approval; low security/privacy scores block promotion. Existing local prototype `learning_unit.py` + `self_improvement.py` was tested separately (10 offline synthetic tests) but **is not installed or verified in this repository**.

## Project routing
- Hermes Core: gateway, receipt/audit, guarded tool routing, acceptance.
- TradeDocs AI: document intelligence, source position and HITL.
- Shipment Intelligence: read-only events, ETA discrepancy.
- Radar: discovery, source trust, dedup and comparisons.
- Designer: approved content and accessible interfaces, not autonomous publishing.

## Non-negotiable gate
PRODUCTION=HOLD; G0/G-CODE/G1=NO-GO; no merge, production deploy, external messages, purchases, installs, secrets, or account linking. This document is research/design evidence only, not implementation or native Windows acceptance.
