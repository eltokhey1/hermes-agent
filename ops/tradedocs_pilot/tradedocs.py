"""Offline structured-input TradeDocs pilot. No network or document mutation."""
import json
import sys
from pathlib import Path

FIELDS = ("invoice_number", "lc_number", "bl_number", "currency", "total_amount", "port_of_discharge")
TYPES = ("invoice", "packing_list", "bill_of_lading", "letter_of_credit")


def audit(documents):
    if not isinstance(documents, dict) or not documents or set(documents) - set(TYPES):
        raise ValueError("Invalid document types")
    if any(not isinstance(doc, dict) for doc in documents.values()):
        raise ValueError("Documents must be objects")
    issues = []
    for field in FIELDS:
        values = [(kind, doc[field]) for kind, doc in documents.items() if field in doc and doc[field] not in (None, "")]
        if any(isinstance(value, (dict, list, bool)) for _, value in values):
            raise ValueError("Unsupported field value: " + field)
        if len({str(value).strip().casefold() for _, value in values}) > 1:
            issues.append({"field": field, "code": "CONFLICT", "sources": [kind for kind, _ in values]})
        if not values:
            issues.append({"field": field, "code": "MISSING", "sources": []})
    return {"status": "REVIEW_REQUIRED" if issues else "NO_DETECTED_CONFLICTS",
            "issues": issues, "documents_checked": sorted(documents)}


def main(argv):
    if len(argv) != 2:
        raise SystemExit("Usage: python tradedocs.py synthetic_input.json")
    path = Path(argv[1])
    if path.stat().st_size > 1_000_000:
        raise ValueError("Input too large")
    print(json.dumps(audit(json.loads(path.read_text(encoding="utf-8"))), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv)
