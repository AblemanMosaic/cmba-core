"""AUTHORING ONLY: renew source bindings after deliberate model/corpus authoring.
Verification never invokes this tool. Pin expected commits before accepting a candidate.
"""
from pathlib import Path
import sys,hashlib,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical,decode
PINS={'model':'2f7ae78f19f7c06e85b176a9f2e1eb83383b41edb158e61c4fb16b653ca34e32','model/j1':'9f8808f3e3f2862f2403355d5484e39475472cc8ad1d4011c0c9a53c32f9e8d3','model/k1':'5df7a5b7230843bba99b93115c08a97d457b82366225d700cb3bb5f7313e9a7b'}
def main():
    paths=[]
    for directory in ('src','tests','tools','examples','schemas','interop'):
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in ('.py','.json','.mjs','.ps1','.sh') and '__pycache__' not in p.parts)
    paths.extend(ROOT/n for n in ('pyproject.toml','RELEASE-BOUNDARY.json'))
    rows=[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(paths))]
    for folder,pin in PINS.items():
        assert decode((ROOT/folder/'COMMITMENT.json').read_bytes())['digest_hex']==pin
        path=ROOT/folder/'REALIZATION-BINDING.json';record=decode(path.read_bytes());record['files']=rows;path.write_bytes(canonical(record))
    print(json.dumps({'authoring':'EXPLICIT_SOURCE_BINDINGS_ONLY','bound_files':len(rows),'semantic_commits':PINS}))
if __name__=='__main__':main()
