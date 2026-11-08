"""Post-L process qualification regressions. No runtime or conformance oracle changes."""
from pathlib import Path
import json,sys,zipfile,copy,os
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import qualification_integrity_r001 as q
import verify_l

def record():
    return {'schema':'cmba.qualification-stage.l1','phase':'tests','status':'PASS',
      'context':{'root':'accepted'},'results':{'tests':{'passed':1}},
      'legs':[{'name':'collect','exit_code':0},{'name':'tests','exit_code':0}],
      'outputs':{'test.log':'0'*64},'authority_effect':'NONE'}

@pytest.mark.parametrize('field,value',[
 ('schema','foreign.success.v99'),('schema',None),('authority_effect','EXECUTE'),
 ('authority_effect',False),('phase','audit'),('status','FAIL'),('status',True),
 ('context',[]),('results',None),('outputs',{}),('outputs',[]),('legs',[]),
 ('legs',[None]),('legs',[{'name':'tests','exit_code':False}]),
 ('legs',[{'name':'tests','exit_code':0.0}]),('legs',[{'name':'tests','exit_code':2}]),
 ('legs',[{'name':'tests','exit_code':0,'extra':True}])])
def test_strict_stage_header(field,value):
    r=record();r[field]=value
    with pytest.raises(ValueError):q.validate_stage_header(r,'tests')

@pytest.mark.parametrize('field',['schema','authority_effect','context','results','legs','outputs'])
def test_stage_missing_field(field):
    r=record();del r[field]
    with pytest.raises(ValueError):q.validate_stage_header(r,'tests')

def test_stage_unknown_field():
    r=record();r['approval']='GRANTED'
    with pytest.raises(ValueError):q.validate_stage_header(r,'tests')

@pytest.mark.parametrize('phase',['tests','workflows','audit','collect','group0','group1','group2','group3'])
def test_valid_stage_schemas(phase):
    r=record();r['phase']=phase
    if phase.startswith('group') or phase=='collect':r['schema']='cmba.native-stage.l1'
    q.validate_stage_header(r,phase)

def test_native_schema_cannot_be_qualification_schema():
    r=record();r['phase']='collect'
    with pytest.raises(ValueError):q.validate_stage_header(r,'collect')

def test_native_blocked_stage_accepts_bounded_terminal_exit_only_when_explicit():
    r=record();r.update(schema='cmba.native-stage.l1',phase='group0',status='BLOCKED')
    r['legs']=[{'name':'group0','exit_code':1}]
    q.validate_stage_header(r,'group0',allow_blocked=True)
    with pytest.raises(ValueError):q.validate_stage_header(r,'group0')
    r['legs'][0]['exit_code']=2
    with pytest.raises(ValueError):q.validate_stage_header(r,'group0',allow_blocked=True)

@pytest.mark.parametrize('raw',[
 b'{"status":"FAIL","status":"PASS"}',
 b'{"nested":{"count":0,"count":911}}',
 b'{"n":NaN}',b'{"n":Infinity}',b'{"n":1.0}'
])
def test_ambiguous_evidence_json_refused(tmp_path,raw):
    p=tmp_path/'record.json';p.write_bytes(raw)
    with pytest.raises(ValueError):q.read_record(p)

def test_evidence_read_only(tmp_path):
    p=tmp_path/'record.json';raw=json.dumps(record(),indent=2).encode();p.write_bytes(raw)
    assert q.read_record(p)==record();assert p.read_bytes()==raw

def test_oversized_evidence_refused(tmp_path,monkeypatch):
    monkeypatch.setattr(q,'MAX_RECORD_BYTES',10);p=tmp_path/'record.json';p.write_bytes(b' '*11)
    with pytest.raises(ValueError,match='LIMIT'):q.read_record(p)

def tree(tmp_path):
    root=tmp_path/'native';(root/'src').mkdir(parents=True);(root/'src/native.py').write_text('x=1\n')
    archive=tmp_path/'frozen.zip'
    with zipfile.ZipFile(archive,'w') as z:z.write(root/'src/native.py','src/native.py')
    return root,archive

@pytest.mark.parametrize('path',['conftest.py','pytest.ini','tests_v02/conftest.py','sitecustomize.py','extra.txt'])
def test_added_native_material_refused_before_collection(tmp_path,path):
    root,archive=tree(tmp_path);p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('# not in frozen source\n')
    with pytest.raises(ValueError,match='TREE_CLOSURE'):q.closed_native_tree(root,archive)

def test_native_missing_file_refused(tmp_path):
    root,archive=tree(tmp_path);(root/'src/native.py').unlink()
    with pytest.raises(ValueError,match='TREE_CLOSURE'):q.closed_native_tree(root,archive)

def test_generated_caches_explicitly_excluded(tmp_path):
    root,archive=tree(tmp_path);(root/'src/__pycache__').mkdir();(root/'src/__pycache__/native.cpython-313.pyc').write_bytes(b'cache')
    (root/'.pytest_cache').mkdir();(root/'.pytest_cache/README.md').write_text('cache')
    assert q.closed_native_tree(root,archive)['members']==1

@pytest.mark.parametrize('path',['src/__pycache__/conftest.py','.pytest_cache/plugin.py'])
def test_source_disguised_as_cache_refused(tmp_path,path):
    root,archive=tree(tmp_path);p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('x=1')
    with pytest.raises(ValueError,match='CACHE_KIND'):q.closed_native_tree(root,archive)

def test_native_link_refused(tmp_path,make_link):
    root,archive=tree(tmp_path);make_link(root/'link',root/'src',target_is_directory=True)
    with pytest.raises(ValueError,match='LINK'):q.closed_native_tree(root,archive)

@pytest.mark.parametrize('name',['conftest.py','pytest.ini','tox.ini','setup.cfg'])
def test_root_hook_configuration_is_fingerprinted(tmp_path,name):
    before=q.root_test_configuration(tmp_path);(tmp_path/name).write_text('extra config')
    after=q.root_test_configuration(tmp_path);assert before[name] is None;assert after[name] is not None

@pytest.mark.parametrize('name',['PYTEST_ADDOPTS','PYTEST_PLUGINS','PYTEST_CURRENT_TEST','PYTEST_DEBUG'])
def test_ambient_pytest_overrides_removed(monkeypatch,name):
    monkeypatch.setenv(name,'unapproved');env=q.test_environment(['/chosen/src'])
    assert name not in env;assert env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']=='1'
    assert env['PYTHONDONTWRITEBYTECODE']=='1';assert env['PYTHONUTF8']=='1'
    assert env['PYTHONPATH']=='/chosen/src'

def test_handoff_is_not_native_registration():
    from cmba_workbench.k1.views import handoff
    from cmba_core.demo import chc
    r=handoff('pippi',chc())['body']
    assert r['operational_integration']=='NOT_ESTABLISHED'
    assert r['included_material']=='REFERENCES_ONLY'
    assert r['decision']=='EXTERNAL_DECISION_REQUIRED'
    assert r['authority_effect']=='NONE'
