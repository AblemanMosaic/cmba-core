import os,stat,hashlib,threading
from pathlib import Path
from copy import deepcopy as cp
import pytest
from cmba_core import Refusal,canonical,decode
from cmba_workbench.k1.effects import LocalEffects,filename
from cmba_workbench.k1.authoring import author
from cmba_workbench.k1.session import Workspace

STATE='a'*64

def payload():return author('cmba.generic',{'hello':'world'})
def host(path,**kw):return LocalEffects(path,current_state=kw.pop('current_state',lambda:STATE),**kw)

def test_prepare_cancel_approve_commit_exact_and_no_overwrite(tmp_path):
    data=payload()
    with host(tmp_path) as h:
        p=h.prepare('bundle',data,name='out.json');assert list(tmp_path.iterdir())==[]
        h.cancel();assert list(tmp_path.iterdir())==[]
        with pytest.raises(Refusal):h.approve(p['plan_hash'])
        p=h.prepare('bundle',data,name='out.json');a=h.approve(p['plan_hash'])
        assert list(tmp_path.iterdir())==[]
        r=h.commit(a);assert r['status']=='LOCAL_FILE_CREATED_AND_READ_BACK'
        assert (tmp_path/'out.json').read_bytes()==canonical(data)
        assert r['output_sha256']==hashlib.sha256(canonical(data)).hexdigest()
        with pytest.raises(Refusal):h.commit(a)
        with pytest.raises(Refusal,match='OVERWRITE_REFUSED'):h.prepare('bundle',data,name='out.json')
    assert sorted(p.name for p in tmp_path.iterdir())==['out.json']

@pytest.mark.parametrize('name',['../evil.json','/tmp/evil.json','x\\y.json','https://x.json','x:ads.json','x .json',
 'nul.json','CON.JSON','con.any.json','com1.json','LPT9.json','aux.json','x..y.json','.hidden.json','foo.py','A.json/../B.json','🌈.json','a'*85+'.json','x\n.json','x.json '])
def test_path_names_refuse_before_any_write(tmp_path,name):
    with host(tmp_path) as h:
        with pytest.raises(Refusal):h.prepare('bundle',payload(),name=name)
    assert list(tmp_path.iterdir())==[]

@pytest.mark.parametrize('approved',[None,True,'yes',{'approved':True},{'token':'anything'}])
def test_serialized_data_cannot_approve(tmp_path,approved):
    with host(tmp_path) as h:
        h.prepare('bundle',payload(),name='out.json')
        with pytest.raises(Refusal,match='HOST_APPROVAL_REQUIRED'):h.commit(approved)
    assert list(tmp_path.iterdir())==[]


def test_cross_host_and_forged_preview_are_not_approval(tmp_path):
    with host(tmp_path) as a,host(tmp_path) as b:
        p=a.prepare('bundle',payload(),name='a.json');q=b.prepare('bundle',payload(),name='b.json')
        token=a.approve(p['plan_hash'])
        with pytest.raises(Refusal):b.commit(token)
        p['body']['target_name']='outside.json'
        result=a.commit(token)
        assert result['plan']['body']['target_name']=='a.json' and not (tmp_path/'outside.json').exists()


def test_expiry_and_input_substitution(tmp_path):
    now=[0];state=[STATE]
    with host(tmp_path,current_state=lambda:state[0],clock=lambda:now[0]) as h:
        p=h.prepare('bundle',payload(),name='a.json',ttl=2);now[0]=2
        with pytest.raises(Refusal,match='EXPIRED'):h.approve(p['plan_hash'])
        now[0]=0;p=h.prepare('bundle',payload(),name='a.json');a=h.approve(p['plan_hash']);state[0]='b'*64
        with pytest.raises(Refusal,match='INPUT_CHANGED'):h.commit(a)
    assert list(tmp_path.iterdir())==[]


def test_target_appearing_after_preview_preserved(tmp_path):
    with host(tmp_path) as h:
        p=h.prepare('bundle',payload(),name='out.json');a=h.approve(p['plan_hash'])
        (tmp_path/'out.json').write_bytes(b'other writer')
        with pytest.raises(Refusal,match='TARGET_CHANGED'):h.commit(a)
    assert (tmp_path/'out.json').read_bytes()==b'other writer'


def test_parent_replacement_refused(tmp_path):
    original=tmp_path/'original';original.mkdir()
    with host(original) as h:
        p=h.prepare('bundle',payload(),name='out.json');a=h.approve(p['plan_hash'])
        original.rename(tmp_path/'old');original.mkdir()
        with pytest.raises(Refusal,match='WORKSPACE_CHANGED'):h.commit(a)
    assert not list(original.iterdir()) and not list((tmp_path/'old').iterdir())


def test_symlink_workspace_or_target_refused(tmp_path,make_link):
    d=tmp_path/'dir';d.mkdir();link=make_link(tmp_path/'link',d,target_is_directory=True)
    with pytest.raises(Refusal,match='SYMLINK'):host(link)
    original=tmp_path/'original';original.mkdir()
    make_link(d/'out.json',original,target_is_directory=True)
    with host(d) as h:
        with pytest.raises(Refusal):h.prepare('bundle',payload(),name='out.json')
    assert not list(original.iterdir())


def test_link_failure_does_not_fallback_to_overwrite(tmp_path,monkeypatch):
    with host(tmp_path) as h:
        p=h.prepare('bundle',payload(),name='out.json');a=h.approve(p['plan_hash'])
        def fail(*_,**__):raise OSError('not supported')
        monkeypatch.setattr(os,'rename' if os.name=='nt' else 'link',fail)
        with pytest.raises(Refusal,match='UNSUPPORTED_FS'):h.commit(a)
    assert list(tmp_path.iterdir())==[]


def test_file_fsync_failure_cleans_staging_and_consumes_token(tmp_path,monkeypatch):
    with host(tmp_path) as h:
        p=h.prepare('bundle',payload(),name='out.json');a=h.approve(p['plan_hash'])
        def fail(*_):raise OSError('disk error')
        monkeypatch.setattr(os,'fsync',fail)
        with pytest.raises(Refusal):h.commit(a)
        with pytest.raises(Refusal):h.commit(a)
    assert list(tmp_path.iterdir())==[]


def test_input_changes_during_staging_never_commits(tmp_path,monkeypatch):
    state=[STATE];original=os.fsync
    with host(tmp_path,current_state=lambda:state[0]) as h:
        p=h.prepare('bundle',payload(),name='out.json');a=h.approve(p['plan_hash'])
        def change(fd):original(fd);state[0]='b'*64
        monkeypatch.setattr(os,'fsync',change)
        with pytest.raises(Refusal,match='INPUT_CHANGED'):h.commit(a)
    assert list(tmp_path.iterdir())==[]


def test_postcommit_directory_fsync_uncertainty_is_not_no_effect(tmp_path,monkeypatch):
    original=os.fsync;calls=[]
    with host(tmp_path) as h:
        p=h.prepare('bundle',payload(),name='out.json');a=h.approve(p['plan_hash'])
        def fail_second(fd):
            calls.append(fd)
            if len(calls)==2:raise OSError('directory durability unknown')
            original(fd)
        monkeypatch.setattr(os,'fsync',fail_second)
        r=h.commit(a)
        assert r['status']=='LOCAL_FILE_CREATED_AND_READ_BACK'
        if os.name=='nt':
            assert r['durability']=='FILE_FSYNC_COMPLETED_DIRECTORY_NOT_ESTABLISHED' and not r['warnings']
        else:assert 'DIRECTORY_FSYNC_FAILED' in r['warnings']
        assert (tmp_path/'out.json').exists()


def test_cooperating_writer_race_never_overwrites(tmp_path):
    barrier=threading.Barrier(2);results=[]
    def writer(number):
        with host(tmp_path) as h:
            value=author('cmba.generic',{'writer':number})
            p=h.prepare('bundle',value,name='shared.json');token=h.approve(p['plan_hash']);barrier.wait()
            try:results.append(('ok',number,h.commit(token)))
            except Refusal as e:results.append(('refused',number,e.code))
    a=threading.Thread(target=writer,args=(1,));b=threading.Thread(target=writer,args=(2,));a.start();b.start();a.join();b.join()
    assert sorted(x[0] for x in results)==['ok','refused']
    winner=next(x[1] for x in results if x[0]=='ok')
    assert decode((tmp_path/'shared.json').read_bytes())['values']['description']['writer']==winner
    assert len(list(tmp_path.iterdir()))==1


def test_workspace_selection_change_invalidates_plan(tmp_path):
    w=Workspace();w.load(payload())
    with host(tmp_path,current_state=w.state_binding) as h:
        p=h.prepare('bundle',w.selected(),name='out.json');a=h.approve(p['plan_hash'])
        w.use_demo_context()
        with pytest.raises(Refusal,match='INPUT_CHANGED'):h.commit(a)
    assert not list(tmp_path.iterdir())

@pytest.mark.parametrize('kind',['bundle','receipt','workspace','disclosure','design','handoff'])
def test_mislabeled_payload_never_reaches_write(tmp_path,kind):
    with host(tmp_path) as h:
        with pytest.raises(Refusal):h.prepare(kind,{'execute':'anything'},name='out.json')
    assert not list(tmp_path.iterdir())

@pytest.mark.parametrize('ttl',[0,-1,301,True,'30',None])
def test_invalid_expiry_refused(tmp_path,ttl):
    with host(tmp_path) as h:
        with pytest.raises(Refusal):h.prepare('bundle',payload(),name='out.json',ttl=ttl)
    assert not list(tmp_path.iterdir())


def test_expiry_during_staging_refuses_final_install(tmp_path,monkeypatch):
    now=[0];original=os.fsync
    with host(tmp_path,clock=lambda:now[0]) as h:
        p=h.prepare('bundle',payload(),name='out.json',ttl=2);a=h.approve(p['plan_hash'])
        def expire(fd):original(fd);now[0]=2
        monkeypatch.setattr(os,'fsync',expire)
        with pytest.raises(Refusal,match='EXPIRED'):h.commit(a)
    assert list(tmp_path.iterdir())==[]
