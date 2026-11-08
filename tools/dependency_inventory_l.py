"""Local observed build/test inventory. Not a vulnerability scan or supply-chain attestation."""
from pathlib import Path
import argparse,hashlib,importlib.metadata,json,platform,sys,sqlite3,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
def run():
    rows=[]
    for name in ('cryptography','cffi','pycparser','jsonschema','attrs','referencing','rpds-py','jsonschema-specifications','pytest','Pillow','setuptools','packaging','iniconfig','pluggy','Pygments','blake3'):
        try:d=importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:rows.append({'name':name,'status':'UNAVAILABLE'});continue
        meta=d.read_text('METADATA') or ''
        rows.append({'name':d.metadata.get('Name',name),'version':d.version,'metadata_sha256':hashlib.sha256(meta.encode()).hexdigest(),
          'license_expression':d.metadata.get('License-Expression'),'license_text_metadata':d.metadata.get('License'),
          'requires_dist':d.metadata.get_all('Requires-Dist') or [],'source':'GENUINE_PREINSTALLED_DISTRIBUTION','status':'OBSERVED'})
    try:
        import tkinter
        tk= tkinter.Tcl().eval('info patchlevel')
    except Exception:tk='UNAVAILABLE'
    return {'schema':'cmba.observed-component-inventory.l1','distribution':'cmba-core','distribution_version':'0.1.0a6',
      'core_runtime_dependencies':[],'optional_requirements':{'signing':['cryptography>=46,<47'],'dkn':['dkn-core==0.2.0rc5']},
      'python':sys.version,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version,'tcl':tk,
      'node':subprocess.check_output([shutil.which('node'),'--version'],text=True).strip() if shutil.which('node') else 'UNAVAILABLE',
      'components':rows,'fresh_dependency_resolution':'NOT_ESTABLISHED','vulnerability_scan':'NOT_PERFORMED',
      'license_legal_review':'NOT_PERFORMED','reproducible_dependency_downloads':'NOT_ESTABLISHED',
      'format':'PROJECT_COMPONENT_INVENTORY_NOT_CLAIMED_SPDX_OR_CYCLONEDX','authority_effect':'NONE'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);a=p.parse_args();r=run();a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print('observed',len(r['components']),'components')
