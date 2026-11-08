"""In-turn/operator replay with exact source and output bindings. No expectation regeneration."""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,xml.etree.ElementTree as ET,importlib.metadata
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical,decode
import check_model,unpack_baseline,run_conformance


def fingerprint(root=ROOT):
    rows={}
    for dirname in ('src','tests','tools','examples','schemas','interop','model','catalogue','docs'):
        for p in sorted((root/dirname).rglob('*')):
            if p.is_file() and not any(x in ('__pycache__','build','dist') or x.endswith('.egg-info') for x in p.relative_to(root).parts) and p.suffix not in ('.pyc','.pyo'):
                rows[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    for name in ('pyproject.toml','SOURCE-REGISTER.json','README.md'):
        rows[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def run(out, native):
    out.mkdir(parents=True,exist_ok=True);before=fingerprint();unpack_baseline.verify()
    env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(ROOT/'src'),str(native/'src')]);env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    legs=[]
    def step(name,command):
        p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,timeout=180)
        (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
        legs.append({'name':name,'exit_code':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),
                     'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()})
        if p.returncode:raise ValueError('REPLAY_LEG_FAILED:'+name)
    step('tests',[sys.executable,'-m','pytest','tests','-q','--junitxml='+str(out/'tests.xml')])
    cases=list(ET.parse(out/'tests.xml').iter('testcase'))
    if not cases or any(list(c) and any(x.tag in ('failure','error','skipped') for x in c) for c in cases):raise ValueError('REPLAY_TESTS_INCOMPLETE')
    for name in ('first_binding','dkn_bridge'):step(name,[sys.executable,str(ROOT/'examples'/f'{name}.py')])
    model=check_model.check(junit=out/'tests.xml')
    conformance=run_conformance.run()
    if before!=fingerprint():raise ValueError('REPLAY_SOURCE_CHANGED')
    result={'schema':'cmba.batch-i-local-run','status':'PASS_SCOPED_ENGINEERING','source_fingerprint':before,
      'tests':{'passed':len(cases),'failed':0,'errors':0,'skipped':0},'workflows':2,'model':model,'conformance':conformance,
      'platform':{'python':platform.python_version(),'system':platform.system(),'machine':platform.machine()},
      'dependencies':{n:importlib.metadata.version(n) for n in ('pytest','cryptography','jsonschema')},
      'test_cases':[{'classname':c.get('classname'),'name':c.get('name')} for c in cases],
      'test_xml_sha256':hashlib.sha256((out/'tests.xml').read_bytes()).hexdigest(),'legs':legs,
      'independent_review':'NOT_PERFORMED','publication':'NOT_PERFORMED','authority_effect':'NONE'}
    (out/'LOCAL-RUN.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--dkn-source',type=Path,required=True);a=p.parse_args()
    try:r=run(a.out.resolve(),a.dkn_source.resolve());code=0
    except Exception as exc:r={'status':'FAIL','error':str(exc),'authority_effect':'NONE'};code=2
    print(json.dumps({k:v for k,v in r.items() if k!='test_cases'},sort_keys=True));raise SystemExit(code)
