"""Offline evaluation; no network, writes, or tool execution."""
import argparse
import json
from pathlib import Path

WEIGHTS = {'security':30,'privacy':15,'compatibility':15,'quality':20,'cost':10,'maintenance':10}
VALID = {'CANDIDATE','UNDER_STUDY','TESTED_SYNTHETIC','VERIFIED','REJECTED'}

def evaluate(record):
    if not isinstance(record,dict) or record.get('status') not in VALID:
        raise ValueError('invalid record/status')
    scores=record.get('scores',{})
    if not isinstance(scores,dict) or set(scores)!=set(WEIGHTS) or any(type(scores[k]) not in (int,float) or not 0<=scores[k]<=5 for k in WEIGHTS):
        raise ValueError('six numeric scores from 0 to 5 required')
    evidence=record.get('evidence',[])
    if not isinstance(evidence,list):
        raise ValueError('evidence must be a list')
    score=round(sum(scores[k]*w for k,w in WEIGHTS.items())/5,2)
    blockers=[k for k in ('security','privacy') if scores[k]<3]
    # A claimed independent test is not proof of provenance: never auto-promote.
    if record['status']=='VERIFIED':
        blockers.append('independent evidence requires external attestation')
    decision='REJECT' if blockers or record['status']=='REJECTED' else ('PILOT_CANDIDATE' if score>=75 else 'STUDY_ONLY')
    if record['status'] in ('CANDIDATE','UNDER_STUDY','TESTED_SYNTHETIC') and decision=='PILOT_CANDIDATE':
        decision='PILOT_CANDIDATE_UNVERIFIED'
    return {'id':record.get('id'),'score':score,'decision':decision,'blockers':blockers,'production':'HOLD','gates':'G0/G-CODE/G1=NO-GO'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('registry',type=Path)
    args=parser.parse_args()
    records=json.loads(args.registry.read_text(encoding='utf-8'))
    if not isinstance(records,list):
        raise ValueError('registry must be list')
    print(json.dumps([evaluate(r) for r in records],ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
