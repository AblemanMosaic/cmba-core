import copy
import pytest
from cmba_core import *
from cmba_core.bindings import digest, validate_binding
from cmba_core.registry import contract
from cmba_core.demo import chc


def generic(value=1):
    d=dimension('state','state','example.state.i1',value,critical=False)
    return bind(profile_reference(contract('cmba.generic')),[d])

def test_stable_binding_and_detached_values():
    b=generic();assert b==generic()
    assert inspect(b)['dimensions'][0]['commitment']=='NOT_SUPPLIED'
    r=inspect(b,{'state':1});assert r['dimensions'][0]['commitment']=='MATCH'
    assert r['signature']=='NOT_CHECKED' and r['authority_effect']=='NONE'
    assert r['external_anchor']=='NOT_PROVIDED'
    assert inspect(b,expected_root=b['binding_root'])['external_anchor']=='MATCHED_CALLER_EXPECTATION'

@pytest.mark.parametrize('field,new',[('dimension_id','other'),('role','another-layer'),('schema_id','example.other.i1'),('critical',True)])
def test_dimension_scope_bound(field,new):
    d=dimension('state','state','example.state.i1',1,critical=False)
    args={'dimension_id':'state','role':'state','schema_id':'example.state.i1','critical':False}
    args[field]=new
    assert dimension(value=1,**args)['value_hash']!=d['value_hash']

@pytest.mark.parametrize('value',[None,False,True,0,'0',[],{}])
def test_types_do_not_alias(value):
    d=dimension('state','state','example.state.i1',value)
    assert d['value_hash']!=dimension('state','state','example.state.i1',1)['value_hash']

@pytest.mark.parametrize('field,value',[
 ('schema','other.schema'),('binding_root','0'*64),('extra','not-ignored')])
def test_binding_outer_mutation(field,value):
    b=generic();b[field]=value
    with pytest.raises(Refusal):inspect(b)

@pytest.mark.parametrize('field,value',[
 ('codec','jcs'),('algorithm','SHA-1'),('critical',1),('value_hash','A'*64),
 ('dimension_id','../bad'),('role',''),('schema_id',None),('extra',False)])
def test_dimension_invalid_headers(field,value):
    b=generic();b['body']['dimensions'][0][field]=value
    b['binding_root']=digest('binding-root',b['body'])
    with pytest.raises(Refusal):inspect(b)

def test_wrong_values_and_extra_values_refuse():
    with pytest.raises(Refusal,match='CMBA_DIMENSION_MISMATCH'):inspect(generic(),{'state':True})
    with pytest.raises(Refusal,match='CMBA_UNBOUND_VALUE'):inspect(generic(),{'wrong':1})

def test_null_present_not_missing():
    b=generic(None)
    assert inspect(b,{'state':None})['dimensions'][0]['commitment']=='MATCH'
    assert inspect(b)['dimensions'][0]['commitment']=='NOT_SUPPLIED'

def test_duplicate_dimension_and_relation():
    p=profile_reference(contract('cmba.generic'));d=dimension('a','state','example.i1',1)
    with pytest.raises(Refusal,match='CMBA_DIMENSION_DUPLICATE'):bind(p,[d,d])
    r=relation('r','references',reference('example.root','1'*64))
    with pytest.raises(Refusal,match='CMBA_RELATION_DUPLICATE'):bind(p,[d],relations=[r,r])

def test_constructor_sorts_but_parser_refuses_unsorted():
    p=profile_reference(contract('cmba.generic'));ds=[dimension(c,'state','example.i1',1) for c in ('z','a')]
    b=bind(p,ds);assert b['body']['dimensions'][0]['dimension_id']=='a'
    b['body']['dimensions'].reverse();b['binding_root']=digest('binding-root',b['body'])
    with pytest.raises(Refusal,match='CMBA_DIMENSION_ORDER'):inspect(b)

def test_no_self_reference_projection_loophole():
    b=generic();b['body']['binding_root']='anything'
    b['binding_root']=digest('binding-root',b['body'])
    with pytest.raises(Refusal,match='CMBA_FIELDS_INVALID'):inspect(b)

def test_clone_defends_mutable_caller():
    p=profile_reference(contract('cmba.generic'));d=dimension('a','state','example.i1',1)
    b=bind(p,[d]);d['role']='changed';p['profile_id']='changed';validate_binding(b)

def test_domain_separation():
    assert len({digest(d,{}) for d in ('binding-root','profile-contract','policy','evaluation-receipt')})==4
    with pytest.raises(Refusal,match='CMBA_DOMAIN_UNSUPPORTED'):digest('invented',{})

def test_comparison_is_not_equivalence():
    a=generic(1);b=generic(2);r=compare(a,b)
    assert r['same_profile'] and not r['same_binding'] and r['dimension_changes']==[{'id':'state','change':'CHANGED'}]
    assert r['semantic_equivalence']=='NOT_ESTABLISHED'

def test_reference_scheme_not_digest_only_identity():
    assert reference('dkn.logical.v0.2-candidate','1'*64)!=reference('cmba.binding.i1','1'*64)

def test_max_dimensions():
    p=profile_reference(contract('cmba.generic'))
    with pytest.raises(Refusal,match='CMBA_DIMENSION_LIMIT'):bind(p,[])
    with pytest.raises(Refusal,match='CMBA_DIMENSION_LIMIT'):bind(p,[dimension('x'+str(i),'state','s.i1',i) for i in range(65)])
