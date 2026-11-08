"""K1 finite host-model vocabulary. These hashes do not authenticate the host."""
import hashlib
from cmba_core import canonical, Refusal
from cmba_core.errors import require

MAX_DOCUMENTS = 64
MAX_HISTORY = 128
MAX_EDGES = 256
MAX_PREVIEW = 120000
DOMAINS = frozenset(('document','workspace','task','context','effect','handoff','design','semantic-contract','host-realization'))

def hash_value(domain, value):
    require(type(domain) is str and domain in DOMAINS, 'CMBA_K_HASH_DOMAIN')
    return hashlib.sha256(('CMBA:K1:'+domain+'\0').encode('ascii')+canonical(value)).hexdigest()

def integer(n, low=0, high=2**63-1):
    require(type(n) is int and low <= n <= high, 'CMBA_K_INTEGER')
    return n

def label(value):
    require(type(value) is str and 0 < len(value.encode('utf8')) <= 128 and
            all(ord(c) >= 32 and ord(c) != 127 for c in value), 'CMBA_K_LABEL')
    canonical(value)
    return value

def no_effect(result):
    result['authority_effect'] = 'NONE'
    return result
