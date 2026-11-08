"""K1 closed READ-ONLY data interface. No file path, approval, signing or execution."""
from cmba_core.bindings import exact
from cmba_core import canonical,Refusal
from cmba_core.codec import clone
from cmba_core.errors import require
from .session import Workspace,admit_bundle,engine
from .views import capabilities,catalogue,design,qualification,preview_disclosure,handoff,matrix,compare_receipts,installed_qualification
from .authoring import author


def dispatch(request):
    canonical(request);exact(request,{'schema','operation','arguments'})
    require(request['schema']=='cmba.workbench-request.k1','CMBA_K_REQUEST_SCHEMA')
    op=request['operation'];a=request['arguments']
    require(type(op) is str and type(a) is dict,'CMBA_K_REQUEST_TYPE')
    if op=='inspect':
        exact(a,{'bundle'});return admit_bundle(a['bundle'])
    if op=='author':
        exact(a,{'profile_id','record','now','parameters','relations'});return author(**a)
    if op=='evaluate':
        exact(a,{'bundle','reader_context'});w=Workspace();w.load(a['bundle']);w.set_reader_context(a['reader_context']);return w.evaluate()
    if op=='replay':
        exact(a,{'packet'});w=Workspace();w.import_receipt(a['packet']);return w.replay_history(0)
    if op=='compare-receipts':exact(a,{'left','right'});return compare_receipts(**a)
    if op=='installed-qualification':exact(a,set());return installed_qualification()
    if op=='compare':
        exact(a,{'left','right'});w=Workspace();l=w.load(a['left'])['document_id'];r=w.load(a['right'])['document_id'];return w.compare_documents(l,r)
    if op=='navigate':
        exact(a,{'workspace','max_nodes','max_edges'});w=Workspace();w.restore(a['workspace']);return w.navigate(max_nodes=a['max_nodes'],max_edges=a['max_edges'])
    if op=='disclosure-preview':
        exact(a,{'private','labels','expected_root'});return preview_disclosure(**a)
    if op=='design':exact(a,{'configuration'});return design(a['configuration'])
    if op=='qualification':exact(a,{'left','right'});return qualification(**a)
    if op=='handoff':exact(a,{'target','bundle','receipt_packet'});return handoff(**a)
    if op=='capabilities':exact(a,set());return {'capabilities':capabilities(),'authority_effect':'NONE'}
    if op=='catalogue':exact(a,set());return catalogue()
    raise Refusal('CMBA_K_OPERATION_UNSUPPORTED')
