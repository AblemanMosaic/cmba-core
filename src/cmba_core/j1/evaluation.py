"""AP-J1 bounded application evaluation, explicit context and exact receipt replay.

I1 objects/evaluator remain untouched. J1 application contracts are explicitly selected
in the existing I1 binding construction, with separate result/context/receipt versions.
"""
from ..codec import canonical,clone
from ..bindings import (exact,inspect,profile_reference,dimension,bind,hex_digest,identifier,digest)
from ..errors import require,Refusal
from ..evaluation import realization_identity
from .common import integer,sequence,equal,validate_authority,hash_value,outcome
from .registry import contract,resolve


def bind_application(profile_id,record):
    c=contract(profile_id)
    require(type(record) is dict,'CMBA_J_RECORD_TYPE')
    dims=[]
    for d in c['required_dimensions']:
        field=d['source_field']
        require(field is None or field in record,'CMBA_J_PROJECTION_FIELD')
        value=record if field is None else record[field]
        dims.append(dimension(d['dimension_id'],d['role'],d['schema_id'],value))
    return {'binding':bind(profile_reference(c),dims),'values':{'record':clone(record)}}



def context_for(binding, *, now, parameters=None, authority=None, evidence=None, clock_source='caller-supplied'):
    """Demo/authoring convenience. Production expected root must be acquired independently."""
    c=resolve(binding['body']['profile'])
    return {'schema':'cmba.evaluation-context.j1','expected_binding_root':binding['binding_root'],
            'policy':{'profile':profile_reference(c),'required_checks':c['predicates'],
                      'parameters':{} if parameters is None else clone(parameters)},
            'authority_snapshot':{'members':[],'revoked_keys':[]} if authority is None else clone(authority),
            'evidence_snapshot':[] if evidence is None else clone(evidence),
            'time':{'epoch':now,'clock_source':clock_source}}


def validate_context(context,c):
    canonical(context);exact(context, {'schema','expected_binding_root','policy','authority_snapshot','evidence_snapshot','time'})
    require(context['schema']=='cmba.evaluation-context.j1','CMBA_J_CONTEXT_SCHEMA');hex_digest(context['expected_binding_root'])
    p=context['policy'];exact(p, {'profile','required_checks','parameters'})
    require(equal(p['profile'],profile_reference(c)),'CMBA_POLICY_PROFILE')
    require(equal(p['required_checks'],c['predicates']),'CMBA_POLICY_CHECKS')
    require(type(p['parameters']) is dict,'CMBA_J_PARAMETERS')
    validate_authority(context['authority_snapshot']);sequence(context['evidence_snapshot'])
    exact(context['time'], {'epoch','clock_source'});integer(context['time']['epoch']);identifier(context['time']['clock_source'])


def _handler(pid,record,context):
    if pid=='cmba.chc.graph':
        from .transforms import assess
        exact(context['policy']['parameters'],set());require(not context['evidence_snapshot'],'CMBA_J_UNCONSUMED_EVIDENCE')
    elif pid in ('cmba.gendev.rich-session','cmba.claim-trace'):
        from .provenance import session,claim_trace
        assess=session if pid=='cmba.gendev.rich-session' else claim_trace
        exact(context['policy']['parameters'],set());require(not context['evidence_snapshot'],'CMBA_J_UNCONSUMED_EVIDENCE')
    elif pid=='cmba.kasd':
        from .governance import jurisdiction as assess
    elif pid=='cmba.consent':
        from .governance import consent as assess
    elif pid=='cmba.coordination':
        from .coordination import assess
    elif pid=='cmba.reconciliation':
        from .reconciliation import assess
    elif pid=='cmba.execution-record':
        from .execution import assess
    elif pid=='cmba.observation':
        from .provenance import observation as assess
    elif pid=='cmba.admissibility':
        from .admissibility import assess
    elif pid=='cmba.disclosure':
        from .disclosure import verify
        exact(context['policy']['parameters'], {'expected_disclosure_root','required_labels'})
        require(not context['evidence_snapshot'],'CMBA_J_UNCONSUMED_EVIDENCE')
        from .common import unique_strings
        labels=unique_strings(context['policy']['parameters']['required_labels'])
        result=verify(record,expected_root=context['policy']['parameters']['expected_disclosure_root'])
        absent=sorted(set(labels)-set(result['details']['disclosed_labels']))
        if absent:
            result['checks']['disclosure.required-labels']='INSUFFICIENT';result['status']='INSUFFICIENT'
        else:result['checks']['disclosure.required-labels']='MATCH'
        result['details']['missing_required_labels']=absent
        return result
    elif pid=='cmba.endorsements':
        from .endorsements import assess_endorsements
        exact(record, {'binding','values'});p=context['policy']['parameters']
        exact(p, {'expected_subject_root','expected_endorsement_policy_hash'})
        return assess_endorsements(record['binding'],record['values'],context['evidence_snapshot'],
            expected_root=p['expected_subject_root'],expected_policy_hash=p['expected_endorsement_policy_hash'],
            authority=context['authority_snapshot'],now=context['time']['epoch'])
    elif pid=='cmba.native-dkn':
        from .native import dispatch
        exact(context['policy']['parameters'],set());require(not context['evidence_snapshot'],'CMBA_J_UNCONSUMED_EVIDENCE')
        report=dispatch(record);native=report['native_result'];state=native.get('status') if type(native) is dict else None
        result=outcome({'native.computation':'MATCH'},{'native':report,'native_status':state,
             'scope':'NESTED_NATIVE_REPORT_NOT_UNIFIED_ADMISSION'},
             ceiling='Actual pinned DKN routine computed the nested native report; interpret its distinct fields under its original profile. No native authority or payload check is implied beyond that report.')
        result['status']='NATIVE_REPORT_COMPUTED'
        return result
    else:raise Refusal('CMBA_J_PROFILE_UNSUPPORTED')
    return assess(record,context)


def evaluate(binding,values,context):
    inspect(binding,values);c=resolve(binding['body']['profile']);validate_context(context,c)
    require(context['expected_binding_root']==binding['binding_root'],'CMBA_EXPECTED_ROOT_MISMATCH')
    required={d['dimension_id']:d for d in c['required_dimensions']}
    dims={d['dimension_id']:d for d in binding['body']['dimensions']}
    for name in required.keys() & dims.keys():
        d=dims[name];r=required[name]
        require(d['critical'] and d['role']==r['role'] and d['schema_id']==r['schema_id'],'CMBA_REQUIRED_DIMENSION_TYPE')
    unknown=sorted(d['dimension_id'] for d in dims.values() if d['critical'] and d['dimension_id'] not in required)
    missing=sorted(set(required)-set(dims))
    if unknown:
        result=outcome({'profile.application':'UNSUPPORTED'},{'unsupported_critical_dimensions':unknown},ceiling=c['claim_ceiling'])
    elif missing or 'record' not in values:
        result=outcome({'profile.application':'INSUFFICIENT'},{'missing_dimensions':missing,'missing_record':'record' not in values},ceiling=c['claim_ceiling'])
    else:
        record=values['record'];require(type(record) is dict,'CMBA_J_RECORD_TYPE')
        for name,r in required.items():
            field=r['source_field']
            if field is not None:
                require(field in record,'CMBA_J_PROJECTION_FIELD')
                actual=dimension(name,r['role'],r['schema_id'],record[field])
                require(equal(actual,dims[name]),'CMBA_J_PROJECTION_MISMATCH')
                if name in values:require(equal(values[name],record[field]),'CMBA_J_PROJECTION_MISMATCH')
        result=_handler(c['profile_id'],record,context)
        result['details']['materialized_dimensions']=sorted(set(required)-{'record'})
    result['uninterpreted_dimensions']=sorted(set(dims)-set(required))
    body={'schema':'cmba.application-receipt-body.j1','binding_root':binding['binding_root'],
          'profile':clone(binding['body']['profile']),'supplied_values_hash':digest('supplied-values',values),
          'context_hash':hash_value('context',context),'policy_hash':digest('policy',context['policy']),
          'authority_snapshot_hash':digest('authority-snapshot',context['authority_snapshot']),
          'evidence_snapshot_hash':digest('evidence-snapshot',context['evidence_snapshot']),
          'time_hash':digest('evaluation-time',context['time']),
          'evaluator':{'id':'cmba.applications.j1','realization_sha256':realization_identity()},
          'result':result,'signature':'NOT_SIGNED'}
    receipt={'schema':'cmba.application-receipt.j1','body':body,'receipt_hash':hash_value('receipt',body)}
    canonical(receipt);return receipt


def replay(receipt,binding,values,context):
    canonical(receipt);exact(receipt, {'schema','body','receipt_hash'})
    require(receipt['schema']=='cmba.application-receipt.j1','CMBA_J_RECEIPT_SCHEMA');hex_digest(receipt['receipt_hash'])
    require(hash_value('receipt',receipt['body'])==receipt['receipt_hash'],'CMBA_J_RECEIPT_HASH')
    require(equal(receipt,evaluate(binding,values,context)),'CMBA_J_RECEIPT_REPLAY_MISMATCH')
    return {'status':'MATCH_EXACT_EVALUATION_REPLAY','receipt_hash':receipt['receipt_hash'],'authority_effect':'NONE'}
