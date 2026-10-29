"""Read-only composition of TradeDocs checks; no external actions."""
from lc_balance import calculate
from shipment_tracker import review
from requirements_registry import assess

def run(payload, today=None):
    if not isinstance(payload, dict):
        raise ValueError('Invalid workflow payload')
    lc = payload['lc']
    shipments = payload['shipments']
    balance = calculate(lc, shipments)
    reviews = [{'shipment_id': s['shipment_id'], 'review': review(s, today)} for s in shipments]
    requirements = assess(payload['route'], payload.get('documents', {}), payload.get('rules', []))
    return {'status': 'NEEDS_HUMAN_REVIEW', 'balance': balance, 'shipment_reviews': reviews, 'requirements': requirements, 'external_actions': 0}
