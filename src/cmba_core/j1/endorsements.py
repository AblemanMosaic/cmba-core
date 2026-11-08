"""SE-J1: typed Ed25519 statements and detached endorsement envelopes.

cryptography/OpenSSL performs signing/verification. Public-key admission is a
byte-preserved copy of frozen DKN rc5's reviewed public-data checker. No DKN import.
Keys are supplied by the caller; no persistence or key generation here. These are
CMBA J1 messages, not DSSE messages and not compatible DKN signatures.
"""
from ..codec import canonical, clone
from ..bindings import exact, inspect, hex_digest, identifier
from ..errors import Refusal, require
from .common import (hash_value, sequence, integer, hex_bytes, interval, valid_time,
                     recognized, validate_authority, outcome)
from ._key_admission import admitted_public_key

KINDS = frozenset(('endorsement','approval','consent-grant','consent-withdrawal',
                   'coordination','observation','execution-observation'))
SIGN_DOMAIN = b'CMBA:J1:ed25519-statement\0'
L = 2**252 + 27742317777372353535851937790883648493


def _backend():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        from cryptography.exceptions import InvalidSignature
        return Ed25519PrivateKey, Ed25519PublicKey, Encoding, PublicFormat, InvalidSignature
    except ImportError as exc:
        raise Refusal('CMBA_J_CRYPTO_DEPENDENCY_UNAVAILABLE') from exc


def public_key(key):
    private, _, encoding, fmt, _ = _backend()
    require(isinstance(key, private), 'CMBA_J_PRIVATE_KEY_TYPE')
    return key.public_key().public_bytes(encoding.Raw, fmt.Raw).hex()


def _public(value):
    raw = hex_bytes(value, size=32)
    require(admitted_public_key(raw), 'CMBA_J_PUBLIC_KEY_INVALID')
    return raw


def seal(kind, payload, key):
    require(type(kind) is str and kind in KINDS, 'CMBA_J_STATEMENT_KIND')
    require(type(payload) is dict, 'CMBA_J_STATEMENT_PAYLOAD'); canonical(payload)
    body = {'schema':'cmba.statement-body.j1','kind':kind,'payload':clone(payload),
            'algorithm':'Ed25519','public_key':public_key(key)}
    _public(body['public_key'])
    signed = {'schema':'cmba.signed-statement.j1','body':body,
              'signature_hex':key.sign(SIGN_DOMAIN + canonical(body)).hex()}
    signed['record_hash'] = hash_value('signed-record', signed)
    return signed


def verify(record, *, expected_kind=None):
    canonical(record)
    exact(record, {'schema','body','signature_hex','record_hash'})
    require(record['schema']=='cmba.signed-statement.j1', 'CMBA_J_STATEMENT_SCHEMA')
    b = record['body']; exact(b, {'schema','kind','payload','algorithm','public_key'})
    require(b['schema']=='cmba.statement-body.j1' and b['algorithm']=='Ed25519', 'CMBA_J_STATEMENT_SCHEMA')
    require(type(b['kind']) is str and b['kind'] in KINDS and type(b['payload']) is dict, 'CMBA_J_STATEMENT_KIND')
    require(expected_kind is None or b['kind']==expected_kind, 'CMBA_J_STATEMENT_KIND')
    raw = _public(b['public_key']); signature = hex_bytes(record['signature_hex'], size=64)
    require(int.from_bytes(signature[32:], 'little') < L, 'CMBA_J_SIGNATURE_INVALID')
    hex_digest(record['record_hash'])
    projected = {k:record[k] for k in ('schema','body','signature_hex')}
    require(hash_value('signed-record', projected)==record['record_hash'], 'CMBA_J_RECORD_HASH')
    _, pub, _, _, invalid = _backend()
    try: pub.from_public_bytes(raw).verify(signature, SIGN_DOMAIN + canonical(b))
    except (invalid, ValueError) as exc: raise Refusal('CMBA_J_SIGNATURE_INVALID') from exc
    return clone(b)


def verified_records(records):
    sequence(records); seen = set(); result = []
    for r in records:
        body = verify(r)
        require(r['record_hash'] not in seen, 'CMBA_J_DUPLICATE_EVIDENCE')
        seen.add(r['record_hash']); result.append((r, body))
    return result


def policy(value):
    exact(value, {'schema','requirements'})
    require(value['schema']=='cmba.endorsement-policy.j1', 'CMBA_J_ENDORSEMENT_POLICY')
    sequence(value['requirements'], minimum=1, limit=16); seen = set()
    for r in value['requirements']:
        exact(r, {'id','role','jurisdiction','action','threshold'})
        for k in ('id','role','jurisdiction','action'): identifier(r[k])
        integer(r['threshold'], 1, 64)
        require(r['id'] not in seen, 'CMBA_J_DUPLICATE'); seen.add(r['id'])
    return value


def bound_policy(binding, values):
    inspect(binding, values)
    entries = [d for d in binding['body']['dimensions'] if d['dimension_id']=='endorsement-policy']
    require(len(entries)==1 and 'endorsement-policy' in values, 'CMBA_J_ENDORSEMENT_POLICY_MISSING')
    require(entries[0]['role']=='endorsement-requirements' and entries[0]['schema_id']=='cmba.endorsement-policy.j1',
            'CMBA_J_ENDORSEMENT_POLICY')
    return policy(values['endorsement-policy'])


def endorse(binding, values, key, *, requirement_id, not_before, not_after, decision='endorse'):
    p = bound_policy(binding, values)
    reqs = [r for r in p['requirements'] if r['id']==requirement_id]
    require(len(reqs)==1 and decision in ('endorse','reject'), 'CMBA_J_ENDORSEMENT_REQUIREMENT')
    r = reqs[0]
    payload = {'binding_root':binding['binding_root'],'policy_hash':hash_value('endorsement-policy',p),
               'requirement_id':requirement_id, 'role':r['role'],'jurisdiction':r['jurisdiction'],
               'action':r['action'],'not_before':not_before,'not_after':not_after,'decision':decision}
    interval(payload)
    return seal('endorsement', payload, key)


def assess_endorsements(binding, values, records, *, expected_root, expected_policy_hash, authority, now):
    p = bound_policy(binding, values); hex_digest(expected_root); hex_digest(expected_policy_hash)
    integer(now); validate_authority(authority)
    require(binding['binding_root']==expected_root, 'CMBA_EXPECTED_ROOT_MISMATCH')
    ph = hash_value('endorsement-policy',p)
    require(ph==expected_policy_hash, 'CMBA_J_POLICY_PIN')
    verified = verified_records(records)
    rows = []; checks = {}
    for req in p['requirements']:
        signed = set(); denied = set(); ineligible = []
        for rec, body in verified:
            if body['kind'] != 'endorsement': continue
            v = body['payload']
            exact(v, {'binding_root','policy_hash','requirement_id','role','jurisdiction','action','not_before','not_after','decision'})
            interval(v); require(v['decision'] in ('endorse','reject'), 'CMBA_J_DECISION')
            expected = {'binding_root':expected_root,'policy_hash':ph,'requirement_id':req['id'],
                        'role':req['role'],'jurisdiction':req['jurisdiction'],'action':req['action']}
            applicable = all(v[k]==val for k,val in expected.items())
            if applicable and valid_time(v,now) and recognized(authority,body['public_key'],req['role'],req['jurisdiction']):
                (signed if v['decision']=='endorse' else denied).add(body['public_key'])
            else: ineligible.append(rec['record_hash'])
        s = 'CONTRADICTED' if denied else 'MATCH' if len(signed)>=req['threshold'] else 'INSUFFICIENT'
        checks[req['id']] = s
        rows.append({'requirement_id':req['id'],'recognized_signers':sorted(signed),
                     'recognized_rejections':sorted(denied),'ineligible_records':sorted(ineligible),'status':s})
    return outcome(checks, {'requirements':rows,'binding_root':expected_root,'policy_hash':ph},
                   ceiling='Distinct recognized keys endorsed exact requirements in the supplied view; not independent humans or execution permission.')


def envelope(binding, values, records):
    p=bound_policy(binding, values); verified_records(records)
    ph=hash_value('endorsement-policy',p)
    for rec in records:
        v=rec['body']['payload']
        exact(v, {'binding_root','policy_hash','requirement_id','role','jurisdiction','action','not_before','not_after','decision'})
        interval(v)
        require(v['decision'] in ('endorse','reject'),'CMBA_J_DECISION')
        require(v['policy_hash']==ph and any(all(v[k]==r[k] for k in ('role','jurisdiction','action')) and
            v['requirement_id']==r['id'] for r in p['requirements']), 'CMBA_J_ENVELOPE_SCOPE')
    require(all(r['body']['kind']=='endorsement' and r['body']['payload'].get('binding_root')==binding['binding_root']
                for r in records), 'CMBA_J_ENVELOPE_SCOPE')
    body = {'schema':'cmba.endorsed-envelope-body.j1','binding':clone(binding),'values':clone(values),
            'endorsements':sorted(clone(records),key=lambda r:r['record_hash'])}
    return {'schema':'cmba.endorsed-envelope.j1','body':body,'envelope_hash':hash_value('envelope',body)}


def verify_envelope(value):
    exact(value, {'schema','body','envelope_hash'})
    require(value['schema']=='cmba.endorsed-envelope.j1','CMBA_J_ENVELOPE_SCHEMA')
    b=value['body'];exact(b, {'schema','binding','values','endorsements'})
    expected=envelope(b['binding'],b['values'],b['endorsements'])
    require(canonical(value)==canonical(expected),'CMBA_J_ENVELOPE_HASH')
    return {'status':'ENVELOPE_SIGNATURES_AND_BINDINGS_VALID','binding_root':b['binding']['binding_root'],
            'envelope_hash':value['envelope_hash'],'recognition':'NOT_CHECKED','authority_effect':'NONE'}
