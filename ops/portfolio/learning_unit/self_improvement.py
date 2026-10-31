"""Proposal-only improvement adapter; no execution."""
from learning_unit import evaluate

PROJECTS=frozenset({'Hermes','TradeDocs AI','Shipment Intelligence','Designer','Radar'})

def propose(record,project,hypothesis,acceptance_test):
    if project not in PROJECTS:
        raise ValueError('unknown project')
    if not all(isinstance(x,str) and x.strip() for x in (hypothesis,acceptance_test)):
        raise ValueError('hypothesis and acceptance test required')
    result=evaluate(record)
    if result['decision']=='REJECT':
        return {'source_id':result['id'],'project':project,'status':'BLOCKED','reason':result['blockers'],'executed':False,'production':'HOLD'}
    return {'source_id':result['id'],'project':project,'hypothesis':hypothesis,'acceptance_test':acceptance_test,'evaluation':result['decision'],'status':'PROPOSED_ONLY','requires':['independent_test','human_approval'],'executed':False,'production':'HOLD','gates':'G0/G-CODE/G1=NO-GO'}
