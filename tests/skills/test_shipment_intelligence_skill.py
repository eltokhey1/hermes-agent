"""Offline contract tests for Shipment Intelligence evidence rules."""
import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'optional-skills/research/shipment-intelligence/scripts/shipment_intelligence.py'
spec=importlib.util.spec_from_file_location('shipment_intelligence',SCRIPT)
si=importlib.util.module_from_spec(spec)
spec.loader.exec_module(si)

SRC='https://example.org/trace/evidence-123'


def dcsa(code='GTIN',classifier='ACT',when='2026-10-18T08:00:00Z',loc='LYKHO',event_id='evt-a'):
    return {'eventID':event_id,'eventType':'EQUIPMENT','equipmentReference':'ABCD1234567',
        'equipmentEventTypeCode':code,'eventClassifierCode':classifier,'eventDateTime':when,
        'eventLocation':{'UNLocationCode':loc},'eventCreatedDateTime':'2026-10-18T09:00:00Z'}


def open_db(tmp_path):return si.connect(tmp_path/'staging.sqlite')


def test_dcsa_actual_status_is_current(tmp_path):
    db=open_db(tmp_path)
    r=si.adapt_dcsa(dcsa(),'carrier',SRC)
    assert si.ingest(db,[r])['inserted']==1
    report=si.evidence_report(db,'ABCD1234567','2026-10-18T10:00:00Z')
    assert report['shipment_state']=='CURRENT_ACTUAL'
    assert report['latest_confirmed_equipment_event']['code']=='GTIN'


def test_idempotent_reimport_with_new_ingestion_time(tmp_path):
    db=open_db(tmp_path)
    r1=si.adapt_dcsa(dcsa(),'carrier',SRC)
    assert si.ingest(db,[r1])['inserted']==1
    r2=si.adapt_dcsa(dcsa(),'carrier',SRC)
    r2['observed_utc']='2026-10-19T10:00:00Z'
    assert si.ingest(db,[r2])['duplicates']==1
    assert db.execute('SELECT COUNT(*) FROM evidence_events').fetchone()[0]==1


def test_conflicting_same_event_id_rollback(tmp_path):
    db=open_db(tmp_path)
    a=si.adapt_dcsa(dcsa(),'carrier',SRC)
    b=si.adapt_dcsa(dcsa(code='DISC'),'carrier',SRC)
    si.ingest(db,[a])
    with pytest.raises(ValueError,match='CONFLICT'):
        si.ingest(db,[b])
    assert db.execute('SELECT code FROM evidence_events').fetchone()[0]=='GTIN'


def test_two_actual_events_same_time_conflict_requires_review(tmp_path):
    db=open_db(tmp_path)
    a=si.adapt_dcsa(dcsa(),'carrier',SRC)
    b=si.adapt_dcsa(dcsa(code='DISC',event_id='evt-b'),'carrier',SRC)
    si.ingest(db,[a,b])
    assert si.evidence_report(db,'ABCD1234567','2026-10-18T10:00:00Z')['shipment_state']=='REVIEW_REQUIRED'


def test_stale_never_current(tmp_path):
    db=open_db(tmp_path)
    si.ingest(db,[si.adapt_dcsa(dcsa(),'carrier',SRC)])
    assert si.evidence_report(db,'ABCD1234567','2026-10-25T10:00:00Z')['shipment_state']=='STALE'


def test_estimated_not_actual(tmp_path):
    db=open_db(tmp_path)
    si.ingest(db,[si.adapt_dcsa(dcsa(classifier='EST'),'carrier',SRC)])
    r=si.evidence_report(db,'ABCD1234567','2026-10-18T10:00:00Z')
    assert r['shipment_state']=='UNKNOWN' and len(r['latest_estimates'])==1


def test_ais_cannot_create_container_status(tmp_path):
    db=open_db(tmp_path)
    ais={'record_id':'position1','imo':9173355,'event_type':'POSITION','time_utc':'2026-10-18T09:00:00Z',
         'lat':32.676,'lon':14.244,'source_url':SRC}
    si.ingest(db,[si.adapt_ais(ais,'aisprovider')])
    assert si.evidence_report(db,'ABCD1234567','2026-10-18T10:00:00Z')['shipment_state']=='UNKNOWN'
    si.link(db,'ABCD1234567','9173355',SRC,'Verified bill of lading identifies vessel')
    report=si.evidence_report(db,'ABCD1234567','2026-10-18T10:00:00Z')
    assert report['shipment_state']=='UNKNOWN'
    assert report['associated_vessels'][0]['last_ais_position']['location']=='32.676, 14.244'


def test_invalid_or_ambiguous_time_unverified(tmp_path):
    e=si.adapt_ais({'record_id':'r1','imo':9173355,'event_type':'ARRIVAL',
        'time_local_unverified':'2026-05-20T19:31:00','time_utc':None,'source_url':SRC},'provider')
    assert e['occurred_utc'] is None and e['reported_local']=='2026-05-20T19:31:00'
    with pytest.raises(ValueError):
        si.adapt_dcsa(dcsa(when='2026-10-18T25:00:00Z'),'carrier',SRC)


def test_maersk_maps_actual_and_retains_uncertain_times(tmp_path):
    doc={'url':SRC,'containers':[{'container_num':'ABCD1234567','locations':[
       {'city':'Khoms','event':{'type':'LOAD','activity':'Load on vessel',
                                 'event_time':'2026-10-18T09:00:00','event_time_type':'ACTUAL'}}]}]}
    events=si.adapt_maersk(doc)
    assert len(events)==1 and events[0]['code']=='LOAD_ON_VESSEL'
    assert events[0]['occurred_utc'] is None
    db=open_db(tmp_path);si.ingest(db,events)
    assert si.evidence_report(db,'ABCD1234567')['shipment_state']=='UNKNOWN'


def test_transport_without_document_cannot_attribute_to_container():
    with pytest.raises(ValueError,match='lacks shipment reference'):
        si.adapt_dcsa({'eventID':'e','eventType':'TRANSPORT','transportEventTypeCode':'ARRI',
          'transportCall':{'vessel':{'vesselIMONumber':'9173355'}}},'carrier',SRC)


def test_offline_cli_roundtrip(tmp_path,capsys):
    db=tmp_path/'test.sqlite'; input_path=tmp_path/'input.json'
    input_path.write_text(json.dumps([dcsa()]),encoding='utf8')
    assert si.main(['--db',str(db),'import-dcsa',str(input_path),'--source-url',SRC])==0
    assert si.main(['--db',str(db),'status','ABCD1234567','--now','2026-10-18T10:00:00Z'])==0
    assert 'CURRENT_ACTUAL' in capsys.readouterr().out


def test_duplicate_entire_import_fails_atomically(tmp_path):
    db=open_db(tmp_path)
    r=si.adapt_dcsa(dcsa(),'carrier',SRC)
    r2=si.adapt_dcsa(dcsa(code='DISC'),'carrier',SRC)
    with pytest.raises(ValueError):si.ingest(db,[r,r2])
    assert db.execute('SELECT COUNT(*) FROM evidence_events').fetchone()[0]==0


@pytest.mark.parametrize('event_id', [None, '', '   '])
def test_provider_event_identity_is_required(event_id):
    with pytest.raises(ValueError, match='provider event id'):
        si.adapt_dcsa(dcsa(event_id=event_id), 'carrier', SRC)


def test_ais_event_without_native_id_is_rejected():
    with pytest.raises(ValueError, match='provider event id'):
        si.adapt_ais({'imo':9173355, 'event_type':'POSITION',
            'time_utc':'2026-10-18T09:00:00Z',
            'lat':32.676, 'lon':14.244, 'source_url':SRC}, 'aisprovider')


@pytest.mark.parametrize('latitude,longitude', [
    (91, 0), (-91, 0), (0, 181), (0, -181),
    ('not-a-latitude', 10), ('nan', 0), (None, 10),
])
def test_invalid_ais_coordinates_are_not_accepted(latitude, longitude):
    record={'record_id':'bad-position', 'imo':9173355, 'event_type':'POSITION',
        'time_utc':'2026-10-18T09:00:00Z',
        'lat':latitude, 'lon':longitude, 'source_url':SRC}
    with pytest.raises(ValueError, match='AIS'):
        si.adapt_ais(record, 'aisprovider')


def test_ais_zero_numeric_provider_id_is_valid():
    record={'record_id':0, 'imo':9173355, 'event_type':'POSITION',
        'time_utc':'2026-10-18T09:00:00Z',
        'lat':32.676, 'lon':14.244, 'source_url':SRC}
    assert si.adapt_ais(record,'aisprovider')['event_id']=='aisprovider:0'


def test_invalid_provider_name_is_rejected():
    with pytest.raises(ValueError, match='provider identity'):
        si.adapt_dcsa(dcsa(), 'carrier source with spaces', SRC)



@pytest.mark.parametrize('bad', [
    {'record_id':'pos-missing','imo':9173355,'event_type':'POSITION',
     'time_utc':'2026-10-18T09:00:00Z','source_url':SRC},
    {'record_id':'pos-no-time','imo':9173355,'event_type':'POSITION',
     'lat':32.676,'lon':14.244,'source_url':SRC},
])
def test_position_missing_coordinates_or_timestamp_fails_closed(bad):
    with pytest.raises(ValueError,match='AIS'):
        si.adapt_ais(bad,'aisprovider')


@pytest.mark.parametrize('code', [None, '', '   '])
def test_missing_dcsa_equipment_event_code_fails_closed(code):
    with pytest.raises(ValueError,match='event code'):
        si.adapt_dcsa(dcsa(code=code),'carrier',SRC)
