"""Offline, fail-closed self-improvement proposal adapter. No writes or execution."""
from learning_unit import evaluate

ALLOWED_PROJECTS = frozenset({'Hermes', 'TradeDocs AI', 'Shipment Intelligence', 'Designer', 'Radar'})

def propose(record, project, hypothesis, acceptance_test):
    if project not in ALLOWED_PROJECTS:
        raise ValueError('unknown project')
    if not all(isinstance(v, str) and v.strip() for v in (hypothesis, acceptance_test)):
        raise ValueError('hypothesis and acceptance test required')
    result = evaluate(record)
    if result['decision'] == 'REJECT':
        return {'source_id': result['id'], 'project': project, 'status': 'BLOCKED', 'reason': result['blockers'], 'production': 'HOLD'}
    return {'source_id': result['id'], 'project': project, 'hypothesis': hypothesis,
            'acceptance_test': acceptance_test, 'evaluation': result['decision'],
            'status': 'PROPOSED_ONLY', 'requires': ['independent_test', 'human_approval'],
            'executed': False, 'production': 'HOLD', 'gates': 'G0/G-CODE/G1=NO-GO'}
