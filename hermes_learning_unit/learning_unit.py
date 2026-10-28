"""Hermes learning/evaluation registry. Offline, read-only, stdlib only."""
import argparse
import json
from pathlib import Path

WEIGHTS = {'security': 30, 'privacy': 15, 'compatibility': 15, 'quality': 20, 'cost': 10, 'maintenance': 10}
VALID = {'CANDIDATE', 'UNDER_STUDY', 'TESTED_SYNTHETIC', 'VERIFIED', 'REJECTED'}

def evaluate(record):
    if record.get('status') not in VALID:
        raise ValueError('invalid status')
    scores = record.get('scores', {})
    if set(scores) != set(WEIGHTS) or any(type(scores[k]) not in (int, float) or not 0 <= scores[k] <= 5 for k in WEIGHTS):
        raise ValueError('six scores between 0 and 5 required')
    score = round(sum(scores[k] * w for k, w in WEIGHTS.items()) / 5, 2)
    evidence = record.get('evidence', [])
    if not isinstance(evidence, list):
        raise ValueError('evidence must be a list')
    blockers = [k for k in ('security', 'privacy') if scores[k] < 3]
    if record['status'] == 'VERIFIED' and not any(
        isinstance(e, dict) and all(isinstance(e.get(k), str) and e[k].strip() for k in ('url', 'sha_or_version', 'test_result'))
        and e.get('independent_test') is True for e in evidence
    ):
        blockers.append('missing independent evidence')
    decision = 'REJECT' if blockers else ('PILOT_CANDIDATE' if score >= 75 else 'STUDY_ONLY')
    if record['status'] in ('CANDIDATE', 'UNDER_STUDY', 'TESTED_SYNTHETIC') and decision == 'PILOT_CANDIDATE':
        decision = 'PILOT_CANDIDATE_UNVERIFIED'
    if record['status'] == 'REJECTED':
        decision = 'REJECT'
    return {'id': record.get('id'), 'score': score, 'decision': decision, 'blockers': blockers, 'production': 'HOLD', 'gates': 'G0/G-CODE/G1=NO-GO'}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('registry', type=Path)
    args = p.parse_args()
    records = json.loads(args.registry.read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('registry must be a list')
    print(json.dumps([evaluate(x) for x in records], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
