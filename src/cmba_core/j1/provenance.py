"""Source-span provenance, claim traces and local supplied-byte observations."""
import hashlib
from ..codec import canonical
from ..bindings import exact, hex_digest, identifier, validate_reference
from ..errors import require
from .common import (sequence, integer, text, hex_bytes, equal, hash_value, outcome,
                     recognized, interval, valid_time)
from .endorsements import verified_records

EVENT_TYPES=('requirement','decision','alternative','uncertainty','trigger','output','claim')


def _session(record):
    exact(record, {'source','events'})
    source=record['source']; exact(source, {'text','sha256','coverage'})
    require(type(source['text']) is str,'CMBA_J_TEXT');canonical(source['text']);hex_digest(source['sha256'])
    require(source['coverage']=='SUPPLIED_RECORD_ONLY','CMBA_J_CAPTURE_CLAIM')
    raw=source['text'].encode('utf-8');source_match=hashlib.sha256(raw).hexdigest()==source['sha256']
    sequence(record['events'],minimum=1);seen=set();quotes=True
    for e in record['events']:
        exact(e, {'id','type','attributed_to','start_byte','end_byte','quote','interpretation','references'})
        identifier(e['id']);identifier(e['attributed_to']);text(e['interpretation'])
        require(e['type'] in EVENT_TYPES and e['id'] not in seen,'CMBA_J_EVENT_TYPE')
        start=integer(e['start_byte'],0,len(raw));end=integer(e['end_byte'],start,len(raw))
        require(type(e['quote']) is str,'CMBA_J_TEXT');canonical(e['quote'])
        sequence(e['references'])
        for ref in e['references']:identifier(ref)
        require(len(set(e['references']))==len(e['references']),'CMBA_J_DUPLICATE')
        for ref in e['references']:
            identifier(ref);require(ref in seen,'CMBA_J_EVENT_REFERENCE')
        try:quote=raw[start:end].decode('utf-8')
        except UnicodeDecodeError:quote=None
        quotes=quotes and quote==e['quote'];seen.add(e['id'])
    return source_match,quotes


def session(record, context):
    source,quotes=_session(record)
    return outcome({'session.source-bytes':'MATCH' if source else 'CONTRADICTED',
                    'session.quoted-spans':'MATCH' if quotes else 'CONTRADICTED','session.attribution':'MATCH'},
                    {'event_count':len(record['events']),'capture':'SUPPLIED_RECORD_ONLY','interpretation_truth':'NOT_ESTABLISHED'},
                    ceiling='Exact supplied source spans and attributed decisions/alternatives/triggers. No source authorship, hidden reasoning, complete capture or interpretation truth proof.')


def claim_trace(record, context):
    exact(record, {'session','claims'})
    source,quotes=_session(record['session']);sequence(record['claims'],minimum=1)
    event_ids={e['id'] for e in record['session']['events']};ids=set()
    for c in record['claims']:
        exact(c, {'id','text','event_refs'});identifier(c['id']);text(c['text']);sequence(c['event_refs'],minimum=1)
        require(c['id'] not in ids,'CMBA_J_DUPLICATE');ids.add(c['id'])
        for ref in c['event_refs']:identifier(ref);require(ref in event_ids,'CMBA_J_CITATION_MISSING')
    return outcome({'trace.sources':'MATCH' if source and quotes else 'CONTRADICTED','trace.references':'MATCH'},
       {'claims':len(ids),'clinical_validity':'NOT_ESTABLISHED','election_validity':'NOT_ESTABLISHED','claim_truth':'NOT_ESTABLISHED'},
       ceiling='Citations resolve to admitted spans only; no truth, entailment, diagnosis, regulatory approval or zero-hallucination guarantee.')


def measure_bytes(raw, *, instrument, method, calibration, jurisdiction):
    require(type(raw) is bytes and len(raw)<=65536,'CMBA_J_MEASUREMENT_LIMIT')
    for ref in (instrument,method,calibration):validate_reference(ref)
    identifier(jurisdiction)
    sha=hashlib.sha256(raw).hexdigest()
    return {'subject':{'scheme':'sha256.bytes','algorithm':'SHA-256','digest_hex':sha},
            'raw_hex':raw.hex(),'measured_digest':sha,'measured_size':len(raw),
            'instrument':instrument,'method':method,'calibration':calibration,'jurisdiction':jurisdiction,
            'measurement_type':'SUPPLIED_BYTES_RECOMPUTED'}


def observation(record, context):
    exact(record, {'subject','raw_hex','measured_digest','measured_size','instrument','method','calibration','jurisdiction','measurement_type'})
    for field in ('subject','instrument','method','calibration'):validate_reference(record[field])
    identifier(record['jurisdiction']);hex_digest(record['measured_digest']);integer(record['measured_size'],0,65536)
    require(record['measurement_type']=='SUPPLIED_BYTES_RECOMPUTED','CMBA_J_OBSERVATION_CLAIM')
    raw=hex_bytes(record['raw_hex']);sha=hashlib.sha256(raw).hexdigest()
    p=context['policy']['parameters'];exact(p, {'expected_instrument','expected_method','expected_calibration','require_observer'})
    require(type(p['require_observer']) is bool,'CMBA_J_BOOLEAN')
    for k in ('expected_instrument','expected_method','expected_calibration'):validate_reference(p[k])
    checks={'observation.bytes':'MATCH' if sha==record['measured_digest'] and len(raw)==record['measured_size'] and
            equal(record['subject'],{'scheme':'sha256.bytes','algorithm':'SHA-256','digest_hex':sha}) else 'CONTRADICTED',
            'observation.references':'MATCH' if all(equal(record[k],p['expected_'+k]) for k in ('instrument','method','calibration')) else 'CONTRADICTED'}
    witnesses=set();denied=set()
    for _,b in verified_records(context['evidence_snapshot']):
        if b['kind']!='observation':continue
        v=b['payload'];exact(v, {'record_hash','decision','not_before','not_after'});hex_digest(v['record_hash']);interval(v)
        require(v['decision'] in ('confirm','deny'),'CMBA_J_DECISION')
        if v['record_hash']==hash_value('observation',record) and valid_time(v,context['time']['epoch']) and recognized(
            context['authority_snapshot'],b['public_key'],'observer',record['jurisdiction']):
            (witnesses if v['decision']=='confirm' else denied).add(b['public_key'])
    checks['observation.testimony']='CONTRADICTED' if denied else 'MATCH' if witnesses or not p['require_observer'] else 'INSUFFICIENT'
    return outcome(checks, {'recognized_observers':sorted(witnesses),'external_measurement':'NOT_ESTABLISHED',
                           'assessed_subject':record['subject']},
       ceiling='Supplied bytes recomputed and exact declared instrument/method/calibration references; optional recognized testimony, not calibration validity or physical measurement truth.')
