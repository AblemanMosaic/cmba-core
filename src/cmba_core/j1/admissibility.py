"""Finite recomputation of child assessments. Receipts supplied as PASS are not inputs."""
from ..bindings import exact, identifier, validate_reference
from ..errors import require
from .common import sequence, equal, outcome

ALLOWED=frozenset(('cmba.kasd','cmba.consent','cmba.observation','cmba.execution-record','cmba.coordination'))


def assess(record, context):
    from .evaluation import evaluate
    exact(record, {'subject','assessments'});validate_reference(record['subject'])
    sequence(record['assessments'],minimum=1,limit=8);require(not context['evidence_snapshot'],'CMBA_J_UNCONSUMED_EVIDENCE')
    params=context['policy']['parameters'];exact(params, {'child_contexts'})
    require(type(params['child_contexts']) is dict,'CMBA_J_CONTEXTS')
    seen=set();rows=[];checks={}
    for child in record['assessments']:
        exact(child, {'id','binding','values'});identifier(child['id'])
        require(child['id'] not in seen,'CMBA_J_DUPLICATE');seen.add(child['id'])
        # Check structural validity in evaluate; avoid arbitrary recursive profile execution.
        from ..bindings import validate_binding
        validate_binding(child['binding'])
        require(child['binding']['body']['profile']['profile_id'] in ALLOWED,'CMBA_J_ADMISSIBILITY_CHILD')
        require(child['id'] in params['child_contexts'],'CMBA_J_CHILD_CONTEXT_MISSING')
        child_context=params['child_contexts'][child['id']]
        require(type(child_context) is dict,'CMBA_J_CONTEXTS')
        # One assessment time; a stale child cannot be laundered through a fresh parent.
        require(equal(child_context.get('time'),context['time']),'CMBA_J_CHILD_TIME')
        receipt=evaluate(child['binding'],child['values'],child_context)
        result=receipt['body']['result']
        subject=result['details'].get('assessed_subject')
        require(subject is not None and equal(subject,record['subject']),'CMBA_J_CHILD_SUBJECT')
        checks[child['id']]='MATCH' if result['status']=='MATCH_FOR_SUPPLIED_EVIDENCE' else result['status']
        rows.append({'id':child['id'],'receipt_hash':receipt['receipt_hash'],'status':result['status'],
                     'profile':child['binding']['body']['profile'],'result':result})
    require(set(params['child_contexts'])==seen,'CMBA_J_UNUSED_CHILD_CONTEXT')
    return outcome(checks, {'assessments':rows,'assessed_subject':record['subject']},
       ceiling='All configured child predicates recomputed for one exact subject and evaluation time. Selected policies/authority snapshots are caller-owned; no global admissibility or effect grant.')
