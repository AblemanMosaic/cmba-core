"""AUTHORING ONLY: freeze reference-assisted K1 cases. Verification never runs this."""
from pathlib import Path
import sys,json
from copy import deepcopy as cp
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical
from cmba_workbench.k1.authoring import example,author
from cmba_workbench.k1.session import Workspace
from cmba_workbench.k1 import views
from reference_k_conformance import dispatch

def main():
    cases=[]
    def add(name,op,**args):
        q={'schema':'cmba.workbench-request.k1','operation':op,'arguments':args}
        cases.append({'id':name,'request':q,'expected':dispatch(q)})
    b=example('cmba.chc.graph');a=author('cmba.generic',{'note':'example'})
    add('inspect-chc','inspect',bundle=b);add('inspect-generic','inspect',bundle=a)
    add('bind-generic','author',profile_id='cmba.generic',record={'x':True},now=0,parameters={},relations=[])
    add('evaluate-chc','evaluate',bundle=b,reader_context=b['context'])
    w=Workspace();w.load(b);w.use_demo_context();w.evaluate();packet=w.receipt_packet()
    add('replay-receipt','replay',packet=packet)
    bad=cp(packet);bad['receipt']['body']['result']['status']='AUTHORIZED'
    add('reject-forged-receipt','replay',packet=bad)
    c=cp(b);c['context']['time']['epoch']=101
    add('same-binding-different-context','compare',left=b,right=c)
    add('different-binding','compare',left=a,right=b)
    w.load(a);add('local-graph','navigate',workspace=w.snapshot(),max_nodes=64,max_edges=256)
    add('truncated-local-graph','navigate',workspace=w.snapshot(),max_nodes=1,max_edges=1)
    s=example('cmba.disclosure');v=s['values']['record']
    add('selected-disclosure','disclosure-preview',private=v,labels=['artifact'],expected_root=v['header']['disclosure_root'])
    add('wrong-disclosure-pin','disclosure-preview',private=v,labels=['artifact'],expected_root='0'*64)
    config={k:v[0] for k,v in views.DESIGN_FIELDS.items()};add('supported-components','design',configuration=config)
    for k,values in views.DESIGN_FIELDS.items():add('unsupported-'+k,'design',configuration={**config,k:values[-1]})
    q={'semantic_commitment':'0'*64,'realization_sha256':'1'*64,'corpus_sha256':'2'*64,'claimed_results':{'pass':True}}
    add('qualification-no-proof','qualification',left=q,right={**q,'realization_sha256':'3'*64})
    add('qualification-types','qualification',left=q,right={**q,'claimed_results':{'pass':1}})
    for target in ('dkn','ccp','ucm','pippi','courthouse'):add('handoff-'+target,'handoff',target=target,bundle=b,receipt_packet=packet)
    add('catalogue-is-not-engines','catalogue');add('capabilities-no-data-approval','capabilities')
    for op in ('approve','commit','write','execute','sign','fetch','publish','trust-update','load-plugin'):
        add('refuse-effect-'+op,op)
    add('unknown-profile','author',profile_id='os.system',record={},now=0,parameters={},relations=[])
    add('unknown-bundle-field','inspect',bundle={**b,'execute':'payload'})
    add('bool-node-budget','navigate',workspace=w.snapshot(),max_nodes=True,max_edges=1)
    add('no-unbounded-graph','navigate',workspace=w.snapshot(),max_nodes=999,max_edges=1)
    a2=Workspace();cc=example('cmba.consent');a2.load(cc);a2.use_demo_context();a2.evaluate();first=a2.receipt_packet()
    context=cp(cc['context']);context['time']['epoch']=201;a2.set_reader_context(context);a2.evaluate()
    add('same-object-expired-assessment','compare-receipts',left=first,right=a2.receipt_packet())
    data={'schema':'cmba.conformance-corpus.k1','oracle':'REFERENCE_ASSISTED_EXACT_CANONICAL_BYTES','scope':'READ_ONLY_K1_NOT_HOST_FILESYSTEM_OR_GUI_EQUIVALENCE','cases':cases}
    (ROOT/'interop/workbench-k1.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n');print('frozen',len(cases),'K1 cases')
if __name__=='__main__':main()
