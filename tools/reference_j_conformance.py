"""J1 test process adapter. Only an explicit host-selected process is executed by the runner."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical,decode,Refusal
from cmba_core.bindings import exact
from cmba_core.errors import require
from cmba_core.j1.abi import dispatch as abi

def dispatch(request):
    try:return {'status':'RESULT','value':abi(request)}
    except Refusal as exc:return {'status':'REFUSED','code':exc.code}

def main():
    try:
        r=decode(sys.stdin.buffer.read(1024*1024+1));exact(r, {'schema','requests'})
        require(r['schema']=='cmba.conformance-requests.j1','CMBA_J_CONFORMANCE_SCHEMA')
        require(type(r['requests']) is list and len(r['requests'])<=16,'CMBA_J_CONFORMANCE_LIMIT')
        result={'schema':'cmba.conformance-results.j1','results':[dispatch(x) for x in r['requests']]}
        sys.stdout.buffer.write(canonical(result)+b'\n');return 0
    except Refusal as e:
        sys.stdout.buffer.write(canonical({'status':'REFUSED','code':e.code})+b'\n');return 2
if __name__=='__main__':raise SystemExit(main())
