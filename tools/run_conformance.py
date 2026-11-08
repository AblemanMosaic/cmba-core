"""Exact-result oracle. Only a host-selected explicit executable may be invoked."""
from pathlib import Path
import argparse,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical,decode
from cmba_core.errors import require,Refusal


def compare_output(raw,expected):
    require(type(raw) is bytes and len(raw)<=1024*1024,'CMBA_CONFORMANCE_OUTPUT_LIMIT')
    # One framing newline is transport only; all remaining bytes must be canonical.
    payload=raw[:-1] if raw.endswith(b'\n') else raw
    actual=decode(payload)
    require(canonical(actual)==canonical(expected),'CMBA_CONFORMANCE_MISMATCH')
    return True


def run(command=None):
    corpus=decode((ROOT/'interop/core-i1.json').read_bytes())
    request={'schema':'cmba.conformance-requests.i1','requests':[c['request'] for c in corpus['cases']]}
    expected={'schema':'cmba.conformance-results.i1','results':[c['expected'] for c in corpus['cases']]}
    cmd=command or [sys.executable,str(ROOT/'tools/reference_conformance.py')]
    result=subprocess.run(cmd,input=canonical(request),capture_output=True,timeout=30)
    require(result.returncode==0,'CMBA_CONFORMANCE_PROCESS')
    compare_output(result.stdout,expected)
    return {'status':'PASS','cases':len(corpus['cases']),'oracle':'EXACT_CANONICAL_RESPONSE_BYTES',
            'alternative_realization':command is not None,'whole_program_equivalence':'NOT_ESTABLISHED','authority_effect':'NONE'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--command',nargs=argparse.REMAINDER);p.add_argument('--out',type=Path);a=p.parse_args()
    try:r=run(a.command);status=0
    except (Refusal,subprocess.TimeoutExpired) as e:r={'status':'FAIL','code':str(e),'authority_effect':'NONE'};status=2
    raw=canonical(r)+b'\n';sys.stdout.buffer.write(raw)
    if a.out:a.out.write_bytes(raw)
    raise SystemExit(status)
