"""SE-J1 and SD-J1 negative tests; explicit trusted expectations, not self-authenticating hashes."""
from copy import deepcopy as cp
import ctypes,ctypes.util,hashlib
import pytest
from cmba_core import canonical,Refusal
from cmba_core.j1 import demo
from cmba_core.j1.common import hash_value
from cmba_core.j1.endorsements import (seal,verify,public_key,endorse,envelope,verify_envelope,
                                       assess_endorsements,SIGN_DOMAIN,admitted_public_key)
from cmba_core.j1.disclosure import make,select,verify as verify_disclosure
from cmba_core.j1.evaluation import evaluate


def test_rfc8032_test_vector_one_backend_and_admission():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    k=Ed25519PrivateKey.from_private_bytes(bytes.fromhex('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60'))
    pub=public_key(k)
    assert pub=='d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a'
    assert admitted_public_key(bytes.fromhex(pub))
    assert k.sign(b'').hex()==('e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555f'
                           'b8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b')

@pytest.mark.parametrize('field,value',[('kind','approval'),('algorithm','other'),('public_key','0'*64),('schema','other'),('payload',{'lie':True})])
def test_signed_body_substitution(field,value):
    e=seal('observation',{'fact':True},demo.fixture_key(10));e['body'][field]=value
    e['record_hash']=hash_value('signed-record',{k:v for k,v in e.items() if k!='record_hash'})
    with pytest.raises(Refusal):verify(e)

@pytest.mark.parametrize('public', ['01'+'00'*31,'00'*32,'ff'*32,'ed'+'ff'*30+'7f'])
def test_inadmissible_keys_rejected(public):
    e=seal('observation',{},demo.fixture_key(10));e['body']['public_key']=public
    e['signature_hex']='01'+'00'*63
    e['record_hash']=hash_value('signed-record',{k:v for k,v in e.items() if k!='record_hash'})
    with pytest.raises(Refusal,match='PUBLIC_KEY_INVALID'):verify(e)

@pytest.mark.parametrize('bad',[True,False,0,[],{},None])
def test_signature_envelope_malformed(bad):
    with pytest.raises(Refusal):verify(bad)

def test_signature_domain_bound_and_canonical_scalar():
    k=demo.fixture_key(12);e=seal('observation',{'a':1},k)
    e['signature_hex']=k.sign(b'OTHER\0'+canonical(e['body'])).hex()
    e['record_hash']=hash_value('signed-record',{name:v for name,v in e.items() if name!='record_hash'})
    with pytest.raises(Refusal,match='SIGNATURE_INVALID'):verify(e)
    e=seal('observation',{'a':1},k);sig=bytes.fromhex(e['signature_hex'])
    e['signature_hex']=(sig[:32]+b'\xff'*32).hex()
    with pytest.raises(Refusal,match='SIGNATURE_INVALID'):verify(e)

def test_detached_body_signature_envelope_no_cycle():
    b=demo.endorsement();record=b['values']['record'];sig=b['context']['evidence_snapshot'][0]
    root=record['binding']['binding_root'];one=envelope(record['binding'],record['values'],[sig])
    second=endorse(record['binding'],record['values'],demo.fixture_key(9),requirement_id='release',not_before=0,not_after=200)
    two=envelope(record['binding'],record['values'],[sig,second])
    assert one['body']['binding']['binding_root']==two['body']['binding']['binding_root']==root
    assert one['envelope_hash']!=two['envelope_hash']
    assert verify_envelope(two)['recognition']=='NOT_CHECKED'
    two['body']['endorsements'][0]['body']['payload']['action']='execute'
    with pytest.raises(Refusal):verify_envelope(two)

def test_unrecognized_extra_signature_not_threshold():
    b=demo.endorsement();r=b['values']['record']
    sig=endorse(r['binding'],r['values'],demo.fixture_key(9),requirement_id='release',not_before=0,not_after=200)
    b['context']['evidence_snapshot']=[sig]
    assert demo.assess(b)['body']['result']['status']=='INSUFFICIENT'

def test_duplicate_statement_not_counted_twice():
    b=demo.endorsement();b['context']['evidence_snapshot']*=2
    with pytest.raises(Refusal,match='DUPLICATE_EVIDENCE'):demo.assess(b)

def test_same_signer_distinct_statements_count_once():
    b=demo.endorsement();r=b['values']['record'];second=endorse(r['binding'],r['values'],demo.fixture_key(8),
      requirement_id='release',not_before=1,not_after=199)
    b['context']['evidence_snapshot'].append(second)
    rr=demo.assess(b)['body']['result'];assert len(rr['details']['requirements'][0]['recognized_signers'])==1

@pytest.mark.parametrize('n',[1,2,3,4,5,7,8,9,16,31,32,63,64])
def test_merkle_non_power_of_two_and_all_paths(n):
    entries=[{'label':f'item-{i:02}','schema_id':'example.item','value':i} for i in range(n)]
    salts=[hashlib.sha256(f'fixture-salt-{i}'.encode()).hexdigest() for i in range(n)]
    b=make(entries,salts=salts)
    for i in sorted(set((0,n//2,n-1))):
        view=select(b,[entries[i]['label']]);r=verify_disclosure(view,expected_root=b['header']['disclosure_root'])
        assert r['details']['disclosed_count']==1
    r=verify_disclosure(b,expected_root=b['header']['disclosure_root'])
    assert r['details']['all_entries_disclosed'] is True

@pytest.mark.parametrize('change',['salt','value','label','schema','index','side','hash','count','root','depth'])
def test_wrong_disclosure_opening_refused(change):
    b=make([{'label':'a','schema_id':'example.item','value':1},{'label':'b','schema_id':'example.item','value':2}],salts=['11'*32,'22'*32])
    root=b['header']['disclosure_root'];v=select(b,['a']);leaf=v['openings'][0]['leaf']
    if change=='salt':leaf['salt_hex']='33'*32
    elif change=='value':leaf['value']=True
    elif change=='label':leaf['label']='other'
    elif change=='schema':leaf['schema_id']='other'
    elif change=='index':leaf['index']=1
    elif change=='side':v['openings'][0]['path'][0]['side']='left'
    elif change=='hash':v['openings'][0]['path'][0]['hash']='0'*64
    elif change=='count':v['header']['leaf_count']=1
    elif change=='root':root='0'*64
    else:v['openings'][0]['path']=[]
    with pytest.raises(Refusal):verify_disclosure(v,expected_root=root)

def test_disclosure_redaction_is_not_proof():
    b=demo.disclosure();v=cp(b['values']['record']);del v['openings'][0]['path']
    with pytest.raises(Refusal):verify_disclosure(v,expected_root=v['header']['disclosure_root'])

def test_disclosure_required_labels_not_vacuous_match():
    b=demo.disclosure();b['context']['policy']['parameters']['required_labels']=['private-notes']
    rr=demo.assess(b)['body']['result'];assert rr['status']=='INSUFFICIENT'
    assert rr['details']['confidentiality']=='NOT_ESTABLISHED'

def test_no_private_material_in_selected_view():
    b=demo.disclosure();raw=canonical(b)
    assert b'PRIVATE-FIXTURE-NOT-TO-DISCLOSE' not in raw
    assert b'22'*32 not in raw
    assert b'private-notes' not in raw

def test_salt_reuse_refused():
    with pytest.raises(Refusal,match='SALT_REUSE'):
        make([{'label':'a','schema_id':'x','value':1},{'label':'b','schema_id':'x','value':2}],salts=['11'*32]*2)

def test_wrong_policy_inside_signed_envelope_refused():
    b=demo.endorsement();r=b['values']['record'];sig=cp(b['context']['evidence_snapshot'][0]);p=sig['body']['payload'];p['policy_hash']='0'*64
    wrong=seal('endorsement',p,demo.fixture_key(8))
    with pytest.raises(Refusal,match='ENVELOPE_SCOPE'):envelope(r['binding'],r['values'],[wrong])
