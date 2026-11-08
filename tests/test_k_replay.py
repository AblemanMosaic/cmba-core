from pathlib import Path
import json,sys,copy
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import verify_k

def make_stage(out):
    root=out/'tests';root.mkdir();(root/'a.log').write_bytes(b'actual output')
    r={'phase':'tests','status':'PASS','context':{'source':'x'},'outputs':{'a.log':verify_k.sha(b'actual output')}}
    (root/'STAGE.json').write_text(json.dumps(r));return root,r

def test_stage_exact_context_and_output(tmp_path):
    root,r=make_stage(tmp_path)
    assert verify_k.stage_read(tmp_path,'tests',{'source':'x'})==r
    with pytest.raises(ValueError):verify_k.stage_read(tmp_path,'tests',{'source':'other'})
    (root/'a.log').write_bytes(b'forged')
    with pytest.raises(ValueError):verify_k.stage_read(tmp_path,'tests',{'source':'x'})

@pytest.mark.parametrize('change',['extra','missing','failed','phase','empty','unsafe'])
def test_incomplete_or_changed_stage_refuses(tmp_path,change):
    root,r=make_stage(tmp_path)
    if change=='extra':(root/'extra.log').write_bytes(b'unknown')
    if change=='missing':(root/'a.log').unlink()
    if change=='failed':r['status']='FAIL'
    if change=='phase':r['phase']='workflows'
    if change=='empty':r['outputs']={}
    if change=='unsafe':r['outputs']={'../outside':verify_k.sha(b'actual output')}
    (root/'STAGE.json').write_text(json.dumps(r))
    with pytest.raises(ValueError):verify_k.stage_read(tmp_path,'tests',{'source':'x'})

def test_collection_identity_preserves_parametrized_names_and_types():
    raw=b'tests/test_a.py::test_a[true]\ntests/test_a.py::TestClass::test_a[1]\n2 tests collected\n'
    assert verify_k.identities(raw)=={('tests.test_a','test_a[true]'),('tests.test_a.TestClass','test_a[1]')}
    with pytest.raises(ValueError):verify_k.identities(b'0 tests collected')
    with pytest.raises(ValueError):verify_k.identities(b'tests/test_a.py::test_a\ntests/test_a.py::test_a\n')
