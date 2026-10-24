"""Local-only LC shipment document tracking. No emails, cloud writes or notifications."""
from datetime import date, timedelta
from urllib.parse import urlparse

def review(record, today=None):
    if not isinstance(record, dict):
        raise ValueError("Expected a record")
    today = today or date.today()
    if not isinstance(today, date):
        raise ValueError("Invalid review date")
    ref = record.get("lc_number")
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError("Missing LC reference")
    alerts = []
    def flag(code, message):
        alerts.append({"code": code, "message": message, "action": "REVIEW_ONLY"})
    for key in ("bl_type", "dhl_tracking_number", "documents_sent_date", "bank_received_date",
                "vessel_eta", "payment_due_date", "payment_received_date"):
        if key not in record or record[key] in ("", None):
            flag("MISSING_" + key.upper(), key + " not confirmed")
    kind = record.get("bl_type")
    if kind not in (None, "", "MBL", "HBL", "UNKNOWN"):
        raise ValueError("Invalid B/L type")
    if kind == "HBL":
        flag("HBL_LC_TERMS", "Verify house bill acceptance against operative LC")
    for field in ("documents_sent_date", "bank_received_date", "vessel_eta", "payment_due_date", "payment_received_date"):
        value = record.get(field)
        if value:
            try:
                parsed = date.fromisoformat(value)
            except (ValueError, TypeError):
                raise ValueError("Invalid ISO date: " + field) from None
            if field in ("vessel_eta", "payment_due_date") and parsed < today and not record.get("payment_received_date" if field == "payment_due_date" else "arrival_confirmed"):
                flag("OVERDUE_" + field.upper(), field + " has passed without confirmation")
            if field == "payment_due_date" and today <= parsed <= today + timedelta(days=7) and not record.get("payment_received_date"):
                flag("UPCOMING_PAYMENT", "Payment due within seven calendar days; verify bank status")
    if record.get("documents_sent_date") and not record.get("dhl_tracking_number"):
        flag("DHL_REQUIRED", "Documents marked sent but DHL tracking missing")
    if record.get("bank_received_date") and not record.get("documents_sent_date"):
        flag("INCONSISTENT_RECEIPT", "Bank receipt recorded without dispatch date")
    if record.get("payment_received_date") and not record.get("payment_confirmation_reference"):
        flag("UNVERIFIED_PAYMENT", "Recorded receipt needs independent bank evidence")
    return {"lc_number": ref, "status": "NEEDS_REVIEW", "alerts": alerts, "notifications_sent": 0}

def validate_drive_folder_url(url):
    """Accept only folder links for future explicit, approval-gated connector setup."""
    if not isinstance(url, str):
        raise ValueError("Invalid URL")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "drive.google.com" or not parsed.path.startswith("/drive/folders/"):
        raise ValueError("Expected an HTTPS Google Drive folder URL")
    return url
