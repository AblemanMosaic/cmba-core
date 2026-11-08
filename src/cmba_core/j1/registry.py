"""Closed installed J1 application registry. No paths or code imports from input data."""
from importlib.resources import files
from ..codec import decode, canonical
from ..bindings import profile_reference, validate_profile_reference
from ..errors import require


def contracts():
    return decode(files('cmba_core').joinpath('data/j1-profiles.json').read_bytes())


def contract(profile_id):
    require(type(profile_id) is str,'CMBA_J_PROFILE_UNSUPPORTED')
    found=[c for c in contracts() if c['profile_id']==profile_id]
    require(len(found)==1,'CMBA_J_PROFILE_UNSUPPORTED')
    return found[0]


def resolve(ref):
    validate_profile_reference(ref);c=contract(ref['profile_id'])
    require(canonical(profile_reference(c))==canonical(ref),'CMBA_PROFILE_COMMITMENT_MISMATCH')
    return c


def capabilities():
    return [{'schema':'cmba.capability.j1','capability_id':c['profile_id']+'.evaluate',
             'profile':profile_reference(c),'effect_class':'PURE_READ','authority_effect':'NONE',
             'input':'binding + values + independent reader context','network':False,
             'subprocess':False,'auto_install':False,'claim_ceiling':c['claim_ceiling']} for c in contracts()]
