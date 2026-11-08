"""Deterministically serialize a frozen tree. Inventory is external to its own hash.

Build explicitly authors FILE-MANIFEST.json. Verification never edits an archive.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,stat,zipfile,io,re,unicodedata
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'__pycache__','.pytest_cache','.venv','build','dist','.git'}


def link_like(path):
    return path.is_symlink() or (hasattr(path,'is_junction') and path.is_junction())


def members(root):
    result={}
    # pathlib orders host-native Path objects.  Sort the serialized relative
    # names instead so Windows and POSIX author the same manifest row order.
    paths=sorted(root.rglob('*'),key=lambda p:p.relative_to(root).as_posix())
    for p in paths:
        rel=p.relative_to(root)
        if any(part in EXCLUDE or part.endswith('.egg-info') for part in rel.parts):continue
        if link_like(p):raise ValueError('PACKAGE_SYMLINK')
        if not p.is_dir() and not stat.S_ISREG(p.stat().st_mode):raise ValueError('PACKAGE_FILE_KIND')
        if p.is_file() and p.suffix not in ('.pyc','.pyo') and rel.as_posix()!='FILE-MANIFEST.json':
            result[rel.as_posix()]=p.read_bytes()
    return result


def build(out,root=ROOT):
    out=Path(out).resolve()
    if out.is_relative_to(root.resolve()):raise ValueError('OUTPUT_MUST_BE_OUTSIDE_SOURCE_TREE')
    files=members(root)
    validate_names(list(files)+['FILE-MANIFEST.json'])
    manifest={'schema':'cmba.source-inventory.i1','scope':'ALL_MEMBERS_EXCEPT_THIS_MANIFEST',
      'files':[{'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for p,b in files.items()],
      'baseline_dkn_sha256':'c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3',
      'authority_effect':'NONE','signature':'NOT_SIGNED'}
    raw=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    (root/'FILE-MANIFEST.json').write_bytes(raw);files['FILE-MANIFEST.json']=raw
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED) as z:
        for p,b in sorted(files.items()):
            i=zipfile.ZipInfo(p,(1980,1,1,0,0,0));i.create_system=3;i.external_attr=(stat.S_IFREG|0o644)<<16
            z.writestr(i,b)
    return verify(out)


# Limits for the SOURCE DOSSIER, not the runtime's much smaller payload profile.
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_MEMBERS = 4096
MAX_MEMBER_BYTES = 128 * 1024 * 1024
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
BASELINE = 'c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3'


def safe_name(name):
    if type(name) is not str or not name or len(name) > 512:
        raise ValueError('ARCHIVE_PATH')
    if unicodedata.normalize('NFC', name) != name or '\\' in name or ':' in name:
        raise ValueError('ARCHIVE_PATH')
    if any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ValueError('ARCHIVE_PATH')
    parts = name.split('/')
    reserved = {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]}
    if any(x in ('', '.', '..') or x.endswith((' ', '.')) or x.split('.')[0].upper() in reserved
           or any(c in '<>"|?*' for c in x) for x in parts):
        raise ValueError('ARCHIVE_PATH')
    return name


def validate_names(names):
    seen=set()
    for name in names:
        safe_name(name)
        key=name.casefold()
        if key in seen: raise ValueError('ARCHIVE_PATH_ALIAS')
        seen.add(key)
    for name in seen:
        parts=name.split('/')
        if any('/'.join(parts[:i]) in seen for i in range(1,len(parts))):
            raise ValueError('ARCHIVE_FILE_DIRECTORY_ALIAS')


def strict_json(raw):
    def pairs(items):
        obj={}
        for k,v in items:
            if k in obj: raise ValueError('MANIFEST_DUPLICATE_FIELD')
            obj[k]=v
        return obj
    def number(_):raise ValueError('MANIFEST_NUMBER')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_float=number,parse_constant=number)


def verify(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file(): raise ValueError('ARCHIVE_FILE_KIND')
    if p.stat().st_size > MAX_ARCHIVE_BYTES: raise ValueError('ARCHIVE_SIZE_LIMIT')
    with p.open('rb') as f: raw=f.read(MAX_ARCHIVE_BYTES+1)
    if len(raw)>MAX_ARCHIVE_BYTES: raise ValueError('ARCHIVE_SIZE_LIMIT')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        infos=z.infolist(); names=[i.filename for i in infos]
        if not 1 <= len(names) <= MAX_MEMBERS: raise ValueError('ARCHIVE_MEMBER_LIMIT')
        if len(names)!=len(set(names)):raise ValueError('ARCHIVE_DUPLICATE')
        validate_names(names)
        if sum(i.file_size for i in infos)>MAX_ARCHIVE_BYTES: raise ValueError('ARCHIVE_EXPANSION_LIMIT')
        if 'FILE-MANIFEST.json' not in names:raise ValueError('ARCHIVE_MANIFEST_MISSING')
        if z.getinfo('FILE-MANIFEST.json').file_size>MAX_MANIFEST_BYTES: raise ValueError('MANIFEST_SIZE_LIMIT')
        m=strict_json(z.read('FILE-MANIFEST.json'))
        if (type(m) is not dict or set(m)!={'schema','scope','files','baseline_dkn_sha256','authority_effect','signature'}
                or m['schema']!='cmba.source-inventory.i1' or m['scope']!='ALL_MEMBERS_EXCEPT_THIS_MANIFEST'
                or m['baseline_dkn_sha256']!=BASELINE or m['authority_effect']!='NONE' or m['signature']!='NOT_SIGNED'):
            raise ValueError('MANIFEST_FIELDS')
        rows=m['files']
        if type(rows) is not list or len(rows)!=len(names)-1:raise ValueError('ARCHIVE_CLOSURE')
        if [r.get('path') for r in rows if type(r) is dict]!=sorted(
                (r.get('path') for r in rows if type(r) is dict)):
            raise ValueError('MANIFEST_ORDER')
        for r in rows:
            if type(r) is not dict or set(r)!={'path','bytes','sha256'}:raise ValueError('MANIFEST_ROW')
            safe_name(r['path'])
            if type(r['bytes']) is not int or not 0<=r['bytes']<=MAX_MEMBER_BYTES:raise ValueError('MANIFEST_SIZE_TYPE')
            if type(r['sha256']) is not str or not re.fullmatch('[0-9a-f]{64}',r['sha256']):raise ValueError('MANIFEST_DIGEST')
        if len(rows)!=len({r['path'] for r in rows}):raise ValueError('MANIFEST_DUPLICATE')
        if set(names)!={r['path'] for r in rows}|{'FILE-MANIFEST.json'}:raise ValueError('ARCHIVE_CLOSURE')
        for i in infos:
            mode=i.external_attr>>16
            if (i.is_dir() or i.create_system != 3 or stat.S_IFMT(mode)!=stat.S_IFREG
                    or i.flag_bits & 1 or i.compress_type != zipfile.ZIP_STORED):
                raise ValueError('ARCHIVE_MEMBER_KIND_OR_ENCODING')
            if i.file_size>MAX_MEMBER_BYTES: raise ValueError('ARCHIVE_MEMBER_SIZE_LIMIT')
        for r in rows:
            b=z.read(r['path'])
            if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('ARCHIVE_MEMBER_MISMATCH')
    return {'status':'PASS','members':len(names),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'authority_effect':'NONE'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--verify',type=Path);a=p.parse_args()
    if bool(a.out)==bool(a.verify):p.error('select exactly one of --out or --verify')
    print(json.dumps(build(a.out) if a.out else verify(a.verify),sort_keys=True))
