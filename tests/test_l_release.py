"""Qualification-tool security regressions, not new protocol features."""
from pathlib import Path
import hashlib,json,stat,sys,zipfile,copy
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import package,verify_l,verify_native_l

def archive(path,entries=None,*,names=None,kind=stat.S_IFREG,size=None,manifest_mutation=None):
    entries=entries or {'payload.txt':b'x'}
    rows=[{'path':p,'bytes':len(v) if size is None else size,'sha256':hashlib.sha256(v).hexdigest()} for p,v in entries.items()]
    m={'schema':'cmba.source-inventory.i1','scope':'ALL_MEMBERS_EXCEPT_THIS_MANIFEST','files':rows,
       'baseline_dkn_sha256':package.BASELINE,'authority_effect':'NONE','signature':'NOT_SIGNED'}
    if manifest_mutation:manifest_mutation(m)
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as z:
        for name,data in [*entries.items(),('FILE-MANIFEST.json',json.dumps(m).encode())]:
            i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.create_system=3;i.external_attr=((kind if name!='FILE-MANIFEST.json' else stat.S_IFREG)|0o644)<<16;z.writestr(i,data)
    return path

@pytest.mark.parametrize('name',['a//b','a/./b','a/../b','/absolute','a\\b','drive:name','CON.txt','a.','a ','a/','\x00name','a\nname'])
def test_archive_nonportable_paths_refused(tmp_path,name):
    # NUL filenames are truncated by zipfile itself, so validate the original path directly.
    if '\0' in name:
        with pytest.raises(ValueError,match='ARCHIVE_PATH'):package.safe_name(name)
        return
    with pytest.raises(ValueError):package.verify(archive(tmp_path/'bad.zip',{name:b'x'}))

@pytest.mark.parametrize('entries',[{'A':b'x','a':b'y'},{'a':b'x','a/b':b'y'},{'e\u0301.txt':b'x'}])
def test_archive_alias_and_prefix_refused(tmp_path,entries):
    with pytest.raises(ValueError):package.verify(archive(tmp_path/'bad.zip',entries))

@pytest.mark.parametrize('kind',[stat.S_IFLNK,stat.S_IFIFO,stat.S_IFDIR,0])
def test_archive_nonregular_members_refused(tmp_path,kind):
    with pytest.raises(ValueError,match='MEMBER_KIND'):package.verify(archive(tmp_path/'bad.zip',kind=kind))

@pytest.mark.parametrize('size',[True,False,1.0,'1',None,-1])
def test_manifest_size_is_exact_integer(tmp_path,size):
    if size is None:
        p=archive(tmp_path/'bad.zip',manifest_mutation=lambda m:m['files'][0].update(bytes=None))
    else:p=archive(tmp_path/'bad.zip',size=size)
    with pytest.raises(ValueError):package.verify(p)

@pytest.mark.parametrize('field,value',[('authority_effect','EXECUTE'),('scope','PARTIAL'),('signature','VERIFIED'),('schema','unknown'),('baseline_dkn_sha256','0'*64)])
def test_manifest_claim_fields_strict(tmp_path,field,value):
    p=archive(tmp_path/'bad.zip',manifest_mutation=lambda m:m.update({field:value}))
    with pytest.raises(ValueError,match='MANIFEST_FIELDS'):package.verify(p)

def test_manifest_duplicate_field_rejected():
    with pytest.raises(ValueError,match='DUPLICATE_FIELD'):package.strict_json(b'{"files":[],"files":[]}')

def test_valid_current_source_profile(tmp_path):
    assert package.verify(archive(tmp_path/'ok.zip'))['members']==2

def test_manifest_rows_use_platform_neutral_relative_name_order(tmp_path):
    root=tmp_path/'source';root.mkdir();(root/'z.txt').write_text('z');(root/'A.txt').write_text('a')
    package.build(tmp_path/'out.zip',root)
    manifest=json.loads((root/'FILE-MANIFEST.json').read_text())
    assert [r['path'] for r in manifest['files']]==['A.txt','z.txt']

def test_unsorted_manifest_rows_refused(tmp_path):
    with pytest.raises(ValueError,match='MANIFEST_ORDER'):
        package.verify(archive(tmp_path/'bad.zip',{'z.txt':b'z','a.txt':b'a'}))

def test_package_does_not_collect_fifo(tmp_path,monkeypatch):
    import os
    root=tmp_path/'source';root.mkdir();pipe=root/'pipe'
    if hasattr(os,'mkfifo'):os.mkfifo(pipe)
    else:
        pipe.write_bytes(b'fixture');real=Path.stat
        def synthetic(self,*args,**kwargs):
            value=real(self,*args,**kwargs)
            if self==pipe:
                fields=list(value);fields[0]=stat.S_IFIFO|0o600;return os.stat_result(fields)
            return value
        monkeypatch.setattr(Path,'stat',synthetic)
    with pytest.raises(ValueError,match='PACKAGE_FILE_KIND'):package.build(tmp_path/'out.zip',root)

def stage(out):
    root=out/'tests';root.mkdir();(root/'log').write_bytes(b'actual')
    r={'schema':'cmba.qualification-stage.l1','authority_effect':'NONE','results':{},'phase':'tests','status':'PASS','context':{'source':'pinned','require_legacy':False},
       'outputs':{'log':verify_l.sha(b'actual')},'legs':[{'name':'collect','exit_code':0},{'name':'tests','exit_code':0}]}
    (root/'STAGE.json').write_text(json.dumps(r));return root,r

@pytest.mark.parametrize('mutation',['extra-dir','extra-file','missing','modified','symlink','wrong-source','bool-int-context','fail','wrong-phase'])
def test_stage_closed_typed_context_and_outputs(tmp_path,mutation,make_link):
    root,r=stage(tmp_path);context=copy.deepcopy(r['context'])
    if mutation=='extra-dir':(root/'untracked').mkdir()
    elif mutation=='extra-file':(root/'untracked').write_text('x')
    elif mutation=='missing':(root/'log').unlink()
    elif mutation=='modified':(root/'log').write_text('forged')
    elif mutation=='symlink':
        (root/'log').unlink();real=tmp_path/'real';real.mkdir();make_link(root/'log',real,target_is_directory=True)
    elif mutation=='wrong-source':r['context']['source']='other'
    elif mutation=='bool-int-context':r['context']['require_legacy']=0
    elif mutation=='fail':r['status']='FAIL'
    else:r['phase']='audit'
    (root/'STAGE.json').write_text(json.dumps(r))
    with pytest.raises(ValueError):verify_l.stage_read(tmp_path,'tests',context)

@pytest.mark.parametrize('legs',[[],[{'name':'collect','exit_code':0}],
    [{'name':'collect','exit_code':False},{'name':'tests','exit_code':0}],
    [{'name':'tests','exit_code':0},{'name':'collect','exit_code':0}],
    [{'name':'collect','exit_code':0},{'name':'tests','exit_code':2}]])
def test_required_completed_legs(legs):
    with pytest.raises(ValueError):verify_l.validate_legs({'legs':legs},['collect','tests'])

@pytest.mark.parametrize('field,value',[('cases',True),('cases',0),('cases',32),('status','FAIL'),('oracle','PYTHON_EQUALITY'),('authority_effect','EXECUTE')])
def test_conformance_receipt_cannot_promote_missing_work(field,value):
    report={'status':'PASS','cases':33,'oracle':'EXACT_CANONICAL_RESPONSE_BYTES','authority_effect':'NONE'};report[field]=value
    with pytest.raises(ValueError):verify_l.validate_conformance(report,33)

def legacy_xml(*,skipped=None,identities=None,declared=33):
    _,expected=verify_l.legacy_contract();identities=expected if identities is None else identities
    rows=[]
    for classname,name in identities:
        child='<skipped message="synthetic"/>' if (classname,name)==skipped else ''
        rows.append(f'<testcase classname="{classname}" name="{name}">{child}</testcase>')
    return f'<testsuites><testsuite tests="{declared}" errors="0" failures="0" skipped="{1 if skipped else 0}">{"".join(rows)}</testsuite></testsuites>'

def test_legacy_pytest9_exact_identities_and_subtests_are_bounded(tmp_path):
    path=tmp_path/'legacy.xml'
    path.write_text(legacy_xml(),encoding='utf-8')
    counts,declared=verify_l.legacy_test_summary(path)
    assert counts['passed']==28 and declared==33
    path.write_text(legacy_xml(declared=34),encoding='utf-8')
    with pytest.raises(ValueError,match='L_LEGACY_TEST_COUNT'):verify_l.legacy_test_summary(path)
    synthetic=[('legacy.C',f'test_{i}') for i in range(28)]
    path.write_text(legacy_xml(identities=synthetic),encoding='utf-8')
    with pytest.raises(ValueError,match='L_LEGACY_TEST_IDENTITY'):verify_l.legacy_test_summary(path)

def test_required_legacy_refuses_before_subprocess_when_source_not_admitted(tmp_path,monkeypatch):
    launched=[]
    def refuse(_):raise ValueError('AUDIT_NATIVE_TREE_CLOSURE')
    monkeypatch.setattr(verify_l,'native_inventory',refuse)
    monkeypatch.setattr(verify_l.subprocess,'run',lambda *a,**k:launched.append((a,k)))
    with pytest.raises(ValueError,match='AUDIT_NATIVE_TREE_CLOSURE'):
        verify_l.run_phase(tmp_path/'out',tmp_path/'native','tests',True)
    assert launched==[]

@pytest.mark.parametrize('value',[None,{}, {'exit_code':False,'terminal':'PASS'},
    {'exit_code':1,'terminal':'PASS'},{'exit_code':0,'terminal':'FAIL'},
    {'exit_code':0,'terminal':'PASS','extra':True}])
def test_legacy_terminal_is_exact(value):
    with pytest.raises(ValueError,match='L_LEGACY_TERMINAL'):
        verify_l.legacy_terminal({'legacy_runtime':value})
    assert verify_l.legacy_terminal({'legacy_runtime':{'exit_code':0,'terminal':'PASS'}})==0

def test_native_platform_coverage_classifies_only_exact_declared_skip(tmp_path,monkeypatch):
    path=tmp_path/'native.xml';ident=('tests_v02.test_batch_e_integration','test_optional_legacy_dependency_explicit')
    path.write_text('<testsuites><testsuite tests="1" failures="0" errors="0" skipped="1">'
        f'<testcase classname="{ident[0]}" name="{ident[1]}"><skipped message="missing-dependency branch only"/></testcase>'
        '</testsuite></testsuites>')
    monkeypatch.setattr(verify_native_l.importlib.util,'find_spec',lambda name:object() if name=='blake3' else None)
    counts,coverage=verify_native_l.native_test_summary(path)
    assert counts=={'passed':0,'not_applicable':1,'blocked':0,'total':1}
    assert coverage[0]['disposition']=='NOT_APPLICABLE'
    path.write_text('<testsuites><testsuite tests="1" failures="0" errors="0" skipped="1">'
        '<testcase classname="unknown.C" name="test_x"><skipped message="anything"/></testcase>'
        '</testsuite></testsuites>')
    counts,coverage=verify_native_l.native_test_summary(path)
    assert counts=={'passed':0,'not_applicable':0,'blocked':1,'total':1}
    assert coverage[0]['disposition']=='BLOCKED'

def test_native_platform_coverage_classifies_only_exact_declared_windows_blocker(tmp_path,monkeypatch):
    path=tmp_path/'native.xml'
    ident=('tests_v02.test_review_rc2','test_empty_source_symlink_ancestor_refused')
    message='OSError: [WinError 1314] A required privilege is not held by the client: synthetic'
    path.write_text('<testsuites><testsuite tests="1" failures="1" errors="0" skipped="0">'
        f'<testcase classname="{ident[0]}" name="{ident[1]}"><failure message="{message}"/></testcase>'
        '</testsuite></testsuites>')
    monkeypatch.setattr(verify_native_l.os,'name','nt')
    counts,coverage=verify_native_l.native_test_summary(path)
    assert counts=={'passed':0,'not_applicable':0,'blocked':1,'total':1}
    assert coverage[0]['disposition']=='BLOCKED'

def test_readonly_stage_does_not_author_models(tmp_path):
    _,r=stage(tmp_path);before=(tmp_path/'tests/STAGE.json').read_bytes()
    assert verify_l.stage_read(tmp_path,'tests',r['context'])==r
    assert before==(tmp_path/'tests/STAGE.json').read_bytes()

@pytest.mark.parametrize('mutation',['root','claim','size-bool','self','duplicate'])
def test_release_envelope_refuses_claim_or_identity_laundering(tmp_path,mutation):
    import release_envelope_a6 as e
    from cmba_core import canonical
    data=tmp_path/'artifact.bin';data.write_bytes(b'x');out=tmp_path/'envelope.json'
    v=e.build([data],out)
    if mutation=='root':v['binding_root']='0'*64
    elif mutation=='claim':v['body']['public_release_gate']='CLEARED';v['binding_root']=e.root(v['body'])
    elif mutation=='size-bool':v['body']['artifacts'][0]['bytes']=True;v['binding_root']=e.root(v['body'])
    elif mutation=='self':v['body']['artifacts'][0]['name']=out.name;v['binding_root']=e.root(v['body'])
    else:v['body']['artifacts']*=2;v['binding_root']=e.root(v['body'])
    out.write_bytes(canonical(v))
    with pytest.raises(ValueError):e.verify(out,tmp_path)
