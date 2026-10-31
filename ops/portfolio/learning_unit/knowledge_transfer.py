"""Deterministic lesson proposal; never distributes knowledge automatically."""
import hashlib
import json
from self_improvement import propose

def prepare_lesson(record,project,hypothesis,acceptance_test,lesson):
    if not isinstance(lesson,str) or not lesson.strip():
        raise ValueError('nonempty lesson required')
    proposal=propose(record,project,hypothesis,acceptance_test)
    if proposal['status']!='PROPOSED_ONLY':
        return {'status':'BLOCKED','reason':proposal['reason'],'executed':False,'distributed':False,'production':'HOLD'}
    payload={'source_id':proposal['source_id'],'project':project,'lesson':lesson.strip(),'hypothesis':hypothesis,'acceptance_test':acceptance_test,'evidence_status':record['status'],'status':'REVIEW_REQUIRED','executed':False,'distributed':False,'production':'HOLD','gates':'G0/G-CODE/G1=NO-GO'}
    canonical=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    payload['content_sha256']=hashlib.sha256(canonical.encode()).hexdigest()
    return payload
