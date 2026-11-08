"""TC-J1 finite deterministic transformation graph. No native compiler/process invocation."""
import hashlib
from importlib.resources import files
from ..codec import canonical, decode
from ..bindings import exact, identifier, hex_digest
from ..errors import require
from .common import hash_value, sequence, integer, text, equal, outcome

RULES=('canonical-json','identity-utf8','concat-utf8')


def toolchain():
    raw=files('cmba_core.j1').joinpath('transforms.py').read_bytes()
    return {'id':'cmba.builtin-transforms.j1','implementation_sha256':hashlib.sha256(raw).hexdigest()}


def transform(rule, inputs):
    exact(rule, {'id','version'});identifier(rule['id']);integer(rule['version'],1,1)
    require(rule['id'] in RULES,'CMBA_J_TRANSFORM_UNSUPPORTED')
    sequence(inputs,minimum=1,limit=16)
    for value in inputs:
        require(type(value) is str,'CMBA_J_TEXT');canonical(value)
    if rule['id']!='concat-utf8':require(len(inputs)==1,'CMBA_J_TRANSFORM_ARITY')
    if rule['id']=='canonical-json':return canonical(decode(inputs[0].encode('utf-8'),canonical_required=False)).decode('utf-8')
    if rule['id']=='identity-utf8':return inputs[0]
    value=''.join(inputs);canonical(value);return value


def assess(record, context):
    exact(record, {'nodes','steps','outputs'})
    sequence(record['nodes'],minimum=1); sequence(record['steps'],minimum=1,limit=32);sequence(record['outputs'],minimum=1)
    nodes={}; checks={'chc.node-bytes':'MATCH','chc.graph':'MATCH','chc.toolchain':'MATCH','chc.recomputed-output':'MATCH'}
    for n in record['nodes']:
        exact(n, {'id','text','sha256'});identifier(n['id']);hex_digest(n['sha256']);canonical(n['text'])
        require(type(n['text']) is str and n['id'] not in nodes,'CMBA_J_GRAPH_NODE')
        if hashlib.sha256(n['text'].encode()).hexdigest()!=n['sha256']:checks['chc.node-bytes']='CONTRADICTED'
        nodes[n['id']]=n
    producers={};step_ids=set()
    for s in record['steps']:
        exact(s, {'id','inputs','output','rule','toolchain'});identifier(s['id']);identifier(s['output'])
        require(s['id'] not in step_ids and s['output'] not in producers,'CMBA_J_GRAPH_DUPLICATE')
        step_ids.add(s['id']);producers[s['output']]=s['id']
        sequence(s['inputs'],minimum=1,limit=16)
        for name in s['inputs']:identifier(name)
        require(s['output'] in nodes and all(n in nodes for n in s['inputs']),'CMBA_J_GRAPH_REFERENCE')
    available=set(nodes)-set(producers); outcomes=[]
    for s in record['steps']:
        require(all(n in available for n in s['inputs']),'CMBA_J_GRAPH_ORDER')
        exact(s['rule'], {'id','version'});identifier(s['rule']['id']);integer(s['rule']['version'])
        exact(s['toolchain'], {'id','implementation_sha256'});identifier(s['toolchain']['id']);hex_digest(s['toolchain']['implementation_sha256'])
        if not equal(s['toolchain'],toolchain()):checks['chc.toolchain']='CONTRADICTED'
        if s['rule']['id'] not in RULES or s['rule']['version']!=1:
            if checks['chc.recomputed-output']!='CONTRADICTED':checks['chc.recomputed-output']='UNSUPPORTED'
            state='UNSUPPORTED'
        else:
            output=transform(s['rule'],[nodes[n]['text'] for n in s['inputs']])
            state='MATCH' if output==nodes[s['output']]['text'] else 'CONTRADICTED'
            if state=='CONTRADICTED':checks['chc.recomputed-output']='CONTRADICTED'
        outcomes.append({'step':s['id'],'status':state});available.add(s['output'])
    require(len(set(record['outputs']))==len(record['outputs']) and all(n in producers for n in record['outputs']), 'CMBA_J_GRAPH_OUTPUT')
    # No unused state can be silently represented as an audited input/output.
    used=set(producers)|{n for s in record['steps'] for n in s['inputs']}
    require(set(nodes)==used,'CMBA_J_GRAPH_UNUSED_NODE')
    return outcome(checks, {'steps':outcomes,'output_ids':record['outputs'],'external_compiler':'NOT_INVOKED'},
      ceiling='Exact finite UTF-8/JSON graph recomputation and supplied toolchain identity; not general compilation correctness or proof of historic execution.')
