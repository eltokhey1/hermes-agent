"""Conservative per-LC shipment utilization; decimal arithmetic, no bank claims."""
from decimal import Decimal, InvalidOperation

def number(value):
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid decimal") from None
    if not d.is_finite() or d < 0:
        raise ValueError("Amounts and quantities must be finite and nonnegative")
    return d

def calculate(lc, shipments):
    if not isinstance(lc, dict) or not isinstance(shipments, list):
        raise ValueError("Invalid inputs")
    reference = lc.get("lc_number")
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError("Missing LC reference")
    currency = lc.get("currency")
    unit = lc.get("unit")
    if not currency or not unit:
        raise ValueError("Missing currency or unit")
    total_qty = number(lc["quantity"])
    total_value = number(lc["amount"])
    tolerance = number(lc.get("quantity_tolerance_pct", 0))
    if tolerance > 100:
        raise ValueError("Unreasonable tolerance")
    qty_limit = total_qty * (1 + tolerance / 100)
    ids = set()
    used_qty = used_value = Decimal("0")
    entries = []
    for s in shipments:
        if not isinstance(s, dict) or s.get("lc_number") != reference:
            raise ValueError("Shipment LC mismatch")
        ident = s.get("shipment_id")
        if not isinstance(ident, str) or not ident.strip() or ident in ids:
            raise ValueError("Missing or duplicate shipment ID")
        ids.add(ident)
        if s.get("currency", currency) != currency or s.get("unit", unit) != unit:
            raise ValueError("Currency or unit mismatch")
        qty = number(s["quantity"])
        value = number(s["amount"])
        state = s.get("status")
        if state not in ("PLANNED", "SHIPPED", "PRESENTED", "HONOURED", "CANCELLED"):
            raise ValueError("Invalid shipment status")
        if state not in ("PLANNED", "CANCELLED"):
            used_qty += qty
            used_value += value
        entries.append({"shipment_id": ident, "status": state, "quantity": str(qty), "amount": str(value)})
    remaining_qty = total_qty - used_qty
    remaining_value = total_value - used_value
    warnings = []
    if used_qty > qty_limit:
        warnings.append("QUANTITY_EXCEEDS_TOLERANCE")
    if used_value > total_value:
        warnings.append("AMOUNT_EXCEEDS_LC_FACE_VALUE")
    if remaining_qty < 0:
        warnings.append("NEGATIVE_NOMINAL_QUANTITY")
    return {"lc_number": reference, "currency": currency, "unit": unit,
            "lc_quantity": str(total_qty), "lc_amount": str(total_value),
            "shipped_quantity": str(used_qty), "allocated_shipment_value": str(used_value),
            "remaining_nominal_quantity": str(remaining_qty),
            "remaining_face_value": str(remaining_value),
            "quantity_limit_with_tolerance": str(qty_limit),
            "shipments": entries, "warnings": warnings,
            "status": "NEEDS_BANK_RECONCILIATION",
            "note": "Not a bank-certified available balance; presentations, amendments and drawings must be reconciled."}
