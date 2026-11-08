"""K1 reference DATA adapter. No host approval or filesystem effect is exposed."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical,decode,Refusal
from cmba_core.bindings import exact
from cmba_core.errors import require
from cmba_workbench.k1.abi import dispatch as workbench_dispatch

def dispatch(request):
    try:return {'status':'RESULT','result':workbench_dispatch(request)}
    except Refusal as e:return {'status':'REFUSED','code':e.code,'authority_effect':'NONE'}

if __name__=='__main__':
    try:
        value=decode(sys.stdin.buffer.read(1048577));exact(value,{'schema','requests'})
        require(value['schema']=='cmba.conformance-requests.k1','CMBA_K_CONFORMANCE_SCHEMA')
        require(type(value['requests']) is list and 1<=len(value['requests'])<=16,'CMBA_K_CONFORMANCE_LIMIT')
        response={'schema':'cmba.conformance-results.k1','results':[dispatch(v) for v in value['requests']]}
        sys.stdout.buffer.write(canonical(response)+b'\n')
    except Refusal as e:
        sys.stdout.buffer.write(canonical({'status':'REFUSED','code':e.code,'authority_effect':'NONE'})+b'\n');raise SystemExit(2)
