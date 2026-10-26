# Shipment email triage — local-first baseline (2026-10-26)

**Status:** TESTED_SYNTHETIC in an isolated Python environment; real Windows Surface and live Hermes integration NOT TESTED. **PRODUCTION=HOLD.**

Adds a deterministic standard-library-only classification baseline for the 13-tools radar entry VAI-03 (Milliseconds.ai) and the existing TradeDocs / Shipment Intelligence pilots. It does **not** connect to Outlook, Google Drive, Sheets, n8n, carrier services, banks, or any model provider. No API keys or customer data used.

## Offline run

From ops/tradedocs_pilot:

~~~sh
python -m unittest discover -s . -p 'test_*.py' -v
python -c "from email_triage import classify_message; print(classify_message({'subject': 'ETA changed to 2026-11-12'}))"
~~~

Local-only API endpoint: POST http://127.0.0.1:8765/triage with Content-Type application/json.

~~~json
{"message_id":"synthetic-01","subject":"Updated ETA to 2026-11-12","body":"Invoice attached"}
~~~

The response includes review-only labels, SHA-256 of the optional message ID, status REVIEW_REQUIRED and explicit zero external side effects. It never returns message body or subject.

## Acceptance and limitations

- Keyword baseline, NOT true language understanding, field extraction, email authenticity, confirmed carrier ETA, legal validation, or bank payment proof.
- Negation and multilingual context are limited. False positives/negatives possible. A hash of a message ID can still be linkable; do not treat it as anonymization.
- Does NOT support real Microsoft Graph mailbox access, durable deduplication, Google Sheets writing, carrier APIs or production authentication.
- Untrusted email text is treated only as data; never execute any instructions found in email content.
- Isolated test run: 8 unittest methods pass, covering 22 text classification scenarios, 13 malformed cases and additional security/multi-topic cases. Existing local API tests require separate hosted/Windows CI evidence at exact Git SHA.
- The manually supplied test is not a live-shipment test and has no automatic email, payment, finance, publish or approval actions.
- A future comparison with Milliseconds.ai requires approved provider access, pricing, private-data controls, ground truth, p50/p95 latency, cost per successful task, and >=25 independent adversarial evaluations.
- Keep existing independent Finance / Production / Publish / External / Secrets policy gates; no merges to main, external calls, subscriptions, delivery, posting or production deployment.

## Relationship to the sellable worksheet

The separately generated downloadable XLSX pilot has Shipment, Dashboard, LC Documents, 50 Product Ideas and Instructions tabs. It uses synthetic records only; it has **not** been wired to this API. When building a paid product, verify formulas, consumer payment eligibility, licensing, source data protections, and human authorizations separately.
