# Persistent State Fail-Closed Regression (owner lab only)

Before fix, synthetic negative tests reproduced **three specific unsafe outcomes**:
1. A high-risk `demo.review` task changed in SQLite to a valid low-risk `demo.echo` payload after approval and was accepted at reservation despite the stored immutable spec hash being unchanged.
2. Reusing an idempotency key still returned a task ID when the matching stored task contract was damaged.
3. A fully emptied events ledger returned valid while persistent tasks remained.

Remediation: `HermesReference._stored_spec()` validates contract shape and the original spec hash on reads and transitions; idempotency reuse also checks persistent contract integrity. Ledger verification requires a unique `SUBMITTED` event for every current task (and no orphan submitted IDs).

The follow-up tests use writable temporary SQLite **only to simulate corruption**; production relies on separate OS ACL/trust boundary and an independent, protected ledger anchor. A hostile actor able to rewrite both DB state and the hash chain is not prevented by this lab. Real approval identity remains unimplemented. No network, subprocess, or physical device functions were added.

Isolated Python 3.13.5: `python -m unittest discover -s tests -q` -> 60 tests PASS. `python -m compileall -q approvals.py orchestrator.py patterns.py physical_sim.py local_router.py tests` -> PASS. **No Windows/CI acceptance claim**. Keep PR Draft and `PRODUCTION = HOLD`.

## Further reproduced integrity gap (same PR, no new project)

Nine added regression tests cover forged task states, valid-but-truncated event suffixes, orphan/replayed transitions, spec hash corruption, and decision-boundary bypass. Before the fix, six ledger-consistency negatives and two decision-boundary negatives failed as expected (the remaining positive case passed). After replay-based verification and transaction-bound guards: **69/69 tests passed** with warnings treated as errors. This hardens only demo references, not real Windows Hermes or a production policy engine.
