"""Separate-language small-core replay. Not a full port or independent certification."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical,decode
from run_conformance import compare_output

def run():
    node=shutil.which('node')
    if not node:raise ValueError('L_NODE_REQUIRED')
    corpus=decode((ROOT/'interop/core-i1.json').read_bytes())
    request={'schema':'cmba.conformance-requests.i1','requests':[x['request'] for x in corpus['cases']]}
    expected={'schema':'cmba.conformance-results.i1','results':[x['expected'] for x in corpus['cases']]}
    p=subprocess.run([node,str(ROOT/'interop/node-l1/core.mjs')],input=canonical(request),capture_output=True,timeout=30)
    if p.returncode:raise ValueError('L_NODE_PROCESS:'+p.stderr.decode('utf8','replace'))
    compare_output(p.stdout,expected)
    return {'schema':'cmba.small-core-comparison.l1','status':'PASS','cases':len(corpus['cases']),
      'operations':['canonical','decode','dimension','bind','inspect','compare'],
      'comparison':'EXACT_CANONICAL_RESPONSE_BYTES','node':subprocess.check_output([node,'--version'],text=True).strip(),
      'checker_sha256':hashlib.sha256((ROOT/'interop/node-l1/core.mjs').read_bytes()).hexdigest(),
      'corpus_sha256':hashlib.sha256((ROOT/'interop/core-i1.json').read_bytes()).hexdigest(),
      'request_sha256':hashlib.sha256(canonical(request)).hexdigest(),
      'response_sha256':hashlib.sha256(p.stdout).hexdigest(),'full_alternative_realization':False,
      'independent_security_review':False,'authority_effect':'NONE'}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path);v=a.parse_args()
    try:r=run();code=0
    except Exception as e:r={'status':'FAIL','error':str(e),'authority_effect':'NONE'};code=2
    raw=canonical(r)+b'\n';sys.stdout.buffer.write(raw)
    if v.out:v.out.write_bytes(raw)
    raise SystemExit(code)
