"""Functional and adversarial application predicates; real signed fixtures, no mocked verifiers."""
import hashlib
from copy import deepcopy as cp
import pytest
from cmba_core import canonical,Refusal
from cmba_core.codec import clone
from cmba_core.bindings import bind,dimension,profile_reference,digest
from cmba_core.j1 import demo
from cmba_core.j1.evaluation import bind_application,context_for,evaluate,replay
from cmba_core.j1.common import hash_value
from cmba_core.j1.endorsements import seal,public_key

FACTORIES=[demo.graph,demo.session,demo.kasd,demo.consent,demo.disclosure,demo.observation,
           demo.coordination,demo.reconciliation,demo.execution,demo.trace,demo.endorsement,demo.admissibility,demo.native]


def rebind(b,record):
    new=bind_application(b['binding']['body']['profile']['profile_id'],record)
    new['context']=cp(b['context']);new['context']['expected_binding_root']=new['binding']['binding_root']
    return new

def result(b):return demo.assess(b)['body']['result']

@pytest.mark.parametrize('factory',FACTORIES,ids=lambda f:f.__name__)
def test_all_family_evaluators(factory):
    b=factory();r=demo.assess(b)
    assert r['body']['result']['status']==('NATIVE_REPORT_COMPUTED' if factory==demo.native else 'MATCH_FOR_SUPPLIED_EVIDENCE')
    assert r['body']['result']['authority_effect']=='NONE'
    assert r['body']['result']['authorization']=='EXTERNAL_DECISION_REQUIRED'
    assert replay(r,b['binding'],b['values'],b['context'])['status']=='MATCH_EXACT_EVALUATION_REPLAY'

@pytest.mark.parametrize('factory',FACTORIES,ids=lambda f:f.__name__)
@pytest.mark.parametrize('bad',[None,False,0,[],{}])
def test_malformed_record_refuses(factory,bad):
    b=factory()
    with pytest.raises(Refusal):result(rebind(b,bad))

@pytest.mark.parametrize('factory',FACTORIES,ids=lambda f:f.__name__)
def test_missing_record_never_matches(factory):
    b=factory();b['values']={}
    assert result(b)['status']=='INSUFFICIENT'

@pytest.mark.parametrize('factory',FACTORIES,ids=lambda f:f.__name__)
def test_reader_pin_required(factory):
    b=factory();b['context']['expected_binding_root']='0'*64
    with pytest.raises(Refusal,match='EXPECTED_ROOT'):result(b)

@pytest.mark.parametrize('factory',FACTORIES,ids=lambda f:f.__name__)
def test_receipt_recomputed_not_rehash_certified(factory):
    b=factory();r=demo.assess(b);r['body']['result']['authority_effect']='EXECUTE'
    r['receipt_hash']=hash_value('receipt',r['body'])
    with pytest.raises(Refusal,match='REPLAY_MISMATCH'):replay(r,b['binding'],b['values'],b['context'])

@pytest.mark.parametrize('change',['time','policy','authority','evidence'])
def test_context_separate_from_object(change):
    b=demo.kasd();before=canonical(b['binding']);old=demo.assess(b)
    if change=='time':b['context']['time']['epoch']=250
    if change=='policy':
        # A new recognized policy must be explicitly selected; omitted required checks refuse.
        b['context']['policy']['required_checks']=[]
        with pytest.raises(Refusal,match='POLICY_CHECKS'):result(b)
        return
    if change=='authority':b['context']['authority_snapshot']['members']=[]
    if change=='evidence':b['context']['evidence_snapshot']=[]
    new=demo.assess(b)
    assert new['receipt_hash']!=old['receipt_hash'] and canonical(b['binding'])==before
    assert new['body']['result']['status']=='INSUFFICIENT'

@pytest.mark.parametrize('which',['output','input','toolchain'])
def test_chc_valid_binding_wrong_relationship(which):
    b=demo.graph();r=cp(b['values']['record'])
    if which in ('input','output'):
        node=r['nodes'][0 if which=='input' else 1];node['text']='{}';node['sha256']=hashlib.sha256(b'{}').hexdigest()
    else:r['steps'][0]['toolchain']['implementation_sha256']='0'*64
    assert result(rebind(b,r))['status']=='CONTRADICTED'

@pytest.mark.parametrize('change',['cycle','duplicate-output','missing-node','unused-node'])
def test_chc_graph_admission(change):
    b=demo.graph();r=cp(b['values']['record'])
    if change=='cycle':r['steps'][0]['inputs']=['output']
    elif change=='duplicate-output':r['steps'].append(cp(r['steps'][0]))
    elif change=='missing-node':r['steps'][0]['output']='absent'
    else:r['nodes'].append({'id':'unused','text':'x','sha256':hashlib.sha256(b'x').hexdigest()})
    with pytest.raises(Refusal):result(rebind(b,r))

def test_chc_unknown_rule_not_executed():
    b=demo.graph();r=cp(b['values']['record']);r['steps'][0]['rule']['id']='shell-exec'
    assert result(rebind(b,r))['status']=='UNSUPPORTED'

def test_source_quote_and_capture_boundary():
    b=demo.session();r=cp(b['values']['record']);r['events'][0]['quote']='invented'
    assert result(rebind(b,r))['status']=='CONTRADICTED'
    r=cp(b['values']['record']);r['source']['coverage']='COMPLETE'
    with pytest.raises(Refusal,match='CAPTURE_CLAIM'):result(rebind(b,r))
    r=cp(b['values']['record']);r['events'][0]['interpretation']='A false interpretation is still only an attributed claim.'
    assert result(rebind(b,r))['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'

@pytest.mark.parametrize('which',['architecture','security'])
def test_joint_approvals_no_missing_jurisdiction_laundering(which):
    b=demo.kasd();b['context']['evidence_snapshot']=[e for e in b['context']['evidence_snapshot'] if e['body']['payload']['requirement_id']==which]
    assert result(b)['status']=='INSUFFICIENT'

@pytest.mark.parametrize('field,value',[('action','execute'),('terms_hash','0'*64),('requirement_id','other'),('role','other'),('jurisdiction','other')])
def test_authentic_but_misscoped_approval(field,value):
    b=demo.kasd();old=b['context']['evidence_snapshot'][0];p=cp(old['body']['payload']);p[field]=value
    b['context']['evidence_snapshot'][0]=seal('approval',p,demo.fixture_key(1))
    assert result(b)['status']=='INSUFFICIENT'

def test_signed_denial_dominates_approval():
    b=demo.kasd();r=b['values']['record'];b['context']['evidence_snapshot'].append(demo.approval(r,'security',demo.fixture_key(2),decision='deny'))
    assert result(b)['status']=='CONTRADICTED'

def test_joint_constraints_overlap_not_assumed_disjoint():
    b=demo.kasd();r=cp(b['values']['record']);r['requirements'][1]['constraints']['encoding']='ascii'
    b=rebind(b,r);b['context']['evidence_snapshot']=[demo.approval(r,'architecture',demo.fixture_key(1)),demo.approval(r,'security',demo.fixture_key(2))]
    rr=result(b);assert rr['status']=='CONTRADICTED' and rr['details']['overlaps'][0]['incompatible_fields']==['encoding']

def test_boolean_not_integer_constraint():
    b=demo.kasd();r=cp(b['values']['record']);r['facts']['public']=1
    assert result(rebind(b,r))['status']=='CONTRADICTED'

@pytest.mark.parametrize('change',['expiry','withdrawal','conditions','renewal','revoked-key','different-actor','different-subject'])
def test_consent_scope_time_and_withdrawal(change):
    b=demo.consent();r=cp(b['values']['record']);g=b['context']['evidence_snapshot'][0]
    if change=='expiry':b['context']['time']['epoch']=200
    elif change=='withdrawal':b['context']['evidence_snapshot'].append(seal('consent-withdrawal',{'grant_hash':g['record_hash'],'at':90},demo.fixture_key(3)))
    elif change=='revoked-key':b['context']['authority_snapshot']['revoked_keys']=[public_key(demo.fixture_key(3))]
    elif change=='conditions':r['facts']['public']=False;b=rebind(b,r)
    elif change=='renewal':r['renewal_context']['purpose']='different';b=rebind(b,r)
    elif change=='different-actor':r['actor']='other';b=rebind(b,r)
    else:r['subject']=demo.ref('other');b=rebind(b,r)
    assert result(b)['status'] in ('NO_MATCH','INSUFFICIENT')

def test_other_key_cannot_withdraw_grant():
    b=demo.consent();g=b['context']['evidence_snapshot'][0]
    b['context']['evidence_snapshot'].append(seal('consent-withdrawal',{'grant_hash':g['record_hash'],'at':0},demo.fixture_key(9)))
    assert result(b)['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'

def test_same_issuer_override_and_renewal():
    b=demo.consent();r=b['values']['record'];g=b['context']['evidence_snapshot'][0]
    b['context']['evidence_snapshot'].append(demo.grant(r,not_before=90,until=110,grant_id='renewed',supersedes=[g['record_hash']]))
    assert result(b)['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    b['context']['time']['epoch']=120
    rr=result(b);assert rr['status']=='NO_MATCH'
    assert any(row['disposition']=='SUPERSEDED' for row in rr['details']['grants'])

def test_subdelegation_not_silently_allowed():
    b=demo.consent();p=cp(b['context']['evidence_snapshot'][0]['body']['payload']);p['delegation_depth']=1
    b['context']['evidence_snapshot']=[seal('consent-grant',p,demo.fixture_key(3))]
    with pytest.raises(Refusal):result(b)

def test_coordinator_terms_and_distinct_keys():
    b=demo.coordination();r=cp(b['values']['record']);r['rounds'][1]['statements']=r['rounds'][1]['statements'][:1]
    assert result(rebind(b,r))['status']=='INSUFFICIENT'
    r=cp(b['values']['record']);r['terms']['cost']=10
    assert result(rebind(b,r))['status']=='INSUFFICIENT'
    r=cp(b['values']['record']);r['participants']=[r['participants'][0]]*2
    with pytest.raises(Refusal,match='DUPLICATE_PARTICIPANT'):result(rebind(b,r))

def test_reconciliation_absent_not_null_and_no_winner():
    b=demo.reconciliation();rr=result(b)
    assert rr['details']['conflict_count']==2 and rr['details']['selected_winner']=='NONE'
    assert rr['details']['recomputed']['conflicts']['gone'][1]=={'snapshot':'b','present':False}
    r=cp(b['values']['record']);r['proposed']['merged']['gone']=None;r['proposed']['conflicts'].pop('gone')
    assert result(rebind(b,r))['status']=='CONTRADICTED'

def test_observation_recomputes_actual_supplied_bytes():
    b=demo.observation();r=cp(b['values']['record']);r['raw_hex']=b'other'.hex()
    assert result(rebind(b,r))['status']=='CONTRADICTED'
    r=cp(b['values']['record']);r['measurement_type']='VERIFIED_PHYSICAL_REALITY'
    with pytest.raises(Refusal,match='OBSERVATION_CLAIM'):result(rebind(b,r))

@pytest.mark.parametrize('field,value',[('target','other'),('operation','execute'),('configuration',{'mode':'write'}),('artifact',demo.ref('other'))])
def test_execution_configuration_substitution(field,value):
    b=demo.execution();r=cp(b['values']['record']);r['observed'][field]=value
    assert result(rebind(b,r))['status']=='CONTRADICTED'

def test_execution_evidence_old_or_unrecognized():
    b=demo.execution();b['context']['time']['epoch']=150
    assert result(b)['status']=='INSUFFICIENT'
    b=demo.execution();b['context']['authority_snapshot']['members']=[]
    assert result(b)['status']=='INSUFFICIENT'

def test_trace_reference_not_truth():
    b=demo.trace();r=cp(b['values']['record']);r['claims'][0]['event_refs']=['missing']
    with pytest.raises(Refusal,match='CITATION_MISSING'):result(rebind(b,r))
    assert result(b)['details']['claim_truth']=='NOT_ESTABLISHED'

def test_composition_recomputes_same_subject_and_time():
    b=demo.admissibility();before=canonical(b['binding']);r=result(b);assert r['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    b['context']['policy']['parameters']['child_contexts']['approval']['evidence_snapshot']=[]
    assert result(b)['status']=='INSUFFICIENT' and canonical(b['binding'])==before
    b=demo.admissibility();b['context']['policy']['parameters']['child_contexts']['approval']['time']['epoch']=99
    with pytest.raises(Refusal,match='CHILD_TIME'):result(b)
    b=demo.admissibility();r=cp(b['values']['record']);r['subject']=demo.ref('other')
    with pytest.raises(Refusal,match='CHILD_SUBJECT'):result(rebind(b,r))

def test_combined_end_to_end_workflow():
    r=demo.joint_workflow()
    assert set(r['initial_statuses'])=={'MATCH_FOR_SUPPLIED_EVIDENCE'}
    assert r['later_status']=='INSUFFICIENT' and r['wrong_output_status']=='CONTRADICTED'
    assert r['same_assessment_object'] and not r['private_content_in_public_view']
    assert r['disclosed_subject']['digest_hex']==r['native_dkn_root']!=r['cmba_dkn_wrapper_root']

def test_projection_hashes_independently_bound_and_checked():
    b=demo.kasd();req=b['binding']['body']['profile']
    # Coherently change one component commitment while retaining the aggregate record.
    dims=cp(b['binding']['body']['dimensions'])
    target=next(d for d in dims if d['dimension_id']=='subject')
    substitute=dimension('subject',target['role'],target['schema_id'],demo.ref('different'))
    dims=[substitute if d['dimension_id']=='subject' else d for d in dims]
    b['binding']=bind(req,dims);b['context']['expected_binding_root']=b['binding']['binding_root']
    with pytest.raises(Refusal,match='PROJECTION_MISMATCH'):result(b)

@pytest.mark.parametrize('factory',FACTORIES,ids=lambda f:f.__name__)
def test_typed_components_not_opaque_record_only(factory):
    b=factory();dims=b['binding']['body']['dimensions']
    assert len(dims)>=3
    r=result(b)
    assert sorted(d['dimension_id'] for d in dims if d['dimension_id']!='record')==r['details']['materialized_dimensions']

@pytest.mark.parametrize('factory',FACTORIES,ids=lambda f:f.__name__)
def test_unknown_critical_is_not_auto_supported(factory):
    b=factory();d=dimension('z-unknown','extension','example.unknown',{'claims':'permission'},critical=True)
    b['binding']=bind(b['binding']['body']['profile'],b['binding']['body']['dimensions']+[d])
    b['context']['expected_binding_root']=b['binding']['binding_root']
    assert result(b)['status']=='UNSUPPORTED'

@pytest.mark.parametrize('which',['authority','time','threshold','phase'])
def test_bool_not_integer_in_security_parameters(which):
    if which=='authority':
        b=demo.kasd();b['context']['authority_snapshot']['members'][0]['public_key']=True
    elif which=='time':b=demo.kasd();b['context']['time']['epoch']=True
    elif which=='threshold':
        b=demo.kasd();r=cp(b['values']['record']);r['requirements'][0]['threshold']=True;b=rebind(b,r)
    else:b=demo.coordination();b['context']['policy']['parameters']['required_phase']=True
    with pytest.raises(Refusal):result(b)
