# TradeDocs — LC logistics and settlement tracker (offline prototype)

`shipment_tracker.review(record, today)` returns review-only alerts. It does not contact DHL, Google Drive, shipping lines, banks, email, or calendar. All dates are ISO YYYY-MM-DD. Inputs are provided manually until independently authorized read-only integrations exist.

Fields: `lc_number`, `bl_type` (MBL/HBL/UNKNOWN), `dhl_tracking_number`, `documents_sent_date`, `bank_received_date`, `vessel_eta`, `arrival_confirmed`, `payment_due_date`, `payment_received_date`, `payment_confirmation_reference`. Bank receipt of documents and payment receipt are distinct events. No due date is calculated from the LC's 60 **working days** clause without a bank-confirmed presentation date, applicable calendar and settlement rule. Carrier ETA is provisional, not guaranteed. HBL vs MBL must be checked against operative LC terms; it does not determine direct vs indirect LC status.

Google Drive: only folder URL validation is included, not OAuth, permissions, uploads or synchronization. Cloud write/read requires explicit EXTERNAL/SECRETS approval and scope-limited connection. Never store actual banking documents in public GitHub. No notification scheduler has been activated. Test with `python -m unittest discover -s . -p 'test_*.py'`; synthetic test file included. PRODUCTION=HOLD.
