"""Check the frozen model and supplied execution references; never author/repair it."""
from pathlib import Path,PurePosixPath
import argparse,ast,hashlib,json,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical,decode
from cmba_core.bindings import digest


def checked_path(root,value):
    p=PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or '\\' in value:raise ValueError('MODEL_PATH_INVALID')
    return root/str(p)


def check(root=ROOT,junit=None,expected_commitment=None):
    c=decode((root/'model/CONTRACT.json').read_bytes());m=decode((root/'model/COMMITMENT.json').read_bytes())
    r=decode((root/'model/REALIZATION-BINDING.json').read_bytes())
    actual=digest('semantic-contract',c)
    if m['digest_hex']!=actual or r['semantic_commitment']!=actual:raise ValueError('MODEL_COMMITMENT_MISMATCH')
    if expected_commitment is not None and expected_commitment!=actual:raise ValueError('MODEL_EXPECTED_COMMITMENT_MISMATCH')
    for row in c['references']+r['files']:
        p=checked_path(root,row['path'])
        if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('MODEL_FILE_MISMATCH:'+row['path'])
    expected={o['id'] for o in c['obligations']};seen=set();cases=[]
    if junit:
        tree=ET.parse(junit)
        for case in tree.iter('testcase'):
            if case.find('failure') is not None or case.find('error') is not None or case.find('skipped') is not None:
                raise ValueError('MODEL_TEST_RUN_INCOMPLETE')
            cases.append((case.attrib.get('classname',''),case.attrib['name'].split('[',1)[0]))
    for row in r['traceability']:
        if row['id'] in seen:raise ValueError('MODEL_DUPLICATE_OBLIGATION')
        seen.add(row['id']);path=checked_path(root,row['test_file'])
        names={n.name for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        if row['test_function'] not in names:raise ValueError('MODEL_TEST_SYMBOL_MISSING')
        if not checked_path(root,row['implementation']).is_file():raise ValueError('MODEL_IMPLEMENTATION_MISSING')
        if junit:
            classname=row['test_file'].removesuffix('.py').replace('/','.')
            if (classname,row['test_function']) not in cases:raise ValueError('MODEL_EXECUTED_TEST_MISSING:'+row['test_function'])
    if seen!=expected:raise ValueError('MODEL_OBLIGATION_COVERAGE')
    return {'status':'PASS_REFERENCE_INTEGRITY','semantic_commitment':actual,'obligations':len(seen),
            'bound_files':len(r['files']),'reference_files':len(c['references']),
            'executed_test_binding':'CHECKED' if junit else 'NOT_CHECKED',
            'external_anchor':'MATCHED_CALLER_EXPECTATION' if expected_commitment else 'NOT_PROVIDED',
            'claim_ceiling':'TRACEABILITY_NOT_PROGRAM_EQUIVALENCE','authority_effect':'NONE'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--junit',type=Path);p.add_argument('--expected-commitment');p.add_argument('--out',type=Path);a=p.parse_args()
    try:result=check(junit=a.junit,expected_commitment=a.expected_commitment);code=0
    except (ValueError,OSError,KeyError) as e:result={'status':'FAIL','code':str(e),'authority_effect':'NONE'};code=2
    raw=canonical(result)+b'\n';sys.stdout.buffer.write(raw)
    if a.out:a.out.write_bytes(raw)
    raise SystemExit(code)
