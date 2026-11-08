"""Explicit installed-wheel probe. No dependency installation/network/sys.path edits."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,zipfile,importlib.metadata

def main():
    p=argparse.ArgumentParser();p.add_argument('--wheel',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--with-optional',action='store_true');a=p.parse_args()
    import cmba_core
    from cmba_core import canonical,decode,Refusal
    from cmba_core.j1 import demo
    from cmba_core.j1.evaluation import evaluate,replay
    base=Path(cmba_core.__file__).resolve().parent.parent
    assert base.is_relative_to(Path(sys.prefix).resolve()),'SOURCE_IMPORT_NOT_INSTALLED'
    checks=[]
    for name,b in [('graph',demo.graph()),('session',demo.session()),('disclosure',demo.disclosure()),('reconciliation',demo.reconciliation()),('trace',demo.trace())]:
        r=evaluate(**b);assert r['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
        assert replay(r,**b)['status']=='MATCH_EXACT_EVALUATION_REPLAY';checks.append(name)
    request={'schema':'cmba.request.j1','operation':'capabilities','arguments':{}}
    executable=Path(sys.executable).parent/('cmba-app.exe' if os.name=='nt' else 'cmba-app')
    run=subprocess.run([str(executable),'-'],input=canonical(request),capture_output=True,timeout=30)
    assert run.returncode==0 and len(decode(run.stdout.rstrip(b'\n')))==13;checks.append('installed-j1-cli')
    if a.with_optional:
        for name,b in demo.all_bundles().items():
            r=demo.assess(b);assert r['body']['result']['status']==('NATIVE_REPORT_COMPUTED' if name=='cmba.native-dkn' else 'MATCH_FOR_SUPPLIED_EVIDENCE')
        d=demo.joint_workflow();assert d['authority_effect']=='NONE';checks+=['all-13-profiles','full-joint-workflow']
        from cmba_core.j1.endorsements import seal,verify
        s=seal('observation',{'probe':'installed'},demo.fixture_key(3));assert verify(s)['kind']=='observation';checks+=['installed-signature-roundtrip']
    else:
        assert importlib.util.find_spec('cryptography') is None
        assert importlib.util.find_spec('dkn_v02') is None
        from cmba_core.j1.endorsements import _backend
        try:_backend()
        except Refusal as e:assert 'DEPENDENCY' in e.code
        else:raise AssertionError('MISSING_OPTIONAL_NOT_REFUSED')
        checks+=['stdlib-only-core','missing-signing-dependency-typed-refusal']
    count=0
    with zipfile.ZipFile(a.wheel) as z:
        for name in z.namelist():
            if name.startswith(('cmba_core/','cmba_workbench/')) and not name.endswith('/'):
                assert (base/name).read_bytes()==z.read(name),name;count+=1
    r={'schema':'cmba.installed-j1-probe','status':'PASS_OUTSIDE_SOURCE_TREE','distribution_version':importlib.metadata.version('cmba-core'),
       'checks':checks,'payload_files_compared':count,'wheel_sha256':hashlib.sha256(a.wheel.read_bytes()).hexdigest(),
       'python':sys.version.split()[0],'prefix':sys.prefix,'import_path':str(cmba_core.__file__),
       'dependency_source':'COPIED_GENUINE_HOST_DISTRIBUTIONS' if a.with_optional else 'NO_THIRD_PARTY_RUNTIME_DEPENDENCIES',
       'fresh_dependency_resolution':'NOT_ESTABLISHED' if a.with_optional else 'NOT_NEEDED_FOR_CORE',
       'authority_effect':'NONE'}
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(json.dumps(r,sort_keys=True))
if __name__=='__main__':main()
