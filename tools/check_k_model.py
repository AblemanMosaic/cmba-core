"""Read-only K1 contract/source/test traceability check. Does not repair or authorize."""
from pathlib import Path
import sys,hashlib,ast,xml.etree.ElementTree as ET,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical,decode
from cmba_workbench.k1.common import hash_value
from check_model import checked_path


def check(root=ROOT, *, junit=None,expected_commitment=None):
    c=decode((root/'model/k1/CONTRACT.json').read_bytes());m=decode((root/'model/k1/COMMITMENT.json').read_bytes());r=decode((root/'model/k1/REALIZATION-BINDING.json').read_bytes())
    h=hash_value('semantic-contract',c)
    if m['digest_hex']!=h or r['semantic_commitment']!=h:raise ValueError('K_MODEL_COMMITMENT')
    if expected_commitment is not None and expected_commitment!=h:raise ValueError('K_MODEL_EXPECTED_COMMITMENT')
    for folder,expected in c['base_semantic_commitments'].items():
        if decode((root/folder/'COMMITMENT.json').read_bytes())['digest_hex']!=expected:raise ValueError('K_BASE_MODEL_MISMATCH')
    for row in c['references']+r['files']:
        p=checked_path(root,row['path'])
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('K_MODEL_FILE:'+row['path'])
    cases=set()
    if junit:
        for case in ET.parse(junit).iter('testcase'):
            if any(x.tag in ('failure','error','skipped') for x in case):raise ValueError('K_MODEL_INCOMPLETE_RUN')
            cases.add((case.get('classname',''),case.get('name','').split('[',1)[0]))
    expected={o['id'] for o in c['obligations']};seen=set()
    for row in r['traceability']:
        if row['id'] in seen:raise ValueError('K_MODEL_DUPLICATE')
        seen.add(row['id']);test=checked_path(root,row['test_file'])
        names={n.name for n in ast.walk(ast.parse(test.read_text())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        if row['test_function'] not in names or not checked_path(root,row['implementation']).is_file():raise ValueError('K_MODEL_SYMBOL')
        if junit and (row['test_file'].removesuffix('.py').replace('/','.'),row['test_function']) not in cases:raise ValueError('K_MODEL_EXECUTED_TEST')
    if seen!=expected:raise ValueError('K_MODEL_COVERAGE')
    return {'status':'PASS_REFERENCE_INTEGRITY','semantic_commitment':h,'obligations':len(seen),
      'bound_files':len(r['files']),'executed_test_binding':'CHECKED' if junit else 'NOT_CHECKED',
      'external_anchor':'MATCHED' if expected_commitment else 'NOT_PROVIDED','claim_ceiling':'TRACEABILITY_NOT_PROGRAM_EQUIVALENCE','authority_effect':'NONE'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--junit',type=Path);p.add_argument('--expected-commitment');a=p.parse_args()
    try:result=check(junit=a.junit,expected_commitment=a.expected_commitment);code=0
    except Exception as e:result={'status':'FAIL','error':str(e),'authority_effect':'NONE'};code=2
    print(canonical(result).decode());raise SystemExit(code)
