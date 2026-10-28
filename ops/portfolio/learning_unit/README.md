# Hermes Learning + Self-Improvement (offline pilot)
Reuses RAD-01/MKT-01, the existing guarded Hermes core and the shared architecture reference in the parent directory. No new agent, runtime permission, schedule or production activation.

## Local usage (Python stdlib only)
```bash
cd ops/portfolio/learning_unit
python -m unittest discover -v
python learning_unit.py registry.example.json
```

- `learning_unit.evaluate(record)`: validates weighted tool/skill evidence, rejects security/privacy scores below 3/5; VERIFIED requires structurally complete independent evidence (not proof that evidence is authentic).
- `self_improvement.propose(record, project, hypothesis, acceptance_test)`: produces proposal only.
- `knowledge_transfer.prepare_lesson(..., lesson)`: hashes a review-required lesson, never distributes it.

Outputs remain PRODUCTION=HOLD, G0/G-CODE/G1=NO-GO. No tool installs, external calls, writes, PR merges, automatic teaching, or promotion. GitHub CI and native Windows acceptance must be independently established for the exact SHA. All examples are synthetic; do not mistake tests for source authenticity or operational readiness.
