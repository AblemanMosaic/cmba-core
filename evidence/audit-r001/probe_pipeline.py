"""Local audit witnesses against unmodified Batch L tooling; no external effects."""
from pathlib import Path
import sys,json,shutil,copy,subprocess,os,hashlib
R=Path(__file__).resolve().parent; B=R/'baseline'
sys.path[:0]=[str(B/'src'),str(B/'tools')]
import verify_l
out=R/'witnesses';out.mkdir(exist_ok=True)
rows=[]
original=R/'cmba-replay'
ctx=json.loads((original/'tests/STAGE.json').read_text())['context']
for label,field,value in [('stage-authority','authority_effect','EXECUTE'),('stage-schema','schema','foreign.success.v99')]:
 target=out/label;shutil.copytree(original,target)
 p=target/'tests/STAGE.json';v=json.loads(p.read_text());v[field]=value;p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
 try:
  result=verify_l.assemble(target,ctx);observation={'accepted':True,'status':result['status'],'final_authority_effect':result['authority_effect']}
 except Exception as e:observation={'accepted':False,'error':str(e)}
 rows.append({'case':label,'changed_field':field,'value':value,**observation})
# A duplicate JSON context property is accepted by the ordinary JSON loader.
target=out/'duplicate-stage-field';shutil.copytree(original,target)
p=target/'tests/STAGE.json';raw=p.read_text();raw=raw.replace('"status": "PASS"','"status": "FAIL", "status": "PASS"');p.write_text(raw)
try:
 result=verify_l.assemble(target,ctx);observation={'accepted':True,'status':result['status']}
except Exception as e:observation={'accepted':False,'error':str(e)}
rows.append({'case':'duplicate-stage-field',**observation})
# A newly added root conftest removes one test from collection without changing expected files.
native=out/'native-contaminated';shutil.copytree(R/'dkn-h',native,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
plugin='def pytest_collection_modifyitems(items):\n    items[:] = [i for i in items if i.nodeid != "tests_v02/test_batch_b.py::test_pack_verify"]\n'
(native/'conftest.py').write_text(plugin)
try:
 inventory=verify_l.native_inventory(native)
 env=os.environ.copy();env.update(PYTHONPATH=os.pathsep.join([str(native/'src'),str(native)]),PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1')
 p=subprocess.run([sys.executable,'-m','pytest','tests_v02','--collect-only','-q','-o','addopts='],cwd=native,env=env,capture_output=True,timeout=40)
 (out/'contaminated-collect.stdout').write_bytes(p.stdout);(out/'contaminated-collect.stderr').write_bytes(p.stderr)
 nodes=[s for s in p.stdout.decode().splitlines() if s.startswith('tests_v02/') and '::' in s]
 rows.append({'case':'extra-native-conftest','inventory':inventory,'collection_exit':p.returncode,'collected_count':len(nodes),'expected_unmodified_count':1173,'removed_node':'tests_v02/test_batch_b.py::test_pack_verify','extra_file_sha256':hashlib.sha256(plugin.encode()).hexdigest()})
except Exception as e:rows.append({'case':'extra-native-conftest','error':str(e)})
(R/'evidence/PRE-REPAIR-WITNESSES.json').write_text(json.dumps(rows,sort_keys=True,indent=2)+'\n')
print(json.dumps(rows,indent=2))
