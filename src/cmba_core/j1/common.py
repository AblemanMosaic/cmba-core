"""J1 finite, exact, type-preserving utilities. No arbitrary code or remote resolution."""
import hashlib
import re
from ..codec import canonical, clone
from ..bindings import exact, identifier, hex_digest, validate_reference
from ..errors import Refusal, require

DOMAINS = frozenset(('statement', 'signed-record', 'endorsement-policy', 'envelope',
    'jurisdiction-terms', 'consent-context', 'coordination-terms', 'coordination-round',
    'observation', 'execution-record', 'disclosure-leaf', 'disclosure-empty',
    'disclosure-node', 'disclosure-root', 'receipt', 'context', 'record',
    'toolchain', 'semantic-contract', 'realization', 'conformance', 'request'))
MAX_RECORDS = 64
STATUSES = ('MATCH', 'CONTRADICTED', 'INSUFFICIENT', 'UNSUPPORTED', 'NO_MATCH')


def hash_value(domain, value):
    require(type(domain) is str and domain in DOMAINS, 'CMBA_J_DOMAIN')
    return hashlib.sha256(('CMBA:J1:' + domain + '\0').encode('ascii') + canonical(value)).hexdigest()


def integer(value, minimum=0, maximum=2**63-1):
    require(type(value) is int and minimum <= value <= maximum, 'CMBA_J_INTEGER')
    return value


def sequence(value, *, limit=MAX_RECORDS, minimum=0):
    require(type(value) is list and minimum <= len(value) <= limit, 'CMBA_J_SEQUENCE_LIMIT')
    return value


def text(value, *, maximum=65536):
    require(type(value) is str, 'CMBA_J_TEXT')
    canonical(value)
    require(0 < len(value.encode('utf-8')) <= maximum, 'CMBA_J_TEXT')
    return value


def hex_bytes(value, *, size=None, maximum=65536):
    require(type(value) is str and len(value) <= maximum*2 and len(value)%2 == 0
            and re.fullmatch('[0-9a-f]*', value) is not None, 'CMBA_J_HEX')
    result = bytes.fromhex(value)
    require(size is None or len(result) == size, 'CMBA_J_HEX_SIZE')
    return result


def equal(left, right):
    return canonical(left) == canonical(right)


def unique_strings(items, *, limit=64):
    sequence(items, limit=limit)
    for item in items: identifier(item)
    require(len(items) == len(set(items)), 'CMBA_J_DUPLICATE')
    return items


def interval(value):
    integer(value['not_before']); integer(value['not_after'])
    require(value['not_before'] < value['not_after'], 'CMBA_J_INTERVAL')


def valid_time(value, now):
    interval(value); integer(now)
    return value['not_before'] <= now < value['not_after']


def outcome(checks, details=None, *, ceiling):
    require(type(checks) is dict and len(checks)>0 and all(v in STATUSES for v in checks.values()), 'CMBA_J_CHECK_RESULT')
    # Known contradiction dominates missing/unsupported evidence; no hidden auto-permission.
    status = next((v for v in ('CONTRADICTED','UNSUPPORTED','INSUFFICIENT','NO_MATCH') if v in checks.values()),
                  'MATCH_FOR_SUPPLIED_EVIDENCE')
    result = {'schema':'cmba.application-result.j1', 'status':status, 'checks':checks,
              'details':{} if details is None else details, 'claim_ceiling':ceiling,
              'authority_effect':'NONE', 'authorization':'EXTERNAL_DECISION_REQUIRED',
              'freshness':'SUPPLIED_VIEW_ONLY', 'semantic_truth':'NOT_ESTABLISHED'}
    canonical(result)
    return result


def validate_authority(snapshot):
    exact(snapshot, {'members','revoked_keys'})
    sequence(snapshot['members']); sequence(snapshot['revoked_keys'])
    seen = set()
    for member in snapshot['members']:
        exact(member, {'public_key','roles','jurisdictions'})
        hex_digest(member['public_key']); unique_strings(member['roles']); unique_strings(member['jurisdictions'])
        require(member['public_key'] not in seen, 'CMBA_J_DUPLICATE_AUTHORITY'); seen.add(member['public_key'])
    for key in snapshot['revoked_keys']: hex_digest(key)
    require(len(snapshot['revoked_keys']) == len(set(snapshot['revoked_keys'])), 'CMBA_J_DUPLICATE')


def recognized(snapshot, key, role, jurisdiction):
    return key not in snapshot['revoked_keys'] and any(
        m['public_key'] == key and role in m['roles'] and jurisdiction in m['jurisdictions']
        for m in snapshot['members'])
