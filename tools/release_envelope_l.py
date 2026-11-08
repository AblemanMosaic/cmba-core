"""Unsigned external review envelope: exact artifacts + model/governance commitments.

No circular dependency: hash the explicit body, then attach binding_root. Never put
this envelope's hash inside its own artifact list. Verification does not mutate files.
"""
from pathlib import Path
import argparse,hashlib,json,sys,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical,decode
DOMAIN=b'CMBA:ENGINEERING-RELEASE:L1\0'

def sha(b):return hashlib.sha256(b).hexdigest()
def root(body):return sha(DOMAIN+canonical(body))
def name_ok(name):
    if type(name) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,160}',name) or '..' in name:
        raise ValueError('L_ENVELOPE_NAME')

def build(paths,out):
    paths=[Path(p).resolve() for p in paths];out=Path(out).resolve()
    if out in paths or len(paths)!=len({p.name for p in paths}):raise ValueError('L_ENVELOPE_SELF_OR_DUPLICATE')
    rows=[]
    for p in sorted(paths,key=lambda p:p.name):
        name_ok(p.name)
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) or not p.is_file():raise ValueError('L_ENVELOPE_MEMBER_KIND')
        b=p.read_bytes();rows.append({'name':p.name,'bytes':len(b),'sha256':sha(b)})
    models={folder:decode((ROOT/folder/'COMMITMENT.json').read_bytes())['digest_hex'] for folder in ['model','model/j1','model/k1']}
    body={'schema':'cmba.engineering-release-body.l1','distribution':'cmba-core','version':'0.1.0a4','artifacts':rows,
      'semantic_commitments':models,'release_boundary_sha256':sha((ROOT/'RELEASE-BOUNDARY.json').read_bytes()),
      'source_inventory_sha256':sha((ROOT/'FILE-MANIFEST.json').read_bytes()),'source_predecessor_sha256':'e2fd92eddb6fd5138665c016b4dc94f54196b8dc7de9995c4370cdbd01c911da',
      'standing':'INFORMATION_ONLY','authority_effect':'NONE','signature':'NOT_SIGNED','public_release_gate':'NOT_CLEARED'}
    envelope={'schema':'cmba.engineering-release-envelope.l1','body':body,'binding_root':root(body)}
    out.write_bytes(canonical(envelope));return envelope

def verify(path,directory):
    path=Path(path);directory=Path(directory)
    v=decode(path.read_bytes())
    if type(v) is not dict or set(v)!={'schema','body','binding_root'} or v['schema']!='cmba.engineering-release-envelope.l1':raise ValueError('L_ENVELOPE_SCHEMA')
    b=v['body'];keys={'schema','distribution','version','artifacts','semantic_commitments','release_boundary_sha256','source_inventory_sha256','source_predecessor_sha256','standing','authority_effect','signature','public_release_gate'}
    if type(b) is not dict or set(b)!=keys or b['schema']!='cmba.engineering-release-body.l1':raise ValueError('L_ENVELOPE_BODY')
    if root(b)!=v['binding_root']:raise ValueError('L_ENVELOPE_ROOT')
    if (b['authority_effect']!='NONE' or b['signature']!='NOT_SIGNED' or b['public_release_gate']!='NOT_CLEARED'
        or b['standing']!='INFORMATION_ONLY' or b['distribution']!='cmba-core' or b['version']!='0.1.0a4'):raise ValueError('L_ENVELOPE_CLAIM')
    rows=b['artifacts'];seen=set()
    if type(rows) is not list or not 1<=len(rows)<=32:raise ValueError('L_ENVELOPE_ARTIFACTS')
    for row in rows:
        if type(row) is not dict or set(row)!={'name','bytes','sha256'}:raise ValueError('L_ENVELOPE_ROW')
        name_ok(row['name'])
        if row['name'] in seen or row['name']==path.name:raise ValueError('L_ENVELOPE_SELF_OR_DUPLICATE')
        seen.add(row['name'])
        if type(row['bytes']) is not int or not 0<=row['bytes']<=256*1024*1024:raise ValueError('L_ENVELOPE_SIZE')
        p=directory/row['name']
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) or not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p.read_bytes())!=row['sha256']:raise ValueError('L_ENVELOPE_MEMBER_MISMATCH')
    # Verify frozen semantics and source inventory in the actual listed source archive,
    # not merely the installed verifier's own adjacent files.
    sources=[r for r in rows if r['name']=='CMBA-Core-0.1.0a4-BATCH-L-REVIEW-CANDIDATE.zip']
    if len(sources)!=1:raise ValueError('L_ENVELOPE_SOURCE_REQUIRED')
    import zipfile
    import package
    package.verify(directory/sources[0]['name'])
    with zipfile.ZipFile(directory/sources[0]['name']) as z:
        if sha(z.read('RELEASE-BOUNDARY.json'))!=b['release_boundary_sha256'] or sha(z.read('FILE-MANIFEST.json'))!=b['source_inventory_sha256']:raise ValueError('L_ENVELOPE_SOURCE_BINDING')
        for folder,pin in b['semantic_commitments'].items():
            if folder not in ('model','model/j1','model/k1'):raise ValueError('L_ENVELOPE_MODEL_PATH')
            if decode(z.read(folder+'/COMMITMENT.json'))['digest_hex']!=pin:raise ValueError('L_ENVELOPE_MODEL_PIN')
        if set(b['semantic_commitments'])!={'model','model/j1','model/k1'}:raise ValueError('L_ENVELOPE_MODELS_INCOMPLETE')
    return {'status':'PASS_EXACT_LISTED_ARTIFACTS','artifacts':len(rows),'binding_root':v['binding_root'],
      'authentication':'NOT_ESTABLISHED_UNSIGNED','authority_effect':'NONE','public_release_gate':'NOT_CLEARED'}

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--build',type=Path);g.add_argument('--verify',type=Path);p.add_argument('--directory',type=Path);p.add_argument('members',nargs='*',type=Path);a=p.parse_args()
    try:r=build(a.members,a.build) if a.build else verify(a.verify,a.directory or a.verify.parent);code=0
    except Exception as e:r={'status':'FAIL','error':str(e)};code=2
    print(canonical(r).decode());raise SystemExit(code)
