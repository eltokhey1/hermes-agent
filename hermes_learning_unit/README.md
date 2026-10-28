# Hermes Learning + Self-Improvement v0.4 (sandbox only)

Three standard-library-only modules:
- `learning_unit.py`: weighted evaluation, evidence structure and fail-closed security/privacy gates.
- `self_improvement.py`: proposal-only improvement, no execution.
- `knowledge_transfer.py`: deterministic SHA-256 lesson receipt, `REVIEW_REQUIRED`, never distributes.

## Local validation
Run from the repository root:
```bash
python -m unittest discover -s hermes_learning_unit -p 'test_*.py' -v
python hermes_learning_unit/learning_unit.py hermes_learning_unit/registry.example.json
```
Expected: 18 tests; local validation only, **not Windows-native acceptance**.

## Security / limitations
`PRODUCTION=HOLD`, `G0/G-CODE/G1=NO-GO`. No auto-merge, tool execution, installs, publication or agent synchronization. Evidence validation checks only structure, not authenticity or independent provenance. A `VERIFIED` label in input is **not** production authorization. Import paths expect tests to run using unittest discover with `-s hermes_learning_unit`.

Before acceptance, run CI on the exact target SHA, negative/adversarial tests, Windows-native checks and independent evaluation. Link to existing 45-WP/120-ID work plan; do not create a duplicate PR.
