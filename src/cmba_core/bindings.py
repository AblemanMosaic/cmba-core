"""Typed dimensions, finite binding bodies, references and exact comparisons.

Binding validates which descriptions were committed. It does not execute, fetch,
interpret arbitrary profiles, establish a signer, or grant authority.
"""
from __future__ import annotations
import hashlib
import re
from typing import Any
from .codec import canonical, clone, CODEC
from .errors import Refusal, require

DOMAINS = {k: ('CMBA:I1:' + k + '\0').encode('ascii') for k in (
    'dimension-value', 'binding-root', 'profile-contract', 'policy', 'authority-snapshot',
    'evidence-snapshot', 'evaluation-time', 'supplied-values', 'evaluation-receipt',
    'catalogue', 'capability-descriptor', 'semantic-contract', 'realization-binding')}
MAX_DIMENSIONS = 64
MAX_RELATIONS = 256


def exact(value: Any, keys: set[str]) -> None:
    require(type(value) is dict and set(value) == keys, 'CMBA_FIELDS_INVALID')


def identifier(value: Any) -> str:
    require(type(value) is str and re.fullmatch(r'[a-z][a-z0-9._:/-]{0,191}', value) is not None,
            'CMBA_IDENTIFIER_INVALID')
    return value


def hex_digest(value: Any) -> str:
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None,
            'CMBA_DIGEST_INVALID')
    return value


def digest(domain: str, value: Any) -> str:
    require(type(domain) is str and domain in DOMAINS, 'CMBA_DOMAIN_UNSUPPORTED')
    return hashlib.sha256(DOMAINS[domain] + canonical(value)).hexdigest()


def reference(scheme: str, digest_hex: str, *, algorithm: str = 'SHA-256') -> dict:
    identifier(scheme); hex_digest(digest_hex)
    require(type(algorithm) is str and algorithm in ('SHA-256', 'BLAKE3-256'), 'CMBA_REFERENCE_ALGORITHM')
    return {'scheme': scheme, 'algorithm': algorithm, 'digest_hex': digest_hex}


def validate_reference(value: Any) -> None:
    exact(value, {'scheme', 'algorithm', 'digest_hex'})
    reference(value['scheme'], value['digest_hex'], algorithm=value['algorithm'])


def profile_reference(contract: dict) -> dict:
    require(type(contract) is dict, 'CMBA_FIELDS_INVALID')
    identifier(contract.get('profile_id')); identifier(contract.get('profile_version'))
    return {'profile_id': contract['profile_id'], 'profile_version': contract['profile_version'],
            'contract_hash': digest('profile-contract', contract)}


def validate_profile_reference(value: Any) -> None:
    exact(value, {'profile_id', 'profile_version', 'contract_hash'})
    identifier(value['profile_id']); identifier(value['profile_version']); hex_digest(value['contract_hash'])


def _value_body(item: dict, value: Any) -> dict:
    return {k: item[k] for k in ('dimension_id','role','schema_id','codec','algorithm','critical')} | {'value': value}


def dimension(dimension_id: str, role: str, schema_id: str, value: Any, *, critical: bool = True) -> dict:
    identifier(dimension_id); identifier(role); identifier(schema_id)
    require(type(critical) is bool, 'CMBA_CRITICAL_TYPE')
    item = {'dimension_id': dimension_id, 'role': role, 'schema_id': schema_id,
            'codec': CODEC, 'algorithm': 'SHA-256', 'critical': critical}
    item['value_hash'] = digest('dimension-value', _value_body(item, value))
    return item


def validate_dimension(item: Any) -> None:
    exact(item, {'dimension_id','role','schema_id','codec','algorithm','critical','value_hash'})
    for k in ('dimension_id','role','schema_id'): identifier(item[k])
    require(item['codec'] == CODEC and item['algorithm'] == 'SHA-256', 'CMBA_ENCODING_UNSUPPORTED')
    require(type(item['critical']) is bool, 'CMBA_CRITICAL_TYPE')
    hex_digest(item['value_hash'])


def relation(relation_id: str, predicate: str, target: dict) -> dict:
    identifier(relation_id); identifier(predicate); validate_reference(target)
    return {'relation_id': relation_id, 'predicate': predicate, 'target': clone(target)}


def _validate_body(body: Any) -> None:
    exact(body, {'schema','profile','dimensions','relations'})
    require(body['schema'] == 'cmba.binding-body.v0.1-i1', 'CMBA_SCHEMA_UNSUPPORTED')
    validate_profile_reference(body['profile'])
    dims = body['dimensions']; rels = body['relations']
    require(type(dims) is list and 1 <= len(dims) <= MAX_DIMENSIONS, 'CMBA_DIMENSION_LIMIT')
    require(type(rels) is list and len(rels) <= MAX_RELATIONS, 'CMBA_RELATION_LIMIT')
    for item in dims: validate_dimension(item)
    names = [d['dimension_id'] for d in dims]
    require(len(set(names)) == len(names), 'CMBA_DIMENSION_DUPLICATE')
    require(names == sorted(names), 'CMBA_DIMENSION_ORDER')
    names = []
    for r in rels:
        exact(r, {'relation_id','predicate','target'})
        identifier(r['relation_id']); identifier(r['predicate']); validate_reference(r['target'])
        names.append(r['relation_id'])
    require(len(set(names)) == len(names), 'CMBA_RELATION_DUPLICATE')
    require(names == sorted(names), 'CMBA_RELATION_ORDER')


def bind(profile: dict, dimensions: list[dict], *, relations: list[dict] | None = None) -> dict:
    validate_profile_reference(profile)
    require(type(dimensions) is list and 1 <= len(dimensions) <= MAX_DIMENSIONS, 'CMBA_DIMENSION_LIMIT')
    require(relations is None or (type(relations) is list and len(relations) <= MAX_RELATIONS), 'CMBA_RELATION_LIMIT')
    for item in dimensions: validate_dimension(item)
    rels = [] if relations is None else clone(relations)
    for r in rels:
        exact(r, {'relation_id','predicate','target'})
        identifier(r['relation_id']); identifier(r['predicate']); validate_reference(r['target'])
    body = {'schema':'cmba.binding-body.v0.1-i1', 'profile':clone(profile),
            'dimensions': sorted(clone(dimensions), key=lambda d: d['dimension_id']),
            'relations': sorted(rels, key=lambda r: r['relation_id'])}
    _validate_body(body)
    return {'schema':'cmba.binding.v0.1-i1', 'body':body, 'binding_root':digest('binding-root',body)}


def validate_binding(binding: Any) -> None:
    canonical(binding)
    exact(binding, {'schema','body','binding_root'})
    require(binding['schema'] == 'cmba.binding.v0.1-i1', 'CMBA_SCHEMA_UNSUPPORTED')
    _validate_body(binding['body']); hex_digest(binding['binding_root'])
    require(digest('binding-root', binding['body']) == binding['binding_root'], 'CMBA_BINDING_MISMATCH')


def inspect(binding: Any, values: dict | None = None, *, expected_root: str | None = None) -> dict:
    validate_binding(binding)
    if expected_root is not None:
        hex_digest(expected_root)
        require(binding['binding_root'] == expected_root, 'CMBA_EXPECTED_ROOT_MISMATCH')
    values = {} if values is None else values
    require(type(values) is dict, 'CMBA_VALUES_TYPE'); canonical(values)
    dims = binding['body']['dimensions']
    require(set(values) <= {d['dimension_id'] for d in dims}, 'CMBA_UNBOUND_VALUE')
    rows = []
    for d in dims:
        supplied = d['dimension_id'] in values
        if supplied:
            require(digest('dimension-value', _value_body(d, values[d['dimension_id']])) == d['value_hash'],
                    'CMBA_DIMENSION_MISMATCH')
        rows.append({'dimension_id': d['dimension_id'], 'role': d['role'], 'schema_id': d['schema_id'],
                     'critical': d['critical'], 'commitment': 'MATCH' if supplied else 'NOT_SUPPLIED',
                     'semantics': 'NOT_EVALUATED'})
    return {'schema':'cmba.inspection.v0.1-i1','status':'BINDING_STRUCTURE_VALID',
            'binding_root':binding['binding_root'], 'profile':clone(binding['body']['profile']),
            'external_anchor':'MATCHED_CALLER_EXPECTATION' if expected_root is not None else 'NOT_PROVIDED',
            'dimensions':rows,'relations':clone(binding['body']['relations']),
            'relation_targets':'NOT_RESOLVED','signature':'NOT_CHECKED',
            'authority_effect':'NONE','semantic_truth':'NOT_ESTABLISHED'}


def compare(left: dict, right: dict) -> dict:
    validate_binding(left); validate_binding(right)
    def diffs(field, key):
        a={v[key]:v for v in left['body'][field]};b={v[key]:v for v in right['body'][field]}
        return [{'id':k,'change':('ADDED' if k not in a else 'REMOVED' if k not in b else 'CHANGED')}
                for k in sorted(a.keys()|b.keys()) if k not in a or k not in b or canonical(a[k])!=canonical(b[k])]
    return {'schema':'cmba.comparison.v0.1-i1', 'left_root':left['binding_root'],'right_root':right['binding_root'],
            'same_binding':left['binding_root']==right['binding_root'],
            'same_profile':canonical(left['body']['profile'])==canonical(right['body']['profile']),
            'dimension_changes':diffs('dimensions','dimension_id'), 'relation_changes':diffs('relations','relation_id'),
            'semantic_equivalence':'NOT_ESTABLISHED','authority_effect':'NONE'}
