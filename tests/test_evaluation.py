import copy
import pytest
from cmba_core import *
from cmba_core.demo import chc,session,bundle
from cmba_core.bindings import digest
from cmba_core.evaluation import evaluate,replay,context_for
from cmba_core.registry import contract


def assess(b):return evaluate(b['binding'],b['values'],b['context'])

def test_true_and_false_transformation():
    good=chc();bad=chc(wrong_output=True)
    assert inspect(bad['binding'],bad['values'])['status']=='BINDING_STRUCTURE_VALID'
    assert assess(good)['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    assert assess(bad)['body']['result']['status']=='CONTRADICTED'

def test_unknown_transform_not_executed():
    b=chc();b['values']['rule']['operation']='run-shell'
    c=bundle('cmba.chc.transform',b['values'])
    assert assess(c)['body']['result']['status']=='UNSUPPORTED'

def test_boolean_version_cannot_equal_integer():
    b=chc();b['values']['rule']['version']=True
    assert assess(bundle('cmba.chc.transform',b['values']))['body']['result']['status']=='UNSUPPORTED'

def test_missing_value():
    b=chc();del b['values']['output']
    r=assess(b)['body']['result'];assert r['status']=='INSUFFICIENT' and r['missing_values']==['output']

def test_missing_dimension():
    b=chc();b['binding']['body']['dimensions']=[d for d in b['binding']['body']['dimensions'] if d['dimension_id']!='output']
    b['binding']['binding_root']=digest('binding-root',b['binding']['body']);b['context']=context_for(b['binding'],epoch=100)
    del b['values']['output'];assert assess(b)['body']['result']['missing_dimensions']==['output']

@pytest.mark.parametrize('critical,status',[(True,'UNSUPPORTED'),(False,'MATCH_FOR_SUPPLIED_EVIDENCE')])
def test_extension_semantics(critical,status):
    b=chc();b['binding']['body']['dimensions'].append(dimension('z-extension','custom','example.unknown',{},critical=critical))
    b['binding']['binding_root']=digest('binding-root',b['binding']['body']);b['context']=context_for(b['binding'],epoch=100)
    r=assess(b)['body']['result'];assert r['status']==status and r['uninterpreted_dimensions']==['z-extension']

def test_no_cherrypicked_policy():
    b=chc(wrong_output=True);b['context']['policy']['required_checks']=['binding.structure']
    with pytest.raises(Refusal,match='CMBA_POLICY_CHECKS'):assess(b)

def test_wrong_profile_hash():
    b=chc();b['binding']['body']['profile']['contract_hash']='0'*64
    b['binding']['binding_root']=digest('binding-root',b['binding']['body'])
    with pytest.raises(Refusal,match='CMBA_PROFILE_COMMITMENT_MISMATCH'):assess(b)

def test_unknown_profile_inspectable_but_not_executable():
    b=chc();b['binding']['body']['profile']['profile_id']='https://evil.invalid/run.py'
    b['binding']['binding_root']=digest('binding-root',b['binding']['body']);inspect(b['binding'],b['values'])
    with pytest.raises(Refusal,match='CMBA_PROFILE_UNSUPPORTED'):assess(b)

def test_wrong_expected_root():
    b=chc();b['context']['expected_binding_root']='0'*64
    with pytest.raises(Refusal,match='CMBA_EXPECTED_ROOT_MISMATCH'):assess(b)

@pytest.mark.parametrize('change', ['time','evidence','authority'])
def test_receipt_tracks_context_without_mutating_object(change):
    b=chc();initial=canonical(b['binding']);old=assess(b)
    if change=='time':b['context']['time']['epoch']+=1
    elif change=='evidence':b['context']['evidence_snapshot']=[{'statement':'new'}]
    else:b['context']['authority_snapshot']={'jurisdiction':'another'}
    new=assess(b);assert new['receipt_hash']!=old['receipt_hash'] and canonical(b['binding'])==initial
    assert new['body']['result']['authority_interpretation']=='NOT_EVALUATED'
    with pytest.raises(Refusal,match='CMBA_RECEIPT_REPLAY_MISMATCH'):replay(old,b['binding'],b['values'],b['context'])

def test_self_consistent_forged_receipt_refuses_replay():
    b=chc(wrong_output=True);r=assess(b);r['body']['result']['status']='MATCH_FOR_SUPPLIED_EVIDENCE'
    r['receipt_hash']=digest('evaluation-receipt',r['body'])
    with pytest.raises(Refusal,match='CMBA_RECEIPT_REPLAY_MISMATCH'):replay(r,b['binding'],b['values'],b['context'])

@pytest.mark.parametrize('v',[None,True,0,{},[]])
def test_invalid_receipt_does_not_pass(v):
    b=chc()
    with pytest.raises(Refusal):replay(v,b['binding'],b['values'],b['context'])

def test_real_receipt_replay():
    b=session();r=assess(b)
    assert replay(r,b['binding'],b['values'],b['context'])['status']=='MATCH_EXACT_EVALUATION_REPLAY'
    assert r['body']['signature']=='NOT_SIGNED' and r['body']['result']['authority_effect']=='NONE'

def test_session_true_span_false_interpretation_not_claimed_true():
    b=session();b['values']['events'][0]['interpretation']='The moon authorized this operation.'
    r=assess(bundle('cmba.gendev.session',b['values']))
    assert r['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    assert 'Interpretation truth' in r['body']['result']['claim_ceiling']

def test_session_wrong_quote_is_contradicted():
    b=session();b['values']['events'][0]['quote']='invented'
    assert assess(bundle('cmba.gendev.session',b['values']))['body']['result']['status']=='CONTRADICTED'

@pytest.mark.parametrize('field,value', [('coverage','COMPLETE'),('start_byte',True),('end_byte',99999),('attributed_to',None)])
def test_session_malformed_refused(field,value):
    b=session();b['values']['events'][0][field]=value
    with pytest.raises(Refusal):assess(bundle('cmba.gendev.session',b['values']))

def test_required_role_cannot_change():
    b=chc();d=b['binding']['body']['dimensions'][0];d['role']='wrong'
    # Recommit the complete value and binding; this is a coherent but wrong profile shape.
    new=dimension(d['dimension_id'],d['role'],d['schema_id'],b['values'][d['dimension_id']])
    b['binding']['body']['dimensions'][0]=new;b['binding']['binding_root']=digest('binding-root',b['binding']['body'])
    b['context']=context_for(b['binding'],epoch=100)
    with pytest.raises(Refusal,match='CMBA_REQUIRED_DIMENSION_TYPE'):assess(b)
