from pathlib import Path
import json
import os
import subprocess
import sys
import pytest
from cmba_core import canonical,decode,Refusal
from cmba_core.abi import dispatch
from cmba_core.demo import chc,session
from cmba_core.registry import catalogue,capability_descriptors,contracts
from cmba_core.cli import read_local
from cmba_workbench.model import Workbench
ROOT=Path(__file__).resolve().parents[1]


def request(op,args):return {'schema':'cmba.request.v0.1-i1','operation':op,'arguments':args}

@pytest.mark.parametrize('op',['execute','publish','install','sign','load-plugin','fetch','eval','__import__','delete','advance-pin'])
def test_effect_operations_refuse(op):
    with pytest.raises(Refusal,match='CMBA_OPERATION_UNSUPPORTED'):dispatch(request(op,{}))

def test_unknown_request_field_cannot_select_code():
    r=request('catalogue',{});r['handler']='os.system'
    with pytest.raises(Refusal,match='CMBA_FIELDS_INVALID'):dispatch(r)

def test_abi_evaluation_and_replay():
    b=chc();args={k:b[k] for k in ('binding','values','context')}
    receipt=dispatch(request('evaluate',args))
    assert dispatch(request('replay',{'receipt':receipt,**args}))['authority_effect']=='NONE'

def test_no_ambient_import_of_dkn():
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
    p=subprocess.run([sys.executable,'-c',"import sys; import cmba_core; import cmba_core.evaluation; assert not any(k.startswith('dkn') for k in sys.modules)"],env=env,capture_output=True)
    assert p.returncode==0,p.stderr

def test_dkn_missing_dependency_is_typed():
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
    code="from cmba_core.profiles.dkn import load_native; from cmba_core import Refusal\ntry: load_native()\nexcept Refusal as e: assert e.code=='CMBA_DKN_DEPENDENCY_UNAVAILABLE'\nelse: raise AssertionError('unexpected native module')"
    p=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True)
    assert p.returncode==0,p.stderr

@pytest.mark.parametrize('op', ['catalogue','capabilities'])
def test_data_requests(op):
    r=dispatch(request(op,{}));assert type(r) is dict;canonical(r)

def test_workbench_requires_explicit_context():
    w=Workbench();w.load(chc())
    with pytest.raises(Refusal,match='CMBA_READER_CONTEXT_REQUIRED'):w.evaluate()
    r=w.evaluate(accept_document_context=True)
    assert r['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    assert w.replay()['status']=='MATCH_EXACT_EVALUATION_REPLAY'

def test_workbench_external_context_pins_winner():
    w=Workbench();b=chc();w.load(b);ctx=b['context'];ctx['expected_binding_root']='0'*64
    with pytest.raises(Refusal,match='CMBA_EXPECTED_ROOT_MISMATCH'):w.evaluate(reader_context=ctx)

def test_workbench_bad_load_clears_prior_selection():
    w=Workbench();w.load(chc())
    with pytest.raises(Refusal):w.load({})
    with pytest.raises(Refusal,match='CMBA_NO_SELECTION'):w.inspect()

def test_workbench_failed_evaluation_clears_receipt():
    w=Workbench();w.load(chc());w.evaluate(accept_document_context=True)
    with pytest.raises(Refusal):w.evaluate()
    with pytest.raises(Refusal,match='CMBA_NO_RECEIPT'):w.replay()

def test_workbench_caller_mutation_isolated():
    w=Workbench();b=session();w.load(b);b['values']['source']['text']='changed'
    assert w.evaluate(accept_document_context=True)['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'

def test_catalogue_complete_relative_to_table():
    c=catalogue();rows=[e for e in c['entries'] if e['kind']=='SOURCE_DOMAIN_INVENTORY']
    assert len(rows)==52 and len({r['sector'] for r in rows})==8
    assert all(not r['callable'] and r['implementation']=='CATALOGUE_ONLY' for r in rows)
    lines=(ROOT/'sources/CMBA_Framework_Whitepaper.md').read_text(encoding='utf-8').splitlines()
    for r in rows:
        assert r['label'] in lines[r['source']['line_start']-1]
        assert r['source_use_case'] in lines[r['source']['line_start']-1]

def test_catalogue_snapshot_matches_runtime():
    assert canonical(json.loads((ROOT/'catalogue/APPLICATIONS.json').read_text(encoding='utf-8')))==canonical(catalogue())

def test_sensitive_domains_stay_descriptive():
    rows=[r for r in catalogue()['entries'] if r['label'] in ('CMBA-Military','CMBA-Weapons','CMBA-Nuclear')]
    assert len(rows)==3 and all(r['planned_scope']=='DESCRIPTIVE_RECORD_ONLY_NO_OPERATIONAL_CONTROL' for r in rows)

def test_capability_registry_no_effects():
    caps=capability_descriptors();assert len(caps)==4
    assert all(c['effect_class']=='PURE_READ' and not c['network'] and not c['auto_install'] for c in caps)

def test_cli_canonical_and_typed_failure(tmp_path):
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
    p=tmp_path/'request.json';p.write_bytes(canonical(request('capabilities',{})))
    good=subprocess.run([sys.executable,'-m','cmba_core.cli',str(p)],capture_output=True,env=env)
    assert good.returncode==0 and decode(good.stdout[:-1])['authority_effect']=='NONE'
    bad=subprocess.run([sys.executable,'-m','cmba_core.cli','-'],input=b'null',capture_output=True,env=env)
    assert bad.returncode==2 and decode(bad.stdout[:-1])['status']=='REFUSED'

def test_cli_cannot_turn_nonregular_file_into_payload(tmp_path):
    expected='CMBA_INPUT_IO' if os.name=='nt' else 'CMBA_INPUT_KIND'
    with pytest.raises(Refusal,match=expected):read_local(str(tmp_path))

def test_cli_refuses_symlink(tmp_path,make_link):
    target=tmp_path/'target';target.write_text('{}');link=make_link(tmp_path/'link',target)
    with pytest.raises(Refusal,match='CMBA_INPUT_SYMLINK'):read_local(str(link))

def test_cli_refuses_missing_file(tmp_path):
    with pytest.raises(Refusal,match='CMBA_INPUT_IO'):read_local(str(tmp_path/'missing'))
