"""Finite equal-or-conflict map reconciliation, including explicit absence semantics."""
from ..codec import canonical, clone
from ..bindings import exact, identifier
from ..errors import require
from .common import sequence, equal, outcome


def reconcile(snapshots):
    sequence(snapshots,minimum=1,limit=16);seen=set()
    for s in snapshots:
        exact(s, {'id','values'});identifier(s['id']);require(s['id'] not in seen,'CMBA_J_DUPLICATE');seen.add(s['id'])
        require(type(s['values']) is dict and len(s['values'])<=64,'CMBA_J_SNAPSHOT_LIMIT');canonical(s['values'])
    snapshots=sorted(snapshots,key=lambda s:s['id']);keys=sorted(set().union(*(s['values'].keys() for s in snapshots)))
    require(len(keys)<=64,'CMBA_J_SNAPSHOT_LIMIT')
    merged={};conflicts={}
    for key in keys:
        rows=[{'snapshot':s['id'],'present':key in s['values'],**({'value':s['values'][key]} if key in s['values'] else {})} for s in snapshots]
        if all(r['present'] for r in rows) and all(equal(r['value'],rows[0]['value']) for r in rows):merged[key]=rows[0]['value']
        else:conflicts[key]=rows
    return clone({'merged':merged,'conflicts':conflicts})


def assess(record,context):
    exact(record, {'snapshots','rule','proposed'});exact(context['policy']['parameters'],set())
    require(not context['evidence_snapshot'],'CMBA_J_UNCONSUMED_EVIDENCE')
    require(equal(record['rule'],{'id':'equal-or-conflict','version':1}),'CMBA_J_RECONCILIATION_RULE')
    expected=reconcile(record['snapshots'])
    return outcome({'reconciliation.exact-proposal':'MATCH' if equal(record['proposed'],expected) else 'CONTRADICTED'},
      {'recomputed':expected,'conflict_count':len(expected['conflicts']),'selected_winner':'NONE'},
      ceiling='Exact finite merge under equal-or-conflict with absence distinct from null. Conflicts are retained; a matching proposal is not conflict-free or globally canonical.')
