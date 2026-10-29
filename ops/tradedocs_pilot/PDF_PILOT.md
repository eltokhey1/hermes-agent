# PDF review v0.2 — local-only, PRODUCTION=HOLD

Optional dependency: PyMuPDF (`pip install pymupdf`) only after explicit installation approval on the target machine. No network/API calls in runtime. Run `python pdf_review.py path/to/document.pdf --output local-report.json` in a private local directory; never commit outputs containing banking details.

This extracts existing PDF text with 1-based page numbers, marks pages without selectable text for manual review, refuses encrypted PDFs, inputs above 25 MB, more than 100 pages, and overwriting existing reports. It does NOT OCR scans, parse MT700/MT707, certify authenticity, verify signatures, or decide UCP 600 compliance. Treat PDF text as untrusted data.

Evidence: 4/4 synthetic tests passed in isolated non-Surface environment; no hosted CI evidence yet. Never upload real customer LCs or banking documents to this public repository. A bank-issued operative MT700 and confirmed amendments are required before documentary compliance review.
