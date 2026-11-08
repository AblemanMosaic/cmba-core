"""EXPLICIT AUTHORING ONLY. Reference-assisted exact fixtures, NOT independent evidence.

Human-specified expected assessment/refusal classes are asserted before freezing full results.
Verification tools never run this file or change expectations.
"""
from pathlib import Path
from copy import deepcopy as cp
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical
from cmba_core.j1 import demo
from cmba_core.j1.evaluation import bind_application
from cmba_core.j1.common import hash_value
from reference_j_conformance import dispatch


def request(op,arguments):return {'schema':'cmba.request.j1','operation':op,'arguments':arguments}

def build():
    cases=[]
    def add(name,req,status=None,refusal=False):
        out=dispatch(req)
        if refusal:assert out['status']=='REFUSED',(name,out)
        elif status is not None:assert out['value']['body']['result']['status']==status,(name,out)
        else:assert out['status']=='RESULT',(name,out)
        cases.append({'id':name,'request':req,'expected':out})
    bundles=demo.all_bundles()
    for name,b in bundles.items():
        add(name+'.match',request('evaluate',b),'NATIVE_REPORT_COMPUTED' if name=='cmba.native-dkn' else 'MATCH_FOR_SUPPLIED_EVIDENCE')
        bad=cp(b);bad['context']['expected_binding_root']='0'*64
        add(name+'.wrong-reader-pin',request('evaluate',bad),refusal=True)
        bad=cp(b);bad['values']={}
        add(name+'.missing-record',request('evaluate',bad),'INSUFFICIENT')
    b=demo.kasd();b['context']['evidence_snapshot']=[];add('joint.missing-approvals',request('evaluate',b),'INSUFFICIENT')
    b=demo.consent();b['context']['time']['epoch']=200;add('consent.expired',request('evaluate',b),'NO_MATCH')
    b=demo.disclosure();b['context']['policy']['parameters']['required_labels']=['private-notes'];add('disclosure.missing-label',request('evaluate',b),'INSUFFICIENT')
    for effect in ('execute','sign','fetch','write','install'):add('effect.'+effect,request(effect,{}),refusal=True)
    b=demo.graph();r=dispatch(request('evaluate',b))['value'];r['body']['result']['authority_effect']='EXECUTE';r['receipt_hash']=hash_value('receipt',r['body'])
    add('replay.rehashed-forgery',request('replay',{'receipt':r,**b}),refusal=True)
    b=demo.graph();r=dispatch(request('evaluate',b))['value'];add('replay.correct',request('replay',{'receipt':r,**b}))
    for op in ('profiles','capabilities'):add(op,request(op,{}))
    # Public statement and proof transport separately exercised.
    b=demo.endorsement();add('signature.valid',request('verify-statement',{'record':b['context']['evidence_snapshot'][0]}))
    b=demo.disclosure();v=b['values']['record'];add('disclosure.valid',request('verify-disclosure',{'view':v,'expected_root':v['header']['disclosure_root']}))
    data={'schema':'cmba.conformance-corpus.j1','provenance':'PUBLIC_TEST_FIXTURES_REFERENCE_ASSISTED_NOT_EQUIVALENCE_PROOF',
          'authority_effect':'NONE','cases':cases}
    (ROOT/'interop/applications-j1.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    examples=ROOT/'examples/j1';examples.mkdir(exist_ok=True)
    for name,b in bundles.items():(examples/(name+'.json')).write_bytes(canonical({'schema':'cmba.workbench-bundle.j1',**b}))
    print('frozen cases',len(cases),'public application bundles',len(bundles))
if __name__=='__main__':build()
