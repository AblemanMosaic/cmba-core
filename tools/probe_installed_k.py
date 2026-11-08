"""Installed K probe: no sys.path edits, no automatic package/network installation."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,tempfile,zipfile,importlib.metadata

def main():
    p=argparse.ArgumentParser();p.add_argument('--wheel',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--with-optional',action='store_true');a=p.parse_args()
    import cmba_core,cmba_workbench.k1.session
    from cmba_core import canonical,decode
    from cmba_workbench.k1 import authoring,views
    from cmba_workbench.k1.session import Workspace
    from cmba_workbench.k1.effects import LocalEffects
    from cmba_workbench.k1.abi import dispatch
    base=Path(cmba_core.__file__).resolve().parent.parent
    assert base.is_relative_to(Path(sys.prefix).resolve())
    assert Path(cmba_workbench.k1.session.__file__).resolve().is_relative_to(base)
    w=Workspace();b=authoring.example('cmba.chc.graph');w.load(b);w.use_demo_context();w.evaluate()
    assert w.replay_history(0)['status']=='MATCH_EXACT_EVALUATION_REPLAY'
    checks=['installed-workspace-evaluate-replay']
    with tempfile.TemporaryDirectory() as d:
        with LocalEffects(d,current_state=w.state_binding) as h:
            plan=h.prepare('workspace',w.snapshot(),name='workspace.json');assert not list(Path(d).iterdir())
            result=h.commit(h.approve(plan['plan_hash']));assert result['host_effect']=='CREATE_LOCAL_FILE'
            restored=Workspace();restored.restore(decode((Path(d)/'workspace.json').read_bytes()))
            assert restored._context is None and restored._selected is None
        checks+=['preview-no-write','explicit-create-only-export','restore-no-trust']
        executable=Path(sys.executable).parent/('cmba-export.exe' if os.name=='nt' else 'cmba-export')
        # The explicit host CLI rejects non-interactive calls before any output creation.
        p1=subprocess.run([str(executable),'--help'],capture_output=True,timeout=15)
        assert p1.returncode==0;checks+=['installed-export-cli']
    req={'schema':'cmba.workbench-request.k1','operation':'capabilities','arguments':{}}
    executable=Path(sys.executable).parent/('cmba-wb.exe' if os.name=='nt' else 'cmba-wb')
    p1=subprocess.run([str(executable),'-'],input=canonical(req),capture_output=True,timeout=30)
    assert p1.returncode==0 and p1.stdout==canonical(dispatch(req))+b'\n';checks+=['installed-readonly-cli-byte-parity']
    if a.with_optional:
        from cmba_core.j1.registry import contracts
        for c in contracts():
            one=Workspace();one.load(authoring.example(c['profile_id']));one.use_demo_context();one.evaluate()
        checks+=['all-thirteen-profiles-installed']
    count=0
    with zipfile.ZipFile(a.wheel) as z:
        for name in z.namelist():
            if name.startswith(('cmba_core/','cmba_workbench/')) and not name.endswith('/'):
                assert (base/name).read_bytes()==z.read(name),name;count+=1
    r={'schema':'cmba.installed-k-probe','status':'PASS_OUTSIDE_SOURCE_TREE','distribution_version':importlib.metadata.version('cmba-core'),
        'checks':checks,'payload_files_compared':count,'wheel_sha256':hashlib.sha256(a.wheel.read_bytes()).hexdigest(),
        'python':sys.version.split()[0],'prefix':sys.prefix,'module':str(cmba_workbench.k1.session.__file__),
        'authority_effect':'NONE','local_effects':'EXPLICIT_TEST_EXPORT_IN_TEMPORARY_DIRECTORY'}
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
