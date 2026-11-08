from pathlib import Path
import hashlib,os,sys,subprocess
from copy import deepcopy as cp
import pytest
from cmba_core import canonical,decode,Refusal
from cmba_core.j1 import demo
from cmba_core.j1.abi import dispatch
from cmba_core.j1.registry import contracts,capabilities
from cmba_core.j1.native import dispatch as native_dispatch,read_collection
from cmba_workbench.applications_j1 import Applications
ROOT=Path(__file__).resolve().parents[1]


def request(op,args):return {'schema':'cmba.request.j1','operation':op,'arguments':args}

@pytest.mark.parametrize('op',['execute','install','write','publish','sign','fetch','eval','plugin','advance-pin','delete'])
def test_effects_unavailable_in_abi(op):
    with pytest.raises(Refusal,match='CMBA_J_OPERATION'):dispatch(request(op,{}))

def test_abi_exact_profile_result_and_replay():
    b=demo.kasd();r=dispatch(request('evaluate',b))
    assert dispatch(request('replay',{'receipt':r,**b}))['status']=='MATCH_EXACT_EVALUATION_REPLAY'
    assert len(dispatch(request('profiles',{})))==13
    assert all(x['effect_class']=='PURE_READ' and not x['auto_install'] for x in dispatch(request('capabilities',{})))

def test_closed_request_cannot_choose_code():
    r=request('profiles',{});r['handler']='os.system'
    with pytest.raises(Refusal):dispatch(r)

def test_optional_dependency_is_not_ambient():
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
    code="import sys;from cmba_core.j1.demo import graph,assess; assert assess(graph())['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'; assert not any(k.startswith(('dkn','cryptography','tkinter')) for k in sys.modules)"
    p=subprocess.run([sys.executable,'-S','-c',code],env=env,capture_output=True)
    assert p.returncode==0,p.stderr

def test_missing_crypto_refuses_not_fallback():
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
    code="from cmba_core.j1.endorsements import public_key;from cmba_core import Refusal\ntry:public_key(None)\nexcept Refusal as e:assert e.code=='CMBA_J_CRYPTO_DEPENDENCY_UNAVAILABLE'\nelse:raise AssertionError()"
    p=subprocess.run([sys.executable,'-S','-c',code],env=env,capture_output=True)
    assert p.returncode==0,p.stderr

def test_workbench_host_context_boundary():
    w=Applications();b=demo.kasd();w.load({'schema':'cmba.workbench-bundle.j1',**b})
    with pytest.raises(Refusal,match='READER_CONTEXT_REQUIRED'):w.evaluate()
    assert w.evaluate(accept_document_context=True)['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    assert w.replay()['status']=='MATCH_EXACT_EVALUATION_REPLAY'
    with pytest.raises(Refusal):w.evaluate(reader_context={})
    with pytest.raises(Refusal,match='NO_RECEIPT'):w.replay()
    with pytest.raises(Refusal):w.load({})
    with pytest.raises(Refusal,match='NO_SELECTION'):w.evaluate()

def test_cli_exact_canonical_and_noncanonical_refusal(tmp_path,make_link):
    b=demo.graph();req=request('evaluate',b)
    p=subprocess.run([sys.executable,'-m','cmba_core.j1.cli','-'],input=canonical(req),capture_output=True)
    assert p.returncode==0 and decode(p.stdout[:-1])['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    for raw in (b'null',b'{} ',b'{"a":1,"a":2}'):
        p=subprocess.run([sys.executable,'-m','cmba_core.j1.cli','-'],input=raw,capture_output=True)
        assert p.returncode==2 and decode(p.stdout[:-1])['status']=='REFUSED'
    f=tmp_path/'x';f.write_bytes(canonical(req));l=make_link(tmp_path/'link',f)
    if make_link.is_actual(l):
        p=subprocess.run([sys.executable,'-m','cmba_core.j1.cli',str(l)],capture_output=True)
        assert p.returncode==2
    else:
        from cmba_core.cli import read_local
        with pytest.raises(Refusal,match='CMBA_INPUT_SYMLINK'):read_local(str(l))

@pytest.mark.parametrize('op',['create','put_artifact','advance_namespace','import_local_index','__class__','execute'])
def test_native_read_adapter_has_no_write_operations(op,tmp_path):
    with pytest.raises(Refusal,match='NATIVE_OPERATION'):read_collection(tmp_path/'absent',op,{},kind='vault')
    assert not (tmp_path/'absent').exists()

def test_real_native_vault_and_index_read(tmp_path):
    from dkn_v02 import pack
    from dkn_v02.navigation import LocalIndex
    from dkn_v02.vault import TransactionalVault
    raw,m=pack({'a.txt':b'hello'},[]);root=m['logical_root']
    vault=TransactionalVault.create(tmp_path/'vault.db');vault.put_artifact(raw)
    original=(tmp_path/'vault.db').read_bytes()
    r=read_collection(tmp_path/'vault.db','resolve_exact',{'logical_root':root},kind='vault')
    assert r['native_result']['result']['logical_root']==root
    assert (tmp_path/'vault.db').read_bytes()==original
    r=read_collection(tmp_path/'vault.db','traverse',{'logical_root':root,'direction':'outgoing','max_depth':2,'max_nodes':8},kind='vault')
    assert r['authority_effect']=='NONE'
    index=LocalIndex(tmp_path/'index');index.add(raw)
    r=read_collection(tmp_path/'index','resolve_exact',{'logical_root':root},kind='index')
    assert r['native_result']['logical_root']==root
    r=read_collection(tmp_path/'index','discover',{'semantic_name':'example.unknown'},kind='index')
    assert r['authority_effect']=='NONE'

def test_native_namespace_and_lifecycle():
    from dkn_v02 import declare_genesis
    from dkn_v02.lifecycle import lifecycle_policy,policy_reference
    k=demo.fixture_key(20)
    gen=declare_genesis(semantic_name='example.j',purpose='test',nonce='one',key=k)
    r=native_dispatch({'operation':'namespace','arguments':{'genesis':gen,'transitions':[]}})
    assert r['native_result']['active_key']==gen['founder_public_key_hex'] and r['native_result']['global_head']=='NOT_ESTABLISHED'
    r=native_dispatch({'operation':'lineage','arguments':{'genesis':gen,'chains':[[]]}})
    assert r['authority_effect']=='NONE'

def test_native_sam_ds_and_lifecycle_reference_cases():
    # Replay selected exact native requests from already frozen corpora, not substitute reports.
    import json
    native=Path(os.environ['DKN_TEST_ROOT'])
    corpora=[('lifecycle',native/'interop/lifecycle-f1-conformance.json'),('distributed',native/'interop/distributed-g1-conformance.json')]
    ran=[]
    for family,path in corpora:
        corpus=json.loads(path.read_text(encoding='utf-8'))
        case=corpus['cases'][0];req=case['request']
        schema={'lifecycle':'dkn.lifecycle-request.v0.2-f1','distributed':'dkn.distributed-request.v0.2-g1'}[family]
        native_request={'schema':schema,'operation':req['operation'],'arguments':req['arguments']}
        r=native_dispatch({'operation':family,'arguments':{'request':native_request}})
        assert canonical(r['native_result'])==canonical(case['expected']['result'])
        assert r['authority_effect']=='NONE';ran.append(family)
    assert set(ran)=={'lifecycle','distributed'}

def test_native_assurance_exact_result():
    import json
    native=Path(os.environ['DKN_TEST_ROOT']);v=json.loads((native/'vectors/v02-sam-vectors.json').read_text(encoding='utf-8'))
    r=native_dispatch({'operation':'assurance','arguments':{'request':v['evaluation_request']}})
    assert canonical(r['native_result'])==canonical(v['evaluation_result'])
