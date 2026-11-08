"""Replay preserved native suite in disjoint groups, comparing exact collected identities."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,platform
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'src')]
import verify_j

def run(out,native):
    out.mkdir(parents=True,exist_ok=True)
    if list(out.iterdir()):raise ValueError('NATIVE_OUTPUT_NOT_EMPTY')
    preservation=verify_j.native_preservation(native)
    env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(native/'src'),str(native)]);env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    def step(name,args):
        p=subprocess.run(args,cwd=native,env=env,capture_output=True,timeout=300)
        (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
        if p.returncode:raise ValueError('NATIVE_LEG_FAILED:'+name)
        return p.stdout
    raw=step('collect',[sys.executable,'-m','pytest','tests_v02','--collect-only','-q','-o','addopts='])
    expected=set()
    for line in raw.decode().splitlines():
        if line.startswith('tests_v02/') and '::' in line:
            parts=line.split('::');expected.add((parts[0].removesuffix('.py').replace('/','.')+('.'+'.'.join(parts[1:-1]) if len(parts)>2 else ''),parts[-1]))
    if not expected:raise ValueError('NATIVE_COLLECTION_EMPTY')
    testfiles=sorted((native/'tests_v02').glob('test_*.py'));seen=set();groups=[]
    for group in range(4):
        selected=testfiles[group::4]
        step('group'+str(group),[sys.executable,'-m','pytest',*[str(p) for p in selected],'-q','--junitxml='+str(out/f'group{group}.xml')])
        counts,cases=verify_j.test_summary(out/f'group{group}.xml');ids={(c['classname'],c['name']) for c in cases}
        if seen&ids:raise ValueError('NATIVE_GROUP_OVERLAP')
        seen|=ids;groups.append(counts)
    if seen!=expected:raise ValueError('NATIVE_IDENTITY_COVERAGE')
    if verify_j.native_preservation(native)!=preservation:raise ValueError('NATIVE_SOURCE_CHANGED')
    report={'schema':'cmba.k-native-replay','status':'PASS_SCOPED_NATIVE_V02','passed':len(seen),'groups':groups,
        'preservation':preservation,'legacy_blake3':'NOT_EXECUTED','all_historical_release_stages':'NOT_REPLAYED',
        'python':platform.python_version(),'system':platform.system(),'authority_effect':'NONE',
        'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
    (out/'NATIVE-REPLAY.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--dkn-source',type=Path,required=True);a=p.parse_args()
    try:r=run(a.out.resolve(),a.dkn_source.resolve());code=0
    except Exception as e:r={'status':'FAIL','error':str(e)};code=2
    print(json.dumps(r));raise SystemExit(code)
