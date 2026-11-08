"""Review-tool integrity checks, not a P/PPI host or runtime authority mechanism.

Trusted local interpreter/OS assumptions remain. These prevent accidental or supplied-file
ambiguity, not fabrication by an adversary controlling the verifier and all evidence.
"""
from pathlib import Path
import hashlib,json,os,stat,zipfile

MAX_RECORD_BYTES=16*1024*1024
STAGE_KEYS={'schema','phase','status','context','results','legs','outputs','authority_effect'}

def read_record(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('AUDIT_RECORD_KIND')
    with path.open('rb') as f:raw=f.read(MAX_RECORD_BYTES+1)
    if len(raw)>MAX_RECORD_BYTES:raise ValueError('AUDIT_RECORD_LIMIT')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('AUDIT_RECORD_DUPLICATE_FIELD')
            result[k]=v
        return result
    def number(_):raise ValueError('AUDIT_RECORD_NUMBER')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=number,parse_float=number)

def validate_stage_header(record,phase,allow_blocked=False):
    if phase in ('tests','workflows','audit'):schema='cmba.qualification-stage.l1'
    elif phase in ('collect','group0','group1','group2','group3'):schema='cmba.native-stage.l1'
    else:raise ValueError('AUDIT_STAGE_PHASE')
    if type(record) is not dict or set(record)!=STAGE_KEYS:raise ValueError('AUDIT_STAGE_FIELDS')
    if record['schema']!=schema or record['phase']!=phase:raise ValueError('AUDIT_STAGE_SCHEMA')
    statuses={'PASS','BLOCKED'} if allow_blocked and schema=='cmba.native-stage.l1' else {'PASS'}
    if record['status'] not in statuses or record['authority_effect']!='NONE':raise ValueError('AUDIT_STAGE_CLAIM')
    if type(record['context']) is not dict or type(record['results']) is not dict:raise ValueError('AUDIT_STAGE_BODY')
    if type(record['outputs']) is not dict or not record['outputs']:raise ValueError('AUDIT_STAGE_OUTPUTS')
    if type(record['legs']) is not list or not record['legs']:raise ValueError('AUDIT_STAGE_LEGS')
    permitted_exits={0,1} if allow_blocked and schema=='cmba.native-stage.l1' and record['status']=='BLOCKED' else {0}
    for leg in record['legs']:
        if type(leg) is not dict or set(leg)!={'name','exit_code'} or type(leg['name']) is not str or not leg['name']:
            raise ValueError('AUDIT_STAGE_LEG_FIELDS')
        if type(leg['exit_code']) is not int or leg['exit_code'] not in permitted_exits:raise ValueError('AUDIT_STAGE_LEG_EXIT')

def closed_native_tree(native,archive):
    """Reject extra noncache material before pytest can load local collection hooks.

Expected files are still byte-compared by verify_l.native_inventory. Ordinary generated
__pycache__ and root .pytest_cache files are excluded under the trusted-host boundary.
No Python source, symlink, junction or special file is allowed in an excluded cache.
"""
    native=Path(native)
    if native.is_symlink() or not native.is_dir():raise ValueError('AUDIT_NATIVE_ROOT')
    with zipfile.ZipFile(archive) as z:expected={i.filename for i in z.infolist() if not i.is_dir()}
    actual=set()
    def scan(directory):
        with os.scandir(directory) as entries:
            for ent in entries:
                p=Path(ent.path);rel=p.relative_to(native);name=rel.as_posix()
                if ent.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()):raise ValueError('AUDIT_NATIVE_LINK:'+name)
                st=ent.stat(follow_symlinks=False)
                if stat.S_ISDIR(st.st_mode):scan(p);continue
                if not stat.S_ISREG(st.st_mode):raise ValueError('AUDIT_NATIVE_FILE_KIND:'+name)
                if '__pycache__' in rel.parts:
                    if p.suffix!='.pyc':raise ValueError('AUDIT_NATIVE_CACHE_KIND:'+name)
                    continue
                if rel.parts[0]=='.pytest_cache':
                    if p.suffix in ('.py','.pyc','.pyo','.pth'):raise ValueError('AUDIT_NATIVE_CACHE_KIND:'+name)
                    continue
                actual.add(name)
    scan(native)
    if actual!=expected:
        raise ValueError('AUDIT_NATIVE_TREE_CLOSURE:'+json.dumps({'extra':sorted(actual-expected),'missing':sorted(expected-actual)},sort_keys=True))
    return {'members':len(actual),'policy':'EXACT_NONCACHE_MEMBERS'}

def root_test_configuration(root):
    """Include root pytest configuration/hooks previously outside the fingerprint's dirs."""
    result={}
    for name in ('conftest.py','pytest.ini','tox.ini','setup.cfg'):
        p=Path(root)/name
        if p.is_symlink():raise ValueError('AUDIT_ROOT_CONFIG_LINK')
        if p.exists() and not p.is_file():raise ValueError('AUDIT_ROOT_CONFIG_KIND')
        result[name]=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    return result

def test_environment(paths):
    env=os.environ.copy()
    # DISABLE_PLUGIN_AUTOLOAD alone excludes installed entrypoints, not explicit overrides.
    for name in ('PYTEST_ADDOPTS','PYTEST_PLUGINS','PYTEST_CURRENT_TEST','PYTEST_DEBUG'):
        env.pop(name,None)
    env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    env['PYTHONDONTWRITEBYTECODE']='1'
    env['PYTHONUTF8']='1'
    env['PYTHONPATH']=os.pathsep.join(str(p) for p in paths)
    return env
