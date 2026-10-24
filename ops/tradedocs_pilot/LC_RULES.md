# MT700 rule prototype — synthetic data only

Use `python -m unittest discover -s . -p 'test_*.py'`. The `lc_rules.review(mt700_text, amendments)` function parses field-tagged plaintext only and returns NEEDS_REVIEW unconditionally. It **does not** authenticate SWIFT messages, MT707 amendments, OCR, or assess UCP 600 compliance. A request for amendment and even caller-supplied BANK_CONFIRMED metadata are never applied automatically.

Fields: 20, 31D, 44C, 44E, 44F, 46A, 47A, 48. Duplicate field tags and missing reference fail closed. The parser is deliberately narrow and cannot reliably parse all SWIFT message formats. Test evidence: 7/7 isolated synthetic unit tests; not Surface or hosted CI. No real LC data should be committed. PRODUCTION=HOLD.
