"""Conservative MT700 field parser and amendment gate for synthetic/local review.

Never infer an operative amendment from a request or unverified MT707 text.
"""
import re

FIELD = re.compile(r'^\s*:(\d{2}[A-Z]?):\s*(.*)$')
IMPORTANT = ('20', '31D', '44C', '44E', '44F', '46A', '47A', '48')


def parse_fields(text):
    if not isinstance(text, str) or len(text) > 200_000:
        raise ValueError('Invalid SWIFT text')
    fields = {}
    current = None
    for line in text.splitlines():
        match = FIELD.match(line)
        if match:
            current = match.group(1)
            if current in fields:
                raise ValueError('Duplicate field: ' + current)
            fields[current] = match.group(2).strip()
        elif current is not None:
            fields[current] += '\n' + line.strip()
    if '20' not in fields or not fields['20']:
        raise ValueError('Missing documentary credit reference field 20')
    return fields


def review(mt700, amendments=()):
    original = parse_fields(mt700)
    issues = []
    for key in IMPORTANT:
        if not original.get(key):
            issues.append({'field': key, 'code': 'MISSING_OR_UNREADABLE', 'decision': 'NEEDS_REVIEW'})
    for index, amendment in enumerate(amendments, 1):
        if not isinstance(amendment, dict) or amendment.get('status') not in ('REQUEST_ONLY', 'UNVERIFIED', 'BANK_CONFIRMED'):
            raise ValueError('Invalid amendment metadata')
        if amendment['status'] != 'BANK_CONFIRMED':
            issues.append({'amendment': index, 'code': 'NOT_PROVEN_OPERATIVE', 'decision': 'NEEDS_REVIEW'})
        else:
            issues.append({'amendment': index, 'code': 'REQUIRES_INDEPENDENT_AUTHENTICATION', 'decision': 'NEEDS_REVIEW'})
    return {'reference': original['20'], 'extracted_fields': {k: original.get(k) for k in IMPORTANT},
            'issues': issues, 'status': 'NEEDS_REVIEW', 'operative_amendments_applied': 0}
