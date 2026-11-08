"""Separate-language small-core checks, with exact typed expected envelopes."""
from pathlib import Path
import random,subprocess,shutil,hashlib
import pytest
from cmba_core import canonical,decode,dimension,bind,inspect,compare
from cmba_core.bindings import reference,relation
from cmba_core.errors import Refusal
from cmba_core.registry import contract
from cmba_core import profile_reference
ROOT=Path(__file__).resolve().parents[1]
CASES=decode((ROOT/'interop/core-i1.json').read_bytes())['cases']

def node_cases(requests):
    node=shutil.which('node');assert node,'Node is mandatory for this declared qualification leg'
    raw=canonical({'schema':'cmba.conformance-requests.i1','requests':requests})
    p=subprocess.run([node,str(ROOT/'interop/node-l1/core.mjs')],input=raw,capture_output=True,timeout=20)
    assert p.returncode==0,p.stderr.decode('utf8','replace')
    return decode(p.stdout.removesuffix(b'\n'))['results']

@pytest.fixture(scope='module')
def node_frozen():return node_cases([c['request'] for c in CASES])

@pytest.mark.parametrize('index',range(len(CASES)),ids=[c['id'] for c in CASES])
def test_frozen_i1_node(index,node_frozen):
    assert canonical(node_frozen[index])==canonical(CASES[index]['expected'])

VALUES=[-(2**63),2**63-1,2**53+1,0,False,True,None,
    {'\uffff':1,'\U00010000':2,'a':3}, {'__proto__':{'polluted':True},'constructor':0},
    'e\u0301','é','\u2028\u2029','\x00\b\t\n\f\r"\\','\U0010ffff',
    {'x':None,'y':False,'z':0}, [2**53+3,-(2**53+3)], {'9':1,'10':2,'2':3}]
@pytest.mark.parametrize('value',VALUES)
def test_numeric_unicode_type_boundaries(value):
    actual=node_cases([{'operation':'canonical','arguments':{'value':value}}])[0]
    assert actual=={'status':'RESULT','value':{'hex':canonical(value).hex()}}

RAW_CASES=[(b'{"x":1,"x":2}','CMBA_DUPLICATE_KEY'),
 (b'{"__proto__":1,"__proto__":2}','CMBA_DUPLICATE_KEY'),
 (b'1.0','CMBA_NUMBER_INVALID'),(b'1e0','CMBA_NUMBER_INVALID'),
 (b'NaN','CMBA_NUMBER_INVALID'),(b'Infinity','CMBA_NUMBER_INVALID'),
 (b'-0','CMBA_NOT_CANONICAL'),(b' 0','CMBA_NOT_CANONICAL'),
 (b'{"z":0,"a":1}','CMBA_NOT_CANONICAL'),(b'"\\u0061"','CMBA_NOT_CANONICAL'),
 (b'"\\ud800"','CMBA_STRING_INVALID'),(b'"\\udfff"','CMBA_STRING_INVALID'),
 (b'"\xed\xa0\x80"','CMBA_JSON_INVALID'),(b'\xef\xbb\xbf0','CMBA_JSON_INVALID'),
 (b'01','CMBA_JSON_INVALID'),(b'[]x','CMBA_JSON_INVALID'),
 (str(2**63).encode(),'CMBA_INTEGER_RANGE'),(str(-2**63-1).encode(),'CMBA_INTEGER_RANGE'),
 (b'['*34+b'0'+b']'*34,'CMBA_DEPTH_LIMIT')]
@pytest.mark.parametrize('raw,code',RAW_CASES)
def test_raw_negative_oracles(raw,code):
    with pytest.raises(Refusal) as e:decode(raw)
    assert e.value.code==code
    actual=node_cases([{'operation':'decode','arguments':{'hex':raw.hex()}}])[0]
    assert actual=={'status':'REFUSED','code':code}

@pytest.mark.parametrize('seed',range(16))
def test_binding_relationship_differential(seed):
    rng=random.Random(seed);values={'field'+str(i):{'n':rng.randrange(-(2**63),2**63),'flag':bool(i%2),'text':'λ🙂'+str(i)} for i in range(1+seed%5)}
    dims=[dimension(k,'metadata','example.record.l1',v,critical=bool(i%2)) for i,(k,v) in enumerate(values.items())]
    rng.shuffle(dims);rels=[relation('edge'+str(i),'depends-on',reference('example.native',hashlib.sha256(str(i).encode()).hexdigest())) for i in range(seed%4)]
    p=profile_reference(contract('cmba.generic'));b=bind(p,dims,relations=rels)
    altered=bind(p,[dimension('replacement','metadata','example.record.l1',seed)])
    requests=[{'operation':'bind','arguments':{'profile':p,'dimensions':dims,'relations':rels}},
        {'operation':'inspect','arguments':{'binding':b,'values':values,'expected_root':b['binding_root']}},
        {'operation':'compare','arguments':{'left':b,'right':altered}}]
    expected=[b,inspect(b,values,expected_root=b['binding_root']),compare(b,altered)]
    assert canonical(node_cases(requests))==canonical([{'status':'RESULT','value':v} for v in expected])

@pytest.mark.parametrize('change',['codec','critical-type','algorithm','dimension-order','self-hash','extra-field','reference-algorithm','profile'])
def test_binding_mutation_refusals(change):
    b=bind(profile_reference(contract('cmba.generic')),[dimension('a','state','example.a',1),dimension('b','metadata','example.b',2)],relations=[relation('edge','depends-on',reference('example.native','1'*64))])
    if change=='codec':b['body']['dimensions'][0]['codec']='jcs'
    elif change=='critical-type':b['body']['dimensions'][0]['critical']=1
    elif change=='algorithm':b['body']['dimensions'][0]['algorithm']='SHA-1'
    elif change=='dimension-order':b['body']['dimensions'].reverse()
    elif change=='self-hash':b['binding_root']='0'*64
    elif change=='extra-field':b['metadata']={}
    elif change=='reference-algorithm':b['body']['relations'][0]['target']['algorithm']='MD5'
    else:b['body']['profile']['contract_hash']='not-a-hash'
    with pytest.raises(Refusal) as e:inspect(b)
    assert node_cases([{'operation':'inspect','arguments':{'binding':b,'values':{},'expected_root':None}}])[0]=={'status':'REFUSED','code':e.value.code}
