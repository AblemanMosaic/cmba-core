"""AUTHORING ONLY: no verifier imports or calls this generator."""
from pathlib import Path
import sys, json, copy
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import *
from cmba_core.registry import contract
from cmba_core.demo import chc,session
from reference_conformance import dispatch


def build():
    cases=[]
    def add(name,op,args):
        request={'operation':op,'arguments':args}
        cases.append({'id':name,'request':request,'expected':dispatch(request)})
    for i,value in enumerate([None,False,True,0,-1,2**63-1,-2**63,'é','e\u0301',{'\ue000':0,'\U00010000':1},[None,False,0]]):
        add(f'canonical-{i:02}','canonical',{'value':value})
    for i,raw in enumerate([b'{"x":1,"x":2}',b'null\n',b'-0',b'1.0',b'{',b'"\\ud800"',b'null',b'false',b'1']):
        add(f'decode-{i:02}','decode',{'hex':raw.hex()})
    args={'dimension_id':'state','role':'state','schema_id':'example.state.v1','value':{'answer':42},'critical':False}
    for field,val in [(None,None),('role','contract'),('value',False),('value',0),('critical',True)]:
        copy_args=copy.deepcopy(args)
        if field is not None:copy_args[field]=val
        add(f'dimension-{len(cases):02}','dimension',copy_args)
    p=profile_reference(contract('cmba.generic'));d=dimension(**args);b=bind(p,[d])
    add('bind-single','bind',{'profile':p,'dimensions':[d],'relations':[]})
    add('bind-duplicate','bind',{'profile':p,'dimensions':[d,d],'relations':[]})
    add('inspect-missing','inspect',{'binding':b,'values':{},'expected_root':None})
    add('inspect-value','inspect',{'binding':b,'values':{'state':args['value']},'expected_root':b['binding_root']})
    add('inspect-wrong-pin','inspect',{'binding':b,'values':{},'expected_root':'0'*64})
    add('inspect-wrong-value','inspect',{'binding':b,'values':{'state':True},'expected_root':None})
    add('compare-equal','compare',{'left':b,'right':b})
    changed=bind(p,[dimension('state','state','example.state.v1',0,critical=False)])
    add('compare-changed','compare',{'left':b,'right':changed})
    return {'schema':'cmba.conformance-corpus.i1','claim_ceiling':'FINITE_REFERENCE_ASSISTED_EXPECTATIONS_NOT_EQUIVALENCE_PROOF','cases':cases}

if __name__=='__main__':
    corpus=build();(ROOT/'interop/core-i1.json').write_bytes(canonical(corpus))
    for name,b in [('chc-correct',chc()),('chc-incorrect',chc(wrong_output=True)),('session',session())]:
        (ROOT/'examples'/f'{name}.json').write_bytes(canonical(b))
    print(len(corpus['cases']),'frozen stable-core cases')
