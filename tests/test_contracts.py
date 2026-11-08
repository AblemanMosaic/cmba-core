from pathlib import Path
import json,copy,sys
import pytest
from jsonschema import Draft202012Validator
from cmba_core import canonical,decode,Refusal
from cmba_core.demo import chc,session
from cmba_core.evaluation import evaluate
from cmba_core.registry import contracts,capability_descriptors
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from reference_conformance import dispatch
from run_conformance import compare_output,run
from export_schemas import build
CORPUS=decode((ROOT/'interop/core-i1.json').read_bytes())

@pytest.mark.parametrize('case',CORPUS['cases'],ids=lambda c:c['id'])
def test_frozen_core_corpus(case):
    assert canonical(dispatch(case['request']))==canonical(case['expected'])

@pytest.mark.parametrize('name',sorted(build()))
def test_schema_export_exact(name):
    current=json.loads((ROOT/'schemas'/f'{name}.schema.json').read_text(encoding='utf-8'))
    assert current==build()[name]
    Draft202012Validator.check_schema(current)

def test_real_objects_satisfy_exported_schemas():
    b=chc();r=evaluate(b['binding'],b['values'],b['context'])
    pairs=[('binding',b['binding']),('bundle',b),('context',b['context']),('receipt',r),('result',r['body']['result'])]
    pairs += [('profile-contract',c) for c in contracts()]
    pairs += [('capability',c) for c in capability_descriptors()]
    for name,value in pairs:Draft202012Validator(build()[name]).validate(value)

def test_schema_not_cryptographic_verification():
    b=chc()['binding'];b['binding_root']='0'*64
    Draft202012Validator(build()['binding']).validate(b)
    from cmba_core import inspect
    with pytest.raises(Refusal):inspect(b)

@pytest.mark.parametrize('value',[None,1,0,{'status':1},[],{'wrong':False}])
def test_conformance_oracle_refuses_bad_envelopes(value):
    with pytest.raises(Refusal):compare_output(canonical(value),{'status':True})

def test_conformance_oracle_bool_int_exact():
    with pytest.raises(Refusal,match='CMBA_CONFORMANCE_MISMATCH'):compare_output(b'{"status":1}',{'status':True})
    with pytest.raises(Refusal,match='CMBA_NOT_CANONICAL'):compare_output(b'{ "status": true }',{'status':True})

def test_external_reference_process_runs():
    assert run()['status']=='PASS'
