"""Batch L qualification: source-bound staged replay, no expectation/model regeneration.

This is unsigned engineering evidence, not authentication of a compromised producer.
No installation, publication or external reviewer submission occurs in this runner.
"""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,importlib.metadata,importlib.util,shutil,sqlite3,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
import verify_i,verify_j,verify_k,check_model,check_j_model,check_k_model
from cmba_core import canonical
PHASES=('tests','workflows','audit');WORKFLOWS=verify_k.WORKFLOWS
PINS={'I1':'2f7ae78f19f7c06e85b176a9f2e1eb83383b41edb158e61c4fb16b653ca34e32',
      'J1':'8734691fb74b3697a09c4eb67b57860fb3c95b2050a0185cd1c651db64dc97a8',
      'K1':'d248731d2654095abd1de21f0d7bcb09fc146f603c44dc16c9bbd5e1e9936431'}
COUNTS={'i1':33,'j1':53,'k1':42}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
def equal(a,b):return canonical(a)==canonical(b)
def fingerprint():
    return sha(json.dumps({'source':verify_i.fingerprint(ROOT),
      'ledger':sha((ROOT/'PROGRAM-LEDGER.json').read_bytes()),
      'release_boundary':sha((ROOT/'RELEASE-BOUNDARY.json').read_bytes()),
      'predecessor_inventory':sha((ROOT/'history/k1/FILE-MANIFEST.json').read_bytes())},sort_keys=True).encode())

def native_inventory(native):
    base=verify_j.native_preservation(native)
    archive=next((ROOT/'baseline/dkn').glob('*BATCH-H-REVIEW-CANDIDATE.zip'))
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            p=native/name
            if p.is_symlink() or not p.is_file() or p.read_bytes()!=z.read(name):raise ValueError('L_NATIVE_FILE_CHANGED:'+name)
        base['all_source_members']=len(z.namelist())
    return base

def context(native,require_legacy=False):
    node=shutil.which('node');node_version=subprocess.check_output([node,'--version'],text=True).strip() if node else 'UNAVAILABLE'
    deps={}
    for n in ('pytest','cryptography','jsonschema','Pillow','setuptools','blake3'):
        try:deps[n]=importlib.metadata.version(n)
        except importlib.metadata.PackageNotFoundError:deps[n]='UNAVAILABLE'
    return {'source_fingerprint':fingerprint(),'native':native_inventory(native),'python':platform.python_version(),
      'system':platform.system(),'machine':platform.machine(),'executable':sys.executable,'prefix':sys.prefix,
      'sqlite':sqlite3.sqlite_version,'node':node_version,'dependencies':deps,
      'pytest_plugin_autoload':'DISABLED','require_legacy':require_legacy}

def stage_read(out,phase,ctx):
    directory=out/phase
    if directory.is_symlink():raise ValueError('L_STAGE_SYMLINK')
    p=directory/'STAGE.json'
    if p.is_symlink():raise ValueError('L_STAGE_SYMLINK')
    r=json.loads(p.read_text())
    if r.get('phase')!=phase or r.get('status')!='PASS' or not equal(r.get('context'),ctx):raise ValueError('L_STAGE_CONTEXT_OR_STATUS')
    outputs=r.get('outputs')
    if type(outputs) is not dict or not outputs:raise ValueError('L_STAGE_EMPTY_OUTPUTS')
    if {p.name for p in directory.iterdir()}!=set(outputs)|{'STAGE.json'}:raise ValueError('L_STAGE_CLOSURE')
    for name,h in outputs.items():
        if type(name) is not str or Path(name).name!=name or name in ('.','..'):raise ValueError('L_STAGE_PATH')
        p=directory/name
        if p.is_symlink() or not p.is_file() or sha(p.read_bytes())!=h:raise ValueError('L_STAGE_OUTPUT_CHANGED')
    return r

def validate_legs(r,names):
    legs=r.get('legs')
    if type(legs) is not list or [x.get('name') for x in legs]!=list(names):raise ValueError('L_STAGE_LEGS')
    if any(type(x.get('exit_code')) is not int or x['exit_code']!=0 for x in legs):raise ValueError('L_STAGE_LEG_EXIT')

def validate_conformance(r,count):
    if (type(r) is not dict or r.get('status')!='PASS' or type(r.get('cases')) is not int
       or r['cases']!=count or r.get('authority_effect')!='NONE'
       or r.get('oracle') not in ('EXACT_CANONICAL_RESPONSE_BYTES','EXACT_CANONICAL_TYPED_RESULTS')):raise ValueError('L_CONFORMANCE_RESULT')

def models(junit):
    return {k:m.check(junit=junit,expected_commitment=PINS[k]) for k,m in [('I1',check_model),('J1',check_j_model),('K1',check_k_model)]}

def assemble(out,ctx):
    stages={p:stage_read(out,p,ctx) for p in PHASES}
    validate_legs(stages['tests'],['collect','tests'])
    counts,cases=verify_j.test_summary(out/'tests/tests.xml')
    if {(c['classname'],c['name']) for c in cases}!=verify_k.identities((out/'tests/collect.stdout').read_bytes()):raise ValueError('L_TEST_IDENTITY_COVERAGE')
    if not equal(counts,stages['tests']['results']['tests']):raise ValueError('L_TEST_COUNT')
    validate_legs(stages['workflows'],WORKFLOWS)
    if stages['workflows']['results'].get('completed')!=list(WORKFLOWS):raise ValueError('L_WORKFLOW_COMPLETENESS')
    ar=stages['audit']['results'];ad=out/'audit'
    validate_legs(stages['audit'],['conformance-i1','conformance-j1','conformance-k1','node-core','gui','native-crypto'])
    for k,n in COUNTS.items():
        actual=json.loads((ad/('conformance-'+k+'.json')).read_text());validate_conformance(actual,n)
        if not equal(actual,ar['conformance'][k]):raise ValueError('L_AUDIT_REPORT_SUBSTITUTION')
    mm=models(out/'tests/tests.xml')
    if not equal(mm,ar['models']) or not equal(mm,json.loads((ad/'models.json').read_text())):raise ValueError('L_MODEL_REPORT_SUBSTITUTION')
    for key,file in [('gui','gui.json'),('native_crypto','native-crypto.json'),('node_core','node-core.json')]:
        actual=json.loads((ad/file).read_text())
        if actual.get('status')!='PASS' or not equal(actual,ar[key]):raise ValueError('L_AUDIT_REPORT_SUBSTITUTION')
    if ar['node_core'].get('cases')!=33 or ar['node_core'].get('full_alternative_realization') is not False:raise ValueError('L_NODE_CLAIM')
    if ar['gui'].get('check_count')!=len(ar['gui'].get('checks',[])) or ar['gui']['check_count']<48:raise ValueError('L_GUI_COMPLETENESS')
    return {'schema':'cmba.batch-l-local-run','status':'PASS_SCOPED_ENGINEERING_EXTERNAL_GATES_OPEN','context':ctx,
      'tests':counts,'inherited':759,'new':counts['passed']-759,'test_cases':cases,'workflows':len(WORKFLOWS),
      'models':mm,'conformance':ar['conformance'],'node_core':ar['node_core'],'gui':ar['gui'],'native_crypto':ar['native_crypto'],
      'stages':{p:sha((out/p/'STAGE.json').read_bytes()) for p in PHASES},
      'legacy_runtime':'NOT_EXECUTED_USE_REQUIRE_LEGACY_GATE','authority_effect':'NONE',
      'local_effects':'EXPLICIT_TEMPORARY_TEST_EXPORTS','independent_review':'NOT_PERFORMED',
      'publication':'NOT_PERFORMED','public_release_gate':'NOT_CLEARED'}

def run_phase(out,native,phase,require_legacy=False):
    out.mkdir(parents=True,exist_ok=True)
    if require_legacy:
        try:import blake3
        except ImportError as e:raise ValueError('L_REQUIRED_LEGACY_BLAKE3_UNAVAILABLE') from e
        # This flag never substitutes a hash or skips unavailable legacy cases.
        env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(native/'src'),str(native)]);env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
        p=subprocess.run([sys.executable,'-m','pytest','tests','-q','--junitxml='+str(out/('legacy-'+phase+'.xml'))],cwd=native,env=env,capture_output=True,timeout=180)
        (out/('legacy-'+phase+'.stdout')).write_bytes(p.stdout);(out/('legacy-'+phase+'.stderr')).write_bytes(p.stderr)
        if p.returncode:raise ValueError('L_REQUIRED_LEGACY_FAILED')
        verify_j.test_summary(out/('legacy-'+phase+'.xml'))
    ctx=context(native,require_legacy)
    if ctx['node']=='UNAVAILABLE':raise ValueError('L_NODE_REQUIRED')
    if phase=='assemble':
        result=assemble(out,ctx)
        if require_legacy:
            legacy={}
            for leg in (*PHASES,'assemble'):
                xml=out/('legacy-'+leg+'.xml');counts,_=verify_j.test_summary(xml)
                names=['legacy-'+leg+suffix for suffix in ('.xml','.stdout','.stderr')]
                legacy[leg]={'tests':counts,'outputs':{n:sha((out/n).read_bytes()) for n in names}}
            result['legacy_runtime']={'status':'PASS_SCOPED_NATIVE_LEGACY','legs':legacy}
        if not equal(ctx,context(native,require_legacy)):raise ValueError('L_SOURCE_CONTEXT_CHANGED')
        if (out/'LOCAL-RUN.json').exists():raise ValueError('L_RECEIPT_EXISTS')
        write(out/'LOCAL-RUN.json',result);return result
    if phase not in PHASES:raise ValueError('L_PHASE_UNKNOWN')
    directory=out/phase;directory.mkdir(exist_ok=True)
    if any(directory.iterdir()):raise ValueError('L_STAGE_NONEMPTY')
    env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(ROOT/'src'),str(native/'src')]);env['DKN_TEST_ROOT']=str(native);env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    legs=[]
    def step(name,args,timeout=180):
        try:p=subprocess.run(args,cwd=ROOT,env=env,capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired as e:
            (directory/(name+'.stdout')).write_bytes(e.stdout or b'');(directory/(name+'.stderr')).write_bytes(e.stderr or b'');raise ValueError('L_TIMEOUT:'+name)
        (directory/(name+'.stdout')).write_bytes(p.stdout);(directory/(name+'.stderr')).write_bytes(p.stderr)
        legs.append({'name':name,'exit_code':p.returncode})
        if p.returncode:raise ValueError('L_LEG_FAILED:'+name)
    if phase=='tests':
        step('collect',[sys.executable,'-m','pytest','tests','--collect-only','-q','-o','addopts='])
        step('tests',[sys.executable,'-m','pytest','tests','-q','--junitxml='+str(directory/'tests.xml')])
        counts,cases=verify_j.test_summary(directory/'tests.xml')
        if {(c['classname'],c['name']) for c in cases}!=verify_k.identities((directory/'collect.stdout').read_bytes()):raise ValueError('L_TEST_IDENTITY_COVERAGE')
        result={'tests':counts}
    elif phase=='workflows':
        for name in WORKFLOWS:step(name,[sys.executable,str(ROOT/'examples'/(name+'.py'))])
        result={'completed':list(WORKFLOWS)}
    else:
        stage_read(out,'tests',ctx)
        for k,tool in [('i1','run_conformance.py'),('j1','run_j_conformance.py'),('k1','run_k_conformance.py')]:
            step('conformance-'+k,[sys.executable,str(ROOT/'tools'/tool),'--out',str(directory/('conformance-'+k+'.json'))])
        step('node-core',[sys.executable,str(ROOT/'tools/crosscheck_l_core.py'),'--out',str(directory/'node-core.json')])
        mm=models(out/'tests/tests.xml');write(directory/'models.json',mm)
        cmd=[sys.executable,str(ROOT/'tools/smoke_workbench_k.py'),'--out',str(directory/'gui.json'),'--screenshot',str(directory/'workbench.png')]
        if shutil.which('xvfb-run'):cmd=['xvfb-run','-a','-s','-screen 0 1600x1100x24']+cmd
        step('gui',cmd)
        step('native-crypto',[sys.executable,str(ROOT/'tools/crosscheck_j_crypto.py'),'--out',str(directory/'native-crypto.json')])
        result={'models':mm,'conformance':{k:json.loads((directory/('conformance-'+k+'.json')).read_text()) for k in COUNTS},
          'node_core':json.loads((directory/'node-core.json').read_text()),'gui':json.loads((directory/'gui.json').read_text()),
          'native_crypto':json.loads((directory/'native-crypto.json').read_text())}
    if not equal(ctx,context(native,require_legacy)):raise ValueError('L_SOURCE_CONTEXT_CHANGED')
    r={'schema':'cmba.qualification-stage.l1','phase':phase,'status':'PASS','context':ctx,'results':result,'legs':legs,
      'outputs':{p.name:sha(p.read_bytes()) for p in sorted(directory.iterdir()) if p.is_file()},'authority_effect':'NONE'}
    write(directory/'STAGE.json',r);return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--dkn-source',type=Path,required=True);p.add_argument('--phase',choices=(*PHASES,'assemble'),required=True);p.add_argument('--require-legacy',action='store_true');a=p.parse_args()
    try:r=run_phase(a.out.resolve(),a.dkn_source.resolve(),a.phase,a.require_legacy);code=0
    except Exception as e:
        r={'status':'FAIL','phase':a.phase,'error':str(e),'authority_effect':'NONE'};code=2
        a.out.mkdir(parents=True,exist_ok=True);write(a.out/('FAILURE-'+a.phase+'.json'),r)
    print(json.dumps({k:v for k,v in r.items() if k not in ('test_cases','outputs','legs')},sort_keys=True));raise SystemExit(code)
