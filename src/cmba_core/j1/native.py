"""Explicit read-only adapters to exact frozen DKN runtime. Never install or migrate.

JSON accepts only data. Filesystem readers are separate Python calls with host-chosen
paths, unavailable through the JSON ABI. Native read semantics are retained verbatim.
"""
import importlib
from ..profiles.dkn import load_native, bind_archive
from ..codec import canonical
from ..bindings import exact, hex_digest
from ..errors import Refusal, require
from .common import hex_bytes


def _module(name):
    load_native()  # hash-check all dkn_v02 modules BEFORE using the optional native runtime
    try:return importlib.import_module('dkn_v02.'+name)
    except ImportError as e:raise Refusal('CMBA_DKN_DEPENDENCY_UNAVAILABLE') from e


def dispatch(request):
    canonical(request);exact(request, {'operation','arguments'})
    op,a=request['operation'],request['arguments'];require(type(op) is str,'CMBA_J_NATIVE_OPERATION')
    native=load_native()
    try:
        if op=='archive':
            exact(a, {'archive_hex','expected_root','certificate'})
            result=bind_archive(hex_bytes(a['archive_hex']),expected_logical_root=a['expected_root'],certificate=a['certificate'])
        elif op=='namespace':
            exact(a, {'genesis','transitions'})
            result=native.verify_transitions(a['genesis'],a['transitions'])
        elif op=='lineage':
            exact(a, {'genesis','chains'});result=_module('lineage').analyze_lineage(**a)
        elif op in ('lifecycle','assurance','distributed'):
            exact(a, {'request'});module={'lifecycle':'lifecycle_abi','assurance':'sam_abi','distributed':'distributed_abi'}[op]
            result=_module(module).dispatch(a['request'])
        else:raise Refusal('CMBA_J_NATIVE_OPERATION')
    except native.Refusal as e:raise Refusal('CMBA_J_NATIVE_REFUSED:'+e.code) from e
    canonical(result)
    return {'schema':'cmba.native-result.j1','operation':op,'native_result':result,
            'native_semantics':'PRESERVED_NOT_UPGRADED','authority_effect':'NONE'}


def read_collection(path, operation, arguments, *, kind):
    """Host-selected existing storage only. Trusted local filesystem/custody assumed."""
    require(kind in ('index','vault'),'CMBA_J_NATIVE_COLLECTION')
    require(type(operation) is str,'CMBA_J_NATIVE_OPERATION');canonical(arguments)
    allowed={'resolve_exact':{'logical_root'},'discover':{'semantic_name'},
             'traverse':{'logical_root','direction','max_depth','max_nodes','max_edges'},
             'compare_namespace':{'namespace_root'}}
    if kind=='vault':
        allowed.pop('compare_namespace')
        allowed['traverse']={'logical_root','direction','max_depth','max_nodes'}
        allowed['read_namespace']={'namespace_root'}
    require(operation in allowed,'CMBA_J_NATIVE_OPERATION');exact(arguments,allowed[operation])
    native=load_native()
    try:
        instance=(_module('vault').TransactionalVault(path) if kind=='vault' else _module('navigation').LocalIndex(path))
        result=getattr(instance,operation)(**arguments)
    except native.Refusal as e:raise Refusal('CMBA_J_NATIVE_REFUSED:'+e.code) from e
    canonical(result)
    return {'schema':'cmba.native-result.j1','operation':operation,'native_result':result,
            'native_semantics':'PRESERVED_NOT_UPGRADED','authority_effect':'NONE'}
