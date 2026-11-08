"""Data-only catalogue and explicit built-in profile contracts.

No plugin discovery, dynamic import from manifests, URL retrieval or executable paths.
The installed package is part of the host trust base, not self-authenticating code.
"""
from importlib.resources import files
from .codec import decode, clone, canonical
from .bindings import profile_reference, validate_profile_reference
from .errors import require


def _data(name):
    return decode(files('cmba_core').joinpath('data', name).read_bytes(), canonical_required=False)


def catalogue():
    return _data('catalogue.json')


def contracts():
    return _data('profiles.json')


def contract(profile_id: str):
    require(type(profile_id) is str, 'CMBA_PROFILE_UNSUPPORTED')
    matches=[c for c in contracts() if c['profile_id']==profile_id]
    require(len(matches)==1, 'CMBA_PROFILE_UNSUPPORTED')
    return matches[0]


def resolve_profile(ref):
    validate_profile_reference(ref)
    result=contract(ref['profile_id'])
    require(canonical(profile_reference(result))==canonical(ref), 'CMBA_PROFILE_COMMITMENT_MISMATCH')
    return result


def capability_descriptors():
    return [{'schema':'cmba.capability.v0.1-i1','capability_id':c['profile_id']+'.evaluate',
             'profile':profile_reference(c),'inputs':'binding, supplied values, reader context',
             'effect_class':'PURE_READ','requires_host_selection':True,'network':False,'subprocess':False,
             'auto_install':False,'authority_effect':'NONE','claim_ceiling':c['claim_ceiling']}
            for c in contracts()]
