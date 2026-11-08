"""Reproducible finite evaluations and separately committed unsigned receipts.

Every receipt binds exact values, policy, authority snapshot, evidence snapshot,
reader time and evaluator source identity. Authority inputs are recorded, NOT
interpreted by I1's three example profile predicates.
"""
from __future__ import annotations
import hashlib
from importlib.resources import files
from .bindings import exact, inspect, hex_digest, identifier, digest, profile_reference
from .codec import canonical, clone
from .errors import Refusal, require
from .registry import resolve_profile


def realization_identity() -> str:
    """Code/data commitment of the installed evaluator, not an authenticity assertion."""
    base=files('cmba_core')
    rows={}
    def walk(node,prefix=''):
        for p in sorted(node.iterdir(), key=lambda x:x.name):
            name=prefix+p.name
            if p.name.startswith('__pycache__'):continue
            if p.is_dir():walk(p,name+'/')
            elif p.name.endswith(('.py','.json')):
                rows[name]=hashlib.sha256(p.read_bytes()).hexdigest()
    walk(base)
    return hashlib.sha256(b'CMBA:I1:evaluator-realization\0'+canonical(rows)).hexdigest()


def context_for(binding: dict, *, epoch: int, jurisdiction: str = 'local-demo') -> dict:
    """Example convenience, not trusted pin acquisition. Applications own these inputs."""
    c=resolve_profile(binding['body']['profile'])
    return {'schema':'cmba.evaluation-context.v0.1-i1',
            'expected_binding_root':binding['binding_root'],
            'policy':{'profile':profile_reference(c),'required_checks':sorted(c['predicates'])},
            'authority_snapshot':{'jurisdiction':jurisdiction,'recognition':'NOT_ESTABLISHED'},
            'evidence_snapshot':[], 'time':{'epoch':epoch,'clock_source':'caller-supplied'}}


def _context(value: dict, c: dict) -> None:
    canonical(value)
    exact(value, {'schema','expected_binding_root','policy','authority_snapshot','evidence_snapshot','time'})
    require(value['schema']=='cmba.evaluation-context.v0.1-i1','CMBA_CONTEXT_SCHEMA')
    hex_digest(value['expected_binding_root'])
    exact(value['policy'], {'profile','required_checks'})
    require(canonical(value['policy']['profile'])==canonical(profile_reference(c)),'CMBA_POLICY_PROFILE')
    require(canonical(value['policy']['required_checks'])==canonical(sorted(c['predicates'])), 'CMBA_POLICY_CHECKS')
    require(type(value['authority_snapshot']) is dict, 'CMBA_AUTHORITY_SNAPSHOT_TYPE')
    require(type(value['evidence_snapshot']) is list, 'CMBA_EVIDENCE_SNAPSHOT_TYPE')
    exact(value['time'], {'epoch','clock_source'})
    require(type(value['time']['epoch']) is int and value['time']['epoch']>=0,'CMBA_TIME_INVALID')
    identifier(value['time']['clock_source'])


def _profile_checks(binding, values, contract):
    required={d['dimension_id']:d for d in contract['required_dimensions']}
    actual={d['dimension_id']:d for d in binding['body']['dimensions']}
    missing=sorted(set(required)-actual.keys())
    for k in sorted(required.keys() & actual.keys()):
        d=actual[k];r=required[k]
        require(d['role']==r['role'] and d['schema_id']==r['schema_id'] and d['critical'],
                'CMBA_REQUIRED_DIMENSION_TYPE')
    unsupported=sorted(d['dimension_id'] for d in actual.values() if d['critical'] and d['dimension_id'] not in required)
    missing_values=sorted(set(required)-values.keys())
    if unsupported or missing or missing_values:
        return {'binding.structure':'MATCH',**{p:'NOT_CHECKED' for p in contract['predicates'] if p!='binding.structure'}}, missing,missing_values,unsupported
    pid=contract['profile_id']
    if pid=='cmba.chc.transform':
        from .profiles.chc import evaluate as handler
    elif pid=='cmba.gendev.session':
        from .profiles.session import evaluate as handler
    elif pid=='cmba.dkn.artifact':
        from .profiles.dkn import evaluate as handler
    elif pid=='cmba.generic':
        handler=lambda _:{}
    else:
        raise Refusal('CMBA_PROFILE_UNSUPPORTED')
    return {'binding.structure':'MATCH',**handler(values)},missing,missing_values,unsupported


def evaluate(binding: dict, values: dict, context: dict) -> dict:
    # Structural/value admission occurs before handler lookup, and cannot confer authority.
    inspection=inspect(binding, values)
    c=resolve_profile(binding['body']['profile']);_context(context,c)
    require(binding['binding_root']==context['expected_binding_root'],'CMBA_EXPECTED_ROOT_MISMATCH')
    checks,missing,absent,unsupported=_profile_checks(binding,values,c)
    require(set(checks)==set(c['predicates']), 'CMBA_EVALUATOR_RESULT')
    require(all(v in ('MATCH','CONTRADICTED','UNSUPPORTED','NOT_CHECKED') for v in checks.values()),'CMBA_EVALUATOR_RESULT')
    if 'CONTRADICTED' in checks.values():status='CONTRADICTED'
    elif unsupported or 'UNSUPPORTED' in checks.values():status='UNSUPPORTED'
    elif missing or absent or 'NOT_CHECKED' in checks.values():status='INSUFFICIENT'
    else:status='MATCH_FOR_SUPPLIED_EVIDENCE'
    result={'schema':'cmba.evaluation-result.v0.1-i1','status':status,'checks':checks,
            'missing_dimensions':missing,'missing_values':absent,'unsupported_critical_dimensions':unsupported,
            'uninterpreted_dimensions':sorted(d['dimension_id'] for d in binding['body']['dimensions']
                if d['dimension_id'] not in {x['dimension_id'] for x in c['required_dimensions']}),
            'authority_effect':'NONE','authority_interpretation':'NOT_EVALUATED',
            'evidence_interpretation':'NOT_EVALUATED','authorization':'EXTERNAL_DECISION_REQUIRED',
            'claim_ceiling':c['claim_ceiling']}
    body={'schema':'cmba.evaluation-receipt-body.v0.1-i1','binding_root':binding['binding_root'],
          'profile':clone(binding['body']['profile']), 'supplied_values_hash':digest('supplied-values',values),
          'policy_hash':digest('policy',context['policy']),
          'authority_snapshot_hash':digest('authority-snapshot',context['authority_snapshot']),
          'evidence_snapshot_hash':digest('evidence-snapshot',context['evidence_snapshot']),
          'time_hash':digest('evaluation-time',context['time']),
          'expected_binding_root':context['expected_binding_root'],
          'evaluator':{'id':'cmba.builtin-evaluator.i1','realization_sha256':realization_identity()},
          'result':result,'signature':'NOT_SIGNED'}
    return {'schema':'cmba.evaluation-receipt.v0.1-i1','body':body,
            'receipt_hash':digest('evaluation-receipt',body)}


def replay(receipt: dict, binding: dict, values: dict, context: dict) -> dict:
    canonical(receipt);exact(receipt, {'schema','body','receipt_hash'})
    require(receipt['schema']=='cmba.evaluation-receipt.v0.1-i1','CMBA_RECEIPT_SCHEMA')
    hex_digest(receipt['receipt_hash'])
    require(digest('evaluation-receipt',receipt['body'])==receipt['receipt_hash'],'CMBA_RECEIPT_HASH_MISMATCH')
    expected=evaluate(binding,values,context)
    require(canonical(expected)==canonical(receipt),'CMBA_RECEIPT_REPLAY_MISMATCH')
    return {'schema':'cmba.receipt-replay.v0.1-i1','status':'MATCH_EXACT_EVALUATION_REPLAY',
            'receipt_hash':receipt['receipt_hash'],'signature':'NOT_SIGNED','authority_effect':'NONE'}
