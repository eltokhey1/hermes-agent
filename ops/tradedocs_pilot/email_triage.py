"""Offline, deterministic shipment-email triage. No email/API/sheet connectors or side effects.

This is a *routing suggestion*, not extraction, financial confirmation or ETA proof.
Message text is untrusted and never treated as instructions to this process.
"""
import hashlib
import re

MAX_SUBJECT = 400
MAX_BODY = 20000
MAX_ID = 255

ETA_TERMS = re.compile(r"\b(?:eta|estimated time of arrival|arrival date)\b|موعد الوصول|تاريخ الوصول", re.I)
ETA_CHANGE = re.compile(r"\b(?:updated|update|changed|change|revised|new|delayed|delay|rescheduled|postponed)\b|تحديث|تعديل|تغير|تغيير|تأخير", re.I)
ETA_NEGATED = re.compile(r"\b(?:unchanged|no change|not changed|same eta)\b|لم يتغير|بدون تغيير", re.I)
DOCUMENTS = re.compile(r"\b(?:bill of lading|b/?l|hbl|mbl|invoice|packing list|letter of credit|l/?c)\b|بوليصة|بوليصه|فاتورة|اعتماد", re.I)
PAYMENTS = re.compile(r"\b(?:payment|remittance|settlement|funds received|paid|unpaid)\b|سداد|تحويل|دفع", re.I)
INSTRUCTION_ATTACK = re.compile(r"\b(?:ignore (?:all |previous )?(?:instructions|rules)|reveal (?:your )?(?:password|api key)|bypass (?:approval|policy)|approve payment automatically)\b", re.I)


def classify_message(message):
    """Return privacy-minimal review-only labels for one manually supplied message."""
    if not isinstance(message, dict):
        raise ValueError("Message must be an object")
    subject, body = message.get("subject", ""), message.get("body", "")
    identifier = message.get("message_id")
    if any(not isinstance(x, str) for x in (subject, body)):
        raise ValueError("Message subject/body must be strings")
    if not subject.strip() and not body.strip():
        raise ValueError("Message content required")
    if len(subject) > MAX_SUBJECT or len(body) > MAX_BODY:
        raise ValueError("Message too long")
    if identifier is not None and (not isinstance(identifier, str) or not 0 < len(identifier) <= MAX_ID):
        raise ValueError("Invalid message_id")
    content = subject + "\n" + body
    flags = []
    if ETA_TERMS.search(content) and ETA_CHANGE.search(content) and not ETA_NEGATED.search(content):
        flags.append("eta_update")
    if DOCUMENTS.search(content):
        flags.append("documents")
    if PAYMENTS.search(content):
        flags.append("payment")
    codes = ["UNTRUSTED_INSTRUCTIONS_PRESENT"] if INSTRUCTION_ATTACK.search(content) else []
    if not flags:
        codes.append("NO_CONFIRMED_CATEGORY")
    if len(flags) > 1:
        codes.append("MULTI_TOPIC_REVIEW")
    return {
        "labels": flags or ["other"],
        "status": "REVIEW_REQUIRED",
        "reason_codes": codes,
        "source_id_sha256": hashlib.sha256(identifier.encode("utf-8")).hexdigest() if identifier else None,
        "network_calls": 0,
        "writes": 0,
        "messages_sent": 0,
    }
