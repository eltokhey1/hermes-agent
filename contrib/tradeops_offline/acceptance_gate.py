"""Pure, fail-closed verification of a TradeOps advisory report.

No authentication, no authorization, no external actions. Contract validation only.
"""
import re

REQUIRED = {'case_id','decision','human_approval_required','automated_release_authorized',
            'flags','document_review','lc_check','eta_evidence','scope'}
ALLOWED = {'READY_FOR_HUMAN_REVIEW_ONLY','BLOCK_FOR_REVIEW'}

def inspect_report(report):
    """Return a non-authorizing contract verdict for a case-review report."""
    invalid = lambda reason: {'contract_valid':False,'status':'INVALID_REPORT','release_authorized':False,'reason':reason}
    if not isinstance(report,dict) or set(report)!=REQUIRED:
        return invalid('missing, extra or non-object report fields')
    if not isinstance(report['case_id'],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{0,95}',report['case_id']):
        return invalid('invalid case identifier')
    if not isinstance(report['decision'],str) or report['decision'] not in ALLOWED:
        return invalid('unknown decision')
    if report['human_approval_required'] is not True or report['automated_release_authorized'] is not False:
        return invalid('a report cannot authorize release or bypass review')
    flags = report['flags']
    if not isinstance(flags,list) or len(flags)>64 or any(not isinstance(x,str) or not x or len(x)>100 for x in flags) or len(set(flags))!=len(flags):
        return invalid('invalid review flags')
    dr,lc,eta=report['document_review'],report['lc_check'],report['eta_evidence']
    if not isinstance(dr,dict) or not isinstance(dr.get('findings'),list):
        return invalid('document review evidence missing')
    if not isinstance(lc,dict) or not isinstance(lc.get('missing'),list):
        return invalid('LC evidence missing')
    if not isinstance(eta,list) or len(eta)>100:
        return invalid('invalid ETA evidence')
    if any(not isinstance(x,dict) or not isinstance(x.get('status'),str) for x in eta):
        return invalid('invalid ETA event report')
    if eta and 'ETA_SOURCE_UNVERIFIED' not in flags:
        return invalid('ETA evidence without independent verification flag')
    if not eta and 'ETA_SOURCE_UNVERIFIED' in flags:
        return invalid('ETA source flag without evidence')
    if any(x['status'] in ('CONFLICT_REQUIRES_REVIEW','SOURCE_DISAGREEMENT_REQUIRES_REVIEW',
                             'HISTORICAL_EVIDENCE_NOT_LATEST','ETA_CHANGED_REQUIRES_REVIEW')
           for x in eta) and 'ETA_EVIDENCE_AMBIGUOUS' not in flags:
        return invalid('ETA conflict hidden from flags')
    if not isinstance(report['scope'],str) or not report['scope'].strip():
        return invalid('unknown review scope')
    if (flags or dr['findings'] or lc['missing']) and report['decision']!='BLOCK_FOR_REVIEW':
        return invalid('findings inconsistent with ready-to-review decision')
    if report['decision']=='BLOCK_FOR_REVIEW' and not (flags or dr['findings'] or lc['missing']):
        return invalid('blocked decision without supporting findings')
    return {'contract_valid':True,'status':report['decision'],
            'release_authorized':False,
            'reason':'manual review required; does not attest to accuracy, authenticity or compliance'}
