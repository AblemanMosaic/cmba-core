import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cmba_core import Refusal,canonical,decode
from cmba_core.profiles.dkn import bind_archive,load_native
from cmba_core.evaluation import context_for,evaluate


def test_native_archive_and_root_preserved():
    n=load_native();raw,m=n.pack({'a.txt':b'a','dir/b.txt':b'b'})
    r=bind_archive(raw,expected_logical_root=m['logical_root'])
    assert r['native_logical_root']==m['logical_root'] and r['binding']['binding_root']!=m['logical_root']
    assert r['binding']['body']['relations'][0]['target']['digest_hex']==m['logical_root']
    assert r['native_report']['status']=='PASS' and r['root_translation']=='NONE_NEW_WRAPPER_ROOT'
    assert r['certificate_report'] is None


def test_native_certificate_not_authority():
    n=load_native();raw,m=n.pack({'a':b'hello'});key=Ed25519PrivateKey.generate();cert=n.certify(m,key)
    r=bind_archive(raw,expected_logical_root=m['logical_root'],certificate=cert)
    assert r['certificate_report']['signature']=='PASS'
    assert r['certificate_report']['authorization']=='NOT_CHECKED'


def test_wrong_native_pin():
    n=load_native();raw,m=n.pack({'a':b'hello'})
    with pytest.raises(Refusal,match='CMBA_DKN_EXPECTED_ROOT_MISMATCH'):bind_archive(raw,expected_logical_root='0'*64)


def test_mutated_payload_refuses():
    n=load_native();raw,m=n.pack({'a':b'hello'})
    bad=raw.replace(b'hello',b'jello')
    with pytest.raises(Refusal,match='CMBA_DKN_NATIVE_REFUSED'):bind_archive(bad,expected_logical_root=m['logical_root'])


def test_manifest_evaluator_does_not_claim_payload_checked():
    n=load_native();raw,m=n.pack({'a':b'hello'});r=bind_archive(raw,expected_logical_root=m['logical_root'])
    e=evaluate(r['binding'],r['values'],context_for(r['binding'],epoch=100))['body']['result']
    assert e['status']=='MATCH_FOR_SUPPLIED_EVIDENCE' and 'structure/root only' in e['claim_ceiling']

@pytest.mark.parametrize('v',[None,False,True,0,2**63-1,-2**63,{'z':[1,False],'a':'é'},['\ue000','\U00010000']])
def test_codec_overlap_native_bytes(v):
    assert canonical(v)==load_native().canonical(v)


def test_no_dependency_renaming():
    n=load_native();assert n.__name__=='dkn_v02.core'
