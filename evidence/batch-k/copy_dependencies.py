from pathlib import Path
import importlib.metadata as m,json,hashlib,sysconfig,subprocess,shutil
names=('cryptography','cffi','pycparser','jsonschema','attrs','jsonschema-specifications','referencing','rpds-py','typing-extensions','Pillow')
target=Path(subprocess.check_output(['/mnt/data/cmba_k_optional_env/bin/python','-c','import sysconfig;print(sysconfig.get_paths()["purelib"])'],text=True).strip())
rows=[]
for name in names:
    dist=m.distribution(name);base=Path(dist.locate_file('')).resolve();files=[]
    for f in dist.files or []:
        src=Path(dist.locate_file(f)).resolve()
        if not src.is_relative_to(base) or not src.is_file() or src.suffix=='.pyc' or '__pycache__' in src.parts:continue
        rel=src.relative_to(base);dst=target/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        h=hashlib.sha256(src.read_bytes()).hexdigest();assert hashlib.sha256(dst.read_bytes()).hexdigest()==h
        files.append({'path':rel.as_posix(),'sha256':h})
    rows.append({'distribution':name,'version':dist.version,'files':files})
report={'schema':'cmba.k-installed-dependencies','source':'EXACT_COPIES_OF_GENUINE_HOST_DISTRIBUTIONS','fresh_resolution':'NOT_ESTABLISHED','distributions':rows}
Path('/mnt/data/cmba_k_runs/INSTALL-DEPENDENCIES.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print([(r['distribution'],r['version'],len(r['files'])) for r in rows])
