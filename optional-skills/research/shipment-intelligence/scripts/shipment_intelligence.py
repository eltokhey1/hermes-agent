#!/usr/bin/env python3
"""Hermes Shipment Intelligence staging CLI: offline evidence-first normalization.

All imports are local/offline. No tracking API calls or inferred shipment events.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlsplit

VERSION = '0.1.1'
MAX_BYTES = 10_000_000
MAX_EVENTS = 5_000
RE_CONTAINER = re.compile(r'^[A-Z]{4}\d{7}$')
RE_IMO = re.compile(r'^\d{7}$')
CATEGORIES = {'SHIPMENT', 'TRANSPORT', 'EQUIPMENT', 'AIS', 'PORT_CALL'}
CLASSIFIERS = {'ACT', 'EST', 'PLN', 'UNK'}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


def aware_utc(value: object) -> str | None:
    """Only explicit timezone offsets/Z are convertible to UTC; never guess."""
    if not isinstance(value, str) or not value.strip():
        return None
    s = value.strip()
    if not (s.endswith(('Z', 'z')) or re.search(r'[+-]\d{2}:\d{2}$', s)):
        return None
    try:
        t = dt.datetime.fromisoformat(s.replace('Z', '+00:00').replace('z', '+00:00'))
        if t.tzinfo is None: return None
        return t.astimezone(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    except ValueError:
        return None


def normalize_classifier(value: object) -> str:
    x = str(value or '').upper().strip()
    return {'ACTUAL': 'ACT', 'A': 'ACT', 'ESTIMATED': 'EST', 'E': 'EST',
            'PLANNED': 'PLN', 'PLAN': 'PLN', 'P': 'PLN'}.get(x, x if x in CLASSIFIERS else 'UNK')


def require_url(url: object) -> str:
    if not isinstance(url, str) or not url.strip() or len(url)>2048:
        raise ValueError('Each event needs an attributable http(s) source_url')
    p=urlsplit(url)
    if p.scheme not in ('http','https') or not p.netloc or p.username or p.password:
        raise ValueError('Invalid source_url')
    return url


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def reference(value: object, kind: str) -> str:
    v=str(value or '').strip().upper()
    if kind == 'container' and not RE_CONTAINER.fullmatch(v):
        raise ValueError('Invalid container reference')
    if kind == 'vessel' and not RE_IMO.fullmatch(v):
        raise ValueError('Invalid IMO')
    if not v or len(v)>120 or any(c.isspace() for c in v):
        raise ValueError('Invalid tracking reference')
    return v

def provider_event_id(provider: object, raw_id: object) -> str:
    """Fail closed on missing provider identities (a prefix alone is not an event ID)."""
    if not isinstance(provider, str) or not provider.strip() or len(provider) > 80 or any(c.isspace() for c in provider):
        raise ValueError('Invalid provider identity')
    if raw_id is None or isinstance(raw_id, bool):
        raise ValueError('Missing provider event id')
    raw = str(raw_id).strip()
    if not raw or len(raw) > 120 or any(ord(c) < 32 for c in raw):
        raise ValueError('Missing/invalid provider event id')
    return provider + ':' + raw


def event(*, eid: object, category: str, subject_type: str, subject_id: object,
          code: object, classifier: object, occurred: object, source_url: object,
          source_name: str, location: object = None, payload: dict,
          observed_at: object = None, reported_local: object = None) -> dict:
    if category not in CATEGORIES: raise ValueError('Invalid category')
    if subject_type not in ('container', 'shipment', 'vessel'): raise ValueError('Invalid subject')
    ident=reference(subject_id, subject_type)
    ident_event=str(eid or '').strip()
    if not ident_event or len(ident_event)>220: raise ValueError('Missing/invalid immutable event id')
    time_utc=aware_utc(occurred)
    if occurred and not time_utc and not reported_local:
        reported_local=occurred
    # Reject malformed timezone-bearing strings instead of silently converting to local
    if occurred and not time_utc and (str(occurred).endswith('Z') or re.search(r'[+-]\d{2}:\d{2}$',str(occurred))):
        raise ValueError('Invalid occurred datetime with timezone')
    observed_utc=aware_utc(observed_at) if observed_at else utc_now()
    if not observed_utc: raise ValueError('observed_at must include timezone')
    clean_code=re.sub(r'\s+', '_', str(code or 'UNKNOWN').upper().strip())
    if not re.fullmatch(r'[A-Z0-9_./-]{1,80}',clean_code): raise ValueError('Invalid event code')
    return dict(event_id=ident_event, category=category, subject_type=subject_type,
                subject_id=ident, code=clean_code,
                classifier=normalize_classifier(classifier), occurred_utc=time_utc,
                reported_local=str(reported_local) if reported_local else None,
                observed_utc=observed_utc, source_url=require_url(source_url),
                source_name=str(source_name)[:100], location=str(location)[:160] if location else None,
                payload=payload)


def adapt_ais(record: dict, provider: str) -> dict:
    imo=reference(record.get('imo'), 'vessel')
    rt=str(record.get('event_type') or 'UNKNOWN').upper()
    typ='AIS' if rt in ('POSITION','AIS_POSITION') else 'PORT_CALL'
    code='POSITION' if typ=='AIS' else {'ARRIVAL':'ARRI','DEPARTURE':'DEPA'}.get(rt,rt)
    loc=record.get('port_name') or record.get('location')
    # Preserve AIS observations without treating them as current ship status.
    if typ=='AIS':
        # A position without a timestamp and both coordinates is not usable as AIS evidence.
        if not aware_utc(record.get('time_utc') or record.get('event_time_utc')):
            raise ValueError('AIS position requires timezone-grounded timestamp')
        lat=record.get('latitude',record.get('lat'))
        lon=record.get('longitude',record.get('lon'))
        if (lat is None) != (lon is None):
            raise ValueError('Incomplete AIS position')
        if lat is None:
            raise ValueError('AIS position requires coordinates')
        if lat is not None:
            try:
                latitude, longitude = float(lat), float(lon)
            except (ValueError, TypeError, OverflowError) as exc:
                raise ValueError('Invalid AIS coordinates') from exc
            if not (math.isfinite(latitude) and math.isfinite(longitude) and -90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError('AIS coordinates out of range')
            loc=f'{lat}, {lon}'
    return event(eid=provider_event_id(provider,record.get('record_id')), category=typ,
        subject_type='vessel',subject_id=imo,code=code,classifier='ACT',
        occurred=record.get('time_utc') or record.get('event_time_utc'),
        source_url=record.get('source_url'),source_name=provider,location=loc,
        payload=record, reported_local=record.get('time_local_unverified'),
        observed_at=None)


def adapt_dcsa(record: dict, provider: str, source_url: str) -> dict:
    cat=str(record.get('eventType') or '').upper()
    if cat not in ('SHIPMENT','TRANSPORT','EQUIPMENT'):
        raise ValueError('DCSA event type must be SHIPMENT/TRANSPORT/EQUIPMENT')
    if cat == 'EQUIPMENT':
        subject_type='container'; ident=record.get('equipmentReference')
    else:
        subject_type='shipment';ident=record.get('transportDocumentReference') or record.get('carrierBookingReference')
        if not ident and cat=='TRANSPORT':
            # A vessel movement alone cannot create a new shipment status.
            raise ValueError('Transport event lacks shipment reference; not a shipment event')
    code=record.get({'SHIPMENT':'shipmentEventTypeCode','TRANSPORT':'transportEventTypeCode',
                     'EQUIPMENT':'equipmentEventTypeCode'}[cat])
    if not isinstance(code, str) or not code.strip():
        raise ValueError('Missing DCSA event code')
    rloc=record.get('eventLocation') or {}
    if isinstance(rloc,dict):
        loc=rloc.get('UNLocationCode') or rloc.get('locationName') or rloc.get('locationCode')
    else: loc=None
    return event(eid=provider_event_id(provider,record.get('eventID')),category=cat,
          subject_type=subject_type,subject_id=ident,code=code,
          classifier=record.get('eventClassifierCode'),occurred=record.get('eventDateTime'),
          source_url=source_url,source_name=provider,location=loc,payload=record,
          observed_at=record.get('eventCreatedDateTime'))


def adapt_maersk(document: dict, source_name='maersk') -> list[dict]:
    """Adapter for the result of Maersk ocean tracking tool; NO API call."""
    src=require_url(document.get('url'))
    result=[]
    containers=document.get('containers') or []
    for c in containers:
        cid=reference(c.get('container_num'),'container')
        for place in c.get('locations') or []:
            ev=place.get('event') or {}
            if not ev.get('type') and not ev.get('activity'): continue
            loc=place.get('location_code') or ', '.join(str(place[x]) for x in ('terminal','city','country') if place.get(x))
            unique = digest({'cid':cid,'event':ev,'location':loc})[:22]
            result.append(event(eid=source_name+':'+cid+':'+unique,category='EQUIPMENT',
                 subject_type='container',subject_id=cid,
                 code=ev.get('activity') or ev.get('type') or 'UNKNOWN',
                 classifier=ev.get('event_time_type'),occurred=ev.get('event_time'),
                 source_url=src,source_name=source_name,location=loc,payload={'event':ev,'place':place}))
    return result


def read_json_records(path: Path) -> list[dict]:
    if not path.is_file() or path.stat().st_size > MAX_BYTES: raise ValueError('Missing or oversized input file')
    text=path.read_text(encoding='utf-8-sig')
    if path.suffix.lower()=='.jsonl':
        records=[json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        doc=json.loads(text)
        records=doc if isinstance(doc,list) else ([doc] if isinstance(doc,dict) else [])
    if not 1 <= len(records) <= MAX_EVENTS or not all(isinstance(x,dict) for x in records):
        raise ValueError('Expected 1..5000 JSON objects')
    return records

SCHEMA='''
CREATE TABLE IF NOT EXISTS evidence_events(
 event_id TEXT PRIMARY KEY, category TEXT NOT NULL, subject_type TEXT NOT NULL,
 subject_id TEXT NOT NULL, code TEXT NOT NULL, classifier TEXT NOT NULL,
 occurred_utc TEXT, reported_local TEXT, observed_utc TEXT NOT NULL,
 source_url TEXT NOT NULL, source_name TEXT NOT NULL, location TEXT,
 payload_json TEXT NOT NULL, record_sha256 TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS subject_lookup ON evidence_events(subject_type,subject_id,occurred_utc);
CREATE TABLE IF NOT EXISTS vessel_links(
 container_id TEXT NOT NULL, vessel_imo TEXT NOT NULL,
 evidence_source TEXT NOT NULL, evidence_note TEXT NOT NULL,
 created_utc TEXT NOT NULL,
 PRIMARY KEY(container_id,vessel_imo,evidence_source)
);
'''


def connect(path: Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con


def ingest(con, items: list[dict]) -> dict:
    out={'inserted':0,'duplicates':0,'rejected':0}
    # Fail atomically on evidence conflict, do not overwrite prior event.
    with con:
        for item in items:
            payload=item['payload']
            stored={k:v for k,v in item.items() if k != 'payload'}
            # Ingestion timestamp may change across retries; it is NOT source-event identity.
            stored.pop('observed_utc', None)
            canonical={'event':stored,'payload':payload}
            sha=digest(canonical)
            exists=con.execute('SELECT record_sha256 FROM evidence_events WHERE event_id=?',
                               (item['event_id'],)).fetchone()
            if exists:
                if exists[0]!=sha: raise ValueError('CONFLICT: event id exists with different evidence: '+item['event_id'])
                out['duplicates']+=1
                continue
            con.execute('INSERT INTO evidence_events VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
                item['event_id'],item['category'],item['subject_type'],item['subject_id'],
                item['code'],item['classifier'],item['occurred_utc'],item['reported_local'],
                item['observed_utc'],item['source_url'],item['source_name'],item['location'],
                json.dumps(payload,ensure_ascii=False,sort_keys=True),sha))
            out['inserted']+=1
    return out


def link(con, container: str, imo: str, source: str, note: str):
    container=reference(container,'container'); imo=reference(imo,'vessel')
    source=require_url(source)
    if len(note.strip()) < 12: raise ValueError('Explicit carrier document or voyage evidence note required')
    with con:
        con.execute('INSERT OR IGNORE INTO vessel_links VALUES (?,?,?,?,?)',
                    (container,imo,source,note.strip(),utc_now()))


def evidence_report(con, container: str, now: str|None=None, stale_hours: int=48) -> dict:
    cid=reference(container,'container')
    now_utc=aware_utc(now) if now else utc_now()
    if not now_utc: raise ValueError('status --now must include valid timezone')
    tnow=dt.datetime.fromisoformat(now_utc.replace('Z','+00:00'))
    rows=con.execute('''SELECT event_id,category,code,classifier,occurred_utc,reported_local,
                         observed_utc,source_url,source_name,location FROM evidence_events
                         WHERE subject_type='container' AND subject_id=? ORDER BY occurred_utc DESC, event_id DESC''',(cid,)).fetchall()
    names=['event_id','category','code','classifier','occurred_utc','reported_local',
           'observed_utc','source_url','source_name','location']
    evs=[dict(zip(names,r)) for r in rows]
    actual=[e for e in evs if e['classifier']=='ACT' and e['occurred_utc'] is not None and e['category']=='EQUIPMENT']
    highest_date=actual[0]['occurred_utc'] if actual else None
    tied=[e for e in actual if e['occurred_utc']==highest_date]
    conflicted=len({(e['code'],e['location']) for e in tied})>1
    latest=None if conflicted else (tied[0] if tied else None)
    if latest:
        delta=(tnow-dt.datetime.fromisoformat(latest['occurred_utc'].replace('Z','+00:00'))).total_seconds()/3600
        fresh = -1 <= delta <= stale_hours
    else: fresh=False
    if conflicted: state='REVIEW_REQUIRED'
    elif not latest: state='UNKNOWN'
    elif not fresh: state='STALE'
    else: state='CURRENT_ACTUAL'
    eta=[e for e in evs if e['classifier'] in ('EST','PLN') and e['occurred_utc'] and e['category']=='EQUIPMENT']
    links=con.execute('SELECT vessel_imo,evidence_source,evidence_note FROM vessel_links WHERE container_id=?',(cid,)).fetchall()
    vessels=[]
    for imo,src,note in links:
        ais=con.execute('''SELECT code,occurred_utc,reported_local,source_url,location FROM evidence_events
            WHERE subject_type='vessel' AND subject_id=? AND category='AIS' AND occurred_utc IS NOT NULL
            ORDER BY occurred_utc DESC LIMIT 1''',(imo,)).fetchone()
        v={'imo':imo,'association_source':src,'association_note':note,'last_ais_position':None,
           'ais_is_current':False}
        if ais:
            t=dt.datetime.fromisoformat(ais[1].replace('Z','+00:00'))
            delta=(tnow-t).total_seconds()/3600
            v['last_ais_position']=dict(code=ais[0],occurred_utc=ais[1],source_url=ais[3],location=ais[4],age_hours=round(delta,1))
            v['ais_is_current']=(-1 <= delta <= stale_hours)
        vessels.append(v)
    return dict(container_id=cid,shipment_state=state,latest_confirmed_equipment_event=latest,
                latest_estimates=eta[:3],conflicting_actual_events=tied if conflicted else [],
                associated_vessels=vessels, event_count=len(evs),
                warnings=['Vessel AIS never independently proves container status or discharge.',
                          'Estimated/planned events are not actual milestones.',
                          'Current-state requires fresh timezone-grounded carrier equipment event.'])


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description='Hermes Shipment Intelligence offline staging tool')
    parser.add_argument('--db',type=Path,default=Path.home()/'.hermes'/'shipment-intelligence.sqlite3')
    sub=parser.add_subparsers(dest='command',required=True)
    for kind in ('ais','dcsa','maersk'):
        x=sub.add_parser('import-'+kind);x.add_argument('file',type=Path)
        x.add_argument('--provider',default={'ais':'historical-ais','dcsa':'dcsa-feed','maersk':'maersk'}[kind])
        if kind=='dcsa': x.add_argument('--source-url',required=True)
    l=sub.add_parser('link-vessel');l.add_argument('container');l.add_argument('imo');l.add_argument('--source-url',required=True);l.add_argument('--note',required=True)
    s=sub.add_parser('status');s.add_argument('container');s.add_argument('--now',help='ISO 8601 UTC/offset timestamp for reproducible audit')
    sub.add_parser('health')
    args=parser.parse_args(argv)
    try:
        con=connect(args.db)
        if args.command.startswith('import-'):
            records=read_json_records(args.file)
            if args.command=='import-ais': evs=[adapt_ais(x,args.provider) for x in records]
            elif args.command=='import-dcsa': evs=[adapt_dcsa(x,args.provider,args.source_url) for x in records]
            else:
                if len(records)!=1: raise ValueError('Maersk input must be one tracking response object')
                evs=adapt_maersk(records[0],args.provider)
            output={'operation':args.command,'result':ingest(con,evs),'parsed':len(evs)}
        elif args.command=='link-vessel':
            link(con,args.container,args.imo,args.source_url,args.note)
            output={'operation':'link-vessel','status':'recorded','not_inferred':True}
        elif args.command=='status':output=evidence_report(con,args.container,args.now)
        else:
            output={'service':'shipment-intelligence','version':VERSION,'offline':True,
                    'stored_events':con.execute('SELECT count(*) FROM evidence_events').fetchone()[0],
                    'vessel_links':con.execute('SELECT count(*) FROM vessel_links').fetchone()[0]}
        print(json.dumps(output,ensure_ascii=False,indent=2))
        return 0
    except (ValueError,sqlite3.Error,OSError,json.JSONDecodeError) as exc:
        print(json.dumps({'error':str(exc),'status':'FAIL_CLOSED'},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())