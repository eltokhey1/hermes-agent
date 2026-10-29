"""Fail-closed trade-document requirements registry; never invent national rules."""
from datetime import date

DOCS = {
 "COMMERCIAL_INVOICE": ("seller", "buyer", "invoice_number", "invoice_date", "description", "quantity", "unit_price", "currency", "total"),
 "PACKING_LIST": ("description", "quantity", "net_weight", "gross_weight"),
 "BILL_OF_LADING": ("bl_number", "shipper", "consignee", "vessel", "loading_port", "discharge_port", "on_board_date"),
 "CERTIFICATE_OF_ORIGIN": ("origin_country", "exporter", "description", "issuer"),
 "INSPECTION_CERTIFICATE": ("issuer", "inspection_date", "results"),
 "PHYTOSANITARY_CERTIFICATE": ("issuer", "commodity", "destination_country"),
 "HEALTH_CERTIFICATE": ("issuer", "commodity", "origin_country"),
 "INSURANCE_CERTIFICATE": ("insured_value", "currency", "coverage"),
 "COURIER_RECEIPT": ("tracking_number", "dispatch_date", "recipient"),
}

def assess(context, documents, rules):
    if not isinstance(context, dict) or not isinstance(documents, dict) or not isinstance(rules, list):
        raise ValueError("Invalid inputs")
    required = ("origin_country", "export_country", "import_country", "commodity", "shipment_date")
    if any(not context.get(x) for x in required):
        raise ValueError("Missing route/product context")
    try:
        date.fromisoformat(context["shipment_date"])
    except (TypeError, ValueError):
        raise ValueError("Invalid shipment date") from None
    findings = []
    for name, fields in DOCS.items():
        if name not in documents:
            continue  # no blanket rule that every document is legally required
        values = documents[name]
        if not isinstance(values, dict):
            raise ValueError("Invalid document")
        for field in fields:
            if not values.get(field):
                findings.append({"document": name, "field": field, "decision": "NEEDS_REVIEW",
                                 "reason": "Recommended core field absent; not automatically an LC discrepancy"})
    for rule in rules:
        if not isinstance(rule, dict) or not all(rule.get(k) for k in ("rule_id", "source", "effective_date", "jurisdiction", "commodity", "document")):
            raise ValueError("Rules require source, effective date, jurisdiction, commodity, document")
        if rule["jurisdiction"] not in (context["origin_country"], context["export_country"], context["import_country"]):
            continue
        if rule["commodity"] != context["commodity"]:
            continue
        if rule["document"] not in DOCS:
            raise ValueError("Unknown document in rule")
        try:
            effective = date.fromisoformat(rule["effective_date"])
        except (TypeError, ValueError):
            raise ValueError("Invalid rule date") from None
        if effective > date.fromisoformat(context["shipment_date"]):
            continue
        if rule["document"] not in documents:
            findings.append({"document": rule["document"], "rule_id": rule["rule_id"],
                             "decision": "NEEDS_REVIEW", "reason": "Source-linked required document not provided"})
    return {"status": "NEEDS_JURISDICTION_AND_LC_REVIEW", "findings": findings,
            "note": "No automatic legal or bank compliance certification; verify source currency and operative LC."}
