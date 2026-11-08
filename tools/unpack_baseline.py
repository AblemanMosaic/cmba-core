"""Explicit, create-only extraction after verifying the pinned exact DKN ZIP."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,zipfile,stat
ROOT=Path(__file__).resolve().parents[1]
EXPECTED='c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3'
SOURCE=ROOT/'baseline/dkn/DKN-core-0.2.0rc5-BATCH-H-REVIEW-CANDIDATE.zip'

def verify():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=EXPECTED:raise ValueError('BASELINE_TRANSPORT_MISMATCH')
    with zipfile.ZipFile(SOURCE) as z:
        names=z.namelist();assert len(names)==len(set(names))==668
        for i in z.infolist():
            p=PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in i.filename or stat.S_ISLNK(i.external_attr>>16):raise ValueError('BASELINE_UNSAFE_PATH')
        manifest=json.loads(z.read('BATCH-H-FILE-MANIFEST.json'));rows=manifest['files']
        if set(names)!={r['path'] for r in rows}|{'BATCH-H-FILE-MANIFEST.json'}:raise ValueError('BASELINE_CLOSURE')
        for r in rows:
            raw=z.read(r['path'])
            if len(raw)!=r['bytes'] or hashlib.sha256(raw).hexdigest()!=r['sha256']:raise ValueError('BASELINE_MEMBER_MISMATCH')
    return {'status':'PASS','source_sha256':EXPECTED,'members':len(names),'authority_effect':'NONE'}

def unpack(destination):
    result=verify();dest=Path(destination)
    if dest.exists() and (not dest.is_dir() or list(dest.iterdir())):raise ValueError('DESTINATION_NOT_EMPTY')
    for p in (dest,*dest.parents):
        if p.is_symlink():raise ValueError('DESTINATION_SYMLINK')
    dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(SOURCE) as z:z.extractall(dest)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('destination',type=Path);a=p.parse_args();print(json.dumps(unpack(a.destination),sort_keys=True))
