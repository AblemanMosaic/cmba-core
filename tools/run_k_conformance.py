"""Frozen exact canonical output oracle. No expectation generation during verification."""
from pathlib import Path
import json,sys,argparse,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical,Refusal
from cmba_core.errors import require
from run_conformance import compare_output

def run(command=None,corpus=None):
    path=Path(corpus) if corpus else ROOT/'interop/workbench-k1.json'
    raw=path.read_bytes();require(len(raw)<=8*1024*1024,'CMBA_K_CORPUS_LIMIT')
    data=json.loads(raw);cases=data['cases'];require(1<=len(cases)<=256,'CMBA_K_CORPUS_LIMIT')
    require(len({c['id'] for c in cases})==len(cases),'CMBA_K_CORPUS_DUPLICATE')
    cmd=command or [sys.executable,str(ROOT/'tools/reference_k_conformance.py')]
    # Batch at most sixteen cases within an explicit bounded request/result envelope.
    # This changes execution grouping only, never the frozen expected values.
    groups=[];group=[]
    for case in cases:
        proposed=group+[case]
        req={'schema':'cmba.conformance-requests.k1','requests':[c['request'] for c in proposed]}
        expected={'schema':'cmba.conformance-results.k1','results':[c['expected'] for c in proposed]}
        if group and (len(proposed)>16 or len(canonical(req))>512*1024 or len(canonical(expected))>512*1024):
            groups.append(group);group=[case]
        else:group=proposed
    if group:groups.append(group)
    for group in groups:
        req={'schema':'cmba.conformance-requests.k1','requests':[c['request'] for c in group]}
        expected={'schema':'cmba.conformance-results.k1','results':[c['expected'] for c in group]}
        p=subprocess.run(cmd,input=canonical(req),capture_output=True,timeout=45)
        require(p.returncode==0,'CMBA_CONFORMANCE_PROCESS')
        compare_output(p.stdout,expected)
    return {'status':'PASS','cases':len(cases),'process_groups':len(groups),'corpus_sha256':hashlib.sha256(raw).hexdigest(),
      'oracle':'EXACT_CANONICAL_TYPED_RESULTS','alternative_command_selected':command is not None,
      'whole_program_equivalence':'NOT_ESTABLISHED','authority_effect':'NONE'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--corpus',type=Path);p.add_argument('--command',nargs=argparse.REMAINDER);a=p.parse_args()
    try:r=run(a.command,a.corpus);code=0
    except (Refusal,subprocess.TimeoutExpired) as e:r={'status':'FAIL','code':str(e),'authority_effect':'NONE'};code=2
    raw=canonical(r)+b'\n';sys.stdout.buffer.write(raw)
    if a.out:a.out.write_bytes(raw)
    raise SystemExit(code)
