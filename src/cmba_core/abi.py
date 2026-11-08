"""Closed, read-only JSON interface. No arbitrary evaluator or path in requests."""
from .bindings import exact, inspect, compare
from .codec import canonical
from .evaluation import evaluate, replay
from .registry import catalogue, capability_descriptors
from .errors import Refusal, require


def dispatch(request: dict) -> dict:
    canonical(request)
    exact(request, {'schema','operation','arguments'})
    require(request['schema']=='cmba.request.v0.1-i1','CMBA_REQUEST_SCHEMA')
    op=request['operation'];args=request['arguments']
    require(type(op) is str and type(args) is dict,'CMBA_REQUEST_TYPE')
    if op=='inspect':
        exact(args, {'binding','values','expected_root'})
        result=inspect(args['binding'],args['values'],expected_root=args['expected_root'])
    elif op=='compare':
        exact(args, {'left','right'});result=compare(**args)
    elif op=='evaluate':
        exact(args, {'binding','values','context'});result=evaluate(**args)
    elif op=='replay':
        exact(args, {'receipt','binding','values','context'});result=replay(**args)
    elif op=='catalogue':
        exact(args,set());result=catalogue()
    elif op=='capabilities':
        exact(args,set());result={'capabilities':capability_descriptors(),'authority_effect':'NONE'}
    else:raise Refusal('CMBA_OPERATION_UNSUPPORTED')
    canonical(result)
    return result
