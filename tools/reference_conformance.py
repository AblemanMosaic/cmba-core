"""Explicit reference process adapter for stable core behavior (not production ABI)."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from cmba_core import canonical,decode,dimension,bind,inspect,compare,Refusal
from cmba_core.bindings import exact
from cmba_core.errors import require

def dispatch(request):
    try:
        exact(request,{'operation','arguments'});op=request['operation'];args=request['arguments']
        require(type(args) is dict,'CMBA_ARGUMENT_TYPE')
        if op=='canonical':
            exact(args,{'value'});value={'hex':canonical(args['value']).hex()}
        elif op=='decode':
            exact(args,{'hex'})
            try:raw=bytes.fromhex(args['hex'])
            except (ValueError,TypeError):raise Refusal('CMBA_BYTES_REQUIRED')
            value=decode(raw)
        elif op=='dimension':
            exact(args,{'dimension_id','role','schema_id','value','critical'});value=dimension(**args)
        elif op=='bind':
            exact(args,{'profile','dimensions','relations'});value=bind(**args)
        elif op=='inspect':
            exact(args,{'binding','values','expected_root'});value=inspect(**args)
        elif op=='compare':
            exact(args,{'left','right'});value=compare(**args)
        else:raise Refusal('CMBA_OPERATION_UNSUPPORTED')
        return {'status':'RESULT','value':value}
    except Refusal as exc:
        return {'status':'REFUSED','code':exc.code}

def main():
    try:
        request=decode(sys.stdin.buffer.read(2*1024*1024))
        exact(request,{'schema','requests'});require(request['schema']=='cmba.conformance-requests.i1','CMBA_REQUEST_SCHEMA')
        require(type(request['requests']) is list and len(request['requests'])<=256,'CMBA_COLLECTION_LIMIT')
        result={'schema':'cmba.conformance-results.i1','results':[dispatch(r) for r in request['requests']]}
        sys.stdout.buffer.write(canonical(result)+b'\n');return 0
    except Refusal as exc:
        sys.stdout.buffer.write(canonical({'status':'REFUSED','code':exc.code})+b'\n');return 2
if __name__=='__main__':raise SystemExit(main())
