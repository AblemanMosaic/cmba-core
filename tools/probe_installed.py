"""Execute with an explicitly selected installed interpreter, outside source.

No sys.path editing, network access, or dependency installation is performed.
"""
from pathlib import Path
import argparse,hashlib,importlib.metadata,importlib.util,json,os,subprocess,sys,zipfile


def main():
    p=argparse.ArgumentParser();p.add_argument('--wheel',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--with-dkn',action='store_true');a=p.parse_args()
    import cmba_core
    from cmba_core import canonical,decode,Refusal
    from cmba_core.demo import chc,session
    from cmba_core.evaluation import context_for,evaluate,replay
    from cmba_core.profiles.dkn import load_native,bind_archive
    base=Path(cmba_core.__file__).resolve().parent.parent
    assert base.is_relative_to(Path(sys.prefix).resolve()),'NOT_INSTALLED_IN_SELECTED_ENVIRONMENT'
    tests=[]
    for name,bundle,expected in [('chc-match',chc(),'MATCH_FOR_SUPPLIED_EVIDENCE'),
        ('chc-incorrect',chc(wrong_output=True),'CONTRADICTED'),('session',session(),'MATCH_FOR_SUPPLIED_EVIDENCE')]:
        r=evaluate(bundle['binding'],bundle['values'],bundle['context'])
        assert r['body']['result']['status']==expected
        assert replay(r,bundle['binding'],bundle['values'],bundle['context'])['status']=='MATCH_EXACT_EVALUATION_REPLAY'
        tests.append({'name':name,'result':expected})
    request={'schema':'cmba.request.v0.1-i1','operation':'capabilities','arguments':{}}
    exe=Path(sys.executable).parent/('cmba.exe' if os.name=='nt' else 'cmba')
    run=subprocess.run([str(exe),'-'],input=canonical(request),capture_output=True,timeout=20)
    assert run.returncode==0 and decode(run.stdout.rstrip(b'\n'))['authority_effect']=='NONE'
    tests.append({'name':'installed-cli','result':'PASS'})
    gui=Path(sys.executable).parent/('cmba-workbench.exe' if os.name=='nt' else 'cmba-workbench')
    assert gui.is_file()
    if a.with_dkn:
        native=load_native()
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        archive,manifest=native.pack({'note.txt':b'installed DKN bridge'})
        cert=native.certify(manifest,Ed25519PrivateKey.generate())
        b=bind_archive(archive,expected_logical_root=manifest['logical_root'],certificate=cert)
        assert b['certificate_report']['signature']=='PASS'
        assert b['certificate_report']['authorization']=='NOT_CHECKED'
        r=evaluate(b['binding'],b['values'],context_for(b['binding'],epoch=100))
        assert r['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
        tests.append({'name':'installed-dkn-certificate-and-wrapper','result':'PASS'})
    else:
        assert importlib.util.find_spec('dkn_v02') is None
        assert importlib.util.find_spec('cryptography') is None
        try:load_native()
        except Refusal as e:assert e.code=='CMBA_DKN_DEPENDENCY_UNAVAILABLE'
        else:raise AssertionError('OPTIONAL_DEPENDENCY_WAS_NOT_REFUSED')
        tests.append({'name':'stdlib-only-core-without-dkn','result':'PASS'})
    compared=0
    with zipfile.ZipFile(a.wheel) as z:
        for name in z.namelist():
            if name.startswith(('cmba_core/','cmba_workbench/')) and not name.endswith('/'):
                assert (base/name).read_bytes()==z.read(name),name;compared+=1
    r={'schema':'cmba.installed-probe.i1','status':'PASS_OUTSIDE_SOURCE_TREE','python':sys.version.split()[0],
       'prefix':sys.prefix,'installed_source':str(cmba_core.__file__),'package_files_compared':compared,
       'wheel_sha256':hashlib.sha256(a.wheel.read_bytes()).hexdigest(),'checks':tests,
       'dependency_source':'HOST_PREINSTALLED_OPTIONAL_DEPENDENCIES' if a.with_dkn else 'STDLIB_ONLY_CORE',
       'fresh_dependency_resolution':'NOT_ESTABLISHED' if a.with_dkn else 'NO_THIRD_PARTY_RUNTIME_DEPENDENCIES',
       'authority_effect':'NONE','gui_launch':'TESTED_SEPARATELY'}
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(json.dumps(r,sort_keys=True))
if __name__=='__main__':main()
