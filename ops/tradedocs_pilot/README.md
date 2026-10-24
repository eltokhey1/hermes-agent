# TradeDocs AI — offline structured-input pilot

**PRODUCTION=HOLD.** No LLM, OCR, email, browser, secrets, payments, external calls, or file modification.

Run `cd ops/tradedocs_pilot && python -m unittest discover -s . -p 'test_*.py' -v` and `python tradedocs.py synthetic_input.json`.

Input: JSON object keyed by `invoice`, `packing_list`, `bill_of_lading`, `letter_of_credit`; values are manually prepared field dictionaries. Output: mismatch/missing-field report. Missing fields are informational; `NO_DETECTED_CONFLICTS` does **not** mean documents are compliant, authentic, complete, or approved. This pilot does not parse PDF or Office documents.

HITL: Finance, Production, Publish, External, Secrets. Never commit real personal, banking, or commercial documents to this public repository.
