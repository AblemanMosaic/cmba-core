"""Batch L qualification: source-bound staged replay, no expectation/model regeneration.

This is unsigned engineering evidence, not authentication of a compromised producer.
No installation, publication or external reviewer submission occurs in this runner.
"""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,importlib.metadata,importlib.util,shutil,sqlite3,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
import verify_i,verify_j,verify_k,check_model,check_j_model,check_k_model
import qualification_integrity_r001 as integrity
from cmba_core import canonical
PHASES=('tests','workflows','audit');WORKFLOWS=verify_k.WORKFLOWS
PINS={'I1':'2f7ae78f19f7c06e85b176a9f2e1eb83383b41edb158e61c4fb16b653ca34e32',
      'J1':'9f8808f3e3f2862f2403355d5484e39475472cc8ad1d4011c0c9a53c32f9e8d3',
      'K1':'5df7a5b7230843bba99b93115c08a97d457b82366225d700cb3bb5f7313e9a7b'}
COUNTS={'i1':33,'j1':53,'k1':42}
LEGACY_CONTRACT=ROOT/'baseline/dkn/DKN-LEGACY-COVERAGE.json'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
def equal(a,b):return canonical(a)==canonical(b)
def fingerprint():
    return sha(json.dumps({'source':verify_i.fingerprint(ROOT),
      'ledger':sha((ROOT/'PROGRAM-LEDGER.json').read_bytes()),
      'process_posture':sha((ROOT/'PROCESS-POSTURE.json').read_bytes()),
      'release_boundary':sha((ROOT/'RELEASE-BOUNDARY.json').read_bytes()),
      'predecessor_inventory':sha((ROOT/'history/k1/FILE-MANIFEST.json').read_bytes()),
      'legacy_coverage_contract':sha(LEGACY_CONTRACT.read_bytes()),
      'native_platform_coverage_contract':sha((ROOT/'baseline/dkn/DKN-NATIVE-PLATFORM-COVERAGE.json').read_bytes()),
      'root_test_configuration':integrity.root_test_configuration(ROOT)},sort_keys=True).encode())

def legacy_contract():
    r=integrity.read_record(LEGACY_CONTRACT)
    keys={'schema','source_archive_sha256','parent_identities','parent_tests',
          'junit_declared_tests','successful_subtests','authority_effect'}
    if type(r) is not dict or set(r)!=keys or r['schema']!='cmba.dkn-legacy-coverage.l1' \
       or r['source_archive_sha256']!='c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3' \
       or r['authority_effect']!='NONE':raise ValueError('L_LEGACY_CONTRACT')
    identities=r['parent_identities']
    if (type(identities) is not list or len(identities)!=r['parent_tests'] or
        r['parent_tests']!=28 or r['successful_subtests']!=5 or
        r['junit_declared_tests']!=r['parent_tests']+r['successful_subtests']):
        raise ValueError('L_LEGACY_CONTRACT')
    parsed=[]
    for row in identities:
        if type(row) is not dict or set(row)!={'classname','name'} or not all(type(row[k]) is str and row[k] for k in row):
            raise ValueError('L_LEGACY_CONTRACT')
        parsed.append((row['classname'],row['name']))
    if len(parsed)!=len(set(parsed)):raise ValueError('L_LEGACY_CONTRACT')
    return r,parsed

def native_inventory(native):
    integrity.closed_native_tree(native, ROOT / 'baseline/dkn/DKN-core-0.2.0rc5-BATCH-H-REVIEW-CANDIDATE.zip')
    base=verify_j.native_preservation(native)
    archive=next((ROOT/'baseline/dkn').glob('*BATCH-H-REVIEW-CANDIDATE.zip'))
    contract,_=legacy_contract()
    archive_sha=sha(archive.read_bytes())
    if archive_sha!=contract['source_archive_sha256']:raise ValueError('L_NATIVE_ARCHIVE_CHANGED')
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            p=native/name
            if p.is_symlink() or not p.is_file() or p.read_bytes()!=z.read(name):raise ValueError('L_NATIVE_FILE_CHANGED:'+name)
        base['all_source_members']=len(z.namelist())
    base['source_archive_sha256']=archive_sha
    return base

def context(native,require_legacy=False):
    # Source admission intentionally precedes node/version subprocesses.
    source_fingerprint=fingerprint();native_state=native_inventory(native)
    node=shutil.which('node');node_version=subprocess.check_output([node,'--version'],text=True).strip() if node else 'UNAVAILABLE'
    deps={}
    for n in ('pytest','cryptography','jsonschema','Pillow','setuptools','blake3'):
        try:deps[n]=importlib.metadata.version(n)
        except importlib.metadata.PackageNotFoundError:deps[n]='UNAVAILABLE'
    return {'source_fingerprint':source_fingerprint,'native':native_state,'python':platform.python_version(),
      'system':platform.system(),'machine':platform.machine(),'executable':sys.executable,'prefix':sys.prefix,
      'sqlite':sqlite3.sqlite_version,'node':node_version,'dependencies':deps,
      'pytest_plugin_autoload':'DISABLED','require_legacy':require_legacy}

def stage_read(out,phase,ctx,allow_blocked=False):
    directory=out/phase
    if directory.is_symlink() or (hasattr(directory,'is_junction') and directory.is_junction()):raise ValueError('L_STAGE_SYMLINK')
    p=directory/'STAGE.json'
    if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()):raise ValueError('L_STAGE_SYMLINK')
    r=integrity.read_record(p)
    integrity.validate_stage_header(r,phase,allow_blocked=allow_blocked)
    statuses={'PASS','BLOCKED'} if allow_blocked else {'PASS'}
    if r.get('phase')!=phase or r.get('status') not in statuses or not equal(r.get('context'),ctx):raise ValueError('L_STAGE_CONTEXT_OR_STATUS')
    outputs=r.get('outputs')
    if type(outputs) is not dict or not outputs:raise ValueError('L_STAGE_EMPTY_OUTPUTS')
    if {p.name for p in directory.iterdir()}!=set(outputs)|{'STAGE.json'}:raise ValueError('L_STAGE_CLOSURE')
    for name,h in outputs.items():
        if type(name) is not str or Path(name).name!=name or name in ('.','..'):raise ValueError('L_STAGE_PATH')
        p=directory/name
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) or not p.is_file() or sha(p.read_bytes())!=h:raise ValueError('L_STAGE_OUTPUT_CHANGED')
    legacy_names={'legacy-'+phase+s for s in ('.xml','.stdout','.stderr')}
    if ctx.get('require_legacy') is True:
        if not legacy_names<=set(outputs):raise ValueError('L_STAGE_LEGACY_OUTPUTS')
        legacy_test_summary(directory/('legacy-'+phase+'.xml'))
        legacy_terminal(r['results'])
    elif legacy_names & set(outputs) or 'legacy_runtime' in r['results']:raise ValueError('L_STAGE_LEGACY_UNCLAIMED')
    return r

def validate_legs(r,names):
    legs=r.get('legs')
    if type(legs) is not list or [x.get('name') for x in legs]!=list(names):raise ValueError('L_STAGE_LEGS')
    if any(type(x.get('exit_code')) is not int or x['exit_code']!=0 for x in legs):raise ValueError('L_STAGE_LEG_EXIT')

def validate_conformance(r,count):
    if (type(r) is not dict or r.get('status')!='PASS' or type(r.get('cases')) is not int
       or r['cases']!=count or r.get('authority_effect')!='NONE'
       or r.get('oracle') not in ('EXACT_CANONICAL_RESPONSE_BYTES','EXACT_CANONICAL_TYPED_RESULTS')):raise ValueError('L_CONFORMANCE_RESULT')

def legacy_terminal(result):
    r=result.get('legacy_runtime') if type(result) is dict else None
    if type(r) is not dict or set(r)!={'exit_code','terminal'} or type(r['exit_code']) is not int \
       or r['exit_code']!=0 or r['terminal']!='PASS':raise ValueError('L_LEGACY_TERMINAL')
    return r['exit_code']

def legacy_test_summary(path):
    """Validate the exact frozen legacy suite's pytest-9 unittest/subtest JUnit shape."""
    contract,expected=legacy_contract()
    tree=ET.parse(path);cases=list(tree.iter('testcase'));seen=set();actual=[]
    for case in cases:
        ident=(case.get('classname'),case.get('name'))
        if not all(ident) or ident in seen:raise ValueError('L_LEGACY_TEST_IDENTITY')
        seen.add(ident);actual.append(ident)
        if any(c.tag in ('failure','error','skipped') for c in case):raise ValueError('L_LEGACY_TEST_INCOMPLETE')
    suites=list(tree.iter('testsuite'))
    if not suites or any(int(s.get(k,'0')) for s in suites for k in ('failures','errors','skipped')):raise ValueError('L_LEGACY_TEST_INCOMPLETE')
    declared=sum(int(s.get('tests','0')) for s in suites)
    if actual!=expected:raise ValueError('L_LEGACY_TEST_IDENTITY')
    if (len(cases),declared)!=(contract['parent_tests'],contract['junit_declared_tests']):raise ValueError('L_LEGACY_TEST_COUNT')
    subtests=declared-len(cases)
    if subtests!=contract['successful_subtests']:raise ValueError('L_LEGACY_SUBTEST_COUNT')
    return {'passed':len(cases),'failed':0,'errors':0,'skipped':0},declared

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
        actual=integrity.read_record(ad/('conformance-'+k+'.json'));validate_conformance(actual,n)
        if not equal(actual,ar['conformance'][k]):raise ValueError('L_AUDIT_REPORT_SUBSTITUTION')
    mm=models(out/'tests/tests.xml')
    if not equal(mm,ar['models']) or not equal(mm,integrity.read_record(ad/'models.json')):raise ValueError('L_MODEL_REPORT_SUBSTITUTION')
    for key,file in [('gui','gui.json'),('native_crypto','native-crypto.json'),('node_core','node-core.json')]:
        actual=integrity.read_record(ad/file)
        if actual.get('status')!='PASS' or not equal(actual,ar[key]):raise ValueError('L_AUDIT_REPORT_SUBSTITUTION')
    if ar['node_core'].get('cases')!=33 or ar['node_core'].get('full_alternative_realization') is not False:raise ValueError('L_NODE_CLAIM')
    if ar['gui'].get('check_count')!=len(ar['gui'].get('checks',[])) or ar['gui']['check_count']<48:raise ValueError('L_GUI_COMPLETENESS')
    witness=ar['gui'].get('visual_witness')
    if (type(witness) is not dict or witness.get('status')!='PASS_VALIDATED_CMBA_WORKBENCH'
        or witness.get('capture_method')!='RAISED_TOPMOST_TK_CLIENT_BOUNDS'
        or witness.get('sha256')!=sha((ad/'workbench.png').read_bytes())
        or ar['gui'].get('installed_environment') is not False):raise ValueError('L_GUI_VISUAL_WITNESS')
    return {'schema':'cmba.batch-l-local-run','status':'PASS_SCOPED_ENGINEERING_EXTERNAL_GATES_OPEN','context':ctx,
      'tests':counts,'cmba_historical_test_subtotal':759,
      'cmba_tests_after_historical_subtotal':counts['passed']-759,'test_cases':cases,'workflows':len(WORKFLOWS),
      'models':mm,'conformance':ar['conformance'],'node_core':ar['node_core'],'gui':ar['gui'],'native_crypto':ar['native_crypto'],
      'stages':{p:sha((out/p/'STAGE.json').read_bytes()) for p in PHASES},
      'legacy_runtime':'NOT_EXECUTED_USE_REQUIRE_LEGACY_GATE','authority_effect':'NONE',
      'local_effects':'EXPLICIT_TEMPORARY_TEST_EXPORTS','independent_review':'NOT_PERFORMED',
      'publication':'NOT_PERFORMED','public_release_gate':'NOT_CLEARED'}

def legacy_paths(out,phase):
    base=out if phase=='assemble' else out/phase
    stem='legacy-'+phase
    return base,tuple(base/(stem+s) for s in ('.xml','.stdout','.stderr'))

def run_phase(out,native,phase,require_legacy=False):
    out.mkdir(parents=True,exist_ok=True)
    if phase not in (*PHASES,'assemble'):raise ValueError('L_PHASE_UNKNOWN')
    if phase=='assemble':
        if (out/'LOCAL-RUN.json').exists():raise ValueError('L_RECEIPT_EXISTS')
    else:
        directory=out/phase;directory.mkdir(exist_ok=True)
        if any(directory.iterdir()):raise ValueError('L_STAGE_NONEMPTY')
    base,legacy_files=legacy_paths(out,phase)
    if any(p.exists() for p in legacy_files):raise ValueError('L_LEGACY_OUTPUT_EXISTS')
    admitted_native=native_inventory(native)
    ctx=context(native,require_legacy)
    if not equal(admitted_native,ctx['native']):raise ValueError('L_SOURCE_CONTEXT_CHANGED')
    if ctx['node']=='UNAVAILABLE':raise ValueError('L_NODE_REQUIRED')
    result=assemble(out,ctx) if phase=='assemble' else None;legacy_exit_code=None
    if require_legacy:
        try:import blake3
        except ImportError as e:raise ValueError('L_REQUIRED_LEGACY_BLAKE3_UNAVAILABLE') from e
        # This flag never substitutes a hash or skips unavailable legacy cases.
        env=integrity.test_environment([native/'src',native])
        scratch=out/('_scratch-legacy-'+phase);scratch.mkdir(exist_ok=False)
        env['TMP']=env['TEMP']=str(scratch)
        xml,stdout,stderr=legacy_files
        p=subprocess.run([sys.executable,'-m','pytest','--confcutdir='+str(native),'tests','-q',
            '--basetemp='+str(scratch/'pytest'),'-p','no:cacheprovider',
            '--junitxml='+str(xml)],cwd=native,env=env,capture_output=True,timeout=180)
        stdout.write_bytes(p.stdout);stderr.write_bytes(p.stderr)
        legacy_exit_code=p.returncode
        if p.returncode:raise ValueError('L_REQUIRED_LEGACY_FAILED')
        legacy_test_summary(xml)
        if not equal(admitted_native,native_inventory(native)):raise ValueError('L_SOURCE_CONTEXT_CHANGED')
    if phase=='assemble':
        if require_legacy:
            legacy={}
            for leg in (*PHASES,'assemble'):
                leg_base,paths=legacy_paths(out,leg);xml=paths[0];counts,declared=legacy_test_summary(xml)
                exit_code=legacy_exit_code if leg=='assemble' else legacy_terminal(integrity.read_record(out/leg/'STAGE.json')['results'])
                legacy[leg]={'tests':counts,'junit_declared_with_subtests':declared,
                  'successful_subtests':declared-counts['passed'],'exit_code':exit_code,
                  'outputs':{p.relative_to(out).as_posix():sha(p.read_bytes()) for p in paths}}
            result['legacy_runtime']={'status':'PASS_SCOPED_NATIVE_LEGACY','legs':legacy}
        if not equal(ctx,context(native,require_legacy)):raise ValueError('L_SOURCE_CONTEXT_CHANGED')
        write(out/'LOCAL-RUN.json',result);return result
    env=integrity.test_environment([ROOT/'src',native/'src']);env['DKN_TEST_ROOT']=str(native)
    if os.name=='nt':env['CMBA_REQUIRE_REAL_LINK']='1'
    scratch=out/('_scratch-'+phase);scratch.mkdir(exist_ok=False)
    env['TMP']=env['TEMP']=str(scratch)
    legs=[]
    def step(name,args,timeout=180):
        try:p=subprocess.run(args,cwd=ROOT,env=env,capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired as e:
            (directory/(name+'.stdout')).write_bytes(e.stdout or b'');(directory/(name+'.stderr')).write_bytes(e.stderr or b'');raise ValueError('L_TIMEOUT:'+name)
        (directory/(name+'.stdout')).write_bytes(p.stdout);(directory/(name+'.stderr')).write_bytes(p.stderr)
        legs.append({'name':name,'exit_code':p.returncode})
        if p.returncode:raise ValueError('L_LEG_FAILED:'+name)
    if phase=='tests':
        pytest_base=['--basetemp='+str(scratch/'pytest'),'-p','no:cacheprovider']
        step('collect',[sys.executable,'-m','pytest','--confcutdir='+str(ROOT),'tests','--collect-only','-q','-o','addopts=',*pytest_base])
        step('tests',[sys.executable,'-m','pytest','--confcutdir='+str(ROOT),'tests','-q',*pytest_base,'--junitxml='+str(directory/'tests.xml')])
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
    if require_legacy:result['legacy_runtime']={'exit_code':legacy_exit_code,'terminal':'PASS'}
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
