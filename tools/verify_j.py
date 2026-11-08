"""Source-bound Batch J replay. Verification NEVER authors models/corpora or installs packages."""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,xml.etree.ElementTree as ET,importlib.metadata,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
import verify_i,unpack_baseline,check_model,check_j_model,run_conformance,run_j_conformance


def sha(raw):return hashlib.sha256(raw).hexdigest()

def fingerprint():
    base=verify_i.fingerprint()
    extra={name:sha((ROOT/name).read_bytes()) for name in ('PROGRAM-LEDGER.json',)}
    return sha(json.dumps({'base':base,'extra':extra},sort_keys=True,separators=(',',':')).encode())

def test_summary(path):
    tree=ET.parse(path);cases=list(tree.iter('testcase'));seen=set()
    if not cases:raise ValueError('J_REPLAY_EMPTY_TEST_SUITE')
    for case in cases:
        ident=(case.get('classname'),case.get('name'))
        if not all(ident) or ident in seen:raise ValueError('J_REPLAY_TEST_IDENTITY')
        seen.add(ident)
        if any(c.tag in ('failure','error','skipped') for c in case):raise ValueError('J_REPLAY_TESTS_INCOMPLETE')
    suites=list(tree.iter('testsuite'))
    if not suites or sum(int(s.get('tests','0')) for s in suites)!=len(cases):raise ValueError('J_REPLAY_TEST_COUNT')
    if any(int(s.get(k,'0')) for s in suites for k in ('failures','errors','skipped')):raise ValueError('J_REPLAY_TESTS_INCOMPLETE')
    return {'passed':len(cases),'failed':0,'errors':0,'skipped':0},[{'classname':a,'name':b} for a,b in sorted(seen)]

def native_preservation(native):
    unpack_baseline.verify()
    source=next((ROOT/'baseline/dkn').glob('*BATCH-H-REVIEW-CANDIDATE.zip'))
    checked=0
    with zipfile.ZipFile(source) as z:
        expected={n for n in z.namelist() if n.startswith('src/') and n.endswith('.py')}
        actual={p.relative_to(native).as_posix() for p in (native/'src').rglob('*.py')}
        if actual!=expected:raise ValueError('J_REPLAY_NATIVE_SOURCE_CLOSURE')
        for name in sorted(expected):
            if (native/name).read_bytes()!=z.read(name):raise ValueError('J_REPLAY_NATIVE_SOURCE_MISMATCH:'+name)
            checked+=1
    return {'status':'PASS','runtime_files':checked,'source_sha256':sha(source.read_bytes())}

def run(out,native):
    out.mkdir(parents=True,exist_ok=True)
    if (out/'LOCAL-RUN.json').exists():raise ValueError('J_REPLAY_EXISTING_RECEIPT')
    before=fingerprint();native_report=native_preservation(native)
    env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(ROOT/'src'),str(native/'src')]);env['DKN_TEST_ROOT']=str(native);env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    legs=[]
    def step(name,command):
        try:p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,timeout=240)
        except subprocess.TimeoutExpired as e:
            (out/(name+'.stdout')).write_bytes(e.stdout or b'');(out/(name+'.stderr')).write_bytes(e.stderr or b'')
            raise ValueError('J_REPLAY_TIMEOUT:'+name) from e
        (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
        legs.append({'name':name,'exit_code':p.returncode,'stdout_sha256':sha(p.stdout),'stderr_sha256':sha(p.stderr)})
        if p.returncode:raise ValueError('J_REPLAY_LEG_FAILED:'+name)
    step('tests',[sys.executable,'-m','pytest','tests','-q','--junitxml='+str(out/'tests.xml')])
    counts,cases=test_summary(out/'tests.xml')
    for name in ('first_binding','dkn_bridge','j1_profiles','joint_applications'):
        step(name,[sys.executable,str(ROOT/'examples'/f'{name}.py')])
    # Isolated reference adapters obtain the pinned native path from the same prepared environment.
    step('conformance-i1',[sys.executable,str(ROOT/'tools/run_conformance.py'),'--out',str(out/'conformance-i1.json')])
    step('conformance-j1',[sys.executable,str(ROOT/'tools/run_j_conformance.py'),'--out',str(out/'conformance-j1.json')])
    models={'I1':check_model.check(junit=out/'tests.xml'),'J1':check_j_model.check(junit=out/'tests.xml')}
    if before!=fingerprint():raise ValueError('J_REPLAY_SOURCE_CHANGED')
    if native_preservation(native)!=native_report:raise ValueError('J_REPLAY_NATIVE_CHANGED')
    result={'schema':'cmba.batch-j-local-run','status':'PASS_SCOPED_ENGINEERING','source_fingerprint':before,
      'tests':counts,'workflows':4,'models':models,'native_preservation':native_report,
      'conformance':{k:json.loads((out/('conformance-'+k+'.json')).read_text()) for k in ('i1','j1')},
      'platform':{'python':platform.python_version(),'system':platform.system(),'machine':platform.machine()},
      'dependencies':{n:importlib.metadata.version(n) for n in ('pytest','cryptography','jsonschema')},
      'test_cases':cases,'legs':legs,'output_hashes':{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()},
      'independent_review':'NOT_PERFORMED','publication':'NOT_PERFORMED','authority_effect':'NONE','public_release_gate':'NOT_CLEARED'}
    (out/'LOCAL-RUN.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--dkn-source',type=Path,required=True);a=p.parse_args()
    try:r=run(a.out.resolve(),a.dkn_source.resolve());code=0
    except Exception as exc:
        r={'schema':'cmba.batch-j-replay-failure','status':'FAIL','error':str(exc),'authority_effect':'NONE'};code=2
        a.out.mkdir(parents=True,exist_ok=True);(a.out/'FAILURE.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ('test_cases','legs','output_hashes')},sort_keys=True));raise SystemExit(code)
