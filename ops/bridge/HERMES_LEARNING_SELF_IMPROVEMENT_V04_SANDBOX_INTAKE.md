# Hermes Learning + Self-Improvement v0.4 — sandbox intake

Status: STAGED_FOR_REVIEW / NOT_INTEGRATED / PRODUCTION=HOLD
G0=NO-GO; G-CODE=NO-GO; G1=NO-GO

This note records an independently tested local candidate; it does not claim that the Python modules are deployed or synchronized with agents.

Local artifact: Hermes_Learning_Self_Improvement_v0.4.zip (8 files).
Offline validation: `python -m unittest discover -s hermes_learning_unit -p 'test_*.py' -v` => 18 tests PASS on 2026-10-28.
Scope: learning/evaluation, proposal-only self-improvement, review-required knowledge transfer.
Evidence levels: TESTED_SYNTHETIC for local tests; UNKNOWN for Windows-native, restore, isolation, and CI on this new commit.

Next acceptance: import reviewed source files only after content inspection; run negative tests and CI on the exact target SHA; require independent Windows-native evidence. Never execute untrusted GitHub sources, auto-run Aider, or enable production.

No duplicate WP/PR; link to existing 45 WP / 120 IDs. No changes to main, external messages, secrets, or Windows services.
