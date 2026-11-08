"""Bounded native replay phases. Exact baseline preserved; no legacy substitution.

Splitting the invocation accommodates short tool windows without treating an XML file
from an interrupted process as a completed test leg. Every group needs a terminal exit.
"""
from pathlib import Path
import argparse,json,os,subprocess,sys,platform,importlib.metadata
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
import verify_l,verify_k,verify_j

def run(out,native,phase):
    out.mkdir(parents=True,exist_ok=True)
    ctx={'native':verify_l.native_inventory(native),'python':platform.python_version(),'system':platform.system(),
         'pytest':importlib.metadata.version('pytest'),'plugins':'DISABLED',
         'runner_sha256':verify_l.sha(Path(__file__).read_bytes())}
    if phase=='assemble':
        results={k:verify_l.stage_read(out,k,ctx) for k in ['collect','group0','group1','group2','group3']}
        expected=verify_k.identities((out/'collect/collect.stdout').read_bytes().replace(b'tests_v02/',b'tests/'))
        expected={(a.replace('tests.','tests_v02.',1),b) for a,b in expected}
        seen=set();groups=[]
        for i in range(4):
            r=results['group'+str(i)];verify_l.validate_legs(r,['group'+str(i)])
            counts,cases=verify_j.test_summary(out/('group'+str(i))/'tests.xml')
            ids={(c['classname'],c['name']) for c in cases}
            if seen & ids:raise ValueError('L_NATIVE_GROUP_OVERLAP')
            seen|=ids;groups.append(counts)
        if expected!=seen:raise ValueError('L_NATIVE_COVERAGE')
        r={'schema':'cmba.native-replay.l1','status':'PASS_SCOPED_NATIVE_V02','passed':len(seen),'groups':groups,
           'context':ctx,'stages':{k:verify_l.sha((out/k/'STAGE.json').read_bytes()) for k in results},
           'legacy_blake3':'NOT_EXECUTED','all_historical_release_stages':'NOT_REPLAYED','authority_effect':'NONE'}
        if (out/'NATIVE-REPLAY.json').exists():raise ValueError('L_NATIVE_RECEIPT_EXISTS')
        verify_l.write(out/'NATIVE-REPLAY.json',r);return r
    directory=out/phase;directory.mkdir(exist_ok=True)
    if any(directory.iterdir()):raise ValueError('L_NATIVE_STAGE_NONEMPTY')
    env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(native/'src'),str(native)]);env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    if phase=='collect':args=[sys.executable,'-m','pytest','tests_v02','--collect-only','-q','-o','addopts=']
    else:
        i=int(phase[-1]);files=sorted((native/'tests_v02').glob('test_*.py'))[i::4]
        args=[sys.executable,'-m','pytest',*[str(p) for p in files],'-q','--junitxml='+str(directory/'tests.xml')]
    p=subprocess.run(args,cwd=native,env=env,capture_output=True,timeout=240)
    (directory/(phase+'.stdout')).write_bytes(p.stdout);(directory/(phase+'.stderr')).write_bytes(p.stderr)
    if p.returncode:raise ValueError('L_NATIVE_PROCESS_FAILED')
    if verify_l.native_inventory(native)!=ctx['native']:raise ValueError('L_NATIVE_CHANGED')
    counts=verify_j.test_summary(directory/'tests.xml')[0] if phase!='collect' else None
    r={'schema':'cmba.native-stage.l1','phase':phase,'status':'PASS','context':ctx,'results':{'tests':counts},
       'legs':[{'name':phase,'exit_code':p.returncode}],
       'outputs':{p.name:verify_l.sha(p.read_bytes()) for p in directory.iterdir() if p.is_file()},'authority_effect':'NONE'}
    verify_l.write(directory/'STAGE.json',r);return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--dkn-source',type=Path,required=True);p.add_argument('--phase',choices=['collect','group0','group1','group2','group3','assemble'],required=True);a=p.parse_args()
    try:r=run(a.out.resolve(),a.dkn_source.resolve(),a.phase);code=0
    except Exception as e:r={'status':'FAIL','error':str(e),'phase':a.phase};code=2
    print(json.dumps(r,sort_keys=True));raise SystemExit(code)
