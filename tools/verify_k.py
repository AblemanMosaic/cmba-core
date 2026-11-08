"""Staged source/environment-bound K replay. Never regenerates models or expectations."""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,importlib.metadata,shutil,sqlite3
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
import verify_i,verify_j,check_model,check_j_model,check_k_model
PHASES=('tests','workflows','audit')
WORKFLOWS=('first_binding','dkn_bridge','j1_profiles','joint_applications','workbench_k','workbench_k_receipts')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def fingerprint():
    return sha(json.dumps({'source':verify_i.fingerprint(ROOT),'program':sha((ROOT/'PROGRAM-LEDGER.json').read_bytes()),
        'predecessor_inventory':sha((ROOT/'history/j1/FILE-MANIFEST.json').read_bytes())},sort_keys=True).encode())
def context(native):
    return {'source_fingerprint':fingerprint(),'native':verify_j.native_preservation(native),
        'python':platform.python_version(),'system':platform.system(),'machine':platform.machine(),
        'executable':sys.executable,'prefix':sys.prefix,'sqlite':sqlite3.sqlite_version,
        'dependencies':{n:importlib.metadata.version(n) for n in ('pytest','cryptography','jsonschema','Pillow')},
        'pytest_plugin_autoload':'DISABLED'}
def identities(raw):
    result=[]
    for line in raw.decode('utf-8').splitlines():
        if line.startswith('tests/') and '::' in line:
            parts=line.split('::');result.append((parts[0].removesuffix('.py').replace('/','.')+('.'+'.'.join(parts[1:-1]) if len(parts)>2 else ''),parts[-1]))
    if not result or len(result)!=len(set(result)):raise ValueError('K_COLLECTION_EMPTY_OR_DUPLICATE')
    return set(result)
def stage_read(out,phase,ctx):
    root=out/phase;r=json.loads((root/'STAGE.json').read_text())
    if r.get('phase')!=phase or r.get('status')!='PASS' or r.get('context')!=ctx:raise ValueError('K_STAGE_CONTEXT_OR_STATUS')
    expected=r.get('outputs',{})
    if not expected or set(p.name for p in root.iterdir() if p.is_file())!=set(expected)|{'STAGE.json'}:raise ValueError('K_STAGE_OUTPUT_CLOSURE')
    for name,h in expected.items():
        if Path(name).name!=name or sha((root/name).read_bytes())!=h:raise ValueError('K_STAGE_OUTPUT_CHANGED')
    return r

def run_phase(out,native,phase):
    out.mkdir(parents=True,exist_ok=True);ctx=context(native)
    if phase=='assemble':
        stages={p:stage_read(out,p,ctx) for p in PHASES}
        counts,cases=verify_j.test_summary(out/'tests/tests.xml')
        if {(c['classname'],c['name']) for c in cases}!=identities((out/'tests/collect.stdout').read_bytes()):raise ValueError('K_TEST_IDENTITY_COVERAGE')
        if counts!=stages['tests']['results']['tests']:raise ValueError('K_TEST_COUNT_MISMATCH')
        if stages['workflows']['results'].get('completed')!=list(WORKFLOWS):raise ValueError('K_WORKFLOW_INCOMPLETE')
        # Re-check live model references and recorded test coverage, not submitted conclusions.
        models={k:m.check(junit=out/'tests/tests.xml') for k,m in [('I1',check_model),('J1',check_j_model),('K1',check_k_model)]}
        audit=stages['audit']['results']
        if models!=audit['models']:raise ValueError('K_MODEL_STAGE_MISMATCH')
        result={'schema':'cmba.batch-k-local-run','status':'PASS_SCOPED_ENGINEERING','context':ctx,'tests':counts,
          'inherited_tests':561,'new_tests':counts['passed']-561,'workflows':len(WORKFLOWS),'models':models,
          'conformance':audit['conformance'],'gui':audit['gui'],'native_crypto':audit['native_crypto'],
          'test_cases':cases,'stages':{p:sha((out/p/'STAGE.json').read_bytes()) for p in PHASES},
          'authority_effect':'NONE','test_local_effects':'EXPLICIT_TEMPORARY_FILE_CREATION',
          'independent_review':'NOT_PERFORMED','publication':'NOT_PERFORMED','public_release_gate':'NOT_CLEARED'}
        if context(native)!=ctx:raise ValueError('K_CONTEXT_CHANGED')
        if (out/'LOCAL-RUN.json').exists():raise ValueError('K_RECEIPT_EXISTS')
        write(out/'LOCAL-RUN.json',result);return result
    if phase not in PHASES:raise ValueError('K_PHASE_UNKNOWN')
    directory=out/phase
    directory.mkdir(exist_ok=True)
    if list(directory.iterdir()):raise ValueError('K_STAGE_OUTPUT_NOT_EMPTY')
    env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(ROOT/'src'),str(native/'src')]);env['DKN_TEST_ROOT']=str(native);env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    legs=[]
    def step(name,args,timeout=300):
        try:p=subprocess.run(args,cwd=ROOT,env=env,capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired as e:
            (directory/(name+'.stdout')).write_bytes(e.stdout or b'');(directory/(name+'.stderr')).write_bytes(e.stderr or b'');raise ValueError('K_TIMEOUT:'+name)
        (directory/(name+'.stdout')).write_bytes(p.stdout);(directory/(name+'.stderr')).write_bytes(p.stderr)
        legs.append({'name':name,'exit_code':p.returncode})
        if p.returncode:raise ValueError('K_LEG_FAILED:'+name)
    if phase=='tests':
        step('collect',[sys.executable,'-m','pytest','tests','--collect-only','-q'])
        step('tests',[sys.executable,'-m','pytest','tests','-q','--junitxml='+str(directory/'tests.xml')])
        counts,cases=verify_j.test_summary(directory/'tests.xml')
        if {(c['classname'],c['name']) for c in cases}!=identities((directory/'collect.stdout').read_bytes()):raise ValueError('K_TEST_IDENTITY_COVERAGE')
        result={'tests':counts}
    elif phase=='workflows':
        for name in WORKFLOWS:step(name,[sys.executable,str(ROOT/'examples'/(name+'.py'))])
        result={'completed':list(WORKFLOWS)}
    else:
        stage_read(out,'tests',ctx)
        for name,tool in [('i1','run_conformance.py'),('j1','run_j_conformance.py'),('k1','run_k_conformance.py')]:
            step('conformance-'+name,[sys.executable,str(ROOT/'tools'/tool),'--out',str(directory/('conformance-'+name+'.json'))])
        models={k:m.check(junit=out/'tests/tests.xml') for k,m in [('I1',check_model),('J1',check_j_model),('K1',check_k_model)]}
        write(directory/'models.json',models)
        cmd=[sys.executable,str(ROOT/'tools/smoke_workbench_k.py'),'--out',str(directory/'gui.json'),'--screenshot',str(directory/'workbench.png')]
        if shutil.which('xvfb-run'):
            cmd=['xvfb-run','-a','-s','-screen 0 1600x1100x24']+cmd
        step('gui',cmd)
        step('native-crypto',[sys.executable,str(ROOT/'tools/crosscheck_j_crypto.py'),'--out',str(directory/'native-crypto.json')])
        gui=json.loads((directory/'gui.json').read_text());crypto=json.loads((directory/'native-crypto.json').read_text())
        if gui.get('status')!='PASS' or crypto.get('status')!='PASS':raise ValueError('K_AUDIT_NOT_PASS')
        result={'models':models,'conformance':{k:json.loads((directory/('conformance-'+k+'.json')).read_text()) for k in ('i1','j1','k1')},'gui':gui,'native_crypto':crypto}
    if context(native)!=ctx:raise ValueError('K_CONTEXT_CHANGED')
    report={'schema':'cmba.replay-stage.k1','phase':phase,'status':'PASS','context':ctx,'results':result,'legs':legs,
      'outputs':{p.name:sha(p.read_bytes()) for p in sorted(directory.iterdir()) if p.is_file()},'authority_effect':'NONE'}
    write(directory/'STAGE.json',report);return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--dkn-source',required=True,type=Path);p.add_argument('--phase',required=True,choices=(*PHASES,'assemble'));a=p.parse_args()
    try:r=run_phase(a.out.resolve(),a.dkn_source.resolve(),a.phase);code=0
    except Exception as e:r={'status':'FAIL','phase':a.phase,'error':str(e),'authority_effect':'NONE'};code=2
    print(json.dumps({k:v for k,v in r.items() if k not in ('test_cases','outputs','legs')},sort_keys=True));raise SystemExit(code)
