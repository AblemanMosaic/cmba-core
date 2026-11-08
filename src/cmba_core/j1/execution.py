"""Supplied execution-record correspondence, never execution of an artifact."""
import hashlib
from ..bindings import exact, validate_reference, identifier, hex_digest
from ..errors import require
from .common import hex_bytes, integer, equal, hash_value, recognized, valid_time, interval, outcome
from .endorsements import verified_records


def assess(record,context):
    exact(record, {'request','observed','result_hex','result','jurisdiction'})
    identifier(record['jurisdiction']);validate_reference(record['result'])
    for obj in (record['request'],record['observed']):
        exact(obj, {'artifact','configuration','target','operation'})
        validate_reference(obj['artifact']);identifier(obj['target']);identifier(obj['operation'])
    raw=hex_bytes(record['result_hex']);sha=hashlib.sha256(raw).hexdigest()
    params=context['policy']['parameters'];exact(params, {'max_age'});integer(params['max_age'],0,2**31)
    signed=set();denied=set();now=context['time']['epoch']
    for _,b in verified_records(context['evidence_snapshot']):
        if b['kind']!='execution-observation':continue
        v=b['payload'];exact(v, {'record_hash','observed_at','decision','not_before','not_after'})
        hex_digest(v['record_hash']);integer(v['observed_at']);interval(v);require(v['decision'] in ('confirm','deny'),'CMBA_J_DECISION')
        if (v['record_hash']==hash_value('execution-record',record) and 0<=now-v['observed_at']<=params['max_age']
            and valid_time(v,now) and recognized(context['authority_snapshot'],b['public_key'],'execution-observer',record['jurisdiction'])):
            (signed if v['decision']=='confirm' else denied).add(b['public_key'])
    return outcome({'execution.correspondence':'MATCH' if equal(record['request'],record['observed']) else 'CONTRADICTED',
                    'execution.result-bytes':'MATCH' if equal(record['result'],{'scheme':'sha256.bytes','algorithm':'SHA-256','digest_hex':sha}) else 'CONTRADICTED',
                    'execution.testimony':'CONTRADICTED' if denied else 'MATCH' if signed else 'INSUFFICIENT'},
      {'recognized_observers':sorted(signed),'assessed_subject':record['request']['artifact'],
       'actual_execution':'NOT_ESTABLISHED','payload_executed':False},
      ceiling='Recorded request/configuration/target/result correspondence and recognized supplied observation only; not runtime measurement truth, execution permission or proof of execution.')
