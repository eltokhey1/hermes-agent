# Hermes Learning + Self-Improvement (offline pilot)
Reuses RAD-01/MKT-01, the existing guarded Hermes core and the shared architecture reference in the parent directory. No new agent, runtime permission, schedule or production activation.

## Local usage (Python stdlib only)
```bash
cd ops/portfolio/learning_unit
python -m unittest discover -v
python learning_unit.py registry.example.json
```

- `learning_unit.evaluate(record)`: weighted tool/skill evaluation; rejects security/privacy scores below 3/5. **A self-declared VERIFIED status is always rejected until external independent attestation is implemented and verified.** No input evidence field can self-promote a candidate.
- `self_improvement.propose(record, project, hypothesis, acceptance_test)`: produces a proposal only.
- `knowledge_transfer.prepare_lesson(..., lesson)`: hashes a review-required lesson; never distributes it.

## Evidence and acceptance
Run tests on the exact source SHA. `python -m unittest discover -v` is a free, local test and does not establish native Windows acceptance. Collect independent attestation, Windows-native test logs, backup/restore and isolation evidence separately. GitHub Actions pending/queued means **UNKNOWN**, not PASS. The existing CI and Docker workflows may execute on this documentation branch; do not infer that any job is successful until its final conclusion is checked.

Outputs remain PRODUCTION=HOLD, G0/G-CODE/G1=NO-GO. No tool installs, external calls, writes, PR merges, automatic teaching, or promotion. All examples are synthetic; do not mistake tests for source authenticity or operational readiness.
