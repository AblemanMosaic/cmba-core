"""SD-J1 salted finite Merkle inclusion. Inclusion is neither encryption nor authorization.

Fresh independent 32-byte salts are generated only by explicit constructor calls.
The header reveals item count. Disclosed openings reveal their salt/label/value.
"""
import secrets
from ..codec import canonical, clone
from ..bindings import exact, hex_digest, identifier
from ..errors import require
from .common import hash_value, sequence, integer, hex_bytes, unique_strings, outcome


def _leaf(value):
    exact(value, {'schema','index','label','schema_id','value','salt_hex'})
    require(value['schema']=='cmba.disclosure-leaf.j1','CMBA_J_DISCLOSURE_SCHEMA')
    integer(value['index'],0,63); identifier(value['label']); identifier(value['schema_id'])
    hex_bytes(value['salt_hex'],size=32); canonical(value['value'])
    return hash_value('disclosure-leaf',value)


def _node(left,right):
    return hash_value('disclosure-node', {'left':left,'right':right})


def make(entries, *, salts=None):
    sequence(entries, minimum=1); labels=[]
    for e in entries:
        exact(e, {'label','schema_id','value'}); identifier(e['label']); identifier(e['schema_id']);canonical(e['value'])
        labels.append(e['label'])
    require(len(set(labels))==len(labels),'CMBA_J_DUPLICATE')
    entries=sorted(clone(entries),key=lambda e:e['label'])
    if salts is None: salts=[secrets.token_bytes(32).hex() for _ in entries]
    sequence(salts);require(len(salts)==len(entries),'CMBA_J_DISCLOSURE_SALTS')
    for salt in salts: hex_bytes(salt,size=32)
    require(len(salts)==len(set(salts)), 'CMBA_J_DISCLOSURE_SALT_REUSE')
    leaves=[{'schema':'cmba.disclosure-leaf.j1','index':i,**e,'salt_hex':salts[i]} for i,e in enumerate(entries)]
    count=len(leaves); width=1 << (count-1).bit_length()
    first=[_leaf(v) for v in leaves] + [hash_value('disclosure-empty',{'index':i}) for i in range(count,width)]
    levels=[first]
    while len(levels[-1])>1:
        last=levels[-1];levels.append([_node(last[i],last[i+1]) for i in range(0,len(last),2)])
    header={'schema':'cmba.disclosure-header.j1','leaf_count':count,'merkle_root':levels[-1][0]}
    header['disclosure_root']=hash_value('disclosure-root',header)
    openings=[]
    for leaf in leaves:
        path=[];pos=leaf['index']
        for level in levels[:-1]:
            path.append({'side':'left' if pos%2 else 'right','hash':level[pos^1]});pos//=2
        openings.append({'leaf':leaf,'path':path})
    return {'header':header,'openings':openings}


def header(value):
    exact(value, {'schema','leaf_count','merkle_root','disclosure_root'})
    require(value['schema']=='cmba.disclosure-header.j1','CMBA_J_DISCLOSURE_SCHEMA')
    integer(value['leaf_count'],1,64);hex_digest(value['merkle_root']);hex_digest(value['disclosure_root'])
    b={k:value[k] for k in ('schema','leaf_count','merkle_root')}
    require(hash_value('disclosure-root',b)==value['disclosure_root'],'CMBA_J_DISCLOSURE_ROOT')


def select(bundle, labels):
    header(bundle['header']); unique_strings(labels)
    found={o['leaf']['label']:o for o in bundle['openings']}
    require(set(labels)<=found.keys(),'CMBA_J_DISCLOSURE_LABEL')
    return {'header':clone(bundle['header']),'openings':[clone(found[label]) for label in sorted(labels)]}


def verify(view, *, expected_root):
    canonical(view);exact(view, {'header','openings'});header(view['header']);hex_digest(expected_root)
    h=view['header'];require(h['disclosure_root']==expected_root,'CMBA_J_DISCLOSURE_PIN')
    sequence(view['openings']);seen=set();labels=set();depth=(h['leaf_count']-1).bit_length()
    for opening in view['openings']:
        exact(opening, {'leaf','path'}); leaf=opening['leaf']; cur=_leaf(leaf); pos=leaf['index']
        require(pos<h['leaf_count'] and pos not in seen and leaf['label'] not in labels,'CMBA_J_DISCLOSURE_DUPLICATE')
        seen.add(pos);labels.add(leaf['label']);sequence(opening['path'],limit=6)
        require(len(opening['path'])==depth,'CMBA_J_DISCLOSURE_PATH')
        for sibling in opening['path']:
            exact(sibling, {'side','hash'});hex_digest(sibling['hash'])
            side='left' if pos%2 else 'right'
            require(sibling['side']==side,'CMBA_J_DISCLOSURE_PATH')
            cur=_node(sibling['hash'],cur) if side=='left' else _node(cur,sibling['hash']);pos//=2
        require(cur==h['merkle_root'],'CMBA_J_DISCLOSURE_PROOF')
    return outcome({'disclosure.inclusion':'MATCH'}, {'root':expected_root,'disclosed_labels':sorted(labels),
             'disclosed_count':len(seen),'committed_count':h['leaf_count'],'all_entries_disclosed':len(seen)==h['leaf_count'],
             'confidentiality':'NOT_ESTABLISHED','unlinkability':'NOT_ESTABLISHED','authentication':'NOT_CHECKED'},
             ceiling='Selected exact openings included in the reader-pinned salted tree. No encryption, completeness of original data, deletion, or access enforcement.')
