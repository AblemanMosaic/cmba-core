"""Closed data-only J1 interface: no private keys, paths, plugin code or effects."""
from ..codec import canonical
from ..bindings import exact
from ..errors import require,Refusal
from .evaluation import evaluate,replay
from .registry import contracts,capabilities


def dispatch(request):
    canonical(request);exact(request, {'schema','operation','arguments'})
    require(request['schema']=='cmba.request.j1','CMBA_J_REQUEST_SCHEMA')
    op,a=request['operation'],request['arguments'];require(type(op) is str,'CMBA_J_OPERATION')
    if op=='evaluate':exact(a, {'binding','values','context'});result=evaluate(**a)
    elif op=='replay':exact(a, {'receipt','binding','values','context'});result=replay(**a)
    elif op=='profiles':exact(a,set());result=contracts()
    elif op=='capabilities':exact(a,set());result=capabilities()
    elif op=='verify-statement':
        from .endorsements import verify
        exact(a, {'record'});result={'body':verify(a['record']),'signature':'VALID','recognition':'NOT_CHECKED','authority_effect':'NONE'}
    elif op=='verify-envelope':
        from .endorsements import verify_envelope
        exact(a, {'envelope'});result=verify_envelope(a['envelope'])
    elif op=='verify-disclosure':
        from .disclosure import verify
        exact(a, {'view','expected_root'});result=verify(**a)
    elif op=='dkn-read':
        from .native import dispatch as dkn
        exact(a, {'request'});result=dkn(a['request'])
    else:raise Refusal('CMBA_J_OPERATION')
    canonical(result);return result
