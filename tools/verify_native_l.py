"""Bounded native replay phases. Exact baseline preserved; no legacy substitution.

Splitting the invocation accommodates short tool windows without treating an XML file
from an interrupted process as a completed test leg. Every group needs a terminal exit.
"""
from pathlib import Path
import argparse,json,os,subprocess,sys,platform,importlib.metadata,importlib.util,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
import verify_l,verify_k,verify_j

COVERAGE_CONTRACT=ROOT/'baseline/dkn/DKN-NATIVE-PLATFORM-COVERAGE.json'

def coverage_contract():
    r=verify_l.integrity.read_record(COVERAGE_CONTRACT)
    if (type(r) is not dict or set(r)!={'schema','source_archive_sha256','collected_tests','skip_rules','default_skip_disposition','authority_effect'}
        or r['schema']!='cmba.dkn-native-platform-coverage.l1'
        or r['source_archive_sha256']!='c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3'
        or r['collected_tests']!=1173 or r['default_skip_disposition']!='BLOCKED' or r['authority_effect']!='NONE'):
        raise ValueError('L_NATIVE_COVERAGE_CONTRACT')
    rules={}
    for row in r['skip_rules']:
        keys={'classname','name','when','reason','disposition'}
        permitted={'OS_NOT_POSIX':'NOT_APPLICABLE','MKFIFO_UNAVAILABLE':'NOT_APPLICABLE',
                   'BLAKE3_AVAILABLE':'NOT_APPLICABLE','WINDOWS_SYMLINK_PRIVILEGE_UNAVAILABLE':'BLOCKED'}
        if (type(row) is not dict or set(row)!=keys or row['disposition'] not in ('NOT_APPLICABLE','BLOCKED')
            or row['when'] not in permitted or row['disposition']!=permitted[row['when']]):raise ValueError('L_NATIVE_COVERAGE_CONTRACT')
        ident=(row['classname'],row['name'])
        if not all(type(v) is str and v for v in (*ident,row['when'],row['reason'])) or ident in rules:raise ValueError('L_NATIVE_COVERAGE_CONTRACT')
        rules[ident]=row
    return r,rules

def rule_applies(rule):
    return {'OS_NOT_POSIX':os.name!='posix','MKFIFO_UNAVAILABLE':not hasattr(os,'mkfifo'),
            'BLAKE3_AVAILABLE':importlib.util.find_spec('blake3') is not None,
            'WINDOWS_SYMLINK_PRIVILEGE_UNAVAILABLE':os.name=='nt'}[rule['when']]

def native_test_summary(path):
    """Return an exact identity-level PASS/N/A plan; any other skip is BLOCKED."""
    contract,rules=coverage_contract();tree=ET.parse(path);coverage=[];seen=set()
    for case in tree.iter('testcase'):
        ident=(case.get('classname'),case.get('name'))
        if not all(ident) or ident in seen:raise ValueError('L_NATIVE_TEST_IDENTITY')
        seen.add(ident)
        failure=case.find('failure');error=case.find('error');skipped=case.find('skipped')
        if error is not None:raise ValueError('L_NATIVE_TEST_FAILED')
        if failure is not None:
            rule=rules.get(ident);message=failure.get('message','')
            if rule and rule['disposition']=='BLOCKED' and rule_applies(rule) and message.startswith(rule['reason']):
                disposition='BLOCKED';reason=rule['when']
            else:raise ValueError('L_NATIVE_TEST_FAILED')
        elif skipped is not None:
            rule=rules.get(ident);message=skipped.get('message','')
            if rule and rule['disposition']=='NOT_APPLICABLE' and rule_applies(rule) and message==rule['reason']:
                disposition='NOT_APPLICABLE';reason=rule['when']
            else:disposition='BLOCKED';reason=message or 'UNCLASSIFIED_SKIP'
        else:disposition='PASS';reason='EXECUTED'
        coverage.append({'classname':ident[0],'name':ident[1],'disposition':disposition,'reason':reason})
    suites=list(tree.iter('testsuite'))
    if not suites or any(int(s.get('errors','0')) for s in suites):raise ValueError('L_NATIVE_TEST_FAILED')
    declared=sum(int(s.get('tests','0')) for s in suites)
    if declared!=len(coverage):raise ValueError('L_NATIVE_TEST_COUNT')
    counts={k:sum(x['disposition']==k for x in coverage) for k in ('PASS','NOT_APPLICABLE','BLOCKED')}
    return {'passed':counts['PASS'],'not_applicable':counts['NOT_APPLICABLE'],'blocked':counts['BLOCKED'],'total':len(coverage)},coverage

def run(out,native,phase):
    out.mkdir(parents=True,exist_ok=True)
    if phase not in ('collect','group0','group1','group2','group3','assemble'):raise ValueError('L_NATIVE_PHASE')
    if phase=='assemble':
        if (out/'NATIVE-REPLAY.json').exists():raise ValueError('L_NATIVE_RECEIPT_EXISTS')
    else:
        directory=out/phase;directory.mkdir(exist_ok=True)
        if any(directory.iterdir()):raise ValueError('L_NATIVE_STAGE_NONEMPTY')
    admitted_native=verify_l.native_inventory(native)
    ctx={'native':admitted_native,'python':platform.python_version(),'system':platform.system(),
         'pytest':importlib.metadata.version('pytest'),'plugins':'DISABLED',
         'runner_sha256':verify_l.sha(Path(__file__).read_bytes()),
         'coverage_contract_sha256':verify_l.sha(COVERAGE_CONTRACT.read_bytes()),
         'qualification_context':verify_l.context(native)}
    if phase=='assemble':
        results={k:verify_l.stage_read(out,k,ctx,allow_blocked=True) for k in ['collect','group0','group1','group2','group3']}
        verify_l.validate_legs(results['collect'],['collect'])
        if results['collect']['results'] != {'tests':None}:raise ValueError('L_NATIVE_COLLECTION_RESULT')
        expected=verify_k.identities((out/'collect/collect.stdout').read_bytes().replace(b'tests_v02/',b'tests/'))
        expected={(a.replace('tests.','tests_v02.',1),b) for a,b in expected}
        contract,_=coverage_contract()
        if len(expected)!=contract['collected_tests']:raise ValueError('L_NATIVE_COLLECTED_COUNT')
        seen=set();groups=[];coverage=[]
        for i in range(4):
            r=results['group'+str(i)];legs=r.get('legs')
            if type(legs) is not list or len(legs)!=1 or legs[0].get('name')!='group'+str(i):raise ValueError('L_NATIVE_STAGE_LEGS')
            counts,cases=native_test_summary(out/('group'+str(i))/'tests.xml')
            if not verify_l.equal(counts,r['results'].get('tests')):raise ValueError('L_NATIVE_COUNT_SUMMARY')
            allowed_exits={0,1} if counts['blocked'] else {0}
            if legs[0].get('exit_code') not in allowed_exits or r['status']!=('BLOCKED' if counts['blocked'] else 'PASS'):
                raise ValueError('L_NATIVE_STAGE_DISPOSITION')
            ids={(c['classname'],c['name']) for c in cases}
            if seen & ids:raise ValueError('L_NATIVE_GROUP_OVERLAP')
            seen|=ids;groups.append(counts);coverage.extend(cases)
        if expected!=seen:raise ValueError('L_NATIVE_COVERAGE')
        passed=sum(x['passed'] for x in groups);na=sum(x['not_applicable'] for x in groups);blocked=sum(x['blocked'] for x in groups)
        status='BLOCKED_SCOPED_NATIVE_V02_EXPLICIT_PLATFORM_COVERAGE' if blocked else 'PASS_SCOPED_NATIVE_V02_EXPLICIT_PLATFORM_COVERAGE'
        r={'schema':'cmba.native-replay.l1','status':status,
           'collected':len(expected),'passed':passed,'not_applicable':na,'blocked':blocked,
           'coverage':sorted(coverage,key=lambda x:(x['classname'],x['name'])),'groups':groups,
           'context':ctx,'stages':{k:verify_l.sha((out/k/'STAGE.json').read_bytes()) for k in results},
           'legacy_blake3':'NOT_EXECUTED','all_historical_release_stages':'NOT_REPLAYED','authority_effect':'NONE'}
        verify_l.write(out/'NATIVE-REPLAY.json',r);return r
    env=verify_l.integrity.test_environment([native/'src',native])
    scratch=out/('_scratch-'+phase);scratch.mkdir(exist_ok=False)
    env['TMP']=env['TEMP']=str(scratch);pytest_base=['--basetemp='+str(scratch/'pytest'),'-p','no:cacheprovider']
    if phase=='collect':args=[sys.executable,'-m','pytest','--confcutdir='+str(native),'tests_v02','--collect-only','-q','-o','addopts=',*pytest_base]
    else:
        i=int(phase[-1]);files=sorted((native/'tests_v02').glob('test_*.py'))[i::4]
        args=[sys.executable,'-m','pytest','--confcutdir='+str(native),*[str(p) for p in files],'-q',*pytest_base,'--junitxml='+str(directory/'tests.xml')]
    p=subprocess.run(args,cwd=native,env=env,capture_output=True,timeout=240)
    (directory/(phase+'.stdout')).write_bytes(p.stdout);(directory/(phase+'.stderr')).write_bytes(p.stderr)
    if verify_l.native_inventory(native)!=ctx['native']:raise ValueError('L_NATIVE_CHANGED')
    if phase=='collect':
        if p.returncode:raise ValueError('L_NATIVE_PROCESS_FAILED')
        counts=None;status='PASS'
    else:
        counts,coverage=native_test_summary(directory/'tests.xml')
        allowed_exits={0,1} if counts['blocked'] else {0}
        if p.returncode not in allowed_exits:raise ValueError('L_NATIVE_PROCESS_DISPOSITION')
        status='BLOCKED' if counts['blocked'] else 'PASS'
    r={'schema':'cmba.native-stage.l1','phase':phase,'status':status,'context':ctx,'results':{'tests':counts},
       'legs':[{'name':phase,'exit_code':p.returncode}],
       'outputs':{p.name:verify_l.sha(p.read_bytes()) for p in directory.iterdir() if p.is_file()},'authority_effect':'NONE'}
    verify_l.write(directory/'STAGE.json',r);return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--dkn-source',type=Path,required=True);p.add_argument('--phase',choices=['collect','group0','group1','group2','group3','assemble'],required=True);a=p.parse_args()
    try:r=run(a.out.resolve(),a.dkn_source.resolve(),a.phase);code=3 if r.get('status','').startswith('BLOCKED') else 0
    except Exception as e:r={'status':'FAIL','error':str(e),'phase':a.phase};code=2
    print(json.dumps(r,sort_keys=True));raise SystemExit(code)
